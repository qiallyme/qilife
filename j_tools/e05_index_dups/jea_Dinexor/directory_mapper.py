from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import shutil
import argparse
from datetime import datetime
import pytesseract
from PIL import Image
import pdf2image
import re
import json
import webbrowser
import threading
import importlib.util
import subprocess
import os # Import the os module

app = Flask(__name__)

def print_directory_tree(root_dir, show_files=True, max_depth=None, current_depth=0, prefix='', log_file=None, include_hidden=True):
    """
    Recursively prints the directory tree structure up to the specified depth and writes to a log file.

    Parameters:
    - root_dir (str): The root directory path.
    - show_files (bool): Whether to include files in the output.
    - max_depth (int): Maximum depth to traverse. None means no limit.
    - current_depth (int): Current depth level in the recursion.
    - prefix (str): The prefix string used for indentation and connectors.
    - log_file (file object): The file to write the log output.
    """
    if max_depth is not None and current_depth >= max_depth:
        return

    try:
        # Get the list of items in the directory
        items = os.listdir(root_dir)
    except PermissionError:
        message = prefix + "└── [Permission Denied]"
        print(message)
        if log_file:
            log_file.write(message + "\n")
        return
    except FileNotFoundError:
        message = prefix + "└── [Directory Not Found]"
        print(message)
        if log_file:
            log_file.write(message + "\n")
        return

    # Sort items: directories first, then files
    items = sorted(items, key=lambda s: s.lower())
    directories = [item for item in items if os.path.isdir(os.path.join(root_dir, item))]
    files = [item for item in items if not os.path.isdir(os.path.join(root_dir, item))]
    
    if not show_files:
        items = directories
    else:
        items = directories + files

    # Iterate over items with enumeration to identify the last item
    for index, item in enumerate(items):
        if not include_hidden and item.startswith('.'): #skip hidden files
            continue
        path = os.path.join(root_dir, item)
        # Determine the connector based on position
        if index == len(items) - 1:
            connector = '└── '
            extension = '    '
        else:
            connector = '├── '
            extension = '│   '

        # Print the current item
        message = prefix + connector + item
        print(message)
        if log_file:
            log_file.write(message + "\n")

        # If the item is a directory, recurse into it
        if os.path.isdir(path):
            print_directory_tree(path, show_files, max_depth, current_depth + 1, prefix + extension, log_file)

def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
    - args: The parsed arguments containing the directory path.
    """
    parser = argparse.ArgumentParser(description='Map and print the directory structure of a given top-level directory.')
    parser.add_argument('directory', nargs='?', default=None, help='Path to the top-level directory (optional)')
    return parser.parse_args()

def get_valid_directory():
    """
    Prompts the user to enter a valid directory path until a valid one is provided.
    
    Returns:
    - str: The absolute path of the valid directory.
    """
    while True:
        user_input = input("Enter the parent directory path: ").strip()
        root_dir = os.path.abspath(user_input)
        if os.path.isdir(root_dir):
            return root_dir
        else:
            print(f"Error: The path '{root_dir}' is not a valid directory. Please try again.")

def get_user_choice():
    """
    Prompts the user to choose between displaying only folders or both folders and files.

    Returns:
    - bool: True if the user chooses to show both, False if only folders.
    """
    while True:
        choice = input("Do you want to display (1) Only Folders or (2) Both Folders and Files? Enter 1 or 2: ").strip()
        if choice == "1":
            return False  # Only folders
        elif choice == "2":
            return True  # Both folders and files
        else:
            print("Invalid choice. Please enter 1 or 2.")

def get_max_depth():
    """
    Prompts the user to specify the maximum depth for traversal.

    Returns:
    - int: The maximum depth, or None if all levels should be shown.
    """
    while True:
        choice = input("Enter the maximum depth to display (1, 2, 3, 4, 5, or 'all' for unlimited): ").strip()
        if choice.lower() == 'all':
            return None
        if choice.isdigit() and int(choice) in {1, 2, 3, 4, 5}:
            return int(choice)
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 'all'.")

def create_log_file(filename_prefix, suffix=""):
    """
    Creates a log file in the Downloads folder with a timestamped name.

    Parameters:
    - filename_prefix (str): The prefix for the log file name.
    - suffix (str, optional): An optional suffix to add to the log file name.

    Returns:
    - file object: The opened log file ready for writing.
    """
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads") # Gets the downloads directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f"{filename_prefix}_{timestamp}{suffix}.txt"
    log_file_path = os.path.join(downloads_dir, log_file_name)
    return open(log_file_path, "w", encoding="utf-8")

def move_empty_folders(source_dir, destination_dir, log_file=None):
    """Moves empty folders and logs the actions, including permission errors."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)

        if os.path.isdir(item_path):
            try:
                if not os.listdir(item_path):
                    try:
                        shutil.move(item_path, os.path.join(destination_dir, item))
                        message = f"Moved empty folder: {item}"
                        print(message)
                        if log_file:
                            log_file.write(message + "\n")
                    except Exception as e:
                        message = f"Error moving {item}: {e}"
                        print(message)
                        if log_file:
                            log_file.write(message + "\n")

            except PermissionError as e:
                message = f"Permission error accessing {item_path}: {e}"
                print(message)
                if log_file:
                    log_file.write(message + "\n")

def extract_text_from_file(file_path, max_chars=5000):
    """Extracts text from various file types with error handling."""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext in ('.png', '.jpg', '.jpeg'):
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
            except Exception as e:
                return f"OCR Error: {e}"
        elif file_ext == '.pdf':
            try:
                images = pdf2image.convert_from_path(file_path)
                text = ""
                for img in images:
                    text += pytesseract.image_to_string(img)
            except Exception as e:
                return f"PDF Processing Error: {e}"
        elif file_ext in ('.txt', '.js', '.json', '.html', '.css', '.java', '.py', '.zcreator', '.doc', '.docx', '.rtf', '.csv', '.xml'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
                return f"File Read Error: {e}"
        elif file_ext in ('.xls', '.xlsx'):
            return "File is a spreadsheet. Text extraction not implemented."
        else:
            return None  # Skip unsupported files

        return text[:max_chars]

    except Exception as e:
        return f"General Error: {e}"

def get_destination_directory(root_dir):
    """Prompts the user for a destination directory."""
    while True:
        dest_input = input("Enter destination directory for empty folders (or press Enter for default Downloads): ").strip()
        if not dest_input:
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            return downloads_dir
        destination_dir = os.path.abspath(dest_input)
        if os.path.exists(destination_dir):
            return destination_dir
        else:
            print("Invalid directory. Please try again.")

def extract_text_from_file(file_path, max_chars=5000):
    """Extracts text from an image or PDF file using OCR."""
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
        elif file_path.lower().endswith('.pdf'):
            images = pdf2image.convert_from_path(file_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)
        else:
            return None  # Skip non-image/PDF files

        # Truncate text to max_chars
        return text[:max_chars]

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None        

def process_log_and_index(log_file_path, index_file_path):
    """Processes the log file, extracts text, and creates an index with error handling."""
    index_data = {}

    try:
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            for line in log_file:
                match = re.search(r'\(Path: (.+)\)', line)
                if match:
                    file_path = match.group(1)
                    if os.path.isfile(file_path):
                        text = extract_text_from_file(file_path)
                        if text:
                            index_data[file_path] = text
                            print(f"Indexed: {file_path}")
                        else:
                            print(f"Skipped: {file_path}")
                    else:
                        print(f"File not found: {file_path}") # Log if file doesn't exist

        try:
            with open(index_file_path, 'w', encoding='utf-8') as index_file:
                json.dump(index_data, index_file, ensure_ascii=False, indent=4)
            print(f"Index created: {index_file_path}")
        except Exception as e:
            print(f"JSON Error: {e}")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        print(f"Log File Error: {e}")

def run_again_prompt():
    """Asks the user if they want to run the program again."""
    while True:
        choice = input("Run the program again? (yes/no): ").lower()
        if choice in ('yes', 'y'):
            return True
        elif choice in ('no', 'n'):
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def main(directories_to_index):
    log_file_path = ""
    try:
        for root_dir in directories_to_index:
            root_dir = os.path.abspath(root_dir)
            if not os.path.isdir(root_dir):
                print(f"Error: The path '{root_dir}' is not a valid directory.")
                continue

            show_files = get_user_choice()
            max_depth = get_max_depth()

            #first Log (directory tree)
            log_file_tree = create_log_file("directory_log", "_tree")
            log_file_path = log_file_tree.name
            print(f"Log file created: {log_file_tree.name}")
            print(f"Resolved path: {root_dir}")
            log_file_tree.write(f"Resolved path: {root_dir}\n")
            print_directory_tree(root_dir, show_files, max_depth, log_file=log_file_tree)
            log_file_tree.close()
            print(f"Directory structure logged in: {log_file_tree.name}")

            # Move Empty Folders
            destination_dir = get_destination_directory(root_dir)
            log_file_move = create_log_file("empty_folder_move", "_move") # updated prefix.
            move_empty_folders(root_dir, destination_dir, log_file=log_file_move)
            log_file_move.close()
            print(f"Empty folders moved. Log file: {log_file_move.name}")

        return directories_to_index[0], log_file_path
    except Exception as e:
        print(f"An unexpected error occured in main: {e}")
        return directories_to_index[0], ""

@app.route('/')
def index():
    return render_template('index.html') #render the html gui

@app.route('/run', methods=['POST'])
def run_program():
    data = request.get_json()
    source_dir = data['sourceDir']
    dest_dir = data['destDir']
    show_files = data['showFiles']
    max_depth = int(data['maxDepth'])

    # Validation (similar to your Python validation)
    if not os.path.isdir(source_dir):
        return jsonify({'error': 'Invalid source directory'}), 400

    directories_to_index = [source_dir]
    root_dir = main(directories_to_index)  # Call your main function
    index_file_path = os.path.join(root_dir, "file_index.json")
    process_log_and_index(os.path.join(os.path.expanduser("~"), "Downloads", f"directory_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tree.txt"), index_file_path)

    return jsonify({'result': f'Processed and indexed directory: {source_dir}'})

@app.route('/run_default', methods=['POST'])
def run_default():
    directories_to_index = [
        "C:\\ProgramData",
        "C:\\Users",
        "E:\\"
    ]
    root_dir = main(directories_to_index, run_default=True)
    index_file_path = os.path.join(root_dir, "file_index.json")
    process_log_and_index(os.path.join(os.path.expanduser("~"), "Downloads", f"directory_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tree.txt"), index_file_path)

    return jsonify({'result': 'Default run completed.'})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')  # Open the GUI in the default browser

def check_and_install_dependencies():
    """Checks if required libraries are installed and installs them if not."""
    requirements_file = 'requirements.txt'  # Path to requirements.txt
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found. Please ensure it is in the same directory as the script.")
        return False

    try:
        subprocess.check_call(
            ['pip', 'install', '-r', requirements_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("Installation from requirements.txt successful. Please run the script again.")
        return False  # Indicate installation was attempted
    except subprocess.CalledProcessError as e:
        print(f"Installation from requirements.txt failed: {e}")
        print("Please install the libraries manually or ensure your requirements.txt is correct.")
        return False  # Indicate installation failed
    return True  # Indicate all libraries are installed

if __name__ == '__main__':
    if not check_and_install_dependencies():
        exit() # Exit if installation was attempted or failed
    threading.Timer(1, open_browser).start()  # Open the browser after 1 second
    app.run(debug=True, use_reloader=False)  # Run Flask (debug=True for development)


#    args = parse_arguments()
#    root_dir = get_valid_directory() if args.directory is None else os.path.abspath(args.directory)

#    if not os.path.isdir(root_dir):
#        print(f"Error: The path '{root_dir}' is not a valid directory.")
#       root_dir = get_valid_directory()

#    show_files = get_user_choice()
#    max_depth = get_max_depth()

#   First Log
#   log_file_tree = create_log_file(root_dir, "_tree")
#   print(f"Log file created: {log_file_tree.name}")
#   print(f"Resolved path: {root_dir}")
#   log_file_tree.write(f"Resolved path: {root_dir}\n")
#   print_directory_tree(root_dir, show_files, max_depth, log_file=log_file_tree)
#    log_file_tree.close()
#    print(f"Directory structure logged in: {log_file_tree.name}")
#
#    # Move Empty Folders
#    destination_dir = get_destination_directory(root_dir)
#    log_file_move = create_log_file(root_dir, "_move")
#    move_empty_folders(root_dir, destination_dir, log_file_move)
#    log_file_move.close()
#    print(f"Empty folders moved. Log file: {log_file_move.name}")

#    return root_dir # return root_dir for indexing.

#if __name__ == "__main__":
#    while True:
#        root_dir = main()
#        if not run_again_prompt():
#            # Indexing step when user chooses not to rerun
#            index_file_path = os.path.join(root_dir, "file_index.json") # Save index in the root directory.
#            process_log_and_index(os.path.join(root_dir, f"directory_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tree.txt"), index_file_path)
#            break