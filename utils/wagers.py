"""Collect and validate wagers before a special clue is revealed."""

import textwrap

import pygame


class WagerMenu:
    def __init__(self, dims, title, category, players, initial=0):
        self.dims = dims
        self.title = title
        self.category = category
        self.players = players
        self.index = 0
        self.amounts = []
        self.value = str(max(players[0][2], min(players[0][3], initial)))
        self.select_all = True
        self.error = ""
        self.font = pygame.font.SysFont("segoeui", 26)
        self.small_font = pygame.font.SysFont("segoeui", 20)
        self.title_font = pygame.font.SysFont("segoeui", 38, bold=True)
        self.panel = pygame.Rect(0, 0, 700, 500)
        self.panel.center = (dims[0] // 2, dims[1] // 2)
        x, y = self.panel.topleft
        self.field = pygame.Rect(x + 45, y + 266, 420, 58)
        self.max_button = pygame.Rect(x + 485, y + 266, 170, 58)
        self.confirm_button = pygame.Rect(x + 45, y + 402, 610, 52)
        pygame.key.start_text_input()

    def confirm(self):
        minimum, maximum = self.players[self.index][2:]
        try:
            amount = int(self.value)
        except ValueError:
            self.error = "Enter a whole-number wager."
            return None
        if not minimum <= amount <= maximum:
            self.error = f"Enter an amount from ${minimum:,} to ${maximum:,}."
            return None
        self.amounts.append(amount)
        self.index += 1
        if self.index == len(self.players):
            pygame.key.stop_text_input()
            return self.amounts
        self.value = str(self.players[self.index][2])
        self.select_all = True
        self.error = ""
        return None

    def handle_event(self, event):
        if event.type == pygame.TEXTINPUT:
            text = "" if self.select_all else self.value
            self.value = (text + event.text)[:10]
            self.select_all = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.value = "" if self.select_all else self.value[:-1]
                self.select_all = False
            elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                self.select_all = True
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.confirm()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.field.collidepoint(event.pos):
                self.select_all = True
            elif self.max_button.collidepoint(event.pos):
                self.value = str(self.players[self.index][3])
                self.select_all = True
            elif self.confirm_button.collidepoint(event.pos):
                return self.confirm()
        return None

    def draw(self, screen):
        overlay = pygame.Surface(self.dims, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (15, 25, 63), self.panel, border_radius=14)
        pygame.draw.rect(screen, (255, 215, 80), self.panel, width=2, border_radius=14)
        x, y = self.panel.topleft
        name, score, minimum, maximum = self.players[self.index]
        screen.blit(self.title_font.render(self.title, True, (255, 215, 80)), (x + 45, y + 24))
        for index, line in enumerate(textwrap.wrap(self.category, 45)[:2]):
            screen.blit(self.font.render(line, True, "white"), (x + 45, y + 85 + 31 * index))
        screen.blit(self.font.render(f"{name}    Score ${score:,}", True, "white"), (x + 45, y + 166))
        screen.blit(self.small_font.render(f"Wager ${minimum:,} to ${maximum:,}", True, (199, 211, 243)), (x + 45, y + 216))
        pygame.draw.rect(screen, (55, 78, 140) if self.select_all else (30, 42, 78), self.field, border_radius=6)
        pygame.draw.rect(screen, (255, 215, 80), self.field, width=2, border_radius=6)
        screen.blit(self.font.render("$ " + self.value, True, "white"), (self.field.x + 15, self.field.y + 13))
        for rect, label in ((self.max_button, "Maximum"), (self.confirm_button, "Lock wager" if self.index < len(self.players) - 1 else "Lock wager and reveal clue")):
            pygame.draw.rect(screen, (38, 66, 145), rect, border_radius=6)
            graphic = self.font.render(label, True, "white")
            screen.blit(graphic, graphic.get_rect(center=rect.center))
        hint = self.error or ("Zero or negative score: continue with a $0 practice wager." if maximum == 0 else "Enter your wager before the clue is revealed.")
        screen.blit(self.small_font.render(hint, True, (255, 190, 120)), (x + 45, y + 347))
        if len(self.players) > 1:
            screen.blit(self.small_font.render(f"Player {self.index + 1} of {len(self.players)}", True, (199, 211, 243)), (x + 45, y + 464))
