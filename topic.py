from datetime import date
from typing import List, Optional
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

class Topic:
    def __init__(
        self,
        id: Optional[int] = 0,
        subject: Optional[str] = "",
        topic: Optional[str] = "",
        description: Optional[str] = "",
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
        self.comments: List[str] = []
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
        data["comments"] = self.comments
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
        self.comments = data["comments"]
        self.score = data["score"]

    def revision_update(self, mistakes: List[str], comments: List[str], score: int):
        self.revisions += 1
        self.last_review = date.today()
        self.mistakes = mistakes

    def get_priority(self):
        if self.score < 3:
            return ("HIGH", "bold red")
        elif self.score < 5:
            return "MEDIUM", "orange"
        elif self.score < 8:
            return "MEDIUM", "yellow"
        else:
            return "LOW", "green"

    def details(self):
        #  HEADER
        header_text = self.get_header_panel()

        #  DESCRIPTION
        desc = self.get_description_panel()

        #  METADATA TABLE
        meta = self.get_meta_table()

        #  MISTAKES
        mistakes_panel = self.get_mistakes_panel()

        #  COMMENTS
        comments_text = self.get_comments_panel()

        return (header_text, desc, meta, mistakes_panel, comments_text)

    def get_comments_panel(self) -> Panel:
        comments_text = (
            "\n".join(f"{i}. {c}" for i, c in enumerate(self.comments))
            if self.comments
            else "[dim]No comments recorded.[/dim]"
        )
        return Panel(
            comments_text,
            title="Comments",
            border_style="yellow",
            expand=True,
        )

    def get_mistakes_panel(self) -> Panel:
        mistakes_text = (
            "\n".join(f"{i}. {m}" for i, m in enumerate(self.mistakes))
            if self.mistakes
            else "[dim]No mistakes recorded.[/dim]"
        )

        return Panel(
            mistakes_text,
            title="Mistakes",
            border_style="red",
            expand=True,
        )

    def get_description_panel(self):
        desc = self.description.strip() or "No description provided."

        return Panel(
            desc,
            title="Description",
            border_style="blue",
            expand=True,
        )

    def get_header_panel(self):
        header_text = Text()
        header_text.append(f"{self.subject}", style="bold cyan")
        header_text.append("  -  ")
        header_text.append(f"{self.topic}", style="bold white")
        header_text.append(f"\nTopic ID: {self.id}", style="dim")
        return Panel(header_text, expand=True)

    def get_meta_table(self):
        meta = Table(show_header=False, box=None)
        meta.add_row("Revisions", str(self.revisions))
        meta.add_row("Last Review", self.last_review.isoformat())
        meta.add_row("Next Review", self.next_review.isoformat())
        meta.add_row("Score", str(self.score))
        return Panel(
            meta,
            title="Revision Stats",
            border_style="green",
            expand=False,
        )

    def clone(self) -> Topic:
        t = Topic()
        t.id = self.id
        t.subject = self.subject
        t.topic = self.topic
        t.description = self.description
        t.revisions = self.revisions
        t.last_review = self.last_review
        t.next_review = self.next_review
        t.mistakes = self.mistakes.copy()
        t.comments = self.comments.copy()
        t.score = self.score
        return t
