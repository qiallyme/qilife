from qinote.nodes import QNode

def template_journal_entry(text, tags=None):
    title = text.split("\n",1)[0][:50]
    return QNode(title, text, tags or ["Journal"])

def template_insight(insight, related_ids=None):
    return QNode(f"Insight: {insight[:30]}", insight, ["Insight"], related_ids or [])

def template_task(task_text, due_date):
    content = f"{task_text}\n\nDue: {due_date}"
    return QNode(f"Task: {task_text[:40]}", content, ["Task"])
