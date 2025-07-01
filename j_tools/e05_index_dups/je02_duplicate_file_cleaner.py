#!/usr/bin/env python3
"""
Duplicate File Finder & Cleaner
--------------------------------
Scans a root directory (within an optional depth limit), finds files with
identical content (hash match), lets you review them, then moves any copies
you select into a dated “duplicates_pending_deletion” folder **and**
simultaneously zips a backup for easy recovery.

Author: Q / QiAlly
Python 3.8+
"""

import os
import hashlib
import time
import shutil
from collections import defaultdict
from zipfile import ZipFile, ZIP_DEFLATED
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# ──────────────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────────────
def get_file_hash(file_path: str, algo: str = "sha256", chunk_size: int = 4096) -> str | None:
    """Return hex digest of a file or None on error."""
    h = hashlib.new(algo)
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError as exc:
        print(f"[!] Error reading {file_path}: {exc}")
        return None

def get_file_size(file_path: str) -> int:
    """Return file size or -1 on error."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return -1

# ──────────────────────────────────────────────────────────────────────────────
# Scanning & duplicate detection
# ──────────────────────────────────────────────────────────────────────────────
def find_duplicates(root_dir: str, depth_limit: int = 3) -> Dict[str, List[str]]:
    """
    Walk `root_dir`, group by size first, then by SHA-256 hash,
    and return {hash: [file1, file2, …]} for true dupes.
    """
    print(f"\n🕵️  Scanning '{root_dir}' (depth ≤ {depth_limit}) …")
    size_map: dict[int, list[str]] = defaultdict(list)
    total = 0

    for root, _, files in os.walk(root_dir):
        rel_depth = Path(root).relative_to(root_dir).parts.__len__()  # depth from root_dir
        if rel_depth > depth_limit:
            continue
        for fname in files:
            path = os.path.join(root, fname)
            if os.path.islink(path):
                continue
            sz = get_file_size(path)
            if sz >= 0:
                size_map[sz].append(path)
                total += 1
                if total % 200 == 0:
                    print(f"   …{total} files scanned", end="\r")
    print(f"   → Completed file walk ({total} files).")

    # candidates that share a size
    candidates = {size: paths for size, paths in size_map.items() if len(paths) > 1}
    if not candidates:
        print("✅ No size-based candidates found.")
        return {}

    print(f"🔍 Hashing {sum(len(v) for v in candidates.values())} candidate files …")
    hash_map: dict[str, list[str]] = defaultdict(list)
    processed = 0
    total_candidates = sum(len(v) for v in candidates.values())
    for paths in candidates.values():
        for p in paths:
            h = get_file_hash(p)
            if h:
                hash_map[h].append(p)
            processed += 1
            if processed % 50 == 0:
                pct = processed / total_candidates * 100
                print(f"   …{processed}/{total_candidates} ({pct:4.1f} %)", end="\r")

    duplicates = {h: lst for h, lst in hash_map.items() if len(lst) > 1}
    print(f"   → Hash pass complete. {len(duplicates)} duplicate group(s) found.")
    return duplicates

# ──────────────────────────────────────────────────────────────────────────────
# Name-based helper (photo.jpg ⇆ photo (1).jpg)
# ──────────────────────────────────────────────────────────────────────────────
_DUP_RE = re.compile(r"([-_ ]\(?\d+\)?| -? ?copy)$", re.IGNORECASE)


def _clean_name(fname: str) -> str:
    return _DUP_RE.sub("", fname).strip()


def is_numbered_duplicate(p1: str, p2: str) -> bool:
    """Return True if filenames differ only by ‘(1)’, ‘-1’, ‘- Copy’, etc."""
    n1, ext1 = os.path.splitext(os.path.basename(p1))
    n2, ext2 = os.path.splitext(os.path.basename(p2))
    if ext1.lower() != ext2.lower():
        return False
    return _clean_name(n1) == _clean_name(n2) and n1 != n2


# ──────────────────────────────────────────────────────────────────────────────
# Duplicate handling / quarantine
# ──────────────────────────────────────────────────────────────────────────────
def handle_duplicates(root_dir: str, dupes: Dict[str, List[str]]) -> None:
    if not dupes:
        print("🎉 Nothing to do; no real duplicates.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    quarantine = os.path.join(root_dir, f"duplicates_pending_deletion_{ts}")
    backup_zip = os.path.join(root_dir, f"duplicate_backup_{ts}.zip")
    index_txt = os.path.join(root_dir, f"duplicate_index_{ts}.txt")
    os.makedirs(quarantine, exist_ok=True)

    # Write index & show summary
    with open(index_txt, "w", encoding="utf-8") as idx:
        for h, paths in dupes.items():
            idx.write(f"Hash {h} ({len(paths)} files)\n")
            for p in paths:
                idx.write(f"   {p}\n")
            idx.write("\n")
    print(f"📄 Index of duplicates saved → {index_txt}")

    # Prompt
    move_choice = input(
        "\nMove all but one copy from each group into quarantine?  "
        "[yes/no/select] ➜ "
    ).strip().lower()

    to_move: list[str] = []

    if move_choice == "yes":
        for paths in dupes.values():
            to_move.extend(paths[1:])  # keep first
    elif move_choice == "select":
        for h, paths in dupes.items():
            print(f"\nHash {h}:")
            for i, p in enumerate(paths, 1):
                tag = "(auto-numbered)" if is_numbered_duplicate(paths[0], p) else ""
                print(f"   [{i}] {p} {tag}")
            pick = input("   Enter numbers to move (e.g. 2,3) or 'none': ").strip().lower()
            if pick and pick != "none":
                try:
                    idxs = [int(n) - 1 for n in pick.split(",") if n.strip()]
                    to_move.extend(paths[i] for i in idxs if 0 <= i < len(paths))
                except ValueError:
                    print("   ✖️  Bad input; skipping this group.")
    else:
        print("↩️  No files moved.")
        return

    if not to_move:
        print("↩️  Nothing selected.")
        return

    # Do moves + backup
    moved = 0
    with ZipFile(backup_zip, "w", ZIP_DEFLATED) as zf:
        for src in set(to_move):  # deduplicate
            base = os.path.basename(src)
            dst = os.path.join(quarantine, base)
            # ensure unique name in quarantine
            stem, ext = os.path.splitext(base)
            counter = 1
            while os.path.exists(dst):
                dst = os.path.join(quarantine, f"{stem}_{counter}{ext}")
                counter += 1
            try:
                shutil.move(src, dst)
                zf.write(dst, arcname=os.path.basename(dst))
                moved += 1
                print(f"   → {src} → {dst}")
            except OSError as exc:
                print(f"   ✖️  Could not move {src}: {exc}")

    print(
        f"\n✅ {moved} file(s) moved to {quarantine}\n"
        f"🗜️  Backup ZIP created → {backup_zip}\n"
        "Please review before permanent deletion."
    )


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("┌──────────────────────────────────────────────┐")
    print("│  Duplicate File Finder & Cleaner (QiAlly)    │")
    print("└──────────────────────────────────────────────┘\n")

    try:
        root = input("Root directory to scan (or 'exit'): ").strip()
        if root.lower() == "exit":
            return
        if not os.path.isdir(root):
            print(f"✖️  '{root}' is not a directory.")
            return

        depth_raw = input("Depth limit [default=3]: ").strip()
        depth = int(depth_raw) if depth_raw.isdigit() else 3

        t0 = time.time()
        dupes = find_duplicates(root, depth)
        print(f"\nScan finished in {time.time() - t0:,.1f} s.")
        handle_duplicates(root, dupes)

    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user. Bye!")


if __name__ == "__main__":
    main()
