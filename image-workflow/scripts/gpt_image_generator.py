#!/usr/bin/env python3
"""
GPT-Image-2 图像生成工具

通过 APIMart API 生成 AI 图像，支持异步批量生成。
每张图片生成完成后立即下载到本地，全部完成后结束。

Usage:
    python gpt_image_generator.py "a cute cat"
    python gpt_image_generator.py "a sunset" --n 3 --size 16:9
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv


API_BASE_URL = "https://api.apimart.ai/v1"
TASK_STATUS_URL = f"{API_BASE_URL}/tasks"

SIZES = ["1:1", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "16:9", "9:16", "2:1", "1:2", "3:1", "1:3", "21:9", "9:21"]
DEFAULT_OUTPUT_DIR = "generated_images"


@dataclass
class GenerationTask:
    task_id: str
    prompt: str
    size: str
    resolution: str


@dataclass
class GenerationResult:
    task_id: str
    prompt: str
    size: str
    resolution: str
    status: str
    url: str = ""
    local_path: str = ""
    error: str = ""


@dataclass
class ProgressTracker:
    """线程安全的进度追踪器。"""
    total: int
    completed: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def increment(self) -> None:
        with self.lock:
            self.completed += 1

    def get_progress(self) -> tuple[int, int]:
        with self.lock:
            return self.completed, self.total


def load_environment() -> Optional[str]:
    """Load API key from .env file."""
    script_dir = Path(__file__).parent.resolve()
    load_dotenv(script_dir / ".env")
    api_key = os.getenv("APIMART_API_KEY")
    if not api_key:
        raise RuntimeError(
            "APIMART_API_KEY not found. Set it in .env file:\n"
            "APIMART_API_KEY=your_api_key_here"
        )
    return api_key


def setup_logging(verbose: bool) -> None:
    import logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_random_size() -> str:
    """随机选择一个图像比例。"""
    return random.choice(SIZES)


def submit_task(
    api_key: str,
    prompt: str,
    size: str,
    resolution: str,
    image_urls: Optional[list[str]] = None,
    official_fallback: bool = False,
) -> GenerationTask:
    """提交图像生成任务。"""
    url = f"{API_BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "resolution": resolution,
        "official_fallback": official_fallback,
    }
    if image_urls:
        payload["image_urls"] = image_urls

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    if data.get("code") != 200:
        error = data.get("error", {})
        raise RuntimeError(f"API Error {error.get('code')}: {error.get('message')}")

    task_data = data["data"][0]
    return GenerationTask(
        task_id=task_data["task_id"],
        prompt=prompt,
        size=size,
        resolution=resolution,
    )


def poll_task(api_key: str, task_id: str, max_wait: int = 300) -> dict:
    """轮询任务状态。"""
    headers = {"Authorization": f"Bearer {api_key}"}
    start_time = time.time()
    poll_interval = 3

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            raise TimeoutError(f"Task {task_id} timed out after {max_wait}s")

        response = requests.get(f"{TASK_STATUS_URL}/{task_id}", headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 200:
            error = data.get("error", {})
            raise RuntimeError(f"API Error {error.get('code')}: {error.get('message')}")

        task_data = data["data"]
        status = task_data.get("status")

        if status == "completed":
            result = task_data.get("result", {})
            images = result.get("images", [])
            if images and images[0].get("url"):
                return {"status": "completed", "url": images[0]["url"][0]}
            raise RuntimeError(f"Task completed but no image URL found")

        if status == "failed":
            error_msg = task_data.get("error", {}).get("message", "Unknown error")
            return {"status": "failed", "error": error_msg}

        if status == "cancelled":
            return {"status": "cancelled", "error": "Task was cancelled"}

        time.sleep(poll_interval)


def download_image(url: str, output_path: Path, timeout: int = 120) -> Path:
    """下载图片到本地。"""
    response = requests.get(url, timeout=timeout, stream=True)
    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path


def process_single_image(
    api_key: str,
    prompt: str,
    size: str,
    resolution: str,
    output_dir: Path,
    image_urls: Optional[list[str]],
    official_fallback: bool,
    max_wait: int,
    progress: ProgressTracker,
    index: int,
) -> GenerationResult:
    """
    处理单张图片：提交任务 -> 等待完成 -> 下载 -> 返回结果。
    在线程池中独立运行。
    """
    import logging

    try:
        # 1. 提交任务
        task = submit_task(
            api_key=api_key,
            prompt=prompt,
            size=size,
            resolution=resolution,
            image_urls=image_urls,
            official_fallback=official_fallback,
        )
        logging.info("[%s] Task submitted: %s", index, task.task_id)

        # 2. 轮询状态
        logging.info("[%s] Waiting for completion...", index)
        result_data = poll_task(api_key, task.task_id, max_wait=max_wait)

        # 3. 下载图片
        if result_data["status"] == "completed":
            safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in prompt[:30])
            output_path = output_dir / f"{safe_name}_{task.task_id[-8:]}.png"
            local_path = download_image(result_data["url"], output_path)
            logging.info("[%s] Downloaded: %s", index, local_path)

            return GenerationResult(
                task_id=task.task_id,
                prompt=prompt,
                size=size,
                resolution=resolution,
                status="completed",
                url=result_data["url"],
                local_path=str(local_path),
            )
        else:
            return GenerationResult(
                task_id=task.task_id,
                prompt=prompt,
                size=size,
                resolution=resolution,
                status=result_data["status"],
                error=result_data.get("error", "Unknown error"),
            )

    except Exception as exc:
        logging.error("[%s] Error: %s", index, exc)
        return GenerationResult(
            task_id="",
            prompt=prompt,
            size=size,
            resolution=resolution,
            status="failed",
            error=str(exc),
        )
    finally:
        progress.increment()


def print_summary(results: list[GenerationResult], progress: ProgressTracker) -> None:
    """打印最终汇总信息。"""
    completed, total = progress.get_progress()
    completed_list = [r for r in results if r.status == "completed"]
    failed_list = [r for r in results if r.status != "completed"]

    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    print(f"Total: {total}  |  Completed: {len(completed_list)}  |  Failed: {len(failed_list)}")
    print("-" * 70)

    for i, result in enumerate(results, 1):
        status_icon = "OK" if result.status == "completed" else "FAIL"
        print(f"[{status_icon}] {i}. {result.prompt[:40]}...")
        if result.status == "completed":
            print(f"     {result.local_path}")

    print("=" * 70)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="GPT-Image-2 异步图像生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python gpt_image_generator.py "a cute cat"
    python gpt_image_generator.py "a sunset" --n 3
    python gpt_image_generator.py "a building" --n 5 --size 16:9 --resolution 2k
        """,
    )
    parser.add_argument("prompt", help="图像描述文本")
    parser.add_argument("--n", type=int, default=1, help="生成数量 (默认: 1)")
    parser.add_argument(
        "--size",
        default="random",
        help=f"图像比例，支持14种比例，也可设置 random 随机选择 (默认: random)"
    )
    parser.add_argument(
        "--resolution",
        default="1k",
        choices=["1k", "2k", "4k"],
        help="输出分辨率 (默认: 1k)"
    )
    parser.add_argument(
        "--image-urls",
        nargs="+",
        help="参考图 URL(s)，用于图生图模式"
    )
    parser.add_argument(
        "--official-fallback",
        action="store_true",
        help="官方渠道兜底"
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"图片保存目录 (默认: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=300,
        help="单个任务最大等待时间，秒 (默认: 300)"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="并发任务数 (默认: 3)"
    )
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")

    args = parser.parse_args(argv)

    import logging
    setup_logging(args.verbose)

    try:
        # Load API key
        api_key = load_environment()
        logging.info("API key loaded")

        # Prepare output directory
        output_dir = Path(args.output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Determine sizes
        if args.size == "random":
            sizes = [get_random_size() for _ in range(args.n)]
            logging.info("Random sizes: %s", sizes)
        else:
            if args.size not in SIZES:
                raise ValueError(f"Invalid size. Must be one of: {SIZES + ['random']}")
            sizes = [args.size] * args.n

        # Print header
        print("\n" + "=" * 70)
        print(f"Generating {args.n} image(s) with {args.concurrency} concurrent tasks")
        print(f"Prompt: {args.prompt}")
        print("=" * 70)

        # Progress tracker
        progress = ProgressTracker(total=args.n)
        results: list[GenerationResult] = []

        # Use thread pool for async processing
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = []
            for i in range(args.n):
                future = executor.submit(
                    process_single_image,
                    api_key,
                    args.prompt,
                    sizes[i],
                    args.resolution,
                    output_dir,
                    args.image_urls,
                    args.official_fallback,
                    args.max_wait,
                    progress,
                    i + 1,
                )
                futures.append(future)

            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                completed, total = progress.get_progress()
                print(f"\n[Progress: {completed}/{total}] {result.prompt[:50]}... -> {result.status}")

        # Print final summary
        print_summary(results, progress)

        # Exit code
        failed_count = len([r for r in results if r.status != "completed"])
        return 0 if failed_count == 0 else 1

    except Exception as exc:
        logging.exception("Error: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())