from notion_client import Client
from common.utils import load_env
import logging

env = load_env()
_notions = Client(auth=env["NOTION_API_KEY"])
_life_db = env["NOTION_LIFE_FEED_DB_ID"]
_qinote_db = env["NOTION_QINOTE_DB_ID"]
logger = logging.getLogger(__name__)

def log_to_life_feed(title: str, timestamp: str, metadata: dict):
    """Create a new page in the Life Feed database."""
    props = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Timestamp": {"date": {"start": timestamp}},
    }
    # add any extra metadata fields
    for key, val in metadata.items():
        props[key] = {"rich_text": [{"text": {"content": str(val)}}]}
    try:
        _notions.pages.create(parent={"database_id": _life_db}, properties=props)
        logger.debug(f"Logged to Life Feed: {title}")
    except Exception as e:
        logger.error(f"Error logging to Life Feed: {e}")
        raise

def log_to_qinote(properties: dict):
    """Create a new page in the QiNote database with given properties dict."""
    try:
        _notions.pages.create(parent={"database_id": _qinote_db}, properties=properties)
        logger.debug("Logged QNode")
    except Exception as e:
        logger.error(f"Error logging to QiNote: {e}")
        raise
