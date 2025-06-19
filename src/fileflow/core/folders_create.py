# create_folders.py

import os

source_directory = r"C:\Users\codyr\My Drive\01_INBOX"

def create_folders_by_type(directory):
    extensions = set()
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            _, ext = os.path.splitext(item)
            if ext:
                extensions.add(ext[1:].upper())  # Remove the dot and uppercase

    for ext in extensions:
        folder_name = os.path.join(directory, ext)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Created folder: {folder_name}")

if __name__ == "__main__":
    create_folders_by_type(source_directory)
    print("Finished creating folders by file type.")