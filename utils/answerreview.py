"""Browse saved question results from a game's library entry."""

import textwrap

import pygame


class AnswerReview:
    def __init__(self, dims, progress, game_id, title):
        self.dims = dims
        self.progress = progress
        self.game_id = game_id
        self.title = title
        self.filter = "all"
        self.entries = []
        self.selected = 0
        self.page = 0
        self.detail_scroll = 0
        self.max_detail_scroll = 0
        self.font = pygame.font.SysFont("segoeui", 21)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.title_font = pygame.font.SysFont("segoeui", 36, bold=True)
        self.back_button = pygame.Rect(dims[0] - 220, 80, 180, 42)
        self.filters = [(name, key, pygame.Rect(40 + index * 145, 138, 132, 40))
                        for index, (name, key) in enumerate((("All", "all"), ("Wrong", "incorrect"), ("Correct", "correct"), ("Skipped", "skip")))]
        self.previous_button = pygame.Rect(40, dims[1] - 62, 120, 40)
        self.next_button = pygame.Rect(175, dims[1] - 62, 120, 40)
        self.details = pygame.Rect(630, 200, dims[0] - 670, dims[1] - 300)
        self.load()

    def load(self):
        self.entries = self.progress.review(self.game_id, self.filter)
        self.selected = 0
        self.page = 0
        self.detail_scroll = 0

    def row_rect(self, row):
        return pygame.Rect(40, 200 + row * 70, 560, 62)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "close"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.collidepoint(event.pos):
                return "close"
            for name, key, rect in self.filters:
                if rect.collidepoint(event.pos):
                    self.filter = key
                    self.load()
            for row in range(7):
                index = self.page * 7 + row
                if index < len(self.entries) and self.row_rect(row).collidepoint(event.pos):
                    self.selected = index
                    self.detail_scroll = 0
            if self.previous_button.collidepoint(event.pos):
                self.page = max(0, self.page - 1)
            elif self.next_button.collidepoint(event.pos):
                self.page = min(max(0, (len(self.entries) - 1) // 7), self.page + 1)
        if event.type == pygame.MOUSEWHEEL:
            if self.details.collidepoint(pygame.mouse.get_pos()):
                self.detail_scroll = max(0, min(self.max_detail_scroll, self.detail_scroll - event.y * 35))
            else:
                self.page = max(0, min(max(0, (len(self.entries) - 1) // 7), self.page - event.y))
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_UP, pygame.K_DOWN) and self.entries:
            self.selected = (self.selected + (1 if event.key == pygame.K_DOWN else -1)) % len(self.entries)
            self.page = self.selected // 7
            self.detail_scroll = 0
        return None

    def label(self, screen, text, position, font=None, color="white"):
        screen.blit((font or self.font).render(text, True, color), position)

    def button(self, screen, rect, text, selected=False):
        pygame.draw.rect(screen, (55, 78, 147) if selected else (25, 39, 85), rect, border_radius=7)
        pygame.draw.rect(screen, (255, 215, 80) if selected else (100, 120, 180), rect, width=2, border_radius=7)
        label = self.font.render(text, True, "white")
        screen.blit(label, label.get_rect(center=rect.center))

    def draw(self, screen):
        screen.fill((10, 14, 43))
        self.label(screen, "Question history", (40, 30), self.title_font, (255, 215, 80))
        self.label(screen, self.title, (40, 87))
        self.button(screen, self.back_button, "Back to library")
        for name, key, rect in self.filters:
            self.button(screen, rect, name, self.filter == key)
        for row, entry in enumerate(self.entries[self.page * 7:self.page * 7 + 7]):
            rect = self.row_rect(row)
            pygame.draw.rect(screen, (38, 66, 145) if self.page * 7 + row == self.selected else (20, 29, 66), rect, border_radius=7)
            title = entry["question"].splitlines()[0]
            while self.font.size(title)[0] > rect.width - 25:
                title = title[:-2] + "…"
            self.label(screen, title, (rect.x + 12, rect.y + 6))
            counts = f"Right {entry['correct']} · Wrong {entry['incorrect']} · Skipped {entry['skipped']}"
            self.label(screen, counts, (rect.x + 12, rect.y + 35), self.small_font, (199, 211, 243))
        pygame.draw.rect(screen, (20, 29, 66), self.details, border_radius=9)
        previous_clip = screen.get_clip()
        viewport = pygame.Rect(self.details.x + 12, self.details.y + 12, self.details.width - 24, self.details.height - 48)
        screen.set_clip(viewport)
        if self.entries:
            entry = self.entries[self.selected]
            x, y = self.details.x + 20, self.details.y + 18 - self.detail_scroll
            self.label(screen, entry["category"], (x, y), color=(255, 215, 80))
            y += 32
            self.label(screen, f"Right {entry['correct']} · Wrong {entry['incorrect']} · Skipped {entry['skipped']}", (x, y), self.small_font)
            y += 35
            self.label(screen, "QUESTION", (x, y), self.small_font, (165, 179, 216))
            y += 26
            for paragraph in entry["question"].splitlines():
                for line in textwrap.wrap(paragraph, 52) or [""]:
                    self.label(screen, line, (x, y), self.small_font)
                    y += 23
            y += 12
            self.label(screen, "CORRECT ANSWER", (x, y), self.small_font, (165, 230, 175))
            y += 26
            for line in textwrap.wrap(entry["answer"], 52):
                self.label(screen, line, (x, y), self.small_font, (165, 230, 175))
                y += 23
            y += 14
            for line in textwrap.wrap("Answered by " + entry["players"], 52):
                self.label(screen, line, (x, y), self.small_font, (165, 179, 216))
                y += 23
            self.max_detail_scroll = max(0, y + self.detail_scroll + 5 - viewport.bottom)
        else:
            self.label(screen, "No results in this view yet.", (self.details.x + 24, self.details.y + 30))
            self.label(screen, "Mark answers Correct, Incorrect or Skip", (self.details.x + 24, self.details.y + 75), self.small_font)
            self.label(screen, "while playing to build your history.", (self.details.x + 24, self.details.y + 101), self.small_font)
        screen.set_clip(previous_clip)
        if self.entries and self.max_detail_scroll:
            self.label(screen, "Scroll in this panel to read more", (self.details.x + 20, self.details.bottom - 27), self.small_font, (165, 179, 216))
        self.button(screen, self.previous_button, "‹ Previous")
        self.button(screen, self.next_button, "Next ›")
        self.label(screen, f"{len(self.entries)} questions · Page {self.page + 1} of {max(1, (len(self.entries) + 6) // 7)}", (320, self.dims[1] - 54), self.small_font)
        self.label(screen, "Filters include any question with that result in your saved history.", (630, self.dims[1] - 54), self.small_font, (165, 179, 216))
