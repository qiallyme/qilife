# move_to_type_folders.py

import os
import shutil

from pathlib import Path

def move_files_to_type_folders(directory):
    # Determine script name to ignore
    script_name = os.path.basename(__file__)
    for item in os.listdir(directory):
        # Skip the running script itself
        if item == script_name:
            continue
        item_path = os.path.join(directory, item)
        # Only handle files (ignore folders)
        if not os.path.isfile(item_path):
            continue
        _, ext = os.path.splitext(item)
        if ext:
            # Extension without the dot, uppercase
            ext_upper = ext[1:].upper()
            destination_folder = os.path.join(directory, ext_upper)
            # Create folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)
            # Move the file
            try:
                shutil.move(item_path, os.path.join(destination_folder, item))
                print(f"Moved '{item}' to '{destination_folder}'")
            except Exception as e:
                print(f"Error moving '{item}': {e}")

if __name__ == "__main__":
    # Prompt user for the directory to organize
    source_directory = input("Enter the path of the directory you want to organize: ").strip()
    if not os.path.isdir(source_directory):
        print(f"Error: '{source_directory}' is not a valid directory. Exiting.")
    else:
        move_files_to_type_folders(source_directory)
        print("Finished moving files to their respective folders.")
