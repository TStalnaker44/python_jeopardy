"""Exercise clue selection on the original GUI, without later feature branches."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import tempfile
import unittest
from unittest.mock import patch
import pygame
from utils.jeopardy_gui import JeopardyGameGUI, GameRound, formatCategoryText
from utils.uiManager import USER_INTERFACE
from tests.fixtures import question_file


class CsvBoardTests(unittest.TestCase):
    def test_all_tiles_and_final_work_in_fixed_and_random_games(self):
        pygame.init()
        try:
            screen = pygame.display.set_mode((1200, 800))
            # Upstream's singleton appends controls on reload: initialize once.
            USER_INTERFACE.setResourcePath("utils/menuButtons.csv")
            for fixed in (True, False):
                with self.subTest(fixed=fixed), tempfile.TemporaryDirectory() as directory:
                    path = question_file(directory, fixed=fixed)
                    game = JeopardyGameGUI(str(path.with_suffix("")), 30, (1200, 800))
                    for round_index in range(2):
                        categories = game._game.getJeopardyRound() if round_index == 0 else game._game.getDoubleJeopardyRound()
                        for column in range(6):
                            for row in range(5):
                                button = game._cats[column].getButtonByPosition(row)
                                if fixed:
                                    self.assertEqual(button._text, f"${(row + 1) * 200:,}")
                                position = button.getCollideRect().center
                                with patch("pygame.mouse.get_pos", return_value=position):
                                    game.handleEvent(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))
                                expected = game._game.getQuestionsByCategory(categories[column])[row]
                                self.assertEqual(game._question, formatCategoryText(expected[0], 30))
                                self.assertIsNotNone(game._questionCard)
                                self.assertEqual(button._text, "")
                                if game._dailyDouble is not None:
                                    game.handleNextSlide()
                                game.handleNextSlide()
                                self.assertIsNotNone(game._answerCard)
                                game.draw(screen)
                                game.handleNextSlide()
                        game.updateRounds()
                    self.assertEqual(game._gameRound, GameRound.FinalJeopardy)
                    game.handleNextSlide()
                    self.assertIsNotNone(game._questionCard)
                    game.handleNextSlide()
                    self.assertIsNotNone(game._answerCard)
        finally:
            pygame.quit()
