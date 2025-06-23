import os
import argparse
from datetime import datetime

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

def get_valid_directory(initial_path=None):
    """
    Prompts the user to enter a valid directory path until a valid one is provided.
    If an initial_path is provided, it attempts to validate that first.
    
    Returns:
    - str: The absolute path of the valid directory.
    """
    if initial_path:
        root_dir = os.path.abspath(initial_path)
        if os.path.isdir(root_dir):
            return root_dir
        else:
            print(f"Error: The provided path '{root_dir}' is not a valid directory.")

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
            return True   # Both folders and files
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
    If a file with the same base name and a previous increment exists, it increments the number.

    Parameters:
    - filename_prefix (str): The prefix for the log file name.
    - suffix (str, optional): An optional suffix to add to the log file name.

    Returns:
    - file object: The opened log file ready for writing.
    """
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Sanitize filename_prefix to remove invalid characters for filenames
    # This is important if filename_prefix is derived from a path
    sanitized_prefix = "".join(c for c in filename_prefix if c.isalnum() or c in (' ', '_', '-')).strip()
    if not sanitized_prefix: # Fallback if sanitation results in empty string
        sanitized_prefix = "log"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_log_file_name = f"{sanitized_prefix}_{timestamp}{suffix}"
    log_file_name = f"{base_log_file_name}.txt"
    log_file_path = os.path.join(downloads_dir, log_file_name)

    counter = 1
    while os.path.exists(log_file_path):
        log_file_name = f"{base_log_file_name}_{counter}.txt"
        log_file_path = os.path.join(downloads_dir, log_file_name)
        counter += 1

    return open(log_file_path, "w", encoding="utf-8")

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

def main(root_dir):
    """
    Main function to orchestrate the directory mapping process for a single root directory.
    """
    try:
        show_files = get_user_choice()
        max_depth = get_max_depth()

        # First Log (directory tree)
        log_file_tree = create_log_file(os.path.basename(root_dir), "_tree")
        print(f"Log file created: {log_file_tree.name}")
        print(f"Resolved path: {root_dir}")
        log_file_tree.write(f"Resolved path: {root_dir}\n")
        print_directory_tree(root_dir, show_files, max_depth, log_file=log_file_tree)
        log_file_tree.close()
        print(f"Directory structure logged in: {log_file_tree.name}")

    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    
    while True:
        # Get a valid root directory, either from args or by prompting the user
        current_root_dir = get_valid_directory(args.directory)
        
        # Call main with the single valid root directory
        main(current_root_dir)
        
        # Reset args.directory to None so that if the user runs again, 
        # they are prompted for a new directory instead of reusing the initial arg.
        args.directory = None 

        if not run_again_prompt():
            break