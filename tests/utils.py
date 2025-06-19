import os
import json
import logging
from dotenv import load_dotenv

def load_env():
    """Load .env file into os.environ and return a dict of our keys."""
    load_dotenv(dotenv_path=".env")
    return {
        "NOTION_API_KEY": os.getenv("NOTION_API_KEY"),
        "NOTION_LIFE_FEED_DB_ID": os.getenv("NOTION_LIFE_FEED_DB_ID"),
        "NOTION_QINOTE_DB_ID": os.getenv("NOTION_QINOTE_DB_ID"),
        "SOURCE_FOLDER": os.getenv("SOURCE_FOLDER"),
        "PROCESSED_FOLDER": os.getenv("PROCESSED_FOLDER"),
        "DEDUP_THRESHOLD": int(os.getenv("DEDUPLICATION_THRESHOLD", 30)),
        "BATCH_SIZE": int(os.getenv("BATCH_SIZE", 5)),
    }

def load_default_config():
    """Load config/default.json."""
    with open("config/default.json", "r") as f:
        return json.load(f)

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Configure a logger that writes to file and stdout."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger
