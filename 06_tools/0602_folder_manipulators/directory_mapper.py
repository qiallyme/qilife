import os
# Ignore rules
IGNORE_FOLDERS = {
    '__pycache__', 'venv', 'env', '.git', 'node_modules',
    '.idea', '.vscode', '.mypy_cache', 'dist', 'build'
}

IGNORE_EXTENSIONS = {
    '.pyc', '.pyo', '.log', '.DS_Store'
}

def is_ignored(path):
    """Check if a path should be ignored based on folder and extension rules."""
    return any(folder in path for folder in IGNORE_FOLDERS) or path.endswith(tuple(IGNORE_EXTENSIONS))

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
    def should_ignore(name, full_path):
        """Check if a file/folder should be skipped based on rules."""
        if name in IGNORE_FOLDERS and os.path.isdir(full_path):
            return True
        for ext in IGNORE_EXTENSIONS:
            if name.endswith(ext):
                return True
        return False

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
            if is_ignored(item):
                continue
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
            print_directory_tree(path, show_files, max_depth, current_depth + 1, prefix + extension, log_file, include_hidden)

if __name__ == "__main__":
    root_directory = input("Enter the root directory to map: ")
    while not os.path.isdir(root_directory):
        print("Invalid directory path. Please try again.")
        root_directory = input("Enter the root directory to map: ")

    depth_str = input("Enter the maximum depth to traverse (leave blank for no limit): ")
    max_depth = None
    if depth_str.strip():
        try:
            max_depth = int(depth_str)
            if max_depth < 0:
                print("Depth must be a non-negative integer.")
                max_depth = None
        except ValueError:
            print("Invalid depth entered. Showing all levels.")

    show_files = True

    include_hidden = True

    default_log_path = os.path.expanduser("~/Downloads/directory_tree.log")
    log_file_path = input(f"Enter the path for the log file (leave blank for '{default_log_path}'): ")
    if not log_file_path.strip():
        log_file_path = default_log_path

    log_output = None
    try:
        # Explicitly open the file with UTF-8 encoding
        log_output = open(log_file_path, 'w', encoding='utf-8')
        print(f"Log output will be saved to: {log_file_path}")
    except IOError:
        print(f"Error: Could not open log file '{log_file_path}' for writing.")

    print("\nDirectory Tree:")
    print_directory_tree(root_directory, show_files, max_depth, log_file=log_output, include_hidden=include_hidden)

    if log_output:
        log_output.close()
        print(f"\nOutput saved to: {log_file_path}")