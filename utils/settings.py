"""In-game audio and display settings."""

import json
import os
from pathlib import Path

import pygame

from polybius.managers import SOUNDS


class SettingsMenu:
    def __init__(self, dims, fullscreen=None):
        self.path = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "PythonJeopardy" / "settings.json"
        saved = self.load()
        self.volume = saved.get("volume", 50)
        if type(self.volume) is not int or not 0 <= self.volume <= 100:
            self.volume = 50
        self.fullscreen = True
        if fullscreen is not None:
            self.fullscreen = fullscreen
        self.open = False
        self.dragging = False
        self.message = ""
        self.font = pygame.font.SysFont("segoeui", 24)
        self.title_font = pygame.font.SysFont("segoeui", 34, bold=True)
        self.button = pygame.Rect(dims[0] - 164, 8, 152, 34)
        self.panel = pygame.Rect(0, 0, 540, 370)
        self.panel.center = (dims[0] // 2, dims[1] // 2)
        x, y = self.panel.topleft
        self.slider = pygame.Rect(x + 40, y + 132, 460, 24)
        self.fullscreen_button = pygame.Rect(x + 40, y + 190, 460, 48)
        self.done_button = pygame.Rect(x + 340, y + 292, 160, 46)
        SOUNDS.setVolume(self.volume / 100)

    def load(self):
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            return saved if isinstance(saved, dict) else {}
        except (OSError, ValueError):
            return {}

    def save(self):
        temporary = self.path.with_suffix(".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(json.dumps({"volume": self.volume, "fullscreen": self.fullscreen}), encoding="utf-8")
            temporary.replace(self.path)
        except OSError:
            self.message = "Could not save settings. Changes apply this session."

    def set_volume(self, x):
        self.volume = max(0, min(100, round((x - self.slider.left) * 100 / self.slider.width)))
        SOUNDS.setVolume(self.volume / 100)
        SOUNDS.unmute()

    def handle_event(self, event):
        """Return a display action. The main loop owns the display surface."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.open = not self.open
            self.dragging = False
            self.save()
            return None
        if not self.open:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.button.collidepoint(event.pos):
                self.open = True
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.open = False
                self.dragging = False
                self.save()
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.slider.inflate(20, 20).collidepoint(event.pos):
                self.dragging = True
                self.set_volume(event.pos[0])
            elif self.fullscreen_button.collidepoint(event.pos):
                return "toggle_fullscreen"
            elif self.done_button.collidepoint(event.pos):
                self.open = False
                self.dragging = False
                self.save()
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_volume(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self.set_volume(event.pos[0])
            self.dragging = False
            self.save()
        return None

    def draw_button(self, screen, rect, text):
        pygame.draw.rect(screen, (38, 66, 145), rect, border_radius=7)
        pygame.draw.rect(screen, (123, 154, 231), rect, width=1, border_radius=7)
        label = self.font.render(text, True, "white")
        screen.blit(label, label.get_rect(center=rect.center))

    def draw(self, screen):
        self.draw_button(screen, self.button, "Settings  F1")
        if not self.open:
            return
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (15, 25, 63), self.panel, border_radius=14)
        pygame.draw.rect(screen, (123, 154, 231), self.panel, width=2, border_radius=14)
        x, y = self.panel.topleft
        screen.blit(self.title_font.render("Settings", True, "white"), (x + 40, y + 24))
        volume_text = f"Volume   {self.volume}%"
        if SOUNDS._mute:
            volume_text += " (muted)"
        screen.blit(self.font.render(volume_text, True, "white"), (x + 40, y + 88))
        track = pygame.Rect(self.slider.left, self.slider.centery - 4, self.slider.width, 8)
        pygame.draw.rect(screen, (72, 84, 121), track, border_radius=4)
        knob_x = self.slider.left + round(self.slider.width * self.volume / 100)
        pygame.draw.rect(screen, (235, 192, 68), (track.left, track.top, knob_x - track.left, track.height))
        pygame.draw.circle(screen, (255, 222, 114), (knob_x, self.slider.centery), 11)
        mode = "On" if self.fullscreen else "Off"
        self.draw_button(screen, self.fullscreen_button, f"Maximized window   {mode}   (F11)")
        hint_font = pygame.font.SysFont("segoeui", 17)
        hint = self.message or "Game timer pauses while settings are open."
        screen.blit(hint_font.render(hint, True, (199, 211, 243)), (x + 40, y + 252))
        self.draw_button(screen, self.done_button, "Done")
