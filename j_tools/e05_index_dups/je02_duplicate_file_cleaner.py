import os
import hashlib
import time
import shutil
from collections import defaultdict
from zipfile import ZipFile, ZIP_DEFLATED
import re
from datetime import datetime

def get_file_hash(file_path, algo='sha256', chunk_size=4096):
    hash_func = hashlib.new(algo)
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        return -1

def find_duplicates(root_dir, depth_limit=3):
    size_map = defaultdict(list)
    total_files_scanned = 0

    print(f"Scanning directory: {root_dir} (up to {depth_limit} levels deep)...")

    for root, _, files in os.walk(root_dir):
        relative_depth = root[len(root_dir.rstrip(os.sep)) + 1:].count(os.sep)
        if relative_depth > depth_limit:
            continue

        for file in files:
            full_path = os.path.join(root, file)
            file_size = get_file_size(full_path)
            if file_size >= 0:
                size_map[file_size].append(full_path)
                total_files_scanned += 1
                if total_files_scanned % 10 == 0:
                    print(f"  - Scanned {total_files_scanned} files...", end='\r')
    print(f"\nFinished initial scan. {total_files_scanned} files found.")

    potential_duplicates_by_size = {
        size: paths for size, paths in size_map.items() if len(paths) > 1
    }

    hash_map = defaultdict(list)
    files_hashed = 0
    total_potential_duplicates = sum(len(paths) for paths in potential_duplicates_by_size.values())
    print(f"\nChecking hashes of {total_potential_duplicates} potential duplicate files...")

    for size, file_list in potential_duplicates_by_size.items():
        for full_path in file_list:
            file_hash = get_file_hash(full_path)
            if file_hash:
                hash_map[file_hash].append(full_path)
                files_hashed += 1
                if files_hashed % 10 == 0:
                    progress = (files_hashed / total_potential_duplicates) * 100
                    print(f"  - Hashed {files_hashed}/{total_potential_duplicates} files ({progress:.2f}%)...", end='\r')
    print(f"\nFinished hashing potential duplicates.")

    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return duplicates

def is_numbered_duplicate(file_path1, file_path2):
    name1, ext1 = os.path.splitext(os.path.basename(file_path1))
    name2, ext2 = os.path.splitext(os.path.basename(file_path2))

    if ext1 != ext2:
        return False

    pattern = re.compile(r'(_\d+|\s\(\d+\))$')
    return bool(pattern.sub('', name1) == pattern.sub('', name2) and name1 != name2)

def handle_duplicates(root_dir, duplicates):
    if not duplicates:
        print("\nNo duplicate files found within the specified depth.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    duplicates_folder = os.path.join(root_dir, f"duplicates_pending_deletion_{timestamp}")
    os.makedirs(duplicates_folder, exist_ok=True)
    backup_zip_path = os.path.join(root_dir, f"duplicate_backup_{timestamp}.zip")
    indexed_file_path = os.path.join(root_dir, f"duplicate_index_{timestamp}.txt")
    moved_count = 0
    indexed_count = 0

    print(f"\n--- Potential Duplicate Files Found ---")
    with open(indexed_file_path, 'w') as index_file:
        for hash_val, files in duplicates.items():
            if len(files) > 1:
                print(f"\nDuplicate files with hash {hash_val}:")
                index_file.write(f"Duplicate files with hash {hash_val}:\n")
                numbered_duplicates = all(is_numbered_duplicate(files[i], files[j])
                                          for i in range(len(files))
                                          for j in range(i + 1, len(files)))
                if numbered_duplicates:
                    print("  (These appear to be numbered duplicates)")
                else:
                    print("  (Caution: These may not be simple numbered duplicates)")

                for i, f in enumerate(files):
                    print(f"  [{i + 1}] {f}")
                    index_file.write(f"  [{i + 1}] {f}\n")
                    indexed_count += 1
                index_file.write("\n")

    print(f"\nAn index of potential duplicate files has been saved to '{indexed_file_path}'.")

    while True:
        confirmation = input(
            "\nDo you want to move the duplicate copies (keeping one of each set) to the "
            f"'{duplicates_folder}' folder? (yes/no/select): "
        ).lower()

        if confirmation == 'yes':
            files_to_move = []
            for hash_val, files in duplicates.items():
                if len(files) > 1:
                    files_to_move.extend(files[1:])
            break
        elif confirmation == 'no':
            print("\nNo files will be moved.")
            return
        elif confirmation == 'select':
            files_to_move = []
            for hash_val, files in duplicates.items():
                if len(files) > 1:
                    print(f"\nSelect files to move for hash {hash_val}:")
                    for i, f in enumerate(files):
                        print(f"  [{i + 1}] {f}")
                    while True:
                        choices = input("Enter numbers of files to move (comma-separated): ")
                        try:
                            indices_to_move = [int(x.strip()) - 1 for x in choices.split(',')]
                            valid_indices = all(0 <= idx < len(files) for idx in indices_to_move)
                            if valid_indices:
                                files_to_move.extend(files[i] for i in indices_to_move)
                                break
                            else:
                                print("Invalid index. Try again.")
                        except ValueError:
                            print("Invalid input. Enter numbers only.")
            break
        else:
            print("Invalid input. Please enter 'yes', 'no', or 'select'.")

    if files_to_move:
        print(f"\nMoving selected duplicate copies to '{duplicates_folder}'...")
        with ZipFile(backup_zip_path, 'w', ZIP_DEFLATED) as backup_zip:
            for file_to_move in files_to_move:
                try:
                    base_name = os.path.basename(file_to_move)
                    new_path = os.path.join(duplicates_folder, base_name)

                    counter = 1
                    while os.path.exists(new_path):
                        name, ext = os.path.splitext(base_name)
                        new_path = os.path.join(duplicates_folder, f"{name}_{counter}{ext}")
                        counter += 1

                    shutil.move(file_to_move, new_path)
                    backup_zip.write(new_path, arcname=os.path.relpath(new_path, root_dir))
                    moved_count += 1
                    print(f"  - Moved and backed up: '{file_to_move}' to '{new_path}' in '{backup_zip_path}'")
                except Exception as e:
                    print(f"  - Error moving '{file_to_move}': {e}")

        print(f"\nSuccessfully moved and backed up {moved_count} duplicate files to '{duplicates_folder}' and '{backup_zip_path}'.")
        print("\nIt is recommended to review the contents of the 'duplicates_pending_deletion' folder and the backup zip before permanently deleting anything.")
    else:
        print("\nNo files were moved.")

    print("\n--- End of Duplicate Handling ---")
