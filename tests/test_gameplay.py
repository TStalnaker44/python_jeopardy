import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import tempfile
import unittest
from unittest.mock import patch
import pygame
import jeopardyGame as app
from utils.jeopardy_gui import JeopardyGameGUI, GameRound
from utils.localplayers import LocalPlayers
from tests.fixtures import question_file


class GameplayTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1200, 800))
        app.initializeManagers()
        app.USER_INTERFACE.setResourcePath("utils/menuButtons.csv")
        self.directory = tempfile.TemporaryDirectory()
        self.path = question_file(self.directory.name)
        self.players = LocalPlayers((1200, 800))
        self.players.names = ["Ada", "Linus", "", "", "", ""]
        self.game = JeopardyGameGUI(str(self.path.with_suffix("")), 30, (1200, 800), self.players)
        self.players.start()

    def tearDown(self):
        self.directory.cleanup()
        pygame.quit()

    def open_clue(self, column=0, row=0):
        position = self.game._cats[column].getButtonByPosition(row).getCollideRect().center
        with patch("pygame.mouse.get_pos", return_value=position):
            self.game.handleEvent(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))

    def wager(self, value):
        self.game.wager.value = str(value)
        self.game.handleEvent(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    def test_daily_double_uses_entered_wager(self):
        self.players.scores = [1500, 600]
        self.game._dailyDoubles = [(GameRound.JeopardyRound, 0, 0)]
        self.open_clue()
        self.wager(1501)
        self.assertIsNotNone(self.game.wager)
        self.wager(725)
        self.game.handleNextSlide()
        self.game.resolveAnswer("correct")
        self.assertEqual(self.players.scores, [2225, 600])
        self.assertEqual(self.players.turn, 1)

    def test_final_uses_each_players_wager(self):
        self.players.scores = [3000, 1500]
        self.players.turn = 1
        self.game._gameRound = GameRound.DoubleJeopardy
        self.game._questionCounter = 30
        self.game.updateRounds()
        self.game.handleNextSlide()
        self.wager(1200)
        self.wager(700)
        self.game.handleNextSlide()
        self.game.resolveAnswer("incorrect")
        self.assertEqual(self.players.scores, [3000, 800])
        self.game.resolveAnswer("correct")
        self.assertEqual(self.players.scores, [4200, 800])
        self.assertTrue(self.players.finished)

    def test_ordinary_question_scores_once(self):
        self.game._dailyDoubles = []
        self.open_clue()
        self.game.handleNextSlide()
        self.game.resolveAnswer("correct")
        self.game.resolveAnswer("correct")
        self.assertEqual(self.players.scores, [200, 0])
        self.assertEqual(self.game._questionCounter, 1)
