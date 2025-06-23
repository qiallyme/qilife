import os
import sys
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / "dev_log.md"

MENU_OPTIONS = {
    "1": "✅ Fixing an import issue",
    "2": "🧪 Testing a specific feature",
    "3": "🔧 Refactoring code structure",
    "4": "🐛 Investigating a bug",
    "5": "⏸ Pausing — will return later",
    "6": "➕ Custom note",
    "7": "📤 Push commit summary to GitHub",
    "8": "❌ Exit"
}

def ensure_log_exists():
    if not LOG_PATH.exists():
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            f.write("# 📓 QiLife Developer Log\n\n")

def log_entry(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n### ⏱ {timestamp}\n- {message}\n"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)
    print(f"\n✅ Logged: {message}\n")

def main():
    ensure_log_exists()
    while True:
        print("\nWhat are you doing right now?\n")
        for key, val in MENU_OPTIONS.items():
            print(f"{key}. {val}")

        choice = input("\nEnter a number (1-8): ").strip()

        if choice == "8":
            print("👋 Exiting log tool.")
            break

        if choice not in MENU_OPTIONS:
            print("❌ Invalid option. Try again.")
            continue

        if choice == "6":
            note = input("Enter your custom note: ").strip()
            log_entry(note)
        elif choice == "7":
            commit_msg = os.popen('git log -1 --pretty=%B').read().strip()
            log_entry(f"📤 Git Commit: {commit_msg}")
        else:
            detail = input("Add optional detail (or press Enter to skip): ").strip()
            log_text = MENU_OPTIONS[choice] + (f" — {detail}" if detail else "")
            log_entry(log_text)

if __name__ == "__main__":
    main()