from datetime import datetime
import os
import csv
import re
# === CONFIGURATION ===
BASE_DIR = r"C:\Users\codyr\My Drive\2_BIZ\22_CLIENTS"
RENAME_LOG = os.path.join(BASE_DIR, f"rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
UNDO_LOG = os.path.join(BASE_DIR, "undo_log.csv")

# === KEYWORD DEFINITIONS ===
BUSINESS_KEYWORDS = ['LLC', 'L.L.C', 'LLP', 'L.L.P', 'INC', 'INC.', 'CORP', 'CORPORATION', 'CO', 'COMPANY', 'S.C.', 'PC', 'PLLC']
TRIM_KEYWORDS = ['account', 'folder', 'client', 'uploads', 'documents', 'docs', 'scans', 'b']

def is_business(name):
    return any(keyword in name.upper() for keyword in BUSINESS_KEYWORDS)

def clean_folder_name(name):
    match = re.match(r'^(\d{3})[_\- ]?(.*)', name)
    if match:
        prefix, rest = match.groups()
        prefix = prefix.strip()

        # Remove known junk keywords
        rest = re.sub(r'\b(' + '|'.join(TRIM_KEYWORDS) + r')\b', '', rest, flags=re.IGNORECASE)
        rest = re.sub(r'[^\w\s,]', '', rest)
        rest = re.sub(r'\s+', '_', rest.strip())
        rest = re.sub(r'_+', '_', rest).strip('_')

        if is_business(rest):
            cleaned = f"{prefix}_{rest.upper()}"
        elif ',' in rest:
            cleaned = f"{prefix}_{','.join([p.strip().title() for p in rest.split(',')])}"
        else:
            cleaned = f"{prefix}_{rest.title()}"
    else:
        cleaned = re.sub(r'\s+', '_', name.strip()).title()

    return cleaned

# === MAIN RENAME FUNCTION ===
def rename_folders(base_dir):
    rename_log = []
    undo_log = []

    for folder in os.listdir(base_dir):
        old_path = os.path.join(base_dir, folder)
        if not os.path.isdir(old_path):
            continue

        new_name = clean_folder_name(folder)
        new_path = os.path.join(base_dir, new_name)

        if folder != new_name and not os.path.exists(new_path):
            os.rename(old_path, new_path)
            rename_log.append([folder, new_name, "Renamed"])
            undo_log.append([new_name, folder])
        else:
            rename_log.append([folder, new_name, "Skipped"])

    # Write logs
    with open(RENAME_LOG, "w", newline='', encoding="utf-8") as logfile:
        writer = csv.writer(logfile)
        writer.writerow(["Original Name", "New Name", "Action"])
        writer.writerows(rename_log)

    with open(UNDO_LOG, "w", newline='', encoding="utf-8") as undofile:
        writer = csv.writer(undofile)
        writer.writerow(["Current Name", "Revert To"])
        writer.writerows(undo_log)

    return RENAME_LOG, UNDO_LOG

# Run final rename
rename_folders(BASE_DIR)
