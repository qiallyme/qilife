import logging
from datetime import date
from a_core.e_utils.ae03_utils import load_env
from src.QiLifeFeed.notion_client import get_life_feed_entries, create_digest_page

logger = logging.getLogger(__name__)
env = load_env()

def summarize_entries(text_blob: str) -> str:
    # TODO: Hook into LM Studio / Notion AI
    return (
        "## Summary\n\n- …\n\n"
        "## Action Items\n\n- …\n\n"
        "## Insights\n\n- …\n\n"
        "## Suggestions\n\n- …"
    )

def generate_daily_digest():
    logger.info("Building daily digest")
    today = date.today().isoformat()
    entries = get_life_feed_entries(env["NOTION_LIFE_FEED_DB_ID"], on_date=today)
    blob = "\n".join(f"{e['timestamp']}: {e['title']}" for e in entries)
    digest = summarize_entries(blob)
    title = f"Daily Digest — {today}"
    create_digest_page(env["NOTION_LIFE_FEED_DB_ID"], title, digest)
    logger.info("Digest created")
