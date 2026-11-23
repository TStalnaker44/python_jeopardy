import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import pygame
import jeopardyGame as app
from utils.jeopardy_gui import JeopardyGameGUI, GameRound
from utils.localplayers import LocalPlayers
from utils.progress import ProgressStore
from utils.gamelibrary import GameLibrary
from tests.fixtures import question_file


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1200, 800))
        app.initializeManagers()
        app.USER_INTERFACE.setResourcePath("utils/menuButtons.csv")
        self.directory = tempfile.TemporaryDirectory()
        self.folder = Path(self.directory.name)
        self.path = question_file(self.folder)
        self.db = ProgressStore(self.folder / "progress.sqlite3")
        players = LocalPlayers((1200, 800))
        players.names = ["Ada", "Linus", "", "", "", ""]
        self.game = JeopardyGameGUI(str(self.path.with_suffix("")), 30, (1200, 800), players, self.db)
        players.start()
        self.game.save_checkpoint(True)

    def tearDown(self):
        self.db.close()
        self.directory.cleanup()
        pygame.quit()

    def reload(self):
        self.game = JeopardyGameGUI.from_checkpoint(self.db.load_checkpoint(self.game.game_id), (1200, 800), self.db)

    def open_clue(self):
        self.game._dailyDoubles = []
        position = self.game._cats[0].getButtonByPosition(0).getCollideRect().center
        with patch("pygame.mouse.get_pos", return_value=position):
            self.game.handleEvent(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))

    def wager(self, amount):
        self.game.wager.value = str(amount)
        self.game.handleEvent(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    def test_closed_game_restores_board_scores_turn_and_timer(self):
        run = self.game.session_id
        self.open_clue()
        self.game.multiplayer.scores = [600, 400]
        self.game.update(7.5)
        self.assertTrue(self.game.save_checkpoint(True))
        self.db.close()
        self.db = ProgressStore(self.folder / "progress.sqlite3")
        self.reload()
        self.assertEqual(self.game.session_id, run)
        self.assertEqual(self.game.multiplayer.scores, [600, 400])
        self.assertEqual(self.game._timer._timer, 22.5)
        self.assertIsNotNone(self.game._questionCard)
        self.assertEqual(self.game._cats[0].getButtonByPosition(0)._text, "")
        self.assertEqual(self.db.summary(self.game.game_id)["played"], 1)

    def test_grading_and_checkpoint_commit_or_rollback_together(self):
        self.open_clue()
        self.game.handleNextSlide()
        self.game.save_checkpoint(True)
        self.db.connection.execute("CREATE TRIGGER fail_save BEFORE UPDATE ON saved_games BEGIN SELECT RAISE(ABORT,'test'); END")
        self.game.resolveAnswer("correct")
        self.assertEqual(self.game.multiplayer.scores, [0, 0])
        self.assertIsNotNone(self.game._answerCard)
        self.assertEqual(self.db.summary(self.game.game_id)["correct"], 0)
        self.db.connection.execute("DROP TRIGGER fail_save")
        self.game.resolveAnswer("correct")
        self.reload()
        self.assertEqual(self.game.multiplayer.scores, [200, 0])
        self.assertEqual(self.game._questionCounter, 1)
        self.assertEqual(self.game.multiplayer.turn, 1)
        self.assertIsNone(self.game._answerCard)

    def test_final_restores_partial_wagers_and_partial_judging(self):
        self.game.multiplayer.scores = [3000, 1500]
        self.game.multiplayer.turn = 1
        self.game._gameRound = GameRound.DoubleJeopardy
        self.game._questionCounter = 30
        self.game.updateRounds()
        self.game.handleNextSlide()
        self.wager(1200)
        self.game.wager.value = "700"
        self.game.save_checkpoint(True)
        self.reload()
        self.assertEqual(self.game.wager.index, 1)
        self.assertEqual(self.game.wager.amounts, [1200])
        self.assertEqual(self.game.wager.value, "700")
        self.wager(700)
        self.game.handleNextSlide()
        self.game.resolveAnswer("incorrect")
        self.reload()
        self.assertEqual(self.game.multiplayer.scores, [3000, 800])
        self.assertEqual(self.game._activeValue, 1200)
        self.game.resolveAnswer("correct")
        self.assertEqual(self.game.multiplayer.scores, [4200, 800])
        self.assertIsNone(self.db.load_checkpoint(self.game.game_id))
        self.assertEqual(self.db.summary(self.game.game_id)["completed"], 1)

    def test_daily_double_restores_unsubmitted_wager(self):
        self.game._dailyDoubles = [(GameRound.JeopardyRound, 0, 0)]
        position = self.game._cats[0].getButtonByPosition(0).getCollideRect().center
        with patch("pygame.mouse.get_pos", return_value=position):
            self.game.handleEvent(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))
        self.game.wager.value = "725"
        self.game.save_checkpoint(True)
        self.reload()
        self.assertEqual(self.game.wager.value, "725")
        self.assertIsNotNone(self.game._dailyDouble)

    def test_restart_requires_roster_or_solo_and_preserves_history(self):
        self.open_clue()
        self.game.handleNextSlide()
        self.game.resolveAnswer("incorrect")
        state = self.db.load_checkpoint(self.game.game_id)
        game = JeopardyGameGUI.from_checkpoint(state, (1200, 800), self.db, restart=True)
        self.assertTrue(game.multiplayer.setup_open)
        self.assertIsNone(game.session_id)
        self.assertEqual(self.db.summary(game.game_id)["played"], 1)
        game.multiplayer.start(solo=True)
        self.assertTrue(game.save_checkpoint(True))
        self.assertEqual(game.multiplayer.names, ["Solo"])
        self.assertEqual(game.multiplayer.scores, [0])
        self.assertNotEqual(game.session_id, self.game.session_id)
        self.assertEqual(self.db.summary(game.game_id)["played"], 2)
        self.assertEqual(self.db.summary(game.game_id)["incorrect"], 1)

    def test_stale_instance_cannot_overwrite_newer_save(self):
        stale = JeopardyGameGUI.from_checkpoint(self.db.load_checkpoint(self.game.game_id), (1200, 800), self.db)
        self.assertTrue(self.game.save_checkpoint(True))
        self.assertFalse(stale.save_checkpoint(True))

    def test_snapshot_contains_questions_without_source_file(self):
        state = self.db.load_checkpoint(self.game.game_id)
        state["source"] = "missing-file"
        game = JeopardyGameGUI.from_checkpoint(state, (1200, 800), self.db)
        self.assertEqual(json.dumps(game._game.snapshot()), json.dumps(self.game._game.snapshot()))

    def test_library_deletion_renumbers_and_retains_history(self):
        second = self.folder / "second.csv"
        second.write_bytes(self.path.read_bytes().replace(b"Category 0", b"Another category"))
        library = GameLibrary((1200, 800), str(self.path), self.folder / "library.json",
                              directory=self.folder, builtin=self.path, progress=self.db)
        self.assertEqual(len(library.entries), 2)
        entry = next(e for e in library.entries if e["game_id"] == self.game.game_id)
        self.assertIn(entry["game_id"], library.saved)
        library.delete_game(entry)
        self.assertEqual(len(library.entries), 1)
        self.assertTrue(library.entries[0]["title"].startswith("1 · "))
        self.assertEqual(self.db.summary(self.game.game_id)["played"], 1)
        library.add_csv(self.path)
        self.assertEqual(len(library.entries), 2)
        self.assertIsNotNone(self.db.load_checkpoint(self.game.game_id))

    def test_main_loop_can_open_and_close_library(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": str(self.folder)}), patch("pygame.event.get", return_value=[pygame.event.Event(pygame.QUIT)]):
            app.main(str(self.path), 30, False, "(1200,800)", show_library=True)
