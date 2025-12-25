from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
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

#STYLES
PROCESS_NAME = "bold blue"
PROCESS_SUCCESS = "bold green"
PROCESS_FAILED = "bold red"
ERROR = "bold red"
EMPTY = "bold yellow"
class App:
    def __init__(self, console: Console):
        self.console: Console = console
        self.delta: List[int] = [0, 1, 3, 7, 10, 21, 35, 60]  # delta for rivision
        self.topics: List[Topic] = []  # all topics
        self.last_id: int = 0  # number of topics (topic id)
        self.tasks: List[Topic] = []  # due tasks for today
        self.recycle_bin: List[Topic] = []
        self.dirty = False

    def run(self):
        if DATA_FILE in listdir():
            self.load_data()
        self.get_due_today()
        self.menu()

    def save(self):
        if not self.dirty:
            return
        data = {}
        topics: List[Topic] = [topic.to_dict() for topic in self.topics]
        recycle_bin: List[Topic] = [topic.to_dict() for topic in self.recycle_bin]
        data["topics"] = topics  #  topics list
        data["recycle_bin"] = recycle_bin
        data["last_id"] = self.last_id  # stores the latest id counter
        with open(DATA_FILE, "wb") as file:
            msgpack.dump(data, file)
            file.close()
        with open(DEBUG_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)  # dump json for debug
            f.close()
        self.dirty = False

    def load_data(self):
        try:
            self.last_id = 0
            self.topics.clear()
            with open(DATA_FILE, "rb") as f:
                data = msgpack.load(f)
                f.close()
            topics = data["topics"]
            recycle_bin = data["recycle_bin"]
            self.last_id = data["last_id"]  # geting the id counter

            for t in topics:
                topic = Topic()
                topic.from_dict(t)
                self.topics.append(topic)

            for t in recycle_bin:
                topic = Topic()
                topic.from_dict(t)
                self.recycle_bin.append(topic)
        except Exception as e:
            self.console.print(f"Error : {e}", style=ERROR)

    def is_due(self, topic: Topic) -> bool:
        return topic.next_review <= date.today()

    def get_due_today(self) -> None:
        self.tasks = [topic for topic in self.topics if self.is_due(topic)]
    def get_table(self,title:str,topics:List[Topic])->Table:
        table = Table(
            title=title,
            header_style="bold cyan",
            show_lines=True,
            expand=True,
        )
        table.add_column("Index", style="bold", ratio=1)
        table.add_column("Subject", style="bold", ratio=2)
        table.add_column("Topic", style="bold", ratio=2)
        table.add_column("Description", ratio=5)
        table.add_column("Priority", justify="center", ratio=1)

        for i,t in enumerate(topics):
            label, style = t.get_priority()
            priority_text = Text(label, style=style)

            table.add_row(str(i),t.subject, t.topic, t.description, priority_text)
        return table
    def list_revision_task(self) -> None:
        "lists the pending tasks(topics) for today as a table"
        if len(self.tasks) == 0:
            self.console.print(f"[{PROCESS_SUCCESS}]Nothing due today. Good work.[/{PROCESS_SUCCESS}]")
            return
        table = self.get_table(title="Today's Revision Report",topics=self.tasks)
        self.console.print(table)

    def list_revision_topics(self, topics: List[Topic]) -> bool:
        "lists the pending tasks(topics) for today as a panel"
        if len(topics) == 0:
            self.console.print(f"[{PROCESS_SUCCESS}]Nothing due today. Good work.[/{PROCESS_SUCCESS}]")
            return False  # False -> tasks empty
        table = self.get_table("Revision list",self.tasks)
        self.console.print(table)
        return True

    def get_multiline(self, message: str) -> str:
        "gets multiline input for fields such as description"
        print(message, "\n")
        self.console.print("[dim]Type 'end' on a new line to finish[/dim]")

        text = ""
        while True:
            data = self.console.input()
            if data == "end":
                break
            text += data
            text += "\n"
        return text

    def list_topics(self, title:str,topics: List[Topic])->bool:
        if len(topics)==0:
            self.console.print("Empty",style=EMPTY)
            return False
        table = self.get_table(title=title,topics=topics)
        with self.console.pager():
            self.console.print(table)
        return True

    # GET DETAILS
    def get_details(self):
        if not self.list_revision_topics(self.topics):
            return
        choice = int(Prompt.ask(prompt="Select topic"))
        topic = self.tasks[choice]
        self.console.clear()
        self.details(topic=topic)

    def details(self, topic: Topic):
        header_text, desc, meta, mistakes_panel, comments_panel = topic.details()
        #  HEADER
        self.console.print(header_text)

        #  DESCRIPTION

        self.console.print(desc)

        #  METADATA TABLE

        self.console.print(meta)

        # MISTAKES
        self.console.print(mistakes_panel)

        #  COMMENTS

        self.console.print(comments_panel)

        self.console.print(Rule())

    # REVISE
    def revice(self):
        self.console.clear()
        if not self.list_revision_topics(self.tasks):
            return
        choice = self.ask_choice("Select topic")
        topic = self.tasks[choice]
        revision = Revision(console=console, revision_delta=self.delta, topic=topic)
        revision.start()
        self.dirty = True
        self.get_due_today()

    # ALL TOPICS
    def list_all(self):
        self.list_topics("Topics",self.topics)

    # REMOVE TOPIC
    def remove_topic(self, index, hard=False):
        topic: Topic = self.topics.pop(index)
        if hard:
            return
        self.recycle_bin.append(topic)
        self.get_due_today()
        self.dirty = True
        self.console.print("Topic removed",style=PROCESS_SUCCESS)

    def remove_topic_prompt(self):
        self.list_all()
        self.console.print("Topic removal",style=PROCESS_NAME)
        index = int(Prompt.ask("Index"))
        intensity = Prompt.ask(
            "Intensity h -> hard (no recovary), s -> soft (can be recovered)",
            choices=["h", "s"],
            default="s",
        )
        self.remove_topic(index, intensity == "h")

    # RECOVER TOPIC
    def recover_topic(self, index: int):
        topic: Topic = self.recycle_bin.pop(index)
        self.topics.append(topic)
        self.get_due_today()
        self.dirty = True
        self.console.print("Topic recovered",style=PROCESS_SUCCESS)

    def recover_topic_prompt(self):
        if not self.list_topics("Recycle bin",self.recycle_bin):
            return
        self.console.print("Topic recovary",style=PROCESS_NAME)
        index = int(Prompt.ask("Index"))
        self.recover_topic(index)

    # NEW TASK
    def new_task(self,index:int):
        topic = self.topics[index]
        if topic in self.tasks:
            self.console.print("Task already exists",style=PROCESS_SUCCESS)
            return
        self.tasks.append(topic)
        self.get_due_today()
        self.dirty = True
        self.console.print("New task added",style=PROCESS_SUCCESS)
    def new_task_prompt(self):
        if not self.list_topics("Available topics",self.topics):
            return
        self.console.print("New task addition",style=PROCESS_NAME)
        index = int(Prompt.ask("Index"))
        self.new_task(index)
    def show_menu(self, options: List[str], title: str):
        menu_text = "\n".join(
            f"[bold cyan]{i+1}[/bold cyan]. {opt}" for i, opt in enumerate(options)
        )
        self.console.print(Panel(menu_text, title=title))

    def ask_choice(self, prompt=">>") -> int:
        while True:
            choice = Prompt.ask(prompt)
            if choice.strip() == "":
                continue 
            return int(choice)

    def menu(self) -> None:
        while True:
            self.show_menu(
                options=[
                    "Today's task",
                    "Complete task",
                    "Get details",
                    "Add new topic",
                    "Add new revision task",
                    "View all topics",
                    "Remove topics",
                    "Recover topics",
                    "View recycle bin",
                    "Exit",
                ],
                title="Main Menu",
            )
            while True:
                try:
                    choice = self.ask_choice()
                    match choice:
                        case 0:
                            continue
                        case 1:
                            self.list_revision_task()
                        case 2:
                            self.revice()
                        case 3:
                            self.get_details()
                        case 4:
                            self.new_topic()
                        case 5:
                            self.new_task_prompt()
                        case 6:
                            self.list_all()
                        case 7:
                            self.remove_topic_prompt()
                        case 8:
                            self.recover_topic_prompt()
                        case 9:
                            self.list_topics("Recycle bin",self.recycle_bin)
                        case 10:
                            self.save()
                            return
                        case _:
                            self.console.print("Invalid choice", style="red")
                            continue
                    Prompt.ask("Press Enter to return")
                    self.console.clear()
                    break
                except Exception as e:
                    self.console.print(f"Error : {e}", style=ERROR)
                except KeyboardInterrupt:
                    return

    def new_topic(self):
        self.console.print("New topic",style=PROCESS_NAME)
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
        self.console.print("Topic added",style=PROCESS_SUCCESS)


if __name__ == "__main__":
    console = Console()
    console.clear()
    app = App(console=console)
    app.run()
    app.save()
