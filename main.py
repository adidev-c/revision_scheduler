from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from revision import Revision
from os import listdir
from topic import Topic
from datetime import date
from typing import List
import json
import msgpack


DATA_FILE = "data.bin"
DEBUG_DATA_FILE = "data.json"


class App:
    def __init__(self, console: Console):
        self.console: Console = console
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
        if not app.dirty:
            return
        data = {}
        topics: List[Topic] = [topic.to_dict() for topic in self.topics]
        data["topics"] = topics  #  topics list
        data["last_id"] = self.last_id  # stores the latest id counter
        json.dump(data, open(DEBUG_DATA_FILE, "w"), indent=4)  # dump json for debug
        msgpack.dump(data, open(DATA_FILE, "wb"))
        self.dirty = False

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
            self.self.console.print(f"Error : {e}", style="bold red")

    def is_due(self, topic: Topic) -> bool:
        return topic.next_review <= date.today()

    def get_due_today(self) -> None:
        self.tasks = [topic for topic in self.topics if self.is_due(topic)]

    def list_revision_task(self, topics: List[Topic]) -> None:
        "lists the pending tasks(topics) for today as a table"
        if len(topics) == 0:
            self.console.print("[bold green]Nothing due today. Good work.[/bold green]")
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
        self.console.print(table)

    def list_revision_topics(self, topics: List[Topic]) -> None:
        "lists the pending tasks(topics) for today as a panel"
        if len(topics) == 0:
            self.console.print("[bold green]Nothing due today. Good work.[/bold green]")
            return
        rev_list = "\n".join(
            f"[bold cyan]{i}[/bold cyan]. {t.topic} - {t.subject}"
            for i, t in enumerate(topics)
        )
        self.console.print(Panel(rev_list, title="Topics"))

    def get_multiline(self, message: str) -> str:
        "gets multiline input for fields such as description"
        print(message, "\n")
        self.console.print("[dim]Type 'end' on a new line to finish[/dim]")

        text = ""
        while True:
            data = self.console.input("")
            if data == "end":
                break
            text += data
            text += "\n"
        return text

    # GET DETAILS
    def get_details(self):
        self.list_revision_topics(self.tasks)
        choice = int(Prompt.ask(prompt="Select topic"))
        topic = self.tasks[choice]
        self.console.clear()
        self.details(topic=topic)

    def details(self, topic: Topic):
        header_text, desc, meta, mistakes_panel, comments_panel = topic.details()
        #  HEADER
        self.console.print(Panel(header_text, expand=True))

        #  DESCRIPTION

        self.console.print(
            Panel(
                desc,
                title="Description",
                border_style="blue",
                expand=True,
            )
        )

        #  METADATA TABLE

        self.console.print(
            Panel(
                meta,
                title="Revision Stats",
                border_style="green",
                expand=False,
            )
        )

        self.console.print(mistakes_panel)

        #  COMMENTS

        self.console.print(comments_panel)

        self.console.print(Rule())

    # REVISE
    def revice(self):
        self.console.clear()
        self.list_revision_topics(self.tasks)
        choice = self.ask_choice("Select topic")
        topic = self.tasks[choice]
        revision = Revision(console=console, revision_delta=self.delta, topic=topic)
        revision.start()
        self.dirty = True
        self.get_due_today()

    def show_menu(self, options: List[str], title: str):
        menu_text = "\n".join(
            f"[bold cyan]{i+1}[/bold cyan]. {opt}" for i, opt in enumerate(options)
        )
        self.console.print(Panel(menu_text, title=title))

    def ask_choice(self, prompt=">>") -> int:
        return int(Prompt.ask(prompt))

    def menu(self) -> None:
        while True:
            self.show_menu(
                options=[
                    "Today's task",
                    "Complete task",
                    "Get details",
                    "Add new topic",
                    "Exit",
                ],
                title="Main Menu",
            )
            while True:
                try:
                    choice = self.ask_choice()
                    match choice:
                        case 1:
                            self.list_revision_task(self.tasks)
                        case 2:
                            self.revice()
                        case 3:
                            self.get_details()
                        case 4:
                            self.new_topic()
                        case 5:
                            self.save()
                            return
                        case _:
                            self.console.print("Invalid choice", style="red")
                            continue
                    Prompt.ask("Press Enter to return")
                    self.console.clear()
                    break
                except Exception as e:
                    self.console.print(f"Error : {e}", style="bold red")
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
    console = Console()
    console.clear()
    app = App(console=console)
    app.run()
    app.save()
