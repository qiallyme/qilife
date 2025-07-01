#python hr_organize_client_folder.py
import os
import shutil
import re
from pathlib import Path

# 🔧 Customize this path to your client folder
client_root = Path.home() / "Downloads" / "Munoz Altamirano, Luis of InnovaHire LLC_360"

# ✅ Clean invalid characters for safety
def sanitize(path_segment):
    return re.sub(r'[<>:"/\\|?*]', '-', path_segment)

# 🔍 Keywords map for routing files based on name
keyword_map = {
    # Tax & Finance
    "tax": "03_Financial & Accounting/Tax Filings/2024_Tax_Return/Filing PDFs",
    "return": "03_Financial & Accounting/Tax Filings/2024_Tax_Return/Filing PDFs",
    "invoice": "03_Financial & Accounting/Invoices & Payments",
    "payment": "03_Financial & Accounting/Invoices & Payments",
    "w2": "03_Financial & Accounting/Tax Filings/1099s-W2s_Payroll",
    "1099": "03_Financial & Accounting/Tax Filings/1099s-W2s_Payroll",
    "payroll": "03_Financial & Accounting/Payroll Invoices",
    "receipt": "03_Financial & Accounting/Invoices & Payments",

    # Legal & Formation
    "certificate": "04_Government and Legal/IDs & Licenses",
    "cp575": "04_Government and Legal/Government Correspondence",
    "ein": "04_Government and Legal/Government Correspondence",

    # Contracts & Forms
    "contract": "02_Agreements & Authorizations/Contracts",
    "agreement": "02_Agreements & Authorizations/Contracts",
    "consent": "02_Agreements & Authorizations/Consent Forms",
    "onboard": "02_Agreements & Authorizations/Intake & Onboarding Forms",

    # HR & Staffing
    "resume": "07_HR & Staffing/Hiring & Onboarding",
    "cv": "07_HR & Staffing/Hiring & Onboarding",
    "offer": "07_HR & Staffing/Hiring & Onboarding",
    "application": "07_HR & Staffing/Hiring & Onboarding",
    "orientation": "07_HR & Staffing/Training & Development",
    "new-hire": "07_HR & Staffing/Hiring & Onboarding",
    "checklist": "07_HR & Staffing/Compliance & Risk Management",
    "employee": "07_HR & Staffing/Employee Files/Client-Provided",
    "plan": "07_HR & Staffing/Policies & Handbooks",
    "staff": "07_HR & Staffing/Policies & Handbooks",

    # Creative & Branding
    "logo": "05_Resources and Templates/Client Copies",
    "brand": "05_Resources and Templates/Client Copies",
    "favicon": "05_Resources and Templates/Client Copies",
    "brochure": "05_Resources and Templates/Client Copies",
    "onepage": "05_Resources and Templates/Client Copies",

    # Deliverables & Documents
    "proposal": "01_Engagements & Worklogs/Reports & Deliverables/One-Time Deliverables",
    "report": "01_Engagements & Worklogs/Reports & Deliverables/Monthly Reports",
    "manual": "05_Resources and Templates/Reference Guides",
    "guide": "05_Resources and Templates/Reference Guides",
    "business_master": "05_Resources and Templates/Reference Guides",

    # Misc Ops & Internal
    "journal": "06_Archives/Inactive_or_Old_Files",
    "task": "06_Archives/Inactive_or_Old_Files",
    "csv": "06_Archives/Inactive_or_Old_Files",
    "html": "06_Archives/Inactive_or_Old_Files",
    "xml": "06_Archives/Inactive_or_Old_Files",
    "zip": "06_Archives/Inactive_or_Old_Files"
}

# 📂 Define the full folder structure
folder_structure = [
    "01_Engagements & Worklogs/Active Engagements",
    "01_Engagements & Worklogs/Completed Projects",
    "01_Engagements & Worklogs/Reports & Deliverables/Monthly Reports",
    "01_Engagements & Worklogs/Reports & Deliverables/One-Time Deliverables",

    "02_Agreements & Authorizations/Contracts",
    "02_Agreements & Authorizations/Consent Forms",
    "02_Agreements & Authorizations/Intake & Onboarding Forms",

    "03_Financial & Accounting/Invoices & Payments",
    "03_Financial & Accounting/Bookkeeping & Spreadsheets",
    "03_Financial & Accounting/Tax Filings/2024_Tax_Return/Filing PDFs",
    "03_Financial & Accounting/Tax Filings/2024_Tax_Return/Supporting Docs & Forms",
    "03_Financial & Accounting/Tax Filings/2023_Tax_Return/Filing PDFs",
    "03_Financial & Accounting/Tax Filings/2023_Tax_Return/Supporting Docs & Forms",
    "03_Financial & Accounting/Tax Filings/1099s-W2s_Payroll",
    "03_Financial & Accounting/Payroll Invoices",

    "04_Government and Legal/IDs & Licenses",
    "04_Government and Legal/Immigration - Compliance",
    "04_Government and Legal/Government Correspondence",

    "05_Resources and Templates/Help Docs",
    "05_Resources and Templates/Client Copies",
    "05_Resources and Templates/Reference Guides",

    "06_Archives/Inactive_or_Old_Files",

    "07_HR & Staffing/Policies & Handbooks",
    "07_HR & Staffing/Employee Files/Templates",
    "07_HR & Staffing/Employee Files/Client-Provided",
    "07_HR & Staffing/Hiring & Onboarding",
    "07_HR & Staffing/Compliance & Risk Management",
    "07_HR & Staffing/Training & Development"
]

# 🔁 Step 1: Create folders if missing
for relative_path in folder_structure:
    full_path = client_root / Path(*[sanitize(p) for p in relative_path.split("/")])
    full_path.mkdir(parents=True, exist_ok=True)

# 🧹 Step 2: Look for files in old/unclassified folders
def move_and_classify_files(base_path):
    for root, dirs, files in os.walk(base_path, topdown=False):
        for file in files:
            file_path = Path(root) / file
            moved = False
            for keyword, target_subpath in keyword_map.items():
                if keyword.lower() in file.lower():
                    destination = client_root / Path(*[sanitize(p) for p in target_subpath.split("/")])
                    destination.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.move(str(file_path), str(destination / file))
                        print(f"Moved: {file} → {destination}")
                        moved = True
                        break
                    except Exception as e:
                        print(f"❌ Failed to move {file}: {e}")
            if not moved:
                print(f"⚠️ Unmatched: {file_path}")

# 🧹 Step 3: Clean up empty folders
def remove_empty_folders(path):
    for root, dirs, _ in os.walk(path, topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            if not any(dir_path.iterdir()):
                dir_path.rmdir()
                print(f"Deleted empty folder: {dir_path}")

# 🚀 Run file organizer
move_and_classify_files(client_root)
remove_empty_folders(client_root)

print("\n✅ Folder structure verified and files organized.")
