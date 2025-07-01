import os
import pathlib
import datetime
import platform

def get_file_creation_date(filepath):
    """
    Attempts to get the creation date of a file.
    On Windows, os.path.getctime returns creation time.
    On Unix-like systems (Linux, macOS), os.path.getctime returns the last metadata change time.
    For true creation time on Unix-like systems, st_birthtime is used if available.
    Falls back to modification time if creation time is not reliably available.
    """
    if platform.system() == 'Windows':
        timestamp = os.path.getctime(filepath)
    else:
        stat = os.stat(filepath)
        try:
            timestamp = stat.st_birthtime
        except AttributeError:
            # st_birthtime is not available on some Unix systems (e.g., older Linux kernels)
            # Fallback to last modification time
            timestamp = stat.st_mtime
    return datetime.datetime.fromtimestamp(timestamp)

def rename_files_with_date_and_text():
    """
    Prompts the user for a directory path and text to append to filenames.
    Renames each file in the directory by adding the custom text and
    the file's creation date (YYYYMMDD format) to the filename.
    Handles potential errors during renaming.
    """
    # 1. Ask for the path
    while True:
        directory_path_str = input("Please enter the directory path containing the files to rename: ")
        directory_path = pathlib.Path(directory_path_str)

        if not directory_path.is_dir():
            print(f"Error: The provided path '{directory_path}' is not a valid directory. Please try again.")
        else:
            break

    # 2. Ask for the text to append
    text_to_append = input("Please enter the text you want to add to the file names (e.g., 'Inova'): ")
    # Sanitize the input text for filenames (replace spaces with hyphens, convert to lowercase)
    sanitized_text = text_to_append.strip().lower().replace(" ", "-")

    print(f"\nScanning for files in: {directory_path}")
    
    # Get all files (not directories) in the specified path
    files_in_directory = [f for f in directory_path.iterdir() if f.is_file()]

    if not files_in_directory:
        print("No files found in the specified directory.")
        return

    print(f"Found {len(files_in_directory)} file(s).")

    for original_file_path in files_in_directory:
        try:
            # Get the creation date
            creation_datetime = get_file_creation_date(original_file_path)
            # Format the date as YYYYMMDD
            date_str = creation_datetime.strftime("%Y%m%d")

            # Get the original file name and its extension
            original_stem = original_file_path.stem  # filename without extension
            original_suffix = original_file_path.suffix  # .csv, .txt, etc.

            # Construct the new file name
            # Format: "custom-text-originalfilename-YYYYMMDD.extension"
            # Adjusted to match the example "inova-file-20220325.csv"
            new_file_name = f"{sanitized_text}-{original_stem}-{date_str}{original_suffix}"
            new_file_path = original_file_path.with_name(new_file_name)

            # Rename the file
            os.rename(original_file_path, new_file_path)
            print(f"Renamed '{original_file_path.name}' to '{new_file_path.name}'")

        except FileNotFoundError:
            print(f"Error: File '{original_file_path.name}' not found. It might have been moved or deleted.")
        except OSError as e:
            print(f"Error renaming '{original_file_path.name}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing '{original_file_path.name}': {e}")

    print("\nFile renaming process completed.")

if __name__ == '__main__':
    rename_files_with_date_and_text()