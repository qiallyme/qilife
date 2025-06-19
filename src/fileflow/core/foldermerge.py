import os
import shutil
import filecmp
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Union

LOG_FILENAME = ".merge_folders_log.json"


def get_log_path(base_path: Path) -> Path:
    """Constructs the full path to the log file."""
    return base_path / LOG_FILENAME


def load_logs(base_path: Path) -> List[Dict[str, Any]]:
    """Loads the log file if it exists."""
    log_path = get_log_path(base_path)
    if log_path.exists():
        with log_path.open('r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_logs(base_path: Path, logs: List[Dict[str, Any]]) -> None:
    """Saves the logs to the log file."""
    log_path = get_log_path(base_path)
    with log_path.open('w') as f:
        json.dump(logs, f, indent=2)


def group_folders(base_path: Path) -> Dict[str, List[Path]]:
    """
    Groups subfolders based on a numeric suffix or a normalized name.

    Returns a dictionary where keys are the grouping identifiers and values are lists of folder paths.
    """
    groups: Dict[str, List[Path]] = {}
    for entry in base_path.iterdir():
        if not entry.is_dir():
            continue

        if entry.name.startswith('.'):
            continue

        nums = re.findall(r"\d+", entry.name)
        if nums:
            key = nums[-1]
        else:
            key = re.sub(r'[^0-9a-zA-Z]+', '', entry.name.lower())

        groups.setdefault(key, []).append(entry)

    return {k: v for k, v in groups.items() if len(v) > 1}


def get_unique_name(path: Path) -> Path:
    """
    Finds a unique name for a file by appending an incremental number.
    """
    if not path.exists():
        return path

    base, ext = path.stem, path.suffix
    i = 1
    new_path = path.with_name(f"{base}_{i}{ext}")
    while new_path.exists():
        i += 1
        new_path = path.with_name(f"{base}_{i}{ext}")
    return new_path


def merge_group(folders: List[Path], session_ops: List[Dict[str, Any]], dry_run: bool = False) -> None:
    """
    Merges a group of similar folders into a single target folder.
    """
    # The target folder is the one with the shortest name
    target = min(folders, key=lambda p: len(p.name))
    print(f"\nMerging {len(folders)} folders into: {target.name}")

    for src in folders:
        if src == target:
            continue

        print(f"  Processing source folder: {src.name}")
        # Ensure the source directory still exists before processing
        if not src.exists():
            print(f"  - Source folder {src.name} no longer exists, skipping.")
            continue

        for src_file in src.iterdir():
            if not src_file.is_file():
                continue

            dest_file = target / src_file.name

            if dest_file.exists():
                if filecmp.cmp(str(src_file), str(dest_file), shallow=False):
                    print(f"    - Deleting duplicate file: {src_file.name}")
                    if not dry_run:
                        src_file.unlink()
                    session_ops.append({
                        'action': 'delete_file',
                        'path': str(src_file),
                        'origin': str(dest_file)
                    })
                else:
                    new_dest = get_unique_name(dest_file)
                    print(f"    - Renaming and moving conflicting file: {src_file.name} -> {new_dest.name}")
                    if not dry_run:
                        shutil.move(str(src_file), new_dest)
                    session_ops.append({
                        'action': 'move',
                        'src': str(src_file),
                        'dest': str(new_dest)
                    })
            else:
                print(f"    - Moving file: {src_file.name}")
                if not dry_run:
                    shutil.move(str(src_file), dest_file)
                session_ops.append({
                    'action': 'move',
                    'src': str(src_file),
                    'dest': str(dest_file)
                })
        
        # After processing files, attempt to remove the source folder
        if not dry_run:
            # Add a small delay to allow cloud sync to release file handles
            time.sleep(1) 
            try:
                # Use shutil.rmtree for more robust deletion of the directory
                shutil.rmtree(src)
                print(f"  - Successfully deleted source folder: {src.name}")
                session_ops.append({'action': 'delete_folder', 'path': str(src)})
            except PermissionError:
                print(f"  - Could not delete folder: {src.name}. It may be in use by another process (like Google Drive). Please delete it manually.")
            except Exception as e:
                print(f"  - An unexpected error occurred while trying to delete {src.name}: {e}")


def save_session(base_path: Path, ops: List[Dict[str, Any]]) -> None:
    """Saves the operations of the current merge session to the log."""
    logs = load_logs(base_path)
    session = {
        'id': time.time(),
        'operations': ops
    }
    logs.append(session)
    save_logs(base_path, logs)


def undo_last(base_path: Path) -> None:
    """Reverts the last merge session."""
    logs = load_logs(base_path)
    if not logs:
        print("No merge sessions found to undo.")
        return

    session = logs.pop()
    print(f"\nReverting session {session['id']}...")

    for op in reversed(session['operations']):
        action = op['action']
        try:
            if action == 'delete_folder':
                Path(op['path']).mkdir(exist_ok=True)
                print(f"  - Re-created folder: {op['path']}")
            elif action == 'delete_file':
                shutil.copy2(op['origin'], op['path'])
                print(f"  - Restored deleted file: {op['path']}")
            elif action == 'move':
                # Ensure the source directory exists before moving back
                Path(op['src']).parent.mkdir(exist_ok=True)
                shutil.move(op['dest'], op['src'])
                print(f"  - Moved back file: {op['dest']} -> {op['src']}")
        except Exception as e:
            print(f"  - Could not perform undo operation for {op}: {e}")


    save_logs(base_path, logs)
    print("Undo complete.")


def main() -> None:
    """Main function to run the folder merging utility."""
    while True:
        base_path_str = input("\nEnter directory path to merge (or 'exit' to quit): ").strip()
        if base_path_str.lower() in ('exit', 'quit'):
            print("Exiting.")
            break

        base_path = Path(base_path_str)
        if not base_path.is_dir():
            print("Invalid directory. Please try again.")
            continue

        groups = group_folders(base_path)
        if not groups:
            print("No similar folders detected at this level.")
            continue

        dry_run_choice = input("Run in dry-run mode to preview changes? (y/n): ").lower().startswith('y')

        if dry_run_choice:
            print("\n--- Starting Dry Run ---")
            temp_ops: List[Dict[str, Any]] = []
            for key, folder_list in groups.items():
                merge_group(folder_list, temp_ops, dry_run=True)
            print("\n--- Dry Run Complete. No files were changed. ---")
            if not temp_ops:
                print("No operations to perform.")
                continue
            proceed = input("Do you want to proceed with the merge? (y/n): ").lower().startswith('y')
            if not proceed:
                continue
        
        print("\n--- Starting Actual Merge ---")
        session_ops: List[Dict[str, Any]] = []
        for key, folder_list in groups.items():
            merge_group(folder_list, session_ops, dry_run=False)

        if not session_ops:
            print("\nNo operations were performed in the actual merge.")
            continue
        
        save_session(base_path, session_ops)
        print("\nMerge operations completed and logged.")
        if input("Undo last merge? (y/n): ").lower().startswith('y'):
            undo_last(base_path)


if __name__ == '__main__':
    main()