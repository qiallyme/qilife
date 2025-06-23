import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {'.git', '.venv', '__pycache__'}
LOG_PATH = PROJECT_ROOT / "import_scan_report.txt"

# Known root-level remaps
FOLDER_REMAP = {
    "00_core": "a_core", "01_gui": "b_gui", "02_scripts": "c_scripts",
    "03_docs": "d_docs", "04_tests": "e_tests", "05_vector_db": "f_vector_db",
    "06_tools": "j_tools", "07_sandbox": "k_sandbox"
}

IMPORT_PATTERN = re.compile(r'^\s*(from|import)\s+([a-zA-Z0-9_.]+)')

def is_valid_import(module_path):
    segments = module_path.split(".")
    current = PROJECT_ROOT
    for seg in segments:
        current = current / seg
        if current.with_suffix(".py").exists():
            return True
        if not current.exists():
            return False
    return True

def scan_file(file_path):
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            match = IMPORT_PATTERN.match(line)
            if match:
                full_import = match.group(2)
                if not is_valid_import(full_import):
                    results.append((i, full_import.strip()))
    return results

def main():
    report_lines = []
    print(f"🔍 Scanning project: {PROJECT_ROOT}")
    
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if any(p in IGNORED_DIRS for p in py_file.parts):
            continue
        if py_file.name.endswith(".bak") or py_file == Path(__file__):
            continue
        
        broken_imports = scan_file(py_file)
        if broken_imports:
            report_lines.append(f"\n❌ {py_file.relative_to(PROJECT_ROOT)}")
            for line_no, imp in broken_imports:
                report_lines.append(f"   [Line {line_no}] Invalid import: {imp}")

    if report_lines:
        with open(LOG_PATH, 'w', encoding='utf-8') as out:
            out.write("\n".join(report_lines))
        print(f"📄 Report written to: {LOG_PATH}")
    else:
        print("✅ All imports look valid.")

if __name__ == "__main__":
    main()
