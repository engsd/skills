#!/usr/bin/env python3
"""
Article Segmentation Tool

Split articles into sections by ## headings or AI-driven smart segmentation.

Usage:
    python segment_article.py article.md
    python segment_article.py article.md --method ai --prompt "split into logical chapters"
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def segment_by_headings(content: str) -> list[dict]:
    """
    Split markdown content by ## headings.
    Returns list of {title, content} dicts.
    """
    sections = []
    lines = content.split("\n")
    current_title = "Introduction"
    current_content = []

    for line in lines:
        if line.startswith("## "):
            if current_content:
                sections.append({
                    "title": current_title,
                    "content": "\n".join(current_content).strip()
                })
            current_title = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_content).strip()
        })

    return sections


def segment_by_ai(content: str, prompt: str) -> list[dict]:
    """
    AI-driven smart segmentation.
    This is a placeholder - actual implementation would call an LLM API.
    """
    # TODO: Integrate with LLM API for smart segmentation
    print("AI segmentation not implemented. Use --method headings instead.")
    print(f"User prompt: {prompt}")
    return []


def load_prompt_template(template_path: Path) -> str:
    """Load user-defined prompt template."""
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return "{subject} in {scene}, {style}"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Segment article into parts")
    parser.add_argument("input", help="Input article file (.md)")
    parser.add_argument("--method", default="headings", choices=["headings", "ai"],
                        help="Segmentation method (default: headings)")
    parser.add_argument("--prompt", default="split into logical sections",
                        help="AI segmentation instruction")
    parser.add_argument("--output-dir", default="segments",
                        help="Output directory for segments")

    args = parser.parse_args(argv)

    try:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            return 1

        content = input_path.read_text(encoding="utf-8")

        if args.method == "headings":
            sections = segment_by_headings(content)
        else:
            sections = segment_by_ai(content, args.prompt)
            if not sections:
                return 1

        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save each section
        for i, section in enumerate(sections, 1):
            safe_title = re.sub(r"[^\w\-.]", "_", section["title"])[:50]
            output_path = output_dir / f"section_{i:02d}_{safe_title}.md"
            output_path.write_text(
                f"# {section['title']}\n\n{section['content']}",
                encoding="utf-8"
            )
            print(f"[{i}/{len(sections)}] {section['title']}")

        print(f"\nTotal: {len(sections)} sections -> {output_dir}")
        return 0

    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())