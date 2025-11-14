#!/usr/bin/env python3
"""
clean.py — read [clean] from pyproject.toml and delete listed paths.
Supports wildcards, recursive globs, and directories.
"""

from pathlib import Path
import shutil
import tomllib  # Python 3.11+
import sys
import glob

def load_clean_paths(pyproject: Path) -> list[str]:
    if not pyproject.exists():
        sys.exit("❌ pyproject.toml not found.")

    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    section = data.get("clean")

    if not section or "paths" not in section:
        sys.exit("❌ No [clean] section or 'paths' found in pyproject.toml.")

    return section["paths"]


def remove_path(path: Path):
    if not path.exists():
        return

    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
        print(f"🗑️  removed dir:  {path}")
    else:
        try:
            path.unlink()
            print(f"🗑️  removed file: {path}")
        except Exception as e:
            print(f"⚠️  could not remove {path}: {e}")

def main():
    print("Cleaning...")
    root = Path(__file__).resolve().parent
    pyproject = root / "pyproject.toml"
    patterns = load_clean_paths(pyproject)

    for pattern in patterns:
        for name in glob.glob(str(root / pattern), recursive=True):
            remove_path(Path(name))

    print("✅ Cleanup complete.")

if __name__ == "__main__":
    main()
