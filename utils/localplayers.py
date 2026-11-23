"""Players, turns, and manual scoring for a game on one screen."""

import pygame
import sqlite3


class LocalPlayers:
    def __init__(self, dims):
        self.dims = dims
        self.names = ["Player 1", "Player 2", "", "", "", ""]
        self.scores = []
        self.turn = 0
        self.setup_open = True
        self.finished = False
        self.focus = 0
        self.select_all = True
        self.error = ""
        self.on_start = None
        self.solo = False
        self.font = pygame.font.SysFont("segoeui", 23)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.title_font = pygame.font.SysFont("segoeui", 34, bold=True)
        self.panel = pygame.Rect(0, 0, 620, 590)
        self.panel.center = (dims[0] // 2, dims[1] // 2)
        x, y = self.panel.topleft
        self.fields = [pygame.Rect(x + 160, y + 124 + i * 48, 410, 40) for i in range(6)]
        self.start_button = pygame.Rect(x + 50, y + 478, 250, 48)
        self.solo_button = pygame.Rect(x + 320, y + 478, 250, 48)
        self.again_button = pygame.Rect(dims[0] // 2 - 130, dims[1] - 150, 260, 48)
        button_width = (dims[0] - 80) // 3
        self.score_buttons = [pygame.Rect(20 + i * (button_width + 20), dims[1] - 62, button_width, 44) for i in range(3)]
        pygame.key.start_text_input()

    @property
    def enabled(self):
        return bool(self.scores)

    def start(self, solo=False):
        if not self.setup_open:
            return
        names = ["Solo"] if solo else [name.strip() for name in self.names if name.strip()]
        if not solo and not names:
            self.error = "Enter at least one player name."
            return
        if len({name.casefold() for name in names}) != len(names):
            self.error = "Use a different name for each player."
            return
        try:
            if self.on_start is not None:
                self.on_start(names)
        except (OSError, sqlite3.Error):
            self.error = "Could not save progress. Try starting again."
            return
        self.names = names
        self.solo = solo
        self.scores = [0] * len(names)
        self.turn = 0
        self.setup_open = False
        pygame.key.stop_text_input()

    def score(self, result, value):
        if self.enabled:
            if result == "correct":
                self.scores[self.turn] += value
            elif result == "incorrect":
                self.scores[self.turn] -= value
            self.turn = (self.turn + 1) % len(self.names)

    def scoreboard_rects(self):
        width = (self.dims[0] - 40) // max(1, len(self.names))
        return [pygame.Rect(20 + i * width, self.dims[1] - 128, width - 8, 76) for i in range(len(self.names))]

    def handle_event(self, event, game):
        if self.setup_open:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self.fields):
                    if rect.collidepoint(event.pos):
                        self.focus = index
                        self.select_all = True
                if self.start_button.collidepoint(event.pos):
                    self.start()
                elif self.solo_button.collidepoint(event.pos):
                    self.start(solo=True)
            elif event.type == pygame.TEXTINPUT:
                current = "" if self.select_all else self.names[self.focus]
                self.names[self.focus] = (current + event.text)[:18]
                self.select_all = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    direction = -1 if event.mod & pygame.KMOD_SHIFT else 1
                    self.focus = (self.focus + direction) % 6
                    self.select_all = True
                elif event.key == pygame.K_BACKSPACE:
                    self.names[self.focus] = "" if self.select_all else self.names[self.focus][:-1]
                    self.select_all = False
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                    self.select_all = True
                elif event.key == pygame.K_RETURN:
                    self.start()
            return True
        if self.finished:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.again_button.collidepoint(event.pos):
                game.new_game_requested = True
            return True
        if game._answerCard is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, result in zip(self.score_buttons, ("correct", "incorrect", "skip")):
                    if rect.collidepoint(event.pos):
                        game.resolveAnswer(result)
                        return True
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_c, pygame.K_w, pygame.K_s):
                result = {pygame.K_c: "correct", pygame.K_w: "incorrect", pygame.K_s: "skip"}[event.key]
                game.resolveAnswer(result)
                return True
        if game.isBoardVisible() and self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.scoreboard_rects()):
                if rect.collidepoint(event.pos):
                    self.turn = index
                    return True
        return False

    def label(self, screen, text, position, font=None, color="white"):
        screen.blit((font or self.font).render(text, True, color), position)

    def button(self, screen, rect, text, color=(38, 66, 145)):
        pygame.draw.rect(screen, color, rect, border_radius=7)
        pygame.draw.rect(screen, (123, 154, 231), rect, width=1, border_radius=7)
        label = self.font.render(text, True, "white")
        screen.blit(label, label.get_rect(center=rect.center))

    def draw(self, screen, game):
        if self.setup_open:
            overlay = pygame.Surface(self.dims, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 185))
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, (15, 25, 63), self.panel, border_radius=14)
            pygame.draw.rect(screen, (123, 154, 231), self.panel, width=2, border_radius=14)
            x, y = self.panel.topleft
            self.label(screen, "Who's playing?", (x + 50, y + 24), self.title_font)
            self.label(screen, "Up to 6 players or teams on this laptop.", (x + 50, y + 77))
            for index, rect in enumerate(self.fields):
                self.label(screen, f"Player {index + 1}", (x + 50, rect.y + 5))
                pygame.draw.rect(screen, (36, 48, 85), rect, border_radius=5)
                border = (255, 215, 80) if index == self.focus else (100, 118, 165)
                pygame.draw.rect(screen, border, rect, width=2, border_radius=5)
                if index == self.focus and self.select_all and self.names[index]:
                    pygame.draw.rect(screen, (55, 89, 169), rect.inflate(-8, -8), border_radius=3)
                self.label(screen, self.names[index], (rect.x + 10, rect.y + 5))
            self.label(screen, self.error or "Leave extra names blank. Tab moves to the next field.", (x + 50, y + 430), self.small_font)
            self.button(screen, self.start_button, "Start game", (30, 100, 66))
            self.button(screen, self.solo_button, "Play solo")
            self.label(screen, "Each clue goes to the next player. Judge after revealing.", (x + 50, y + 536), self.small_font)
            self.label(screen, "Daily Doubles and Final Jeopardy use entered wagers.", (x + 50, y + 562), self.small_font)
            return
        if self.finished:
            screen.fill((15, 25, 63))
            self.label(screen, "Game complete", (50, 40), self.title_font)
            if self.enabled:
                high_score = max(self.scores)
                winners = [name for name, score in zip(self.names, self.scores) if score == high_score]
                heading = "Winner" if len(winners) == 1 else "Tie"
                for index, text in enumerate([heading] + winners):
                    self.label(screen, text, (50, 100 + index * 36), color=(255, 215, 80))
                for index, (name, score) in enumerate(sorted(zip(self.names, self.scores), key=lambda pair: pair[1], reverse=True)):
                    self.label(screen, f"{name}    ${score:,}", (self.dims[0] // 2, 110 + index * 52))
            self.button(screen, self.again_button, "Play again")
            return
        value = game._activeValue
        text = f"Solo practice · Score ${self.scores[0]:,}" if self.solo else f"Turn: {self.names[self.turn]}"
        if not game.isBoardVisible():
            label = "Wager" if game._activeIsDailyDouble or game._final_wagers else "Clue value"
            text += f"    |    {label} ${value:,}"
        self.label(screen, text, (16, 9), self.small_font, (255, 225, 130))
        if game.progress_error or game.checkpoint_error:
            self.label(screen, game.progress_error or game.checkpoint_error, (16, 48), self.small_font, (255, 160, 140))
        if game.isBoardVisible() and self.enabled:
            for index, rect in enumerate(self.scoreboard_rects()):
                selected = index == self.turn
                pygame.draw.rect(screen, (38, 66, 145) if selected else (15, 25, 63), rect, border_radius=7)
                pygame.draw.rect(screen, (255, 215, 80) if selected else (100, 118, 165), rect, width=2, border_radius=7)
                name = self.names[index]
                while self.small_font.size(name)[0] > rect.width - 16:
                    name = name[:-2] + "…"
                self.label(screen, name, (rect.x + 8, rect.y + 8), self.small_font)
                self.label(screen, f"${self.scores[index]:,}", (rect.x + 8, rect.y + 34))
            self.label(screen, "Click a player to change whose turn it is.", (20, self.dims[1] - 36), self.small_font)
        elif game._answerCard is not None:
            labels = (f"Correct +${value:,}  [C]", f"Incorrect −${value:,}  [W]", "Skip / no score  [S]")
            for rect, text, color in zip(self.score_buttons, labels, ((30, 100, 66), (140, 43, 50), (38, 66, 145))):
                self.button(screen, rect, text, color)
