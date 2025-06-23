import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from a_core.e_utils.ae03_utils import load_env, setup_logger
from a_core.a_fileflow.aa04_analyze import analyze_file
from a_core.a_fileflow.aa06_rename import generate_new_name
from a_core.a_fileflow.aa07_filer import move_file
from a_core.b_lifelog.ab06_notion_logger import log_to_life_feed

env = load_env()
logger = setup_logger("QiFileFlow", "logs/fileflow.log")

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        src_path = event.src_path
        logger.info(f"Detected new file: {src_path}")
        meta = analyze_file(src_path)
        new_name = generate_new_name(src_path, meta)
        dest_path = move_file(src_path, new_name)
        # Log to Notion
        log_to_life_feed(
            title=f"📄 {new_name}",
            timestamp=meta.get("timestamp"),
            metadata={"original_path": src_path, "destination": dest_path}
        )

def start_monitor():
    path = env["SOURCE_FOLDER"]
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    logger.info(f"Monitoring folder: {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
# src/QiFileFlow/monitor.py (excerpt)

from a_core.e_utils.ae03_utils import load_env, setup_logger
import os

env = load_env()
logger = setup_logger("QiFileFlow", "logs/fileflow.log")

def get_folder(key: str, prompt: str) -> str:
    path = env.get(key)
    if not path or "path/to" in path:
        # ask user if env is unset or left as placeholder
        path = input(f"{prompt}: ").strip()
    return path

def start_monitor():
    source = get_folder("SOURCE_FOLDER", 
                        "Enter the full path to your live_feed folder")
    processed = get_folder("PROCESSED_FOLDER",
                           "Enter the full path to your processed folder")

    # now use `source` and `processed` instead of env["…"]
    logger.info(f"Monitoring {source}, moving to {processed}")
    # … rest of watchdog setup …
