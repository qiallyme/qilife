import os
import shutil
import argparse
import logging
import csv

# Set the root directory for the operation. This should be the main project folder.
ROOT = os.getcwd()

# Define the target structure for your project.
# Keys are destination folders relative to ROOT.
# Values are dictionaries where keys are subdirectories (or "" for direct files)
# and values are lists of filenames that should reside there.
# Any files or empty folders not matching this structure will be candidates for cleanup.
structure = {
    "src": {
        "ai": [],
        "common": ["config.py", "ocr.py", "utils.py", "hashing.py", "init_db.py"],
        "constants": [],
        "core": ["processor.py"],
        "fileflow": ["rename_client_folders.py", "foldermerge.py", "foldersCreate.py"],
        "lifelog": ["spyme.py"],
        "qinote": ["notiondelpages.py"],
        "ui": ["gui_file_processor.py", "main_ui.py", "clicks_output.ahk"],
        "utils": [],
    },
    "tests": {
        "": ["test_fileflow.sh", "test_fileflow.bat"]
    },
    "delete": {
        "": ["import os.py", "diskfix.py", "newnew.py"] # Files that should end up in a 'delete' folder
    },
    "root": {
        "": ["README.md", ".env", ".gitignore", "requirements.txt", "qiapp_workspace.code-workspace", "directory_mapper.py"]
    }
}

# --- Logging Setup ---
LOG_FILE = "organize_log.txt"

# Configure handlers with UTF-8 encoding for file output
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
# StreamHandler for console output (no encoding specified, relies on system default)
stream_handler = logging.StreamHandler() 

logging.basicConfig(level=logging.INFO,
                    format='%(message)s',
                    handlers=[
                        file_handler,
                        stream_handler
                    ])

# --- Global Data for Rollback ---
# Stores actions for potential undo:
# For moves: {'action': 'MOVE', 'source': 'new_path', 'destination': 'original_path'}
# For deletions: {'action': 'CREATE', 'path': 'deleted_file_path'} (to recreate)
# For directory deletions: {'action': 'CREATE_DIR', 'path': 'deleted_dir_path'} (to recreate)
rollback_data = []

# --- Helper Functions ---

def normalize_path(path: str) -> str:
    """Normalizes a path to be absolute and consistent for comparisons."""
    return os.path.normpath(os.path.abspath(path))

def find_all_files_in_root(filename: str, start_dir: str) -> list[str]:
    """
    Recursively searches for all instances of a filename within start_dir and its subdirectories.
    Returns a list of full paths where the file was found.
    """
    found_paths = []
    logging.debug(f"🔎 Searching for all instances of '{filename}' in '{start_dir}'...")
    for dirpath, dirnames, filenames in os.walk(start_dir):
        if filename in filenames:
            found_path = os.path.join(dirpath, filename)
            found_paths.append(normalize_path(found_path))
            logging.debug(f"✅ Found '{filename}' at '{found_path}'")
    if not found_paths:
        logging.debug(f"❌ '{filename}' not found in '{start_dir}' and its subdirectories.")
    return found_paths

def create_empty_file(file_path: str, dry_run: bool = False):
    """
    Creates an empty file at the specified path.
    Creates necessary parent directories if they don't exist.
    Records the creation for rollback (as a deletion).
    """
    dest_dir = os.path.dirname(file_path)
    if not os.path.exists(dest_dir):
        if dry_run:
            logging.info(f"📁 [DRY RUN] Would create directory: {dest_dir} for new file.")
        else:
            try:
                os.makedirs(dest_dir, exist_ok=True)
                logging.info(f"📁 Created directory: {dest_dir} for new file.")
            except OSError as e:
                logging.error(f"❌ Error creating directory {dest_dir} for new file: {e}")
                return

    if dry_run:
        logging.info(f"➕ [DRY RUN] Would create empty file: {file_path}")
    else:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                pass # Creates an empty file
            logging.info(f"➕ Created empty file: {file_path}")
            # For creation, rollback means deleting the created file.
            rollback_data.append({'action': 'DELETE', 'path': os.path.relpath(file_path, ROOT)})
        except Exception as e:
            logging.error(f"❌ Error creating empty file {file_path}: {e}")

def delete_file(file_path: str, dry_run: bool = False):
    """
    Deletes a file. Records the deletion for rollback (as a creation).
    """
    if dry_run:
        logging.info(f"🗑️ [DRY RUN] Would delete: {file_path}")
    else:
        try:
            os.remove(file_path)
            logging.info(f"🗑️ Deleted: {file_path}")
            # For deletion, rollback means recreating the file.
            rollback_data.append({'action': 'CREATE', 'path': os.path.relpath(file_path, ROOT)})
        except FileNotFoundError:
            logging.warning(f"⚠️ File not found (during deletion attempt): {file_path}")
        except Exception as e:
            logging.error(f"❌ Error deleting {file_path}: {e}")

def move_file(src_path: str, dest_path: str, dry_run: bool = False):
    """
    Moves a file from src_path to dest_path. Creates destination directories if they don't exist.
    Records the move for rollback.
    """
    dest_dir = os.path.dirname(dest_path)

    # Ensure the destination directory exists
    if not os.path.exists(dest_dir):
        if dry_run:
            logging.info(f"📁 [DRY RUN] Would create directory: {dest_dir}")
        else:
            try:
                os.makedirs(dest_dir, exist_ok=True)
                logging.info(f"📁 Created directory: {dest_dir}")
            except OSError as e:
                logging.error(f"❌ Error creating directory {dest_dir}: {e}")
                return

    if dry_run:
        logging.info(f"📝 [DRY RUN] Would move: {src_path} → {dest_path}")
    else:
        try:
            shutil.move(src_path, dest_path)
            logging.info(f"✅ Moved: {src_path} → {dest_path}")
            # Record for rollback: source is where it ended up, destination is where it came from
            rollback_data.append({'action': 'MOVE', 'source': os.path.relpath(dest_path, ROOT), 'destination': os.path.relpath(src_path, ROOT)})
        except FileNotFoundError:
            logging.warning(f"⚠️ File not found (during move attempt): {src_path}")
        except Exception as e:
            logging.error(f"❌ Error moving {src_path}: {e}")

def delete_empty_directories(start_dir: str, expected_dirs: set[str], dry_run: bool = False):
    """
    Recursively deletes empty directories starting from start_dir,
    excluding directories that are explicitly expected by the structure.
    Records deleted directories for rollback.
    """
    logging.info(f"\n🗑️ Checking for and deleting empty directories in '{start_dir}'...")
    deleted_any = False
    
    # Walk from bottom-up (dirpath is the directory, dirnames are its immediate subdirectories)
    # This ensures child directories are processed and potentially deleted before parents.
    for dirpath, dirnames, filenames in os.walk(start_dir, topdown=False):
        # Skip the root directory itself from deletion
        if normalize_path(dirpath) == normalize_path(ROOT):
            continue

        # Check if the directory is empty and not an explicitly expected directory
        is_empty = not dirnames and not filenames # No subdirs AND no files
        is_expected = normalize_path(dirpath) in expected_dirs

        if is_empty and not is_expected:
            if dry_run:
                logging.info(f"🧹 [DRY RUN] Would delete empty directory: {dirpath}")
            else:
                try:
                    os.rmdir(dirpath)
                    logging.info(f"🧹 Deleted empty directory: {dirpath}")
                    # For directory deletion, rollback means recreating the directory.
                    rollback_data.append({'action': 'CREATE_DIR', 'path': os.path.relpath(dirpath, ROOT)})
                    deleted_any = True
                except OSError as e:
                    logging.error(f"❌ Error deleting directory {dirpath}: {e}")
                except Exception as e:
                    logging.error(f"❌ Unexpected error deleting directory {dirpath}: {e}")
    
    if not deleted_any and not dry_run:
        logging.info("ℹ️ No empty directories were deleted.")

def generate_rollback_file():
    """
    Generates a CSV file with actions for rolling back moves, creations, and deletions.
    """
    if not rollback_data:
        logging.info("ℹ️ No file system changes were made, no rollback file generated.")
        return

    rollback_csv_path = os.path.join(ROOT, "rollback_log.csv")
    try:
        with open(rollback_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # action: 'MOVE', 'DELETE', 'CREATE', 'CREATE_DIR'
            # path1: Source for MOVE, path for DELETE/CREATE_DIR, created path for CREATE
            # path2: Destination for MOVE
            fieldnames = ['action', 'path1', 'path2'] 
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in rollback_data:
                if entry['action'] == 'MOVE':
                    writer.writerow({'action': 'MOVE', 'path1': entry['source'], 'path2': entry['destination']})
                elif entry['action'] == 'DELETE': # Rollback for creation is deletion
                    writer.writerow({'action': 'DELETE', 'path1': entry['path'], 'path2': ''})
                elif entry['action'] == 'CREATE': # Rollback for deletion is creation
                    writer.writerow({'action': 'CREATE', 'path1': entry['path'], 'path2': ''})
                elif entry['action'] == 'CREATE_DIR': # Rollback for directory deletion is directory creation
                    writer.writerow({'action': 'CREATE_DIR', 'path1': entry['path'], 'path2': ''})
        logging.info(f"📄 Rollback log generated: {rollback_csv_path}")
        logging.info("To undo changes: 'MOVE' (path1 -> path2), 'DELETE' (delete path1), 'CREATE' (create empty path1), 'CREATE_DIR' (create dir path1).")
    except Exception as e:
        logging.error(f"❌ Error generating rollback file: {e}")

def organize_project(dry_run: bool = False):
    """
    Performs a comprehensive organization of the project directory based on the 'structure'.
    It ensures all defined files are in their correct single location, deletes duplicates,
    identifies unlisted files, and removes unnecessary empty directories.
    """
    logging.info(f"\n{'[DRY RUN] ' if dry_run else ''}🔧 Starting comprehensive project directory organization...")

    # --- Step 1: Prepare Expected Paths and Directories ---
    # Store all target file paths and expected directory paths for quick lookup
    defined_file_targets = set() # Absolute paths of where files *should* be
    expected_directory_paths = set() # Absolute paths of directories that *should* exist

    # Add the root itself to expected directories
    expected_directory_paths.add(normalize_path(ROOT))

    for folder, subcontents in structure.items():
        # Add top-level target folders (e.g., 'src', 'tests', 'delete', 'root')
        current_level_dir = os.path.join(ROOT, folder)
        expected_directory_paths.add(normalize_path(current_level_dir))

        for subdir, files in subcontents.items():
            if subdir: # If it's a sub-directory, add it to expected paths
                nested_dir = os.path.join(ROOT, folder, subdir)
                expected_directory_paths.add(normalize_path(nested_dir))
            
            # For each file, determine its final target path and add to defined_file_targets
            for filename in files:
                if subdir:
                    target_file_path = os.path.join(ROOT, folder, subdir, filename)
                else:
                    target_file_path = os.path.join(ROOT, folder, filename)
                defined_file_targets.add(normalize_path(target_file_path))
    
    # Ensure all expected directories exist (create if dry_run is False)
    logging.info("\n📁 Ensuring all target directories exist...")
    for dir_path in sorted(list(expected_directory_paths)):
        if not os.path.exists(dir_path):
            if dry_run:
                logging.info(f"📁 [DRY RUN] Would create expected directory: {dir_path}")
            else:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logging.info(f"📁 Created expected directory: {dir_path}")
                    # Only record directory creation for rollback if it wasn't already expected
                    if dir_path not in expected_directory_paths: # This check is actually redundant due to how expected_directory_paths is built
                         rollback_data.append({'action': 'DELETE_DIR', 'path': os.path.relpath(dir_path, ROOT)})
                except OSError as e:
                    logging.error(f"❌ Error creating expected directory {dir_path}: {e}")


    # --- Step 2: Process Each Defined File ---
    logging.info("\n🔄 Processing defined files: Moving or Creating...")
    # Keep track of files already processed to avoid redundant operations
    processed_files_canonical = set()

    for folder, subcontents in structure.items():
        for subdir, files in subcontents.items():
            for filename in files:
                # Calculate the canonical (target) destination path for this file
                if subdir:
                    canonical_dest_path = os.path.join(ROOT, folder, subdir, filename)
                else:
                    canonical_dest_path = os.path.join(ROOT, folder, filename)
                canonical_dest_path = normalize_path(canonical_dest_path)

                if canonical_dest_path in processed_files_canonical:
                    # This means we've already handled a file that maps to this target path
                    # (e.g., if two entries in 'structure' somehow point to the same file name/path, which shouldn't happen)
                    continue
                processed_files_canonical.add(canonical_dest_path)

                # Find all current locations of this filename in the actual file system
                current_file_locations = find_all_files_in_root(filename, ROOT)

                # Filter out the canonical destination if it's among the current locations
                # and treat it as the primary if it exists and is correct.
                # If the canonical destination exists and is the only instance, it's 'in place'.
                if canonical_dest_path in current_file_locations:
                    current_file_locations.remove(canonical_dest_path) # Remove the good one from the list of duplicates
                    if not current_file_locations: # If no other copies exist
                        logging.info(f"⏩ Already in place: {canonical_dest_path}")
                    else:
                        logging.info(f"✅ Primary in place: {canonical_dest_path}. Remaining duplicates will be handled.")
                        # Duplicates will be handled in the cleanup phase

                # If the canonical destination does NOT exist, handle it
                else:
                    if current_file_locations:
                        # File exists somewhere else, move the first found instance to the canonical spot
                        source_to_move = current_file_locations.pop(0) # Take the first one
                        move_file(source_to_move, canonical_dest_path, dry_run)
                    else:
                        # File not found anywhere, create an empty one
                        logging.warning(f"⚠️ '{filename}' not found anywhere. Creating empty file at: {canonical_dest_path}")
                        create_empty_file(canonical_dest_path, dry_run)
                
                # Any remaining locations in current_file_locations are duplicates that need deletion
                for duplicate_path in current_file_locations:
                    logging.info(f"🗑️ Found duplicate for {filename}: {duplicate_path}. Deleting...")
                    delete_file(duplicate_path, dry_run)


    # --- Step 3: Comprehensive Cleanup of Undefined Files ---
    # Scan the entire project directory for files that are not in defined_file_targets
    # (and are not the script itself or log files).
    logging.info("\n🧹 Identifying and deleting unlisted files...")
    script_name = os.path.basename(__file__)
    
    # Collect all files currently in the file system
    all_current_fs_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            all_current_fs_files.append(normalize_path(full_path))

    for file_path in all_current_fs_files:
        if file_path not in defined_file_targets:
            base_filename = os.path.basename(file_path)
            # Exclude the script itself and the log files generated by the script
            if base_filename == script_name or \
               base_filename == LOG_FILE or \
               base_filename == "rollback_log.csv":
                continue
            
            # If it's a file that was just created as a placeholder, don't delete it again.
            # This is implicitly handled because create_empty_file adds it to the FS and target_dest_path set.

            logging.info(f"🗑️ Unlisted file: {file_path}. Deleting...")
            delete_file(file_path, dry_run)


    # --- Step 4: Delete Empty Directories ---
    # This must be done after all file movements and deletions,
    # and it must respect the expected_directory_paths.
    delete_empty_directories(ROOT, expected_directory_paths, dry_run)

    logging.info(f"\n{'[DRY RUN] ' if dry_run else ''}✅ Comprehensive organization complete.")

    if not dry_run:
        generate_rollback_file()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize project directory.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Perform a dry run without making any changes to the file system.")
    args = parser.parse_args()

    # Clear previous log file on each run for fresh logging
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8'):
            pass # Truncate the file

    if not args.dry_run:
        response = input("This script will reorganize and clean your project files (including deleting duplicates and empty folders). Do you want to proceed? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            logging.info("Operation cancelled by user.")
            exit()

    organize_project(dry_run=args.dry_run)
