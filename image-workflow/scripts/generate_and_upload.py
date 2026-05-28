#!/usr/bin/env python3
"""
Generate image and upload to Cloudinary.

Fixed settings:
- Resolution: 1K
- Default styles: oil painting, Chinese classical, ink wash

Usage:
    python generate_and_upload.py --prompt "..." --output-dir ./output
    python generate_and_upload.py --prompt "..." --style "chinese_classical"
"""

import argparse
import os
import random
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


API_BASE_URL = "https://api.apimart.ai/v1"
TASK_STATUS_URL = f"{API_BASE_URL}/tasks"

# Style keywords mapping
STYLES = {
    "oil_painting": [
        "oil painting style, classical brushwork, rich textures, dramatic lighting",
        "baroque oil painting, Renaissance aesthetic, museum quality, fine art",
        "classical European illustration, oil on canvas, warm tones"
    ],
    "chinese_classical": [
        "traditional Chinese painting style, Gongbi technique, elegant composition",
        "ancient Chinese scroll painting, refined brushwork, poetic atmosphere",
        "classical East Asian illustration, delicate lines, harmonious colors"
    ],
    "ink_wash": [
        "Chinese ink wash painting style, sumi-e technique, minimalist brushstrokes",
        "black ink on rice paper, traditional Asian art, serene atmosphere",
        "contemporary ink wash, elegant simplicity, contemplative mood"
    ]
}

# Aspect ratio with bias (16:9 and 3:4 more likely)
RATIOS = {
    "16:9": 25,  # Wide scenes
    "3:4": 25,   # Portrait-oriented scenes
    "1:1": 15,
    "4:3": 10,
    "3:2": 10,
    "2:3": 10,
    "9:16": 5,
}

# Fixed resolution
RESOLUTION = "1k"


def load_env() -> dict:
    script_dir = Path(__file__).parent
    load_dotenv(script_dir / ".env")
    return {
        "apikey": os.getenv("APIMART_API_KEY"),
        "cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "api_key": os.getenv("CLOUDINARY_API_KEY"),
        "api_secret": os.getenv("CLOUDINARY_API_SECRET"),
    }


def get_weighted_ratio() -> str:
    """Select ratio with bias towards 16:9 and 3:4."""
    ratios = list(RATIOS.keys())
    weights = list(RATIOS.values())
    return random.choices(ratios, weights=weights, k=1)[0]


def apply_style(prompt: str, style: str = None) -> str:
    """Apply style keywords to prompt."""
    if style and style in STYLES:
        style_phrase = random.choice(STYLES[style])
        return f"{prompt}, {style_phrase}"

    # Randomly choose a default style
    random_style = random.choice(list(STYLES.keys()))
    style_phrase = random.choice(STYLES[random_style])
    return f"{prompt}, {style_phrase}"


def submit_task(apikey: str, prompt: str, size: str, resolution: str = RESOLUTION) -> str:
    """Submit image generation task."""
    url = f"{API_BASE_URL}/images/generations"
    headers = {"Authorization": f"Bearer {apikey}", "Content-Type": "application/json"}
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
        raise RuntimeError(f"API Error: {data}")
    return data["data"][0]["task_id"]


def poll_task(apikey: str, task_id: str, max_wait: int = 300) -> str:
    """Poll until task completes."""
    headers = {"Authorization": f"Bearer {apikey}"}
    start = time.time()
    while time.time() - start < max_wait:
        response = requests.get(f"{TASK_STATUS_URL}/{task_id}", headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        task = data["data"]
        if task["status"] == "completed":
            return task["result"]["images"][0]["url"][0]
        if task["status"] == "failed":
            raise RuntimeError(f"Task failed: {task.get('error')}")
        time.sleep(3)
    raise TimeoutError(f"Task timed out after {max_wait}s")


def download_image(url: str, output_path: Path) -> Path:
    """Download image from URL."""
    response = requests.get(url, timeout=120, stream=True)
    response.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)
    return output_path


def upload_to_cloudinary(image_path: Path, cloud_name: str, api_key: str, api_secret: str) -> str:
    """Upload image to Cloudinary."""
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)
    result = cloudinary.uploader.upload(str(image_path), resource_type="image", folder="ai-generated")
    return result.get("secure_url", "")


def main():
    parser = argparse.ArgumentParser(description="Generate image and upload to Cloudinary (1K resolution)")
    parser.add_argument("--prompt", required=True, help="Image prompt")
    parser.add_argument("--size", default=None, help=f"Aspect ratio (default: auto-weighted, biased to 16:9/3:4)")
    parser.add_argument("--style", default=None, choices=["oil_painting", "chinese_classical", "ink_wash", "random"],
                        help=f"Style (default: random from oil/chinese/ink)")
    parser.add_argument("--output-dir", default="C:/Users/eng/Desktop/output-html", help="Output directory")
    args = parser.parse_args()

    env = load_env()
    if not all(env.values()):
        print("Error: Missing environment variables. Check .env file.")
        sys.exit(1)

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Apply style
    styled_prompt = apply_style(args.prompt, args.style)

    # Get ratio
    ratio = args.size if args.size else get_weighted_ratio()

    print(f"Prompt: {styled_prompt}")
    print(f"Ratio: {ratio} | Resolution: {RESOLUTION}")

    # Generate
    task_id = submit_task(env["apikey"], styled_prompt, ratio, RESOLUTION)
    print(f"Task: {task_id} - Waiting...")

    # Poll
    url = poll_task(env["apikey"], task_id)
    print(f"Generated: {url}")

    # Download
    output_dir = Path(args.output_dir)
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in args.prompt[:30])
    local_path = download_image(url, output_dir / f"{safe_name}_{task_id[-8:]}.png")
    print(f"Downloaded: {local_path}")

    # Upload
    cloudinary_url = upload_to_cloudinary(local_path, env["cloud_name"], env["api_key"], env["api_secret"])
    print(f"\nCloudinary URL: {cloudinary_url}")

    # Output for piping
    print(f"\n[URL]{cloudinary_url}[/URL]")


if __name__ == "__main__":
    main()