#!/usr/bin/env python3
"""
Empty Folder Collector

Recursively scans a root directory for empty folders at any level, and moves them
into a single "Empty_Folders" folder under the root so you can review and delete them.

Usage:
    python move_empty_folders.py

Dependencies:
    Only Python 3.6+ (uses pathlib).
"""
import os
import shutil
from pathlib import Path

def collect_empty_folders(root: Path) -> list[Path]:
    """
    Walk the directory tree bottom-up and collect paths of empty folders.

    Args:
        root: Path to start scanning.

    Returns:
        List of Paths for empty folders.
    """
    empty_dirs = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        current = Path(dirpath)
        # Skip the destination folder if it already exists
        if current.name == 'Empty_Folders':
            continue
        # Check if truly empty (no files or subdirs)
        if not any(current.iterdir()):
            empty_dirs.append(current)
    return empty_dirs


def main():
    root_input = input("Enter root directory to scan for empty folders: ").strip()
    root = Path(root_input).expanduser().resolve()
    if not root.is_dir():
        print(f"Error: '{root}' is not a valid directory.")
        return

    # Create destination for empties
    dest_root = root / 'Empty_Folders'
    dest_root.mkdir(exist_ok=True)

    print(f"Scanning '{root}' for empty folders...\n")
    empties = collect_empty_folders(root)
    if not empties:
        print("No empty folders found.")
        return

    print(f"Found {len(empties)} empty folder(s):")
    for e in empties:
        print(f"  - {e}")

    confirm = input("\nMove these folders into 'Empty_Folders'? (yes/[no]) ").strip().lower()
    if confirm not in ('y', 'yes'):
        print("Operation cancelled.")
        return

    # Move each empty folder
    for folder in empties:
        try:
            # Compute unique destination path
            dest = dest_root / folder.name
            count = 1
            while dest.exists():
                dest = dest_root / f"{folder.name}_{count}"
                count += 1
            shutil.move(str(folder), str(dest))
            print(f"Moved: {folder} -> {dest}")
        except Exception as ex:
            print(f"Failed to move {folder}: {ex}")

    print("\nDone. Review 'Empty_Folders' for deletion.")

if __name__ == '__main__':
    main()
