"""Independent text-fitting regressions, runnable on upstream master plus this fix."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import unittest
from unittest.mock import patch
import pygame
from polybius.graphics import MultiLineTextBox
from utils.questioncard import QuestionCard


class QuestionTextTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1200, 800))

    def tearDown(self):
        pygame.quit()

    def assert_fits(self, card):
        text = MultiLineTextBox(card._question, (0, 0), card._font, card._fontColor)
        self.assertLessEqual(text.getWidth(), card._width - 80)
        self.assertLessEqual(text.getHeight(), card._height - 180)
        card.draw(pygame.Surface((1200, 800)))

    def test_short_clue_keeps_original_font(self):
        card = QuestionCard("Short clue", (1200, 800))
        original = pygame.font.SysFont("futura bold", 64)
        self.assertEqual(card._font.get_height(), original.get_height())
        self.assert_fits(card)

    def test_tall_answer_shrinks_to_fit(self):
        short = QuestionCard("Short clue", (1200, 800))
        answer = QuestionCard("\n".join(["A longer answer with multiple lines"] * 24), (1200, 800))
        self.assertLess(answer._font.get_height(), short._font.get_height())
        self.assert_fits(answer)

    def test_wide_clue_shrinks_to_fit(self):
        card = QuestionCard("Wide question text " * 8, (1200, 800))
        self.assert_fits(card)

    def test_original_board_still_opens_a_clue_and_answer(self):
        from utils.jeopardy_gui import JeopardyGameGUI
        from utils.uiManager import USER_INTERFACE
        USER_INTERFACE.setResourcePath("utils/menuButtons.csv")
        game = JeopardyGameGUI("JEOPARDY_CSV_REAL", 30, (1200, 800))
        game._dailyDoubles = []
        position = game._cats[0].getButtonByPosition(0).getCollideRect().center
        with patch("pygame.mouse.get_pos", return_value=position):
            game.handleEvent(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))
        self.assertIsNotNone(game._questionCard)
        game.handleNextSlide()
        self.assertIsNotNone(game._answerCard)
        game.handleNextSlide()
        self.assertEqual(game._questionCounter, 1)
