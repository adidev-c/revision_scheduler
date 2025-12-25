from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from topic import Topic
from typing import List
from datetime import date, timedelta


class Revision:
    def __init__(self, topic: Topic, console: Console, revision_delta: List[int]):
        self.topic: Topic = topic
        self.console: Console = console
        self.delta = revision_delta

        self.virtual_topic = topic.clone()

    def show_menu(self, options: List[str], title: str):
        menu_text = "\n".join(
            f"[bold cyan]{i+1}[/bold cyan]. {opt}" for i, opt in enumerate(options)
        )
        self.console.print(Panel(menu_text, title=title))

    def ask_choice(self, prompt=">>") -> int:
        return int(Prompt.ask(prompt))

    def sync_topic(self):
        self.virtual_topic.revisions += 1
        self.topic.revisions = self.virtual_topic.revisions
        idx = min(self.virtual_topic.revisions, len(self.delta) - 1)
        days = self.delta[idx]
        self.topic.next_review = date.today() + timedelta(days=days)
        self.topic.last_review = date.today()
        self.topic.comments.clear()
        self.topic.mistakes.clear()
        self.topic.comments = self.virtual_topic.comments
        self.topic.mistakes = self.virtual_topic.mistakes

    def restore_topic(self) -> None:
        self.virtual_topic = self.topic.clone()

    def show_topic(self):
        header_text, desc, meta, mistakes_panel, comments_panel = (
            self.virtual_topic.details()
        )
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

    # COMMENTS EDIT
    def edit_comments(self):
        self.console.clear()
        while True:
            self.show_menu(
                options=[
                    "Show comments",
                    "Add comment",
                    "Remove comment",
                    "Clear all comments",
                    "Restore",
                    "Exit comment section",
                ],
                title="Comment Editor Menu",
            )

            while True:
                try:
                    choice = self.ask_choice()
                    match choice:
                        case 1:
                            self.show_comments()
                        case 2:
                            self.add_comment()
                        case 3:
                            self.remove_comment()
                        case 4:
                            self.clear_all_comments()
                        case 5:
                            self.restore_comments()
                        case 6:
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
                    if self.bool_prompt(
                        "Quit without saving comments?" "Quit without saving comments?"
                    ):
                        return
                    continue

    def show_comments(self):
        self.console.print(self.virtual_topic.get_comments_panel())

    def add_comment(self):
        comment = Prompt.ask("Comment")
        self.virtual_topic.comments.append(comment)

    def remove_comment(self):
        if not self.virtual_topic.comments:
            self.console.print("[dim]No comment recorded.[/dim]")
        self.console.print(self.virtual_topic.get_comments_panel())
        index = int(Prompt.ask("Select"))
        self.virtual_topic.comments.pop(index)

    def clear_all_comments(self):
        clear = self.bool_prompt("Clear all comments?")
        if not clear:
            return
        self.virtual_topic.comments.clear()

    def restore_comments(self):
        restore = self.bool_prompt("Restore all comments?")
        if not restore:
            return
        self.virtual_topic.comments = self.topic.comments.copy()

    # MISTAKES

    def edit_mistakes(self):
        self.console.clear()
        while True:
            self.show_menu(
                options=[
                    "Show mistakes",
                    "Add mistake",
                    "Remove mistakes",
                    "Clear all mistakes",
                    "Restore",
                    "Exit mistakes section",
                ],
                title="Mistake Editor Menu",
            )

            while True:
                try:
                    choice = self.ask_choice()
                    match choice:
                        case 1:
                            self.show_mistakes()
                        case 2:
                            self.add_mistake()
                        case 3:
                            self.remove_mistake()
                        case 4:
                            self.clear_all_mistakes()
                        case 5:
                            self.restore_mistakes()
                        case 6:
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
                    quit = self.bool_prompt("Quit without saving mistakes?")
                    if quit:
                        return
                    continue

    def show_mistakes(self):
        self.console.print(self.virtual_topic.get_mistakes_panel())

    def add_mistake(self):
        mistake = Prompt.ask("Mistake")
        self.virtual_topic.mistakes.append(mistake)

    def remove_mistake(self):
        if not self.virtual_topic.mistakes:
            self.console.print("[dim]No Mistake recorded.[/dim]")
        self.console.print(self.virtual_topic.get_mistakes_panel())
        index = int(Prompt.ask("Select"))
        self.virtual_topic.mistakes.pop(index)

    def clear_all_mistakes(self):
        clear = self.bool_prompt("Clear all mistakes?")
        if not clear:
            return
        self.virtual_topic.mistakes.clear()

    def restore_mistakes(self):
        clear = self.bool_prompt("Restore all mistakes?")
        if not clear:
            return
        self.virtual_topic.mistakes = self.topic.mistakes.copy()

    # SCORE TOPIC
    def score_topic(self):
        score = int(Prompt.ask("New score (1-10)"))
        self.virtual_topic.score = score

    # RESTORE TOPIC
    def restore_edited_topic(self):
        if not self.bool_prompt("Restore topic?"):
            return
        self.restore_topic()

    def bool_prompt(self, prompt: str):
        "Yes or no prompts"
        if Prompt.ask(prompt=prompt, choices=["y", "n"], default="n") == "n":
            return False
        return True

    def start(self):
        self.menu()

    def menu(self):
        self.console.clear()
        while True:
            self.show_menu(
                options=[
                    "Edit comments",
                    "Edit mistakes",
                    "Score topic",
                    "Show topic",
                    "Restore topic",
                    "Save & Exit (Mark as done)",
                    "Exit without saving (Mark as incomplete)",
                ],
                title="Revision Menu",
            )

            while True:
                try:
                    choice = self.ask_choice()
                    match choice:
                        case 1:
                            self.edit_comments()
                        case 2:
                            self.edit_mistakes()
                        case 3:
                            self.score_topic()
                        case 4:
                            self.show_topic()
                        case 5:
                            self.restore_edited_topic()
                        case 6:
                            self.sync_topic()
                            return
                        case 7:
                            if not self.bool_prompt("Exit the editor without saving?"):
                                continue
                            self.restore_topic()
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
                    quit = self.bool_prompt("Quit without saving?")
                    if quit:
                        return
                    continue
