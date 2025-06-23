import logging
from a_core.e_utils.ae03_utils import load_env, setup_logger
from a_core.b_lifelog.ab03_ingest import ingest_email_events, ingest_calendar_events, ingest_task_events

env = load_env()
logger = setup_logger("QiLifeFeed", "logs/lifelog.log")

def run_capture():
    logger.info("Starting LifeFeed capture pipeline")
    try:
        ingest_email_events()
        ingest_calendar_events()
        ingest_task_events()
        logger.info("Capture complete")
    except Exception as e:
        logger.error(f"Error in capture pipeline: {e}")
        raise
