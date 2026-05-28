#!/usr/bin/env python3
"""
Batch upload local photos to Cloudinary.

Usage:
    python cloudinary_photo_uploader.py --source <file_or_folder>

Environment (.env file in same directory):
    CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.exceptions import NotFound as CloudinaryNotFound


DEFAULT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif", ".avif"}


@dataclass(frozen=True)
class UploadCandidate:
    local_path: Path
    public_id: str
    size_bytes: int


@dataclass
class UploadResult:
    local_path: str
    public_id: str
    status: str
    secure_url: str = ""
    bytes: int = 0
    error: str = ""


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def configure_cloudinary() -> str:
    """
    Configure Cloudinary from environment variables.
    Returns the cloud name if successful.
    Raises RuntimeError if configuration fails.
    """
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if cloudinary_url:
        # Parse cloudinary:// URL manually for reliability
        # Format: cloudinary://api_key:api_secret@cloud_name
        try:
            prefix = "cloudinary://"
            if not cloudinary_url.startswith(prefix):
                raise ValueError(f"Invalid CLOUDINARY_URL format. Must start with '{prefix}'")

            remainder = cloudinary_url[len(prefix):]
            if "@" not in remainder:
                raise ValueError("Invalid CLOUDINARY_URL format. Missing '@' separator.")

            credentials, cloud = remainder.rsplit("@", 1)
            if ":" not in credentials:
                raise ValueError("Invalid CLOUDINARY_URL format. Missing ':' between api_key and api_secret.")

            key, secret = credentials.split(":", 1)
            cloudinary.config(
                cloud_name=cloud.strip(),
                api_key=key.strip(),
                api_secret=secret.strip(),
                secure=True,
            )
            logging.debug("Configured Cloudinary from CLOUDINARY_URL (cloud: %s)", cloud)
            return cloud.strip()
        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to parse CLOUDINARY_URL: {exc}") from exc

    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        return cloud_name

    raise RuntimeError(
        "Cloudinary credentials not found. Set CLOUDINARY_URL or "
        "CLOUDINARY_CLOUD_NAME/CLOUDINARY_API_KEY/CLOUDINARY_API_SECRET"
    )


def verify_connection() -> bool:
    """Test Cloudinary connection by fetching account info."""
    try:
        cloudinary.api.account()
        return True
    except Exception as exc:
        logging.warning("Could not verify connection: %s", exc)
        return True  # Allow upload to proceed even if verification fails


def parse_extensions(raw: str) -> set[str]:
    extensions: set[str] = set()
    for item in raw.split(","):
        item = item.strip().lower()
        if item:
            extensions.add(item if item.startswith(".") else f".{item}")
    return extensions


def iter_files(source: Path, recursive: bool) -> list[Path]:
    if source.is_file():
        return [source]
    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")
    if not source.is_dir():
        raise ValueError(f"Source path is neither a file nor a directory: {source}")
    pattern = "**/*" if recursive else "*"
    return [p for p in source.glob(pattern) if p.is_file()]


def sanitize_public_id_part(part: str) -> str:
    part = part.strip()
    part = re.sub(r"\s+", "_", part)
    part = re.sub(r"[^\w\-.]+", "_", part, flags=re.UNICODE)
    part = re.sub(r"_+", "_", part)
    return part.strip("._-") or "untitled"


def build_public_id(
    file_path: Path,
    source_root: Path,
    cloud_folder: str,
    preserve_structure: bool,
) -> str:
    if preserve_structure and source_root.is_dir():
        relative = file_path.relative_to(source_root).with_suffix("")
        parts = [sanitize_public_id_part(p) for p in relative.parts]
    else:
        parts = [sanitize_public_id_part(file_path.stem)]

    folder_parts = [sanitize_public_id_part(p) for p in cloud_folder.replace("\\", "/").split("/") if p.strip()]
    return "/".join(folder_parts + parts)


def discover_candidates(
    source: Path,
    recursive: bool,
    extensions: set[str],
    cloud_folder: str,
    preserve_structure: bool,
) -> tuple[list[UploadCandidate], list[UploadResult]]:
    source_root = source if source.is_dir() else source.parent
    candidates: list[UploadCandidate] = []
    skipped: list[UploadResult] = []

    for file_path in iter_files(source, recursive):
        suffix = file_path.suffix.lower()
        size_bytes = file_path.stat().st_size

        if suffix not in extensions:
            skipped.append(UploadResult(
                local_path=str(file_path),
                public_id="",
                status="skipped_extension",
                bytes=size_bytes,
                error=f"Unsupported extension: {suffix or '(none)'}",
            ))
            continue

        public_id = build_public_id(file_path, source_root, cloud_folder, preserve_structure)
        candidates.append(UploadCandidate(local_path=file_path, public_id=public_id, size_bytes=size_bytes))

    return candidates, skipped


def asset_exists(public_id: str) -> bool:
    try:
        cloudinary.api.resource(public_id, resource_type="image")
        return True
    except CloudinaryNotFound:
        return False
    except CloudinaryError as exc:
        if "not found" in str(exc).lower() or "404" in str(exc):
            return False
        raise


def upload_single(
    candidate: UploadCandidate,
    overwrite: bool,
    tags: Optional[list[str]],
) -> UploadResult:
    try:
        response = cloudinary.uploader.upload(
            str(candidate.local_path),
            resource_type="image",
            public_id=candidate.public_id,
            use_filename=False,
            unique_filename=False,
            overwrite=overwrite,
            tags=tags,
        )
        return UploadResult(
            local_path=str(candidate.local_path),
            public_id=candidate.public_id,
            status="uploaded",
            secure_url=response.get("secure_url", ""),
            bytes=candidate.size_bytes,
        )
    except Exception as exc:
        return UploadResult(
            local_path=str(candidate.local_path),
            public_id=candidate.public_id,
            status="failed",
            bytes=candidate.size_bytes,
            error=str(exc),
        )


def upload_with_retry(
    candidate: UploadCandidate,
    overwrite: bool,
    tags: Optional[list[str]],
    retries: int,
    retry_delay: float,
) -> UploadResult:
    for attempt in range(1, retries + 2):
        result = upload_single(candidate, overwrite, tags)
        if result.status == "uploaded" or attempt > retries:
            return result
        logging.warning(
            "Upload failed (attempt %s/%s), retrying in %.1fs | file=%s",
            attempt, retries + 1, retry_delay * (2 ** (attempt - 1)), candidate.local_path
        )
        time.sleep(retry_delay * (2 ** (attempt - 1)))
    return result


def write_report(report_path: Path, results: list[UploadResult]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["status", "local_path", "public_id", "secure_url", "bytes", "error"])
        writer.writeheader()
        for result in results:
            writer.writerow({
                "status": result.status,
                "local_path": result.local_path,
                "public_id": result.public_id,
                "secure_url": result.secure_url,
                "bytes": result.bytes,
                "error": result.error,
            })


def print_urls(results: list[UploadResult]) -> None:
    """Print Cloudinary URLs for successfully uploaded files."""
    urls = [r.secure_url for r in results if r.status == "uploaded" and r.secure_url]
    if urls:
        print("\n" + "=" * 60)
        print("UPLOADED URLs:")
        print("=" * 60)
        for url in urls:
            print(url)
        print("=" * 60)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Upload local photos to Cloudinary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cloudinary_photo_uploader.py --source photo.jpg
    python cloudinary_photo_uploader.py --source ./photos --recursive
    python cloudinary_photo_uploader.py --source ./photos --cloud-folder my-folder
        """,
    )
    parser.add_argument("--source", required=True, help="Local file or directory to upload.")
    parser.add_argument("--cloud-folder", default="local-photos", help="Cloudinary folder prefix.")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories.")
    parser.add_argument("--preserve-structure", action="store_true", help="Preserve folder structure.")
    parser.add_argument("--tags", default="", help="Comma-separated Cloudinary tags.")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip existing assets.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing assets.")
    parser.add_argument("--retries", type=int, default=2, help="Retry count.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs.")
    parser.add_argument("--report", default="upload_report.csv", help="CSV report path.")

    args = parser.parse_args(argv)
    setup_logging(args.verbose)

    try:
        # Load .env from script directory
        script_dir = Path(__file__).parent.resolve()
        load_dotenv(script_dir / ".env")
        logging.debug("Loaded .env from: %s", script_dir / ".env")

        # Configure Cloudinary
        cloud_name = configure_cloudinary()
        logging.info("Cloudinary configured for cloud: %s", cloud_name)

        source = Path(args.source).expanduser().resolve()
        extensions = parse_extensions(",".join(DEFAULT_EXTENSIONS))
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] or None

        # Discover files
        candidates, skipped = discover_candidates(
            source=source,
            recursive=args.recursive,
            extensions=extensions,
            cloud_folder=args.cloud_folder,
            preserve_structure=args.preserve_structure,
        )

        if not candidates:
            logging.info("No files to upload.")
            return 0

        logging.info("Found %s file(s) to upload, %s skipped", len(candidates), len(skipped))

        # Upload files
        results = list(skipped)
        for i, candidate in enumerate(candidates, 1):
            logging.info("[%s/%s] Uploading: %s", i, len(candidates), candidate.public_id)

            if args.skip_existing and not args.overwrite and asset_exists(candidate.public_id):
                logging.info("Skipped (exists): %s", candidate.public_id)
                results.append(UploadResult(
                    local_path=str(candidate.local_path),
                    public_id=candidate.public_id,
                    status="skipped_existing",
                    bytes=candidate.size_bytes,
                ))
                continue

            result = upload_with_retry(
                candidate=candidate,
                overwrite=args.overwrite,
                tags=tags,
                retries=max(args.retries, 0),
                retry_delay=1.5,
            )

            if result.status == "uploaded":
                logging.info("SUCCESS: %s", result.secure_url)
            else:
                logging.error("FAILED: %s", result.error)

            results.append(result)

        # Write report
        report_path = Path(args.report).expanduser()
        write_report(report_path, results)
        logging.info("Report: %s", report_path.resolve())

        # Summary
        summary = {}
        for r in results:
            summary[r.status] = summary.get(r.status, 0) + 1
        print(f"\nSummary: {summary}")

        # Print URLs
        print_urls(results)

        return 0 if summary.get("failed", 0) == 0 else 1

    except Exception as exc:
        logging.exception("Error: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
