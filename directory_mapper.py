import os
import datetime
import logging
import sys

# --- Configuration ---
# List of common system directory names to exclude (case-insensitive)
# Add any other specific directories you want to always exclude here.
EXCLUDE_SYSTEM_DIRS = [
    "$recycle.bin",              # Windows Recycle Bin
    "system volume information", # Windows system folder
    "$windows.~bt",              # Windows Update temporary files
    "$windows.~ws",              # Windows Upgrade files
    "recycled",                  # Linux/macOS Recycle Bin variations
    ".trash",                    # Linux/macOS Trash variations
    "program files",             # Example: If mapping C:\, might want to skip these large system folders
    "program files (x86)",
    "windows",
    "msocache",                  # Microsoft Office Cache
    "config.msi",                # Windows Installer cache
    "appdata",                   # User's application data (can be large and contains many hidden files)
    "documents and settings",    # Old Windows user profile path
    "desktop",                   # Often contains many transient files/shortcuts
    "my documents",
    "my pictures",
    "my music",
    "my videos",
    "downloads",                 # As the log output folder, might want to exclude if mapping parent
    "temp",                      # Temporary files
    "tmp"                        # Temporary files
]

# --- Logging Setup ---
# Determine the Downloads folder path
# This works for Windows, macOS, and Linux
try:
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder, exist_ok=True)
except Exception as e:
    # Fallback if Downloads folder cannot be determined or created
    downloads_folder = os.getcwd()
    print(f"Warning: Could not determine/create Downloads folder. Logging to current directory: {downloads_folder}. Error: {e}")

# Generate a timestamp for the log file name
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(downloads_folder, f"directory_map_{timestamp}.txt")

# Set up logging to both a file and the console
# FileHandler explicitly uses utf-8 encoding for file output
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
# StreamHandler for console output (no encoding specified, relies on system default)
stream_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(level=logging.INFO,
                    format='%(message)s', # Only the message, no extra log info (like time, level)
                    handlers=[
                        file_handler,
                        stream_handler
                    ])

# --- Directory Mapping Function ---

def map_directory_tree(start_path: str, max_depth: int, current_depth: int = 0, indent: str = '', exclude_hidden: bool = True, exclude_system: bool = True):
    """
    Recursively prints and logs the directory tree structure.

    Args:
        start_path (str): The starting directory path to map.
        max_depth (int): The maximum number of levels to go down from the start_path.
                         -1 for infinite depth.
        current_depth (int): The current recursion level (for internal use).
        indent (str): Internal parameter for indentation in the tree.
        exclude_hidden (bool): If True, files/directories starting with '.' are excluded.
        exclude_system (bool): If True, common system directories (from EXCLUDE_SYSTEM_DIRS) are excluded.
    """
    if not os.path.exists(start_path):
        logging.error(f"Error: Path '{start_path}' does not exist.")
        return
    if not os.path.isdir(start_path):
        logging.error(f"Error: Path '{start_path}' is not a directory.")
        return

    # Stop recursion if max_depth is reached (and it's not infinite depth)
    if max_depth != -1 and current_depth > max_depth:
        return

    try:
        # Get all items in the current directory
        items = os.listdir(start_path)
    except PermissionError:
        logging.warning(f"{indent}├── [Permission Denied] {os.path.basename(start_path)}")
        return
    except Exception as e:
        logging.error(f"{indent}├── [Error Listing Directory] {os.path.basename(start_path)}: {e}")
        return
    
    # Filter out hidden and system items
    filtered_items = []
    for item in items:
        # Exclude hidden files/directories (starting with '.')
        if exclude_hidden and item.startswith('.'):
            continue
        
        # Exclude common system directories (case-insensitive)
        if exclude_system and item.lower() in EXCLUDE_SYSTEM_DIRS:
            continue

        filtered_items.append(item)

    # Sort filtered items for consistent output
    filtered_items.sort()

    for i, item in enumerate(filtered_items):
        item_path = os.path.join(start_path, item)
        
        is_last_item = (i == len(filtered_items) - 1)
        
        # Determine the prefix for the current item in the tree
        prefix = "└── " if is_last_item else "├── "
        
        # Print and log the current item
        logging.info(f"{indent}{prefix}{item}")

        # If it's a directory and we haven't reached max_depth, recurse
        if os.path.isdir(item_path):
            if max_depth == -1 or current_depth < max_depth:
                next_indent = indent + ("    " if is_last_item else "│   ")
                # Pass the exclude_system flag to recursive calls
                map_directory_tree(item_path, max_depth, current_depth + 1, next_indent, exclude_hidden, exclude_system)

# --- Main Execution Block ---

if __name__ == "__main__":
    logging.info("✨ Directory Mapper ✨")
    logging.info("This script will display your directory tree, excluding hidden files and folders (those starting with a '.'),")
    logging.info("and common system directories (like Recycle Bin, System Volume Information).")
    logging.info(f"All output will also be saved to: {LOG_FILE}")
    
    # Loop until a valid directory is provided
    while True:
        user_path = input("\nPlease enter the path of the directory you want to map (e.g., C:\\MyProject or . for current directory): ")
        
        # Resolve "." to the current working directory
        if user_path == ".":
            start_dir = os.getcwd()
        else:
            start_dir = os.path.abspath(user_path) # Use abspath to handle relative paths

        if os.path.isdir(start_dir):
            break
        else:
            logging.error(f"Invalid path: '{user_path}'. Please enter a valid directory path.")

    # Loop until a valid depth is provided
    while True:
        try:
            depth_input = input("Enter maximum depth to traverse (-1 for infinite depth): ")
            max_depth = int(depth_input)
            break
        except ValueError:
            logging.error("Invalid input. Please enter an integer.")

    logging.info(f"\nMapping directory: {start_dir}")
    logging.info(f"Maximum depth: {'Infinite' if max_depth == -1 else max_depth}")
    logging.info("-" * 30)

    # Start mapping the directory tree
    # The initial call has current_depth = 0 and passes both exclude flags
    map_directory_tree(start_dir, max_depth, exclude_hidden=True, exclude_system=True)
    
    logging.info("-" * 30)
    logging.info(f"\nMapping complete! Output saved to: {LOG_FILE}")
