import os
from datetime import datetime
import shutil

def organize_screenshots_by_creation_date(screenshot_dir, output_root_dir=None):
    """
    Organizes screenshots into subfolders based on their creation date.

    Args:
        screenshot_dir (str): The directory containing the screenshots.
        output_root_dir (str, optional): The root directory where date folders will be created.
                                         If None, date folders will be created within the
                                         screenshot_dir. Defaults to None.
    """
    if output_root_dir is None:
        output_root_dir = screenshot_dir

    date_folders = {}  # Keep track of created folders

    for filename in os.listdir(screenshot_dir):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        filepath = os.path.join(screenshot_dir, filename)
        try:
            # Get the creation timestamp
            creation_timestamp = os.path.getctime(filepath)
            # Convert timestamp to datetime object
            creation_date_obj = datetime.fromtimestamp(creation_timestamp)
            date_folder_name = creation_date_obj.strftime('%Y-%m-%d')
            destination_folder = os.path.join(output_root_dir, date_folder_name)

            # Create the date folder if it doesn't exist
            if date_folder_name not in date_folders:
                os.makedirs(destination_folder, exist_ok=True)
                date_folders[date_folder_name] = destination_folder

            # Move the image to the date folder
            destination_filepath = os.path.join(destination_folder, filename)
            shutil.move(filepath, destination_filepath)
            print(f"Moved '{filename}' (created on {date_folder_name}) to '{destination_folder}'")

        except Exception as e:
            print(f"Error processing '{filename}': {e}")

# --- Production Execution ---
if __name__ == "__main__":
    screenshot_directory = r"C:\Users\codyr\My Drive\05_ARCHIVE\Screenshots"  # **SET YOUR DIRECTORY HERE**
    output_base_directory = os.path.join(screenshot_directory, "ProcessedScreenshots") # Optional output directory
    os.makedirs(output_base_directory, exist_ok=True) # Create if it doesn't exist

    print(f"Organizing screenshots from: {screenshot_directory}")
    print(f"Date folders will be created in: {output_base_directory}")

    organize_screenshots_by_creation_date(screenshot_directory, output_base_directory)

    print("\nScreenshot organization based on creation date complete.")
    print(f"Check the '{output_base_directory}' folder for the organized screenshots.")