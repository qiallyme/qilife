import os
import shutil
import pathlib
import datetime # Not strictly needed for this script, but good to keep from previous context if other functions are in the same file.

def consolidate_files_and_clean_folders():
    """
    Asks the user for a root directory. It then moves all files from
    subfolders within that root to the root directory itself.
    Empty subfolders are then moved to a 'folders_to_delete' directory
    created within the root.
    """
    while True:
        root_dir_str = input("Please enter the root directory path where files should be consolidated: ")
        root_dir = pathlib.Path(root_dir_str)

        if not root_dir.is_dir():
            print(f"Error: The provided path '{root_dir}' is not a valid directory. Please try again.")
        else:
            break

    folders_to_delete_dir = root_dir / "folders_to_delete"
    folders_to_delete_dir.mkdir(exist_ok=True)
    print(f"\nEmpty folders will be moved to: {folders_to_delete_dir}")

    # List to keep track of folders that might become empty
    # We'll process them from deepest to shallowest to ensure proper cleanup
    folders_to_check = []

    print(f"\nConsolidating files to: {root_dir}")

    # Walk through the directory tree from bottom up
    # This ensures that we process files in sub-subfolders before their parent subfolders,
    # and makes it easier to identify truly empty folders after file moves.
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        current_folder = pathlib.Path(dirpath)

        # Skip the root directory itself and the 'folders_to_delete' directory
        if current_folder == root_dir or current_folder == folders_to_delete_dir:
            continue

        print(f"\nProcessing folder: {current_folder.relative_to(root_dir)}")

        # Move files from the current folder to the root_dir
        for filename in filenames:
            source_file_path = current_folder / filename
            destination_file_path = root_dir / filename

            try:
                # Handle potential filename conflicts in the root directory
                if destination_file_path.exists():
                    stem = destination_file_path.stem
                    suffix = destination_file_path.suffix
                    counter = 1
                    while (root_dir / f"{stem}_{counter}{suffix}").exists():
                        counter += 1
                    new_destination_name = f"{stem}_{counter}{suffix}"
                    final_destination_path = root_dir / new_destination_name
                    print(f"  Conflict: '{filename}' already exists in root. Moving as '{new_destination_name}'.")
                else:
                    final_destination_path = destination_file_path

                shutil.move(source_file_path, final_destination_path)
                print(f"  Moved '{source_file_path.relative_to(root_dir)}' to '{final_destination_path.name}'")
            except Exception as e:
                print(f"  Error moving '{source_file_path.relative_to(root_dir)}': {e}")

        # After moving files, add this folder to the list to check for emptiness later
        folders_to_check.append(current_folder)

    print("\nChecking for empty folders...")
    # Now, iterate through the collected folders from deepest to shallowest
    # and move them if they are empty
    for folder_path in folders_to_check:
        try:
            # Re-check if the folder is empty after files might have been moved out of it
            # and its subfolders might have been moved.
            if not os.listdir(folder_path): # os.listdir returns an empty list if directory is empty
                print(f"  Folder '{folder_path.relative_to(root_dir)}' is empty. Moving to '{folders_to_delete_dir.name}'.")
                shutil.move(folder_path, folders_to_delete_dir / folder_path.name)
            else:
                print(f"  Folder '{folder_path.relative_to(root_dir)}' is not empty. Keeping it.")
        except Exception as e:
            print(f"  Error processing folder '{folder_path.relative_to(root_dir)}': {e}")

    print("\nConsolidation and cleanup process completed.")

if __name__ == '__main__':
    consolidate_files_and_clean_folders()