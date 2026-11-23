"""Question-set library and game selection."""

import csv
import hashlib
import json
import re
from pathlib import Path
import shutil
import sqlite3
import sys
import textwrap

import pygame

from .jeopardy import JeopardyQuestions
from .answerreview import AnswerReview


TITLES = {"JEOPARDY_CSV_REAL.csv": "Classic Jeopardy · General trivia"}


def choose_csv():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        return filedialog.askopenfilename(parent=root, title="Add a Jeopardy question set", filetypes=[("Jeopardy CSV files", "*.csv")])
    finally:
        root.destroy()


class GameLibrary:
    def __init__(self, dims, preferred, state_path, directory=None, builtin=None, progress=None):
        self.dims = dims
        project = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
        self.directory = Path(directory) if directory is not None else project / "questions"
        self.builtin = Path(builtin) if builtin is not None else Path("questions/JEOPARDY_CSV_REAL.csv").resolve()
        self.state_path = Path(state_path)
        preferred_path = Path(preferred)
        if preferred_path.suffix.lower() != ".csv":
            preferred_path = Path(str(preferred_path) + ".csv")
        self.preferred = preferred_path.resolve()
        self.selected = 0
        self.page = 0
        self.open = True
        self.message = ""
        self.entries = []
        self.progress = progress
        self.statistics = {}
        self.saved = {}
        self.review_screen = None
        self.delete_pending = None
        self.delete_error = ""
        self.font = pygame.font.SysFont("segoeui", 24)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.title_font = pygame.font.SysFont("segoeui", 38, bold=True)
        self.navigation = pygame.Rect(dims[0] - 320, 8, 144, 34)
        self.list_rect = pygame.Rect(40, 155, 670, 490)
        self.detail_rect = pygame.Rect(740, 155, dims[0] - 780, 430)
        self.start_button = pygame.Rect(740, 605, dims[0] - 780, 48)
        self.saved_resume_button = pygame.Rect(740, 605, (dims[0] - 796) // 2, 48)
        self.restart_button = pygame.Rect(self.saved_resume_button.right + 16, 605, self.saved_resume_button.width, 48)
        self.add_button = pygame.Rect(740, 675, (dims[0] - 800) // 2, 44)
        self.refresh_button = pygame.Rect(self.add_button.right + 20, 675, self.add_button.width, 44)
        self.resume_button = pygame.Rect(40, dims[1] - 67, 245, 42)
        self.previous_button = pygame.Rect(515, 654, 90, 36)
        self.next_button = pygame.Rect(620, 654, 90, 36)
        self.review_button = pygame.Rect(764, 523, (dims[0] - 844) // 2, 42)
        self.delete_button = pygame.Rect(self.review_button.right + 16, 523, self.review_button.width, 42)
        self.delete_panel = pygame.Rect(0, 0, 700, 330)
        self.delete_panel.center = (dims[0] // 2, dims[1] // 2)
        self.cancel_delete_button = pygame.Rect(self.delete_panel.x + 40, self.delete_panel.y + 245, 280, 48)
        self.confirm_delete_button = pygame.Rect(self.delete_panel.x + 340, self.delete_panel.y + 245, 320, 48)
        try:
            saved = json.loads(self.state_path.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                self.preferred = Path(saved.get("selected", str(self.preferred)))
        except (OSError, ValueError, TypeError):
            pass
        self.refresh()

    @property
    def selected_entry(self):
        return self.entries[self.selected] if self.entries else None

    def entry_key(self, path):
        if path.resolve() == self.builtin.resolve():
            return "builtin:classic"
        return "file:" + str(path.resolve()).casefold()

    def refresh(self):
        selected_path = self.selected_entry["path"] if self.selected_entry else self.preferred
        self.directory.mkdir(parents=True, exist_ok=True)
        paths = [path for path in self.directory.rglob("*") if path.is_file() and path.suffix.lower() == ".csv"]
        for extra in (self.preferred, self.builtin):
            if extra.is_file():
                paths.append(extra)
        paths = sorted(set(path.resolve() for path in paths), key=lambda path: (path == self.builtin, path.name.casefold()))
        hidden = self.progress.hidden_games() if self.progress is not None else set()
        self.entries = []
        for path in paths:
            key = self.entry_key(path)
            if key in hidden:
                continue
            entry = {"path": path, "library_key": key, "title": TITLES.get(path.name, path.stem.replace("_", " ")), "error": ""}
            try:
                questions = JeopardyQuestions(str(path.with_suffix("")))
                entry["title"] = questions.title or entry["title"]
                count = sum(len(questions._jeopardyRound[category]) for category in questions._categories)
                entry.update(clues=count, categories=len(questions._categories), finals=len(questions._finalJeopardy))
                entry["game_id"] = hashlib.sha256(path.read_bytes()).hexdigest()
            except (OSError, ValueError, csv.Error) as error:
                entry["error"] = str(error)
            title = re.sub(r"^\s*(?:\d+\s*·\s*|0\d+\s+)", "", entry["title"]).strip()
            entry["title"] = f"{len(self.entries) + 1} · {title or path.stem.replace('_', ' ')}"
            self.entries.append(entry)
        self.selected = next((index for index, entry in enumerate(self.entries) if entry["path"] == selected_path), 0)
        if self.entries and self.entries[self.selected]["path"] != selected_path:
            self.selected = next((index for index, entry in enumerate(self.entries) if entry["path"].name == selected_path.name), self.selected)
        self.page = self.selected // 7
        self.refresh_statistics()

    def refresh_statistics(self):
        self.saved = self.progress.saved_games() if self.progress is not None else {}
        if self.progress is not None:
            self.statistics = {entry["game_id"]: self.progress.summary(entry["game_id"]) for entry in self.entries if not entry["error"]}

    def remember(self):
        if self.selected_entry is None:
            return
        temporary = self.state_path.with_suffix(".tmp")
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(json.dumps({"selected": str(self.selected_entry["path"])}), encoding="utf-8")
            temporary.replace(self.state_path)
        except OSError:
            self.message = "Your game will start. The selection could not be saved."

    def add_csv(self, source):
        source = Path(source).resolve()
        if source.suffix.lower() != ".csv":
            raise ValueError("Choose a CSV question file.")
        JeopardyQuestions(str(source.with_suffix("")))
        destination = source if source.is_relative_to(self.directory.resolve()) else self.directory / source.name
        suffix = 2
        while destination.exists() and destination.resolve() != source:
            if hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256(source.read_bytes()).digest():
                break
            destination = self.directory / f"{source.stem} ({suffix}).csv"
            suffix += 1
        if not destination.exists():
            temporary = destination.with_suffix(".tmp")
            shutil.copyfile(source, temporary)
            layout = source.with_suffix(".layout.json")
            if layout.exists():
                layout_temporary = destination.with_suffix(".layout.tmp")
                shutil.copyfile(layout, layout_temporary)
                layout_temporary.replace(destination.with_suffix(".layout.json"))
            temporary.replace(destination)
        if self.progress is not None:
            self.progress.restore_game(self.entry_key(destination))
        self.refresh()
        self.selected = next(index for index, entry in enumerate(self.entries) if entry["path"] == destination.resolve())
        self.page = self.selected // 7
        self.message = "Added to your question library."

    def row_rect(self, row):
        return pygame.Rect(self.list_rect.x, self.list_rect.y + row * 70, self.list_rect.width, 62)

    def handle_event(self, event, can_resume):
        if self.delete_pending is not None:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.delete_pending = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.cancel_delete_button.collidepoint(event.pos):
                    self.delete_pending = None
                elif self.confirm_delete_button.collidepoint(event.pos):
                    try:
                        self.delete_game(self.delete_pending)
                    except (OSError, sqlite3.Error) as error:
                        self.delete_error = "Could not delete this game. Try again."
                    else:
                        self.delete_pending = None
            return None
        if self.review_screen is not None:
            if self.review_screen.handle_event(event) == "close":
                self.review_screen = None
            return None
        if not self.open:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_F2) or (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.navigation.collidepoint(event.pos)
            ):
                self.open = True
                self.refresh_statistics()
                pygame.key.stop_text_input()
                return "opened"
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume" if can_resume else "quit"
            if event.key == pygame.K_RETURN:
                return self.start_selected()
            if event.key == pygame.K_DELETE:
                self.request_delete()
            if event.key in (pygame.K_UP, pygame.K_DOWN) and self.entries:
                direction = 1 if event.key == pygame.K_DOWN else -1
                self.selected = (self.selected + direction) % len(self.entries)
                self.page = self.selected // 7
        if event.type == pygame.MOUSEWHEEL:
            maximum = max(0, (len(self.entries) - 1) // 7)
            self.page = max(0, min(maximum, self.page - event.y))
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row in range(7):
                index = self.page * 7 + row
                if index < len(self.entries) and self.row_rect(row).collidepoint(event.pos):
                    self.selected = index
                    self.message = ""
            if self.has_saved_game() and self.restart_button.collidepoint(event.pos):
                return "restart"
            if self.start_button.collidepoint(event.pos):
                return self.start_selected()
            if self.review_button.collidepoint(event.pos) and self.progress is not None and self.selected_entry and not self.selected_entry["error"]:
                entry = self.selected_entry
                self.review_screen = AnswerReview(self.dims, self.progress, entry["game_id"], entry["title"])
            if self.delete_button.collidepoint(event.pos):
                self.request_delete()
            if can_resume and self.resume_button.collidepoint(event.pos):
                return "resume"
            if self.previous_button.collidepoint(event.pos):
                self.page = max(0, self.page - 1)
            elif self.next_button.collidepoint(event.pos):
                self.page = min(max(0, (len(self.entries) - 1) // 7), self.page + 1)
            elif self.refresh_button.collidepoint(event.pos):
                self.refresh()
                self.message = "Library refreshed."
            elif self.add_button.collidepoint(event.pos):
                try:
                    source = choose_csv()
                    if source:
                        self.add_csv(source)
                except (OSError, ValueError, csv.Error, sqlite3.Error) as error:
                    self.message = str(error)
        return None

    def request_delete(self):
        if self.selected_entry is not None and self.progress is not None:
            self.delete_pending = dict(self.selected_entry)
            self.delete_error = ""

    def delete_game(self, entry):
        self.progress.hide_game(entry["library_key"])
        self.refresh()
        self.remember()
        self.message = f"Deleted {entry['title']} from the library."

    def start_selected(self):
        if self.selected_entry is None:
            self.message = "Add a question CSV to start a game."
        elif self.selected_entry["error"]:
            self.message = self.selected_entry["error"]
        else:
            return "resume_saved" if self.has_saved_game() else "start"
        return None

    def has_saved_game(self):
        return bool(self.selected_entry and self.selected_entry.get("game_id") in self.saved)

    def label(self, screen, text, position, font=None, color="white"):
        screen.blit((font or self.font).render(text, True, color), position)

    def button(self, screen, rect, text, enabled=True):
        pygame.draw.rect(screen, (38, 66, 145) if enabled else (38, 43, 65), rect, border_radius=7)
        pygame.draw.rect(screen, (123, 154, 231), rect, width=1, border_radius=7)
        label = self.font.render(text, True, "white" if enabled else (150, 155, 175))
        screen.blit(label, label.get_rect(center=rect.center))

    def draw_navigation(self, screen):
        self.button(screen, self.navigation, "Library  F2")

    def draw(self, screen, can_resume):
        if self.review_screen is not None:
            self.review_screen.draw(screen)
            return
        screen.fill((10, 14, 43))
        self.label(screen, "Your Jeopardy library", (40, 35), self.title_font, (255, 215, 80))
        self.label(screen, "Choose your questions, then choose your players.", (40, 91))
        for row, entry in enumerate(self.entries[self.page * 7:self.page * 7 + 7]):
            index = self.page * 7 + row
            rect = self.row_rect(row)
            selected = index == self.selected
            pygame.draw.rect(screen, (38, 66, 145) if selected else (20, 29, 66), rect, border_radius=8)
            pygame.draw.rect(screen, (255, 215, 80) if selected else (68, 85, 140), rect, width=2, border_radius=8)
            title = entry["title"]
            while self.font.size(title)[0] > rect.width - 30:
                title = title[:-2] + "…"
            self.label(screen, title, (rect.x + 15, rect.y + 6))
            detail = "Needs attention · select for details" if entry["error"] else f"{entry['clues']:,} clues · {entry['categories']} categories · {entry['finals']} Final Jeopardy"
            stats = self.statistics.get(entry.get("game_id"))
            if stats:
                detail = f"{entry['clues']:,} clues · Played {stats['played']} · Right {stats['correct']} · Wrong {stats['incorrect']}"
            if entry.get("game_id") in self.saved:
                detail += " · Saved"
            self.label(screen, detail, (rect.x + 15, rect.y + 35), self.small_font, (199, 211, 243))
        pygame.draw.rect(screen, (20, 29, 66), self.detail_rect, border_radius=10)
        entry = self.selected_entry
        if entry:
            x, y = self.detail_rect.x + 24, self.detail_rect.y + 24
            for line in textwrap.wrap(entry["title"], 28):
                self.label(screen, line, (x, y), color=(255, 215, 80))
                y += 33
            detail = entry["error"] or ("Every clue is played in one game." if entry["clues"] == 60 and entry["categories"] == 12 else "Each game randomly selects 60 clues and one Final Jeopardy question.")
            for line in textwrap.wrap(detail, 34):
                self.label(screen, line, (x, y + 18), self.small_font, (199, 211, 243))
                y += 27
            y += 36
            stats = self.statistics.get(entry.get("game_id"))
            if stats:
                lines = [f"Played {stats['played']} · Completed {stats['completed']}",
                         f"Right {stats['correct']} · Wrong {stats['incorrect']}",
                         f"Skipped {stats['skipped']}",
                         f"Questions recorded {stats['seen']} / {entry['clues'] + entry['finals']}"]
            else:
                lines = textwrap.wrap(entry["path"].name, 34)[:4]
            for line in lines:
                self.label(screen, line, (x, y), self.small_font, (199, 211, 243))
                y += 29
            if self.progress is not None and not entry["error"]:
                self.button(screen, self.review_button, "Review answers")
        if self.has_saved_game():
            self.button(screen, self.saved_resume_button, "Resume game")
            self.button(screen, self.restart_button, "Restart game")
        else:
            self.button(screen, self.start_button, "Start selected game", bool(entry and not entry["error"]))
        self.button(screen, self.add_button, "Add CSV…")
        self.button(screen, self.refresh_button, "Refresh")
        self.button(screen, self.previous_button, "‹ Prev", self.page > 0)
        self.button(screen, self.next_button, "Next ›", (self.page + 1) * 7 < len(self.entries))
        if can_resume:
            self.button(screen, self.resume_button, "Resume current game")
        page_count = max(1, (len(self.entries) + 6) // 7)
        self.label(screen, f"{len(self.entries)} question sets · Page {self.page + 1} of {page_count}", (40, 655), self.small_font, (199, 211, 243))
        for index, line in enumerate(textwrap.wrap(self.message, 105)[:2]):
            self.label(screen, line, (40, 695 + index * 22), self.small_font, (255, 215, 80))
        self.button(screen, self.delete_button, "Delete game", bool(entry and self.progress is not None))
        if self.delete_pending is not None:
            self.draw_delete_confirmation(screen)

    def draw_delete_confirmation(self, screen):
        overlay = pygame.Surface(self.dims, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 205))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (35, 24, 47), self.delete_panel, border_radius=12)
        pygame.draw.rect(screen, (235, 110, 120), self.delete_panel, width=2, border_radius=12)
        x, y = self.delete_panel.topleft
        self.label(screen, "Delete this game from the library?", (x + 40, y + 25))
        for index, line in enumerate(textwrap.wrap(self.delete_pending["title"], 44)[:2]):
            self.label(screen, line, (x + 40, y + 78 + index * 31), color=(255, 215, 80))
        self.label(screen, "Saved play counts and answer history are retained.", (x + 40, y + 157), self.small_font)
        self.label(screen, self.delete_error or "Re-import the CSV to restore it. Escape cancels.", (x + 40, y + 195), self.small_font, (235, 190, 190))
        self.button(screen, self.cancel_delete_button, "Cancel")
        pygame.draw.rect(screen, (150, 38, 55), self.confirm_delete_button, border_radius=7)
        label = self.font.render("Delete game", True, "white")
        screen.blit(label, label.get_rect(center=self.confirm_delete_button.center))
