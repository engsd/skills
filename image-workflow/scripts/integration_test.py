#!/usr/bin/env python3
"""
GPT-Image-2 图片生成 → Cloudinary 上传 完整流程测试

1. 并行生成 N 张图片
2. 下载到本地
3. 根据提示词重命名
4. 上传到 Cloudinary
5. 返回 URL

Usage:
    python integration_test.py "a sunset over ocean"
    python integration_test.py "a modern building" --n 2
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv


# ============ GPT-Image-2 配置 ============
API_BASE_URL = "https://api.apimart.ai/v1"
TASK_STATUS_URL = f"{API_BASE_URL}/tasks"
SIZES = ["1:1", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "16:9", "9:16", "2:1", "1:2", "3:1", "1:3", "21:9", "9:21"]


@dataclass
class GenerationResult:
    task_id: str
    prompt: str
    size: str
    resolution: str
    status: str
    url: str = ""
    local_path: str = ""
    cloudinary_url: str = ""
    error: str = ""


@dataclass
class ProgressTracker:
    total: int
    completed: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def increment(self) -> None:
        with self.lock:
            self.completed += 1

    def get_progress(self) -> tuple[int, int]:
        with self.lock:
            return self.completed, self.total


# ============ 通用工具函数 ============

def load_env_file(env_path: Path) -> dict[str, str]:
    """加载 .env 文件到字典。"""
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def setup_logging(verbose: bool) -> None:
    import logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_random_size() -> str:
    return random.choice(SIZES)


def sanitize_filename(text: str, max_len: int = 50) -> str:
    """根据提示词生成安全的文件名。"""
    # 取前 max_len 个字符
    name = text[:max_len]
    # 替换不安全字符
    name = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
    name = name.strip("._- ")
    return name or "image"


# ============ GPT-Image-2 函数 ============

def submit_task(
    api_key: str,
    prompt: str,
    size: str,
    resolution: str,
) -> str:
    """提交图像生成任务，返回 task_id。"""
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
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    if data.get("code") != 200:
        error = data.get("error", {})
        raise RuntimeError(f"API Error {error.get('code')}: {error.get('message')}")

    return data["data"][0]["task_id"]


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
            return {"status": "failed", "error": task_data.get("error", {}).get("message", "Unknown error")}

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


# ============ Cloudinary 函数 ============

def upload_to_cloudinary(image_path: Path, cloud_name: str, api_key: str, api_secret: str) -> str:
    """上传图片到 Cloudinary，返回 URL。"""
    import cloudinary
    import cloudinary.uploader

    # 配置 Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )

    # 上传文件
    result = cloudinary.uploader.upload(
        str(image_path),
        resource_type="image",
        folder="ai-generated",
    )

    return result.get("secure_url", "")


# ============ 主流程函数 ============

def process_single_image(
    apikey: str,
    cloud_name: str,
    api_key: str,
    api_secret: str,
    prompt: str,
    size: str,
    resolution: str,
    output_dir: Path,
    max_wait: int,
    progress: ProgressTracker,
    index: int,
) -> GenerationResult:
    """处理单张图片：生成 → 下载 → 重命名 → 上传。"""
    import logging

    try:
        # 1. 提交任务
        logging.info("[%s] Submitting task...", index)
        task_id = submit_task(apikey, prompt, size, resolution)
        logging.info("[%s] Task submitted: %s", index, task_id)

        # 2. 轮询状态
        logging.info("[%s] Waiting for completion...", index)
        result_data = poll_task(apikey, task_id, max_wait=max_wait)

        if result_data["status"] != "completed":
            return GenerationResult(
                task_id=task_id,
                prompt=prompt,
                size=size,
                resolution=resolution,
                status=result_data["status"],
                error=result_data.get("error", "Unknown error"),
            )

        # 3. 下载临时文件
        temp_path = output_dir / f"temp_{task_id[-8:]}.png"
        download_image(result_data["url"], temp_path)
        logging.info("[%s] Downloaded to temp file", index)

        # 4. 根据提示词重命名
        safe_name = sanitize_filename(prompt)
        final_path = output_dir / f"{safe_name}_{task_id[-8:]}.png"
        shutil.move(temp_path, final_path)
        logging.info("[%s] Renamed to: %s", index, final_path.name)

        # 5. 上传到 Cloudinary
        logging.info("[%s] Uploading to Cloudinary...", index)
        cloudinary_url = upload_to_cloudinary(final_path, cloud_name, api_key, api_secret)
        logging.info("[%s] Uploaded: %s", index, cloudinary_url)

        return GenerationResult(
            task_id=task_id,
            prompt=prompt,
            size=size,
            resolution=resolution,
            status="completed",
            url=result_data["url"],
            local_path=str(final_path),
            cloudinary_url=cloudinary_url,
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


def print_summary(results: list[GenerationResult]) -> None:
    """打印汇总报告。"""
    completed = [r for r in results if r.status == "completed"]
    failed = [r for r in results if r.status != "completed"]

    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    print(f"Total: {len(results)}  |  Completed: {len(completed)}  |  Failed: {len(failed)}")
    print("-" * 70)

    for i, result in enumerate(results, 1):
        status_icon = "OK" if result.status == "completed" else "FAIL"
        prompt_preview = result.prompt[:40]
        print(f"\n[{status_icon}] {i}. {prompt_preview}...")
        if result.status == "completed":
            print(f"     Local:  {result.local_path}")
            print(f"     Cloud:  {result.cloudinary_url}")
        else:
            print(f"     Error: {result.error}")

    print("\n" + "=" * 70)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="GPT-Image-2 → Cloudinary 完整流程测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python integration_test.py "a sunset over ocean"
    python integration_test.py "a modern building" --n 2 --resolution 2k
        """,
    )
    parser.add_argument("prompt", help="图像描述文本")
    parser.add_argument("--n", type=int, default=2, help="生成数量 (默认: 2)")
    parser.add_argument("--size", default="random", help="图像比例 (默认: random)")
    parser.add_argument("--resolution", default="1k", choices=["1k", "2k", "4k"], help="分辨率 (默认: 1k)")
    parser.add_argument("--output-dir", default="integration_test_output", help="输出目录 (默认: integration_test_output)")
    parser.add_argument("--max-wait", type=int, default=300, help="单个任务最大等待时间 (默认: 300)")
    parser.add_argument("--concurrency", type=int, default=3, help="并发任务数 (默认: 3)")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")

    args = parser.parse_args(argv)

    import logging
    setup_logging(args.verbose)

    try:
        # 加载配置
        script_dir = Path(__file__).parent.resolve()
        load_dotenv(script_dir / ".env")

        apikey = os.getenv("APIMART_API_KEY")
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")

        if not apikey:
            raise RuntimeError("APIMART_API_KEY not found in .env")
        if not cloud_name or not api_key or not api_secret:
            raise RuntimeError("Cloudinary credentials not found in .env")

        logging.info("Configuration loaded")

        # 准备输出目录
        output_dir = Path(args.output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # 确定尺寸
        if args.size == "random":
            sizes = [get_random_size() for _ in range(args.n)]
        else:
            sizes = [args.size] * args.n

        # 打印头部
        print("\n" + "=" * 70)
        print(f"INTEGRATION TEST: Generate → Download → Rename → Upload")
        print("=" * 70)
        print(f"Prompt: {args.prompt}")
        print(f"Count: {args.n}  |  Size: {args.size}  |  Resolution: {args.resolution}")
        print(f"Output: {output_dir}")
        print("=" * 70)

        # 进度追踪
        progress = ProgressTracker(total=args.n)
        results: list[GenerationResult] = []

        # 并行处理
        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = []
            for i in range(args.n):
                future = executor.submit(
                    process_single_image,
                    apikey,
                    cloud_name,
                    api_key,
                    api_secret,
                    args.prompt,
                    sizes[i],
                    args.resolution,
                    output_dir,
                    args.max_wait,
                    progress,
                    i + 1,
                )
                futures.append(future)

            # 收集结果
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                completed, total = progress.get_progress()
                status = "OK" if result.status == "completed" else "FAIL"
                print(f"\n[Progress: {completed}/{total}] [{status}] {result.prompt[:50]}...")

        # 打印汇总
        print_summary(results)

        # 返回码
        failed_count = len([r for r in results if r.status != "completed"])
        return 0 if failed_count == 0 else 1

    except Exception as exc:
        logging.exception("Error: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())