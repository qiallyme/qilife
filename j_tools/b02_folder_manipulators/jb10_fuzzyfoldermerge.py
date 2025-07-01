#!/usr/bin/env python3
"""
Folder Merger Script

This script scans a given root directory for folders with similar names (typos,
underscores vs spaces, minor variations) and merges their contents into a single
"canonical" folder per group. It supports a dry-run mode to preview changes.

Dependencies:
    pip install rapidfuzz
"""
import os
import shutil
from pathlib import Path
from rapidfuzz import process, fuzz


def find_clusters(root: Path, threshold: int) -> list[list[Path]]:
    """
    Identify clusters of similar folder names under the root directory based on a similarity threshold.

    Args:
        root: Path object pointing to the root directory.
        threshold: Similarity threshold (0-100).

    Returns:
        List of clusters, each a list of Paths to merge together.
    """
    folders = [p for p in root.iterdir() if p.is_dir()]
    names = [p.name for p in folders]

    clusters = []
    visited = set()

    for idx, name in enumerate(names):
        if name in visited:
            continue
        matches = process.extract(
            name,
            names,
            scorer=fuzz.ratio,
            score_cutoff=threshold,
            limit=None
        )
        group = [folders[idx]]
        visited.add(name)
        for other_name, score, other_idx in matches:
            if other_name != name and other_name not in visited:
                group.append(folders[other_idx])
                visited.add(other_name)
        if len(group) > 1:
            clusters.append(group)
    return clusters


def merge_cluster(cluster: list[Path], dry_run: bool = True) -> Path:
    """
    Merge all folders in a cluster into a single target folder.

    Args:
        cluster: List of folder Paths to merge.
        dry_run: If True, only print actions without performing moves.

    Returns:
        The Path of the target (canonical) folder.
    """
    target = max(cluster, key=lambda p: len(p.name))
    print(f"Merging into target folder: '{target.name}'")

    for folder in cluster:
        if folder == target:
            continue
        print(f"  - Processing folder: '{folder.name}'")
        for item in folder.iterdir():
            dest = target / item.name
            if dry_run:
                print(f"      [DRY] Would move: {item} -> {dest}")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                print(f"      Moving: {item} -> {dest}")
                shutil.move(str(item), str(dest))
        if not dry_run:
            try:
                folder.rmdir()
                print(f"      Removed empty folder: {folder}")
            except OSError:
                print(f"      Could not remove folder (not empty): {folder}")
    return target


def main():
    # Prompt for root directory
    root_input = input("Enter the root directory to scan for merges: ").strip()
    root = Path(root_input).expanduser().resolve()
    if not root.is_dir():
        print(f"Error: '{root}' is not a valid directory.")
        return

    # Prompt for similarity threshold
    try:
        threshold_input = input("Enter similarity threshold (0-100, default 80): ").strip()
        threshold = int(threshold_input) if threshold_input else 80
    except ValueError:
        print("Invalid threshold value, using default 80.")
        threshold = 80

    # Ask for dry-run vs commit
    commit_choice = input("Perform actual merge? Type 'yes' to commit, anything else for dry-run: ").strip().lower()
    dry_run = commit_choice not in ('yes', 'y')
    mode = 'DRY-RUN' if dry_run else 'COMMIT'
    print(f"\nRunning in {mode} mode on: {root}\nSimilarity threshold: {threshold}%\n")

    clusters = find_clusters(root, threshold)
    if not clusters:
        print("No similar folders detected. Nothing to merge.")
        return

    print(f"Found {len(clusters)} cluster(s) of similar folders to merge:\n")
    for i, cluster in enumerate(clusters, 1):
        names = [p.name for p in cluster]
        print(f"  Cluster {i}: {', '.join(names)}")

    if dry_run:
        print("\nDry-run complete. No changes were made.")
    else:
        confirm = input("\nProceed with merging these folders? Type 'yes' to continue: ").strip().lower()
        if confirm not in ('yes', 'y'):
            print("Merge cancelled by user.")
            return
        print()
        for cluster in clusters:
            merge_cluster(cluster, dry_run=False)
        print("\nMerge completed successfully.")


if __name__ == "__main__":
    main()
