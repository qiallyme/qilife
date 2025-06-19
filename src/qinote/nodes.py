from datetime import datetime

class QNode:
    def __init__(self, title, content, tags=None, links=None):
        self.title = title
        self.content = content
        self.tags = tags or []
        self.links = links or []
        self.created = datetime.utcnow().isoformat()

    def to_notion_props(self):
        return {
            "Title": {"title":[{"text":{"content":self.title}}]},
            "Content": {"rich_text":[{"text":{"content":self.content}}]},
            "Created": {"date":{"start":self.created}},
            "Tags": {"multi_select":[{"name":t} for t in self.tags]},
            "Links": {"relation":[{"id":l} for l in self.links]}
        }
