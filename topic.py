from datetime import date, timedelta
from typing import List, Optional


class Topic:
    def __init__(
        self,
        id: Optional[int] = 0,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        description: Optional[str] = None,
        lastreview: Optional[date] = None,
        nextreview: Optional[date] = None,
    ):
        self.id: int = id
        self.subject: str = subject
        self.topic: str = topic
        self.description: str = description
        self.revisions: int = 0
        self.next_review: date = nextreview
        self.last_review: date = lastreview
        self.mistakes: List[str] = []
        self.score = 0

    def to_dict(self):
        data = {}
        data["id"] = self.id
        data["subject"] = self.subject
        data["topic"] = self.topic
        data["description"] = self.description
        data["revisions"] = self.revisions
        data["last_review"] = self.last_review.isoformat()
        data["next_review"] = self.next_review.isoformat()
        data["mistakes"] = self.mistakes
        data["score"] = self.score
        return data

    def from_dict(self, data):
        self.id = data["id"]
        self.subject = data["subject"]
        self.topic = data["topic"]
        self.description = data["description"]
        self.revisions = data["revisions"]
        self.last_review = date.fromisoformat(data["last_review"])
        self.next_review = date.fromisoformat(data["next_review"])
        self.mistakes = data["mistakes"]
        self.score = data["score"]

    def get_priority(self):
        if self.score < 3:
            return ("HIGH", "bold red")
        elif self.score < 5:
            return "MEDIUM", "orange"
        elif self.score < 8:
            return "MEDIUM", "yellow"
        else:
            return "LOW", "green"
