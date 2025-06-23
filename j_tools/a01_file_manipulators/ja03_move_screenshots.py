import os
import re
import shutil

def delete_screenshots(directory, mode):
    """
    Moves screenshot files to a 'check before delete' folder based on the selected mode.

    Args:
        directory (str): The path to the directory containing screenshots.
        mode (str): The deletion mode ('1' for digit-based, '2' for pattern-based).
    """
    try:
        delete_folder = os.path.join(directory, "check before delete")
        os.makedirs(delete_folder, exist_ok=True)
        print(f"Safety folder is: {delete_folder}\n")

        # Get a list of all items and filter for files only, excluding subdirectories.
        all_items = os.listdir(directory)
        files = [f for f in all_items if os.path.isfile(os.path.join(directory, f))]
        
        moved_count = 0

        # --- Mode 1: Original Logic (Delete based on filename's last digit) ---
        if mode == '1':
            print("Running Round 1: Moving files based on filename's last digit...")
            for filename in files:
                match = re.search(r'(\d+)\D*$', filename)  # Extract trailing numbers
                if match:
                    numeric_part = match.group(1)
                    # Files ending in these numbers will be moved.
                    if numeric_part and numeric_part[-1] in ('1', '2', '3', '5', '6', '7', '9', '0'):
                        source_filepath = os.path.join(directory, filename)
                        destination_filepath = os.path.join(delete_folder, filename)
                        try:
                            shutil.move(source_filepath, destination_filepath)
                            print(f"Moved: {filename}")
                            moved_count += 1
                        except OSError as e:
                            print(f"Error moving {filename}: {e}")

        # --- Mode 2: New Pattern Logic ---
        elif mode == '2':
            # This pattern matches your request: "erase one, skip two, erase one, skip one, erase one, skip two"
            # It moves 3 out of every 8 files, or 37.5%.
            print("Running Round 2: Moving files using a custom pattern...")
            print("Pattern: Move 1, Skip 2, Move 1, Skip 1, Move 1, Skip 2")
            
            # Sort files to ensure a consistent, predictable order for the pattern.
            files.sort()
            
            for i, filename in enumerate(files):
                # The pattern repeats every 8 files. We move files at indices 0, 3, and 5 in the cycle.
                # This corresponds to the 1st, 4th, and 6th files.
                if i % 8 == 0 or i % 8 == 3 or i % 8 == 5:
                    source_filepath = os.path.join(directory, filename)
                    destination_filepath = os.path.join(delete_folder, filename)
                    try:
                        shutil.move(source_filepath, destination_filepath)
                        print(f"Moved: {filename}")
                        moved_count += 1
                    except OSError as e:
                        print(f"Error moving {filename}: {e}")
                else:
                    # Optional: uncomment the line below to see which files are being skipped.
                    # print(f"Skipped: {filename}")
                    pass

        print(f"\nFinished processing. Moved {moved_count} files to '{delete_folder}'.")
        print("Please review the files in this folder before deleting them permanently.")

    except FileNotFoundError:
        print(f"Error: Directory not found: {directory}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    """Handles user input and starts the file deletion process."""
    screenshot_directory = input("Enter the directory containing the screenshots: ")
    if not os.path.isdir(screenshot_directory):
        print(f"Error: Directory not found: {screenshot_directory}")
        return

    print("\nPlease choose a deletion method:")
    print("  1: Round 1 (Original method: moves files based on last digit)")
    print("  2: Round 2 (New method: moves files in a patterned sequence)")

    choice = input("Enter your choice (1 or 2): ")

    if choice in ['1', '2']:
        delete_screenshots(screenshot_directory, choice)
    else:
        print("Invalid choice. Please run the script again and enter 1 or 2.")

if __name__ == "__main__":
    main()