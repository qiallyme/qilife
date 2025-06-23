import os
import re
from pathlib import Path

# Mapping of old folder names to new ones
FOLDER_MAP = {
    "00_core": "a_core",
    "01_gui": "b_gui",
    "02_scripts": "c_scripts",
    "03_docs": "d_docs",
    "04_tests": "e_tests",
    "05_vector_db": "f_vector_db",
    "06_tools": "j_tools",
    "07_sandbox": "k_sandbox",
}

def replace_imports_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    updated = content
    for old, new in FOLDER_MAP.items():
        # Replace `from a_core...` and `import a_core...`
        updated = re.sub(rf'\b(from|import)\s+{re.escape(old)}([^\w])',
                         rf'\1 {new}\2', updated)

    if updated != content:
        # Backup original
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        file_path.rename(backup_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"✅ Updated: {file_path}")
    else:
        print(f"⚪ No change: {file_path}")

def refactor_repo(root_path):
    print(f"🔍 Scanning Python files in: {root_path}")
    for path in Path(root_path).rglob('*.py'):
        if path.resolve ==Path(__file__).resolve():
            continue
        replace_imports_in_file(path)

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    refactor_repo(repo_root)
