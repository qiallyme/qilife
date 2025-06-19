from notion_client import Client

class NotionClient:
    def __init__(self, token: str):
        self.notion = Client(auth=token)

    def query_db(self, database_id: str, **kwargs):
        return self.notion.databases.query(database_id=database_id, **kwargs).get("results", [])

    def create_page(self, parent_db_id: str, properties: dict, children: list = None):
        return self.notion.pages.create(parent={"database_id": parent_db_id}, properties=properties, children=children or [])

def get_life_feed_entries(db_id: str, on_date: str):
    nc = NotionClient(token="")  # TODO: pass in real token (use load_env)
    # TODO: filter by date property == on_date
    return [{"timestamp":"2025-05-28T10:00:00","title":"Sample"}]

def create_digest_page(db_id: str, title: str, content: str):
    nc = NotionClient(token="")  # TODO
    props = {"Title": {"title": [{"text": {"content": title}}]}}
    children = [
        {"object":"block","type":"heading_2","heading_2":{"text":[{"type":"text","text":{"content":"Digest"}}]}},
        {"object":"block","type":"paragraph","paragraph":{"text":[{"type":"text","text":{"content":content}}]}}
    ]
    nc.create_page(db_id, props, children)
