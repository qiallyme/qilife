import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {'.git', '.venv', '__pycache__'}
LOG_PATH = PROJECT_ROOT / "import_fix_suggestions.txt"

# Map old/broken imports to new paths (expandable)
FIX_MAP = {
    "common.utils": "a_core.e_utils.ae03_utils",
    "common.notion_logger": "a_core.b_lifelog.ab06_notion_logger",
    "qilifefeed.ingest": "a_core.b_lifelog.ab03_ingest",
    "qinote.nodes": "a_core.c_qinote.ac01_nodes",
    "qifileflow.analyze": "a_core.a_fileflow.aa04_analyze",
    "qifileflow.rename": "a_core.a_fileflow.aa06_rename",
    "qifileflow.filer": "a_core.a_fileflow.aa07_filer",
}

def find_imports(line):
    pattern = re.compile(r'\b(?:from|import)\s+([a-zA-Z0-9_.]+)')
    match = pattern.search(line)
    return match.group(1) if match else None

def dryrun_fix():
    report_lines = []
    print(f"🔍 Dry run: scanning for import fixes in {PROJECT_ROOT}...")

    for py_file in PROJECT_ROOT.rglob("*.py"):
        if any(p in IGNORED_DIRS for p in py_file.parts):
            continue
        if py_file.name.endswith(".bak") or py_file == Path(__file__):
            continue

        with open(py_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        changes = []
        for i, line in enumerate(lines):
            imp = find_imports(line)
            if imp and imp in FIX_MAP:
                changes.append((i + 1, imp, FIX_MAP[imp]))

        if changes:
            report_lines.append(f"\n📝 {py_file.relative_to(PROJECT_ROOT)}")
            for line_no, old, new in changes:
                report_lines.append(f"   [Line {line_no}] {old} → {new}")

    if report_lines:
        with open(LOG_PATH, 'w', encoding='utf-8') as log:
            log.write("\n".join(report_lines))
        print(f"✅ Dry run complete. Suggestions saved to:\n{LOG_PATH}")
    else:
        print("🎉 No matching imports found for replacement.")

if __name__ == "__main__":
    dryrun_fix()
