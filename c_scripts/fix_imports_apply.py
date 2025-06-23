#fix_imports_apply.py
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUGGESTIONS_FILE = PROJECT_ROOT / "import_fix_suggestions.txt"

def parse_suggestions():
    fixes = {}
    current_file = None

    with open(SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("📝"):
                current_file = PROJECT_ROOT / line[2:].strip()
                fixes[current_file] = []
            elif current_file and "→" in line:
                match = re.match(r"\[Line (\d+)] (.+?) → (.+)", line)
                if match:
                    line_no = int(match.group(1)) - 1  # zero-based index
                    old = match.group(2).strip()
                    new = match.group(3).strip()
                    fixes[current_file].append((line_no, old, new))
    return fixes

def apply_fixes(fix_map):
    for file_path, changes in fix_map.items():
        if not file_path.exists():
            print(f"❌ File missing: {file_path}")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        file_path.rename(backup_path)

        print(f"🛠️ Applying fixes to: {file_path.relative_to(PROJECT_ROOT)}")
        for line_no, old, new in changes:
            original = lines[line_no]
            lines[line_no] = original.replace(old, new)
            print(f"   ✔ Line {line_no + 1}: {old} → {new}")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Updated and backed up to: {backup_path.name}\n")

if __name__ == "__main__":
    fixes = parse_suggestions()
    apply_fixes(fixes)
