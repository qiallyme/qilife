import os
import hashlib
import shutil

# --- SETTINGS ---
client_root = r'C:\Users\codyr\Downloads\Munoz Altamirano, Luis of InnovaHire LLC_360'

# --- MAPPINGS ---
folder_renames = {
    "01_Engagements & Worklogs": "01_Client Engagements",
    "02_Agreements & Authorizations": "02_Contracts & Intake",
    "03_Financial & Accounting": "03_Accounting",
    "05_Resources and Templates": "05_Client Resources",
    "07_HR & Staffing": "07_HR & Staffing",
}

file_renames = {
    "EIN-Innova Hire LLC.png": "EIN Certificate - InnovaHire.png",
    "INNOVAHIRE_ONEPAGE_BROCHURE_DIRECT_PLACEMENTS.pdf": "One-Pager - Direct Placements.pdf",
    "Executive Operations Assistant.pdf": "Job Description - Executive Operations Assistant.pdf",
    "Internal New Hire Orientation Check List-30.11-IN1135.1-09182018.pdf": "Checklist - New Hire Orientation.pdf",
    "New-hire-first-day-checklist.pdf": "Checklist - First Day New Hire.pdf",
}

# --- FOLDER RENAME ---
for root, dirs, _ in os.walk(client_root):
    for old_name in dirs:
        if old_name in folder_renames:
            old_path = os.path.join(root, old_name)
            new_path = os.path.join(root, folder_renames[old_name])
            if not os.path.exists(new_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed folder: {old_path} → {new_path}")
                except Exception as e:
                    print(f"Error renaming {old_path}: {e}")

# --- FILE RENAME ---
for root, _, files in os.walk(client_root):
    for file in files:
        if file in file_renames:
            old_path = os.path.join(root, file)
            new_path = os.path.join(root, file_renames[file])
            try:
                os.rename(old_path, new_path)
                print(f"Renamed file: {file} → {os.path.basename(new_path)}")
            except Exception as e:
                print(f"Error renaming {file}: {e}")

# --- DUPLICATE DETECTION ---
seen_hashes = {}
duplicates = []

def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

for root, _, files in os.walk(client_root):
    for file in files:
        path = os.path.join(root, file)
        try:
            fhash = file_hash(path)
            if fhash in seen_hashes:
                duplicates.append((path, seen_hashes[fhash]))
                os.remove(path)
                print(f"Removed duplicate: {path}")
            else:
                seen_hashes[fhash] = path
        except Exception as e:
            print(f"Error hashing {file}: {e}")

print("\n✅ Finished organizing and cleaning client folder.")
