import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import time

ROOT = Path(__file__).resolve().parent
c_scripts_dir = ROOT / "c_scripts"
log_script = ROOT / "dev_log.py"
watcher_script = ROOT / "log_watcher.py"
app_script = ROOT.parent / "app.py"
venv_path = ROOT.parent / ".venv"
venv_python = venv_path / "Scripts" / "python.exe"
venv_pip = venv_path / "Scripts" / "pip.exe"
venv_streamlit = venv_path / "Scripts" / "streamlit.exe"
requirements_file = ROOT.parent / "requirements.lock.txt"
log_md = ROOT.parent / "dev_log.md"
session_log = ROOT / "c01_reports" / "session_summary_log.md"
cursor_path = Path("C:/Users/codyr/AppData/Local/Programs/cursor/Cursor.exe")

start_time = time.time()
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_line = f"\n### ⏱ {timestamp}\n- 📦 Launched from run_dev.py (desktop or script)\n"
with open(log_md, 'a', encoding='utf-8') as f:
    f.write(log_line)

session_summary = []

def notify(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)

try:
    print("📝 Starting Dev Log Menu...")
    subprocess.run([str(venv_python), str(log_script)], check=True)
    session_summary.append("✅ Dev Log Menu launched")
except Exception as e:
    session_summary.append(f"❌ Dev Log Menu failed: {e}")

try:
    print("👀 Launching Log Watcher in background...")
    subprocess.Popen([str(venv_python), str(watcher_script)])
    session_summary.append("✅ Log Watcher started")
except Exception as e:
    session_summary.append(f"❌ Log Watcher failed: {e}")

try:
    print("🚀 Opening Cursor in QiLife folder...")
    if cursor_path.exists():
        subprocess.Popen([str(cursor_path), str(ROOT.parent)])
        session_summary.append("✅ Cursor opened in QiLife folder")
    else:
        session_summary.append("❌ Cursor not found at expected path.")
except Exception as e:
    session_summary.append(f"❌ Cursor failed: {e}")

try:
    print("💾 Installing Requirements...")
    if venv_pip.exists():
        subprocess.run([str(venv_pip), "install", "-r", str(requirements_file)], check=True)
        session_summary.append("✅ Requirements installed")
    else:
        session_summary.append("❌ pip not found. Is your venv set up?")
except Exception as e:
    session_summary.append(f"❌ Installing requirements failed: {e}")

try:
    print("🧪 Running Streamlit App...")
    if venv_streamlit.exists():
        subprocess.run([str(venv_streamlit), "run", str(app_script)], check=True)
        session_summary.append("✅ Streamlit app launched")
    else:
        session_summary.append("❌ Streamlit executable not found in venv")
except Exception as e:
    session_summary.append(f"❌ Streamlit App failed: {e}")

end_time = time.time()
duration_minutes = round((end_time - start_time) / 60, 2)
session_summary.append(f"⏳ Duration: {duration_minutes} minutes")

summary_block = f"\n---\n## 🧠 QiLife Dev Session Summary – {timestamp}\n" + "\n".join(f"- {line}" for line in session_summary) + "\n"
with open(session_log, 'a', encoding='utf-8') as f:
    f.write(summary_block)

notify("QiLife Dev Session Summary", "\n".join(session_summary))
