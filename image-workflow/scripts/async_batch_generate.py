#!/usr/bin/env python3
"""
Submit GPT-Image-2 jobs asynchronously, poll them as a batch, download results,
upload to Cloudinary, and optionally replace markdown image placeholders.

Input prompt JSON is an array of objects. Required fields:
  id, placeholder, prompt
Optional fields:
  style_key, aspect_ratio, alt, title, style_theme, subtheme

Usage:
  python async_batch_generate.py --prompts prompts.json --article article.md
  python async_batch_generate.py --prompts prompts.json --submit-concurrency 3

Default output layout:
  C:/Users/eng/Desktop/output-html/images/  downloaded PNGs
  C:/Users/eng/Desktop/output-html/json/    prompts and results JSON
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from requests import RequestException

from generate_and_upload import (
    API_BASE_URL,
    RESOLUTION,
    apply_style,
    download_image,
    load_env,
    submit_task,
    upload_to_cloudinary,
)


BATCH_TASK_STATUS_URL = f"{API_BASE_URL}/tasks/batch"
SINGLE_TASK_STATUS_URL = f"{API_BASE_URL}/tasks"
TERMINAL_STATUSES = {"completed", "failed", "cancelled"}
DEFAULT_OUTPUT_ROOT = Path("C:/Users/eng/Desktop/output-html")


def resolve_output_layout(output_dir_arg: str, results_arg: str | None, prompts_path: Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir_arg)

    # Keep the shared output folder tidy by default. If callers pass an
    # explicit images directory, honor it; otherwise put image files under it.
    image_dir = output_dir if output_dir.name.lower() == "images" else output_dir / "images"

    if results_arg:
        results_path = Path(results_arg)
    else:
        json_dir = output_dir.parent / "json" if output_dir.name.lower() == "images" else output_dir / "json"
        results_path = json_dir / f"{prompts_path.stem}_results.json"

    return image_dir, results_path


@dataclass
class ImageJob:
    data: dict[str, Any]
    index: int
    styled_prompt: str = ""
    task_id: str = ""
    apimart_url: str = ""
    local_path: str = ""
    cloudinary_url: str = ""
    status: str = "pending"
    error: str = ""
    task: dict[str, Any] = field(default_factory=dict)

    @property
    def image_id(self) -> Any:
        return self.data.get("id", self.index)

    @property
    def placeholder(self) -> str:
        return str(self.data.get("placeholder", f"IMAGE_PLACEHOLDER_{self.image_id}"))

    @property
    def alt(self) -> str:
        return str(self.data.get("alt", self.data.get("title", f"Generated image {self.image_id}")))


def read_prompt_jobs(path: Path) -> list[ImageJob]:
    items = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(items, list) or not items:
        raise ValueError("Prompt JSON must be a non-empty array.")

    jobs: list[ImageJob] = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Prompt item #{index} must be an object.")
        if not item.get("prompt"):
            raise ValueError(f"Prompt item #{index} is missing required field: prompt")
        if not item.get("placeholder"):
            item["placeholder"] = f"IMAGE_PLACEHOLDER_{item.get('id', index)}"
        jobs.append(ImageJob(data=item, index=index))
    return jobs


def write_json(path: Path, jobs: list[ImageJob]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    for job in jobs:
        record = {
            **job.data,
            "styled_prompt": job.styled_prompt,
            "task_id": job.task_id,
            "status": job.status,
            "apimart_url": job.apimart_url,
            "local_path": job.local_path,
            "cloudinary_url": job.cloudinary_url,
            "error": job.error,
        }
        if job.task:
            record["task"] = job.task
        payload.append(record)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def submit_one(apikey: str, job: ImageJob, resolution: str, submit_retries: int, retry_delay: int) -> ImageJob:
    style_key = job.data.get("style_key") or job.data.get("style") or None
    if style_key == "random":
        style_key = None
    job.styled_prompt = apply_style(str(job.data["prompt"]), style_key)
    ratio = str(job.data.get("aspect_ratio") or job.data.get("size") or "auto")
    last_error: Exception | None = None
    for attempt in range(1, max(1, submit_retries) + 1):
        try:
            job.task_id = submit_task(apikey, job.styled_prompt, ratio, resolution)
            job.status = "submitted"
            return job
        except RequestException as exc:
            last_error = exc
            if attempt >= max(1, submit_retries):
                break
            time.sleep(retry_delay * attempt)
    if last_error:
        raise last_error
    return job


def fetch_single_task(apikey: str, task_id: str, language: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {apikey}"}
    response = requests.get(
        f"{SINGLE_TASK_STATUS_URL}/{task_id}",
        headers=headers,
        params={"language": language},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200:
        raise RuntimeError(f"Task status API error for {task_id}: {data}")
    return data["data"]


def fetch_batch_tasks(apikey: str, task_ids: list[str], language: str) -> dict[str, dict[str, Any]]:
    headers = {"Authorization": f"Bearer {apikey}", "Content-Type": "application/json"}
    try:
        response = requests.post(
            BATCH_TASK_STATUS_URL,
            headers=headers,
            json={"task_ids": task_ids, "language": language},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 200:
            raise RuntimeError(f"Batch task status API error: {data}")
        raw_items = data.get("data", [])
        if isinstance(raw_items, dict):
            if all(isinstance(value, dict) for value in raw_items.values()):
                return {
                    task_id: {**task, "id": task.get("id") or task_id}
                    for task_id, task in raw_items.items()
                }
            raw_items = raw_items.get("tasks") or raw_items.get("data") or raw_items.get("items") or []
        tasks = {item.get("id") or item.get("task_id"): item for item in raw_items if isinstance(item, dict)}
        if tasks:
            return tasks
    except Exception as exc:
        print(f"[WARN] Batch status query failed; falling back to per-task polling: {exc}", file=sys.stderr)

    return {task_id: fetch_single_task(apikey, task_id, language) for task_id in task_ids}


def extract_image_url(task: dict[str, Any]) -> str:
    images = task.get("result", {}).get("images", [])
    if not images:
        raise ValueError(f"Completed task has no result.images: {task.get('id')}")
    first_url = images[0].get("url")
    if isinstance(first_url, list) and first_url:
        return first_url[0]
    if isinstance(first_url, str):
        return first_url
    raise ValueError(f"Completed task has no image URL: {task.get('id')}")


def resolve_completed_task(apikey: str, task: dict[str, Any], language: str) -> dict[str, Any]:
    if task.get("result", {}).get("images"):
        return task
    task_id = task.get("id") or task.get("task_id")
    if not task_id:
        return task
    return fetch_single_task(apikey, str(task_id), language)


def poll_until_done(
    apikey: str,
    jobs: list[ImageJob],
    results_path: Path,
    initial_delay: int,
    poll_interval: int,
    max_wait: int,
    language: str,
) -> None:
    if initial_delay:
        print(f"Initial delay: {initial_delay}s")
        time.sleep(initial_delay)

    started = time.time()
    pending = {job.task_id: job for job in jobs}
    while pending:
        if time.time() - started > max_wait:
            pending_ids = ", ".join(pending)
            raise TimeoutError(f"Timed out waiting for tasks: {pending_ids}")

        tasks = fetch_batch_tasks(apikey, list(pending), language)
        for task_id, task in tasks.items():
            job = pending.get(task_id)
            if not job:
                continue
            job.task = task
            job.status = str(task.get("status", "unknown"))
            progress = task.get("progress", "?")
            print(f"[{job.image_id}] {task_id}: {job.status} ({progress}%)")

            if job.status == "completed":
                resolved_task = resolve_completed_task(apikey, task, language)
                job.task = resolved_task
                job.apimart_url = extract_image_url(resolved_task)
                pending.pop(task_id, None)
            elif job.status in {"failed", "cancelled"}:
                job.error = json.dumps(task.get("error", task), ensure_ascii=False)
                pending.pop(task_id, None)

        write_json(results_path, jobs)
        if pending:
            time.sleep(poll_interval)

    failed = [job for job in jobs if job.status != "completed"]
    if failed:
        summary = "; ".join(f"{job.image_id}: {job.error or job.status}" for job in failed)
        raise RuntimeError(f"One or more image tasks failed: {summary}")


def safe_filename(job: ImageJob) -> str:
    title = str(job.data.get("title") or job.data.get("prompt") or f"image_{job.image_id}")
    safe = "".join(char if char.isalnum() or char in "-_ " else "_" for char in title[:48]).strip()
    return safe or f"image_{job.image_id}"


def download_and_upload_one(env: dict[str, str], output_dir: Path, job: ImageJob) -> ImageJob:
    local_path = output_dir / f"{job.image_id}_{safe_filename(job)}_{job.task_id[-8:]}.png"
    download_image(job.apimart_url, local_path)
    job.local_path = str(local_path)
    job.cloudinary_url = upload_to_cloudinary(local_path, env["cloud_name"], env["api_key"], env["api_secret"])
    return job


def download_and_upload_all(
    env: dict[str, str],
    output_dir: Path,
    jobs: list[ImageJob],
    results_path: Path,
    upload_concurrency: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=upload_concurrency) as executor:
        futures = {executor.submit(download_and_upload_one, env, output_dir, job): job for job in jobs}
        for future in as_completed(futures):
            job = futures[future]
            try:
                future.result()
                print(f"[{job.image_id}] Uploaded: {job.cloudinary_url}")
            except Exception as exc:
                job.status = "failed"
                job.error = f"download/upload failed: {exc}"
                raise
            finally:
                write_json(results_path, jobs)


def replace_article_placeholders(article_path: Path, jobs: list[ImageJob]) -> None:
    text = article_path.read_text(encoding="utf-8")
    for job in jobs:
        marker = f"<!-- {job.placeholder} -->"
        markdown = f"![{job.alt}]({job.cloudinary_url})"
        if marker in text:
            text = text.replace(marker, markdown, 1)
        elif job.placeholder in text and job.cloudinary_url not in text:
            raise ValueError(f"Found placeholder text without markdown comment wrapper: {job.placeholder}")
        else:
            print(f"[WARN] Placeholder not found, skipped: {marker}", file=sys.stderr)
    article_path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Async batch GPT-Image-2 generation + Cloudinary upload")
    parser.add_argument("--prompts", required=True, help="JSON prompt array")
    parser.add_argument("--article", default=None, help="Optional markdown file to replace IMAGE_PLACEHOLDER markers")
    parser.add_argument("--output-dir", default="C:/Users/eng/Desktop/output-html", help="Local image output directory")
    parser.add_argument("--results", default=None, help="Results JSON path")
    parser.add_argument("--resolution", default=RESOLUTION, choices=["1k", "2k", "4k"], help="Output resolution")
    parser.add_argument("--submit-concurrency", type=int, default=3, help="Concurrent task submissions")
    parser.add_argument("--submit-retries", type=int, default=3, help="Retry count for task submission")
    parser.add_argument("--submit-retry-delay", type=int, default=5, help="Base seconds between submit retries")
    parser.add_argument("--upload-concurrency", type=int, default=3, help="Concurrent download/upload workers")
    parser.add_argument("--initial-delay", type=int, default=10, help="Seconds to wait before first poll")
    parser.add_argument("--poll-interval", type=int, default=5, help="Seconds between polls")
    parser.add_argument("--max-wait", type=int, default=900, help="Maximum polling time in seconds")
    parser.add_argument("--language", default="zh", choices=["zh", "en", "ko", "ja"], help="Task status language")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompts_path = Path(args.prompts)
    output_dir, results_path = resolve_output_layout(args.output_dir, args.results, prompts_path)

    env = load_env()
    if not all(env.values()):
        raise SystemExit("Error: Missing environment variables. Check scripts/.env.")

    jobs = read_prompt_jobs(prompts_path)
    print(f"Loaded {len(jobs)} prompt(s). Submitting asynchronously...")

    with ThreadPoolExecutor(max_workers=max(1, args.submit_concurrency)) as executor:
        futures = {
            executor.submit(
                submit_one,
                env["apikey"],
                job,
                args.resolution,
                args.submit_retries,
                args.submit_retry_delay,
            ): job
            for job in jobs
        }
        for future in as_completed(futures):
            job = futures[future]
            try:
                future.result()
                print(f"[{job.image_id}] Submitted: {job.task_id}")
            except Exception as exc:
                job.status = "failed"
                job.error = f"submit failed: {exc}"
                write_json(results_path, jobs)
                raise

    write_json(results_path, jobs)
    poll_until_done(
        env["apikey"],
        jobs,
        results_path,
        args.initial_delay,
        args.poll_interval,
        args.max_wait,
        args.language,
    )
    download_and_upload_all(env, output_dir, jobs, results_path, max(1, args.upload_concurrency))

    if args.article:
        replace_article_placeholders(Path(args.article), jobs)
        print(f"Updated article: {args.article}")

    write_json(results_path, jobs)
    print(f"Results: {results_path}")


if __name__ == "__main__":
    main()
