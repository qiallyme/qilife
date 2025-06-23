import os

def create_folder_structure(root_dir):
    """
    Creates the specified folder structure under the given root directory.

    Args:
        root_dir (str): The root directory where the folders will be created.
    """
    folders = [
        "0_INBOX",
        "01_REVIEW",
        "02_UNSORTED_DOCS",
        "03_UNSORTED_MEDIA",
        "04_SCREENSHOTS",
        "05_DOWNLOADS",
        "06_NEEDS_ACTION",
        "1_PERSONAL",
        "11_DOCS",
        "111_IDS",
        "112_MEDICAL",
        "113_EDUCATION",
        "114_HOME",
        "115_INSURANCE",
        "116_MEMORIES",
        "117_JOURNAL",
        "12_MEDIA",
        "14_FINANCE",
        "15_PROJECTS",
        "16_CONTACTS",
        "161_FAMILY",
        "162_FRIENDS",
        "162_NETWORK",
        "2_BIZ",
        "21_ADMIN",
        "22_CLIENTS",
        "221_TEMPLATES",
        "222_TAXES",
        "222LF_LASTNAME, FIRST",
        "222LF_INTAKE",
        "222LF_DOCS",
        "222LF_TAXES",
        "222LF_COMMS",
        "222LF_FINANCIALS",
        "23_PROJECTS",
        "24_MARKETING",
        "25_HR",
        "26_ACCOUNTING",
        "261_BANKING",
        "262_ASSETS",
        "263_LIABILITY",
        "264_EQUITY",
        "265_INCOME",
        "266_EXPENSE",
        "267_TAXES",
        "27_OPERATIONS",
        "3_LEGAL",
        "31_AGREEMENTS",
        "32_CASES",
        "33_LICENSES",
        "34_COMPLIANCE",
        "35_NOTICES",
        "36_REFUNDS",
        "4_TOOLS",
        "41_AUTOMATIONS",
        "42_DEV-CODE",
        "43_SOFTWARE",
        "44_MEDIA",
        "45_AI-CONFIGS",
        "46_TEMPLATES",
        "47_BACKUPS",
        "48_RECOVERY",
        "5_SHRED",
        "51_DELETE",
        "52_AUTOSHRED",
        "6_ARCHIVED",
        "61_CLIENTS",
        "62_PROJECTS",
        "63_EMPLOYEES",
        "64_LICENSES",
        "65_TAXES",
        "66_LEGACY",
        "67_ENTITIES",
        "7_TEMP",
        "71_TESTING",
        "72_TRANSFER",
        "73_ASSETS",
        "74_RANDOM",
        "75_ZIPS",
        "8_PUBLIC",
        "81_RESOURCES",
        "82_MEDIA",
        "83_WEBSITE",
        "84_MISC",
        "9_TRASH",
        "91_JUNK",
        "92_CORRUPTED",
        "93_DUPLICATES"
    ]

    for folder in folders:
        folder_path = os.path.join(root_dir, folder)
        try:
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        except OSError as e:
            print(f"Error creating folder {folder_path}: {e}")
            #  Don't stop, try to create the rest of the folders.

if __name__ == "__main__":
    root_directory = input("Enter the root directory where the folders should be created: ")
    # Ensure the root directory exists
    if not os.path.exists(root_directory):
        try:
            os.makedirs(root_directory)
            print(f"Created root directory: {root_directory}")
        except OSError as e:
            print(f"Error creating root directory {root_directory}: {e}")
            exit()  # Exit if the root cannot be created.
    create_folder_structure(root_directory)
    print("Folder structure creation complete.")
