import os
import re
import csv
from datetime import datetime

# === CONFIG ===
BASE_DIR = r"C:\Users\codyr\My Drive\2_BIZ\22_CLIENTS"
LOG_PATH = os.path.join(BASE_DIR, f"rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
UNDO_PATH = os.path.join(BASE_DIR, "undo_log.csv")

BUSINESS_KEYWORDS = ['LLC', 'L.L.C', 'LLP', 'L.L.P', 'INC', 'INC.', 'CORP', 'CORPORATION', 'CO', 'COMPANY', 'S.C.', 'PC', 'PLLC']
IGNORE_KEYWORDS = ['template', 'form', 'agreement', 'worksheet', 'report', 'pdf', 'scans', 'upload', 'document', 'notes', 'images']

# Regex patterns
already_prefixed_individual = re.compile(r"^225I_[^,]+,[^,]+$")
already_prefixed_business = re.compile(r"^224B_")
comma_name_pattern = re.compile(r"^[^,]+,[^,]+$")
system_folder_pattern = re.compile(r"^\d{3}[_\- ]")
date_pattern = re.compile(r"(\d{2})[-_](\d{2})[-_](\d{4})[ _](\d{2})[._](\d{2})")

def is_business(name):
    return any(keyword in name.replace(",", "").upper() for keyword in BUSINESS_KEYWORDS)

def is_ignorable(name):
    return any(keyword in name.lower() for keyword in IGNORE_KEYWORDS)

def format_individual_name(name):
    parts = name.strip().replace("_", " ").split()
    if len(parts) >= 4:
        last = " ".join(parts[-2:])
        first_middle = " ".join(parts[:-2])
    elif len(parts) == 3:
        last = parts[2]
        first_middle = " ".join(parts[:2])
    elif len(parts) == 2:
        last = parts[1]
        first_middle = parts[0]
    else:
        return f"225I_{parts[0]}"
    return f"225I_{last},{first_middle}"

def format_business_name(name):
    return f"224B_{name.strip()}"

def clean_timestamp(name):
    match = re.search(date_pattern, name)
    if match:
        day, month, year, hour, minute = match.groups()
        new_ts = f"{year}{month}{day}-{hour}{minute}"
        return re.sub(date_pattern, new_ts, name)
    return name

def perform_live_rename(base_dir):
    log = []
    undo = []

    for folder in os.listdir(base_dir):
        original_path = os.path.join(base_dir, folder)
        if not os.path.isdir(original_path):
            continue

        original_name = folder
        folder = folder.replace("SRVPRO SHARED - ", "").strip()
        folder = clean_timestamp(folder)

        if already_prefixed_business.match(folder) or already_prefixed_individual.match(folder):
            log.append([original_name, folder, "Already formatted"])
            continue
        if system_folder_pattern.match(folder):
            log.append([original_name, folder, "Skipped: System folder tag"])
            continue
        if is_ignorable(folder):
            log.append([original_name, folder, "Skipped: Ignored keyword"])
            continue

        if comma_name_pattern.match(folder):
            new_name = f"225I_{folder.strip()}"
        elif is_business(folder):
            new_name = format_business_name(folder)
        else:
            new_name = format_individual_name(folder)

        new_path = os.path.join(base_dir, new_name)

        if os.path.exists(new_path):
            log.append([original_name, new_name, "Skipped: Target exists"])
        else:
            os.rename(original_path, new_path)
            log.append([original_name, new_name, "Renamed"])
            undo.append([new_name, original_name])

    # Write logs
    with open(LOG_PATH, "w", newline="", encoding="utf-8") as logfile:
        writer = csv.writer(logfile)
        writer.writerow(["Original Name", "New Name", "Action"])
        writer.writerows(log)

    with open(UNDO_PATH, "w", newline="", encoding="utf-8") as undofile:
        writer = csv.writer(undofile)
        writer.writerow(["Current Name", "Revert To"])
        writer.writerows(undo)

    return LOG_PATH, UNDO_PATH

# Execute live rename and logging
perform_live_rename(BASE_DIR)
