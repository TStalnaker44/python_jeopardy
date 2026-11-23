import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
import unittest
from utils.questioncard import QuestionCard


class QuestionTextTests(unittest.TestCase):
    def test_long_clues_shrink_and_render(self):
        pygame.init()
        try:
            short = QuestionCard("Short clue", (1200, 800))
            long = QuestionCard("\n".join(["A longer clue with multiple lines"] * 24), (1200, 800))
            short.draw(pygame.Surface((1200, 800)))
            long.draw(pygame.Surface((1200, 800)))
            self.assertLess(long._font.get_height(), short._font.get_height())
            long.draw(pygame.Surface((1200, 800)))
        finally:
            pygame.quit()

