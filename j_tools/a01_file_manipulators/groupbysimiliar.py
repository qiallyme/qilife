#!/usr/bin/env python3
"""
Group Files by Fuzzy Matching

This script scans a root directory (recursively), clusters file names
based on fuzzy string-similarity (typos, punctuation/spacing), and moves
each cluster into its own folder under a specified output directory.

Dependencies:
    pip install rapidfuzz
"""
import os
import shutil
from pathlib import Path
from rapidfuzz import process, fuzz


def find_file_clusters(files: list[Path], threshold: int) -> list[list[Path]]:
    """
    Cluster file paths by fuzzy similarity of names.

    Args:
        files: List of file Paths to cluster.
        threshold: Similarity threshold (0-100).

    Returns:
        List of clusters, each a list of Paths.
    """
    names = [f.name for f in files]
    clusters = []
    visited = set()

    for idx, name in enumerate(names):
        if idx in visited:
            continue
        # find similar file names
        matches = process.extract(
            name,
            names,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold,
            limit=None
        )
        group = []
        for other_name, score, other_idx in matches:
            if other_idx not in visited:
                group.append(files[other_idx])
                visited.add(other_idx)
        if group:
            clusters.append(group)
    return clusters


def main():
    root_input = input("Enter root directory to scan for files: ").strip()
    root = Path(root_input).expanduser().resolve()
    if not root.is_dir():
        print(f"Error: '{root}' is not a valid directory.")
        return

    try:
        threshold_input = input("Enter similarity threshold (0-100, default 85): ").strip()
        threshold = int(threshold_input) if threshold_input else 85
    except ValueError:
        print("Invalid threshold; using default 85.")
        threshold = 85

    output_dir = root / "Grouped_Files"
    output_dir.mkdir(exist_ok=True)
    print(f"\nScanning files under {root}...\n")

    # Collect all files
    all_files = [p for p in root.rglob('*') if p.is_file()]
    if not all_files:
        print("No files found to group.")
        return

    clusters = find_file_clusters(all_files, threshold)

    if not clusters:
        print("No similar file groups detected.")
        return

    print(f"Found {len(clusters)} group(s):\n")
    for i, group in enumerate(clusters, 1):
        print(f"Group {i} ({len(group)} files):")
        for f in group:
            print(f"  - {f}")
        print()

    confirm = input("Move grouped files into subfolders? Type 'yes' to proceed: ").strip().lower()
    if confirm not in ('yes', 'y'):
        print("Operation cancelled.")
        return

    # Move clusters
    for i, group in enumerate(clusters, 1):
        # name folder by first filename (sanitized) or index
        base_name = group[0].stem.replace(' ', '_')[:50]
        dest_folder = output_dir / f"group_{i:02d}_{base_name}"
        dest_folder.mkdir(exist_ok=True)
        for file_path in group:
            try:
                shutil.move(str(file_path), str(dest_folder / file_path.name))
            except Exception as e:
                print(f"Failed to move {file_path}: {e}")
    print(f"\nDone. Check grouped folders under {output_dir}")


if __name__ == "__main__":
    main()
