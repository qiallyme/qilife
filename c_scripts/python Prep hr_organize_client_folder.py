import os
import shutil
import re
from datetime import datetime

# Set your client folder path
client_folder = r"C:\Users\codyr\Downloads\Munoz Altamirano, Luis of InnovaHire LLC_360"

# Keyword-based rename rules: pattern : new_name format (prefix + original)
rename_rules = {
    r"\bein[-_ ]?innova\b": "EIN Letter - ",
    r"cp575": "IRS CP575 Notice - ",
    r"resume": "Resume - ",
    r"executive operations assistant": "Job Description - Executive Assistant - ",
    r"brand guide": "Brand Guide - ",
    r"checklist": "Checklist - ",
    r"onboarding": "Onboarding Form - ",
    r"brochure": "Brochure - ",
    r"proposal": "Proposal - ",
    r"logo": "Logo - ",
    r"certificate of organization": "Business Registration - ",
    r"tasks": "Task Export - ",
    r"journal": "Internal Journal - ",
    r"receipt": "Receipt - ",
    r"orientation": "Orientation Checklist - ",
    r"sitemap": "Sitemap File - ",
}

# Target folders that may need renaming for clarity
folder_renames = {
    "01_Engagements & Worklogs": "01_Client Engagements",
    "02_Agreements & Authorizations": "02_Client Agreements",
    "03_Financial & Accounting": "03_Financial Records",
    "05_Resources and Templates": "05_Client Resources",
    "07_HR & Staffing": "07_HR Files",
}

# Rename folders
# Rename folders
for old, new in folder_renames.items():
    old_path = os.path.join(client_folder, old)
    new_path = os.path.join(client_folder, new)

    # Skip if same name
    if os.path.abspath(old_path) == os.path.abspath(new_path):
        continue

    try:
        if os.path.exists(old_path) and not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"Renamed folder: {old} → {new}")
        elif os.path.exists(old_path) and os.path.exists(new_path):
            print(f"Target folder already exists, skipping rename: {new}")
    except PermissionError as e:
        print(f"PermissionError: Could not rename {old} → {new} | {e}")
    except Exception as e:
        print(f"Error renaming folder {old} → {new}: {e}")


# Prepare log
renamed_files_log = []

# Walk through the directory and rename files
for root, dirs, files in os.walk(client_folder):
    for file in files:
        old_path = os.path.join(root, file)
        filename_lower = file.lower()

        for pattern, new_prefix in rename_rules.items():
            if re.search(pattern, filename_lower):
                file_ext = os.path.splitext(file)[1]
                cleaned_name = re.sub(r"[_\- ]+", " ", os.path.splitext(file)[0]).title().strip()
                new_name = new_prefix + cleaned_name + file_ext
                new_path = os.path.join(root, new_name)

                if not os.path.exists(new_path):  # avoid overwriting
                    os.rename(old_path, new_path)
                    renamed_files_log.append((file, new_name))
                    print(f"Renamed: {file} → {new_name}")
                break

# Log output
if renamed_files_log:
    log_file = os.path.join(client_folder, f"_rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(log_file, "w", encoding="utf-8") as f:
        for old, new in renamed_files_log:
            f.write(f"{old} → {new}\n")
    print(f"\nRename log saved to: {log_file}")
else:
    print("\nNo matches found for renaming.")

