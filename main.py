from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from os import listdir
from topic import Topic
from datetime import date
from typing import List
import json
import msgpack

console = Console()

DATA_FILE = "data.bin"
DEBUG_DATA_FILE = "data.json"


class App:
    def __init__(self):
        self.delta = [0, 1, 3, 7, 10, 21, 35, 60]  # delta for rivision
        self.topics: List[Topic] = []  # all topics
        self.total_topics = 0  # number of topics

    def run(self):
        if DATA_FILE in listdir():
            self.load_data()
        self.menu()

    def save(self):
        data: List[Topic] = [topic.to_dict() for topic in self.topics]
        json.dump(data, open(DEBUG_DATA_FILE, "w"), indent=4)
        msgpack.dump(data, open(DATA_FILE, "wb"))

    def load_data(self):
        try:
            self.total_topics = 0
            self.topics.clear()
            topics = msgpack.load(open(DATA_FILE, "rb"))
            for t in topics:
                topic = Topic()
                topic.from_dict(t)
                self.topics.append(topic)
                self.total_topics += 1
        except Exception as e:
            console.print(f"Error : {e}", style="bold red")

    def is_due(self, topic: Topic):
        return topic.next_review <= date.today()

    def get_due_today(self):
        due_today = [topic for topic in self.topics if self.is_due(topic)]
        return due_today

    def revision_task(self, topics: List[Topic]):
        if len(topics) == 0:
            console.print("[bold green]Nothing due today. Good work.[/bold green]")
            return
        table = Table(
            title="Today's Revision Report",
            header_style="bold cyan",
            show_lines=True,
            expand=True,
        )
        table.add_column("Subject", style="bold", ratio=2)
        table.add_column("Topic", style="bold", ratio=2)
        table.add_column("Description", ratio=5)
        table.add_column("Priority", justify="center", ratio=1)

        for t in topics:
            label, style = t.get_priority()
            priority_text = Text(label, style=style)

            table.add_row(t.subject, t.topic, t.description, priority_text)
        console.print(table)

    def list_revision_topics(self, topics: Topic):
        if len(topics) == 0:
            console.print("[bold green]Nothing due today. Good work.[/bold green]")
            return
        rev_list = "\n".join(
            f"[bold cyan]{t.id}[/bold cyan]. {t.topic} - {t.subject}" for t in topics
        )
        console.print(Panel(rev_list, title="Tpics"))

    def get_multiline(self, message: str) -> str:
        "gets multiline input for fields such as description"
        print(message, "\n")
        text = ""
        while True:
            data = console.input("")
            if data == "end":
                break
            text += data
            text += "\n"
        return text

    def menu(self) -> None:
        while True:
            options = ["Today's task", "Complete task", "Add new topic", "Exit"]

            menu_text = "\n".join(
                f"[bold cyan]{i+1}[/bold cyan]. {opt}" for i, opt in enumerate(options)
            )

            console.print(Panel(menu_text, title="Main Menu"))
            while True:
                try:
                    choice = int(Prompt.ask("Choice"))
                    match choice:
                        case 1:
                            self.revision_task(self.get_due_today())
                        case 2:
                            self.list_revision_topics(self.get_due_today())
                        case 3:
                            self.new_topic()
                        case 4:
                            self.save()
                            return
                        case _:
                            console.print("Invalid choice", style="red")
                            continue
                    break
                except Exception as e:
                    console.print(f"Error : {e}", style="bold red")
                except KeyboardInterrupt:
                    return

    def new_topic(self):
        subject = Prompt.ask("Subject")
        topic_name = Prompt.ask("Topic")
        description = self.get_multiline("Description ('end' to end)")
        today = date.today()
        topic = Topic(
            id=self.total_topics + 1,
            subject=subject,
            topic=topic_name,
            description=description,
            lastreview=today,
            nextreview=today,
        )
        self.topics.append(topic)
        self.total_topics += 1


if __name__ == "__main__":
    console.clear()
    app = App()
    app.run()
