#!/usr/bin/env python3
"""
Remove citation markers from markdown files.

Removes patterns like $ ^{3} $, $ ^{2} $, etc.
Supports various citation formats commonly found in academic/markdown content.

Usage:
    python remove_citations.py --file "path/to/file.md"
    python remove_citations.py --file "path/to/file.md" --dry-run
"""

import argparse
import re
import sys
from pathlib import Path


# Citation patterns to remove
CITATION_PATTERNS = [
    # $ ^{number} $ - main pattern
    (r'\$\s*\^\{(\d+)\}\s*\$', ''),
    # $ ^{number} $ - without braces
    (r'\$\s*\^\d+\s*\$', ''),
    # Superscript with numbers: ^{1}, ^{2}, etc.
    (r'\^\{(\d+)\}', ''),
    # Standalone superscript: ^1, ^2
    (r'\^(\d+)', ''),
    # Wikipedia-style citation: [1], [2]
    (r'\[\^?\d+\]', ''),
    # Multiple consecutive citations cleanup: , , → ,
    (r',\s*,', ','),
    # Leading/trailing punctuation cleanup
    (r'\s+([,.])\s+', r' \1 '),
    # Multiple horizontal spaces only; preserve markdown line breaks.
    (r'[ \t]{2,}', ' '),
]


def remove_citations(content: str) -> tuple[str, int]:
    """Remove citation markers from content. Returns (cleaned_content, count)."""
    count = 0
    result = content

    for pattern, replacement in CITATION_PATTERNS:
        new_result, replaced = re.subn(pattern, replacement, result)
        count += replaced
        result = new_result

    # Clean up orphaned punctuation
    result = re.sub(r'\s+([,.])\s+', r'\1 ', result)
    result = re.sub(r'[ \t]{2,}', ' ', result)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip(), count


def process_file(filepath: Path, dry_run: bool = False, verbose: bool = False) -> None:
    """Process a single markdown file."""
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    content = filepath.read_text(encoding='utf-8')
    cleaned, count = remove_citations(content)

    if dry_run:
        print(f"[DRY RUN] Would remove {count} citation markers from: {filepath}")
        if verbose:
            print("--- Changes would be made ---")
            # Show first 500 chars of diff
            print(cleaned[:500] + "..." if len(cleaned) > 500 else cleaned)
    else:
        filepath.write_text(cleaned, encoding='utf-8')
        print(f"Removed {count} citation markers from: {filepath}")


def process_directory(dirpath: Path, dry_run: bool = False, recursive: bool = False) -> None:
    """Process all markdown files in a directory."""
    if recursive:
        files = list(dirpath.rglob("*.md"))
    else:
        files = list(dirpath.glob("*.md"))

    if not files:
        print(f"No markdown files found in: {dirpath}")
        return

    print(f"Found {len(files)} markdown file(s)")

    for f in files:
        process_file(f, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(description="Remove citation markers from markdown files")
    parser.add_argument("--file", "-f", help="Specific file to process")
    parser.add_argument("--dir", "-d", help="Directory to process (all .md files)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--recursive", "-r", action="store_true", help="Process directories recursively")
    args = parser.parse_args()

    if args.file:
        process_file(Path(args.file), dry_run=args.dry_run, verbose=args.verbose)
    elif args.dir:
        process_directory(Path(args.dir), dry_run=args.dry_run, recursive=args.recursive)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
