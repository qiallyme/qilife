import logging
from a_core.b_lifelog.ab06_notion_logger import log_to_life_feed
from a_core.e_utils.ae03_utils import load_env

env = load_env()
logger = logging.getLogger(__name__)

def ingest_email_events():
    logger.info("Ingesting emails")
    # TODO: Replace with Gmail API calls
    dummy = [{"id":"e1","subject":"Test","timestamp":"2025-05-28T10:00:00"}]
    for m in dummy:
        log_to_life_feed(f"📧 {m['subject']}", m["timestamp"], {"message_id": m["id"]})

def ingest_calendar_events():
    logger.info("Ingesting calendar")
    # TODO: Replace with Calendar API calls
    dummy = [{"id":"c1","summary":"Standup","start":"2025-05-28T09:00:00"}]
    for e in dummy:
        log_to_life_feed(f"📅 {e['summary']}", e["start"], {"event_id": e["id"]})

def ingest_task_events():
    logger.info("Ingesting tasks")
    # TODO: Replace with Tasks API calls
    dummy = [{"id":"t1","title":"Do thing","status":"completed","updated":"2025-05-28T08:00:00"}]
    for t in dummy:
        icon = "✅" if t["status"]=="completed" else "🕒"
        log_to_life_feed(f"{icon} {t['title']}", t["updated"], {"task_id": t["id"], "status": t["status"]})
