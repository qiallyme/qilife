import logging
from a_core.e_utils.ae03_utils import load_env
from notion_client import Client

env = load_env()
logger = logging.getLogger(__name__)

class QiNoteAPI:
    def __init__(self):
        self.notion = Client(auth=env["NOTION_API_KEY"])
        self.db_id = env["NOTION_QINOTE_DB_ID"]

    def create_qnode(self, props: dict):
        return self.notion.pages.create(parent={"database_id": self.db_id}, properties=props)

    def query_qnodes(self, filter: dict = None):
        args = {"database_id": self.db_id}
        if filter:
            args["filter"] = filter
        return self.notion.databases.query(**args).get("results", [])
