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
        self.last_id = 0  # number of topics (topic id)
        self.tasks = []  # due tasks for today
        self.dirty = False

    def run(self):
        if DATA_FILE in listdir():
            self.load_data()
        self.get_due_today()
        self.menu()

    def save(self):
        data = {}
        topics: List[Topic] = [topic.to_dict() for topic in self.topics]
        data["topics"] = topics  #  topics list
        data["last_id"] = self.last_id  # stores the latest id counter
        json.dump(data, open(DEBUG_DATA_FILE, "w"), indent=4)  # dump json for debug
        msgpack.dump(data, open(DATA_FILE, "wb"))

    def load_data(self):
        try:
            self.last_id = 0
            self.topics.clear()
            data = msgpack.load(open(DATA_FILE, "rb"))
            topics = data["topics"]
            self.last_id = data["last_id"]  # geting the id counter
            for t in topics:
                topic = Topic()
                topic.from_dict(t)
                self.topics.append(topic)
        except Exception as e:
            console.print(f"Error : {e}", style="bold red")

    def is_due(self, topic: Topic) -> bool:
        return topic.next_review <= date.today()

    def get_due_today(self) -> None:
        self.tasks = [topic for topic in self.topics if self.is_due(topic)]

    def list_revision_task(self, topics: List[Topic]) -> None:
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

    def list_revision_topics(self, topics: List[Topic]) -> None:
        "lists the pending tasks(topics) for today as a table"
        if len(topics) == 0:
            console.print("[bold green]Nothing due today. Good work.[/bold green]")
            return
        rev_list = "\n".join(
            f"[bold cyan]{i}[/bold cyan]. {t.topic} - {t.subject}"
            for i, t in enumerate(topics)
        )
        console.print(Panel(rev_list, title="Topics"))

    def get_multiline(self, message: str) -> str:
        "gets multiline input for fields such as description"
        print(message, "\n")
        console.print("[dim]Type 'end' on a new line to finish[/dim]")

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
                            self.list_revision_task(self.tasks)
                        case 2:
                            self.list_revision_topics(self.tasks)
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
        description = self.get_multiline("Description")
        today = date.today()
        topic = Topic(
            id=self.last_id + 1,
            subject=subject,
            topic=topic_name,
            description=description,
            lastreview=today,
            nextreview=today,
        )
        self.topics.append(topic)
        self.last_id += 1
        self.get_due_today()
        self.dirty = True


if __name__ == "__main__":
    console.clear()
    app = App()
    app.run()
    if app.dirty:
        app.save()
