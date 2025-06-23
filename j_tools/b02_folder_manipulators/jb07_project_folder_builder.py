import os
import json

def create_folder_hierarchy(base_path):
    """
    Creates the folder hierarchy for the life_feed_automation project.

    Args:
        base_path (str): The base directory where the folder structure will be created.
    """
    # Create the main directory
    main_dir = os.path.join(base_path, "life_feed_automation")
    os.makedirs(main_dir, exist_ok=True)

    # Create the modules directory and its files
    modules_dir = os.path.join(main_dir, "modules")
    os.makedirs(modules_dir, exist_ok=True)
    # Create the __init__.py file
    with open(os.path.join(modules_dir, "__init__.py"), "w") as f:
        pass # Create an empty file
    # Create the preprocess.py file
    with open(os.path.join(modules_dir, "preprocess.py"), "w") as f:
        pass
    # Create the ocr.py file
    with open(os.path.join(modules_dir, "ocr.py"), "w") as f:
        pass
    # Create the notion_logger.py
    with open(os.path.join(modules_dir, "notion_logger.py"), "w") as f:
        pass
    # Create the utils.py
    with open(os.path.join(modules_dir, "utils.py"), "w") as f:
        pass

    # Create the tests directory and its file
    tests_dir = os.path.join(main_dir, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    # Create the test_hashing.py
    with open(os.path.join(tests_dir, "test_hashing.py"), "w") as f:
        pass

    # Create the config directory and its file
    config_dir = os.path.join(main_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    # Create the settings.json
    settings_data = {"param1": "value1", "param2": "value2"}  # Example data
    with open(os.path.join(config_dir, "settings.json"), "w") as f:
        json.dump(settings_data, f, indent=4)  # Write JSON data to the file

    # Create the Screenshots_Monitor directory and its subdirectories
    screenshots_dir = os.path.join(main_dir, "Screenshots_Monitor")
    live_feed_dir = os.path.join(screenshots_dir, "live_feed")
    staging_dir = os.path.join(screenshots_dir, "staging")
    to_review_dir = os.path.join(screenshots_dir, "to_review")
    processed_dir = os.path.join(screenshots_dir, "processed")

    os.makedirs(live_feed_dir, exist_ok=True)
    os.makedirs(staging_dir, exist_ok=True)
    os.makedirs(to_review_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # Create the .env and requirements.txt files
    with open(os.path.join(main_dir, ".env"), "w") as f:
        f.write("VAR1=value1\nVAR2=value2") # add dummy data
    with open(os.path.join(main_dir, "requirements.txt"), "w") as f:
        f.write("package1==1.0.0\npackage2==2.0.0")  # Add dummy data

if __name__ == "__main__":
    # Prompt the user for the base directory
    base_path = input("Enter the base directory where the folder structure should be created: ")
    create_folder_hierarchy(base_path)
    print(f"Folder hierarchy created successfully in {base_path}")
