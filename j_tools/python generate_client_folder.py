import os
import re
from pathlib import Path
from datetime import datetime

# 🔧 Settings
downloads_path = str(Path.home() / "Downloads")

# ✅ Clean invalid characters for Windows folder names
def sanitize(path_segment):
    return re.sub(r'[<>:"/\\|?*]', '-', path_segment)

# 📥 Get client name
client_name = input("Enter Client Name (or leave blank to use timestamp): ").strip()
if not client_name:
    client_name = f"Client_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
client_name = sanitize(client_name)

# 📁 Base folder
base_folder = os.path.join(downloads_path, f"{client_name}_360")

# 📂 Folder structure
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
    
    "04_Government and Legal/IDs & Licenses",
    "04_Government and Legal/Immigration - Compliance",
    "04_Government and Legal/Government Correspondence",
    
    "05_Resources and Templates/Help Docs",
    "05_Resources and Templates/Client Copies",
    "05_Resources and Templates/Reference Guides",
    
    "06_Archives/Inactive_or_Old_Files"
]

# 🛠️ Create folders safely
for path in folder_structure:
    # Sanitize each segment in the path
    safe_path = os.path.join(base_folder, *[sanitize(p) for p in path.split("/")])
    os.makedirs(safe_path, exist_ok=True)

print(f"\n✅ Client folder template created at:\n{base_folder}")
