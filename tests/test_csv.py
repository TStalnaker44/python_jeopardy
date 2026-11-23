import csv
import tempfile
import unittest
from utils.jeopardy import JeopardyGame, JeopardyQuestions
from tests.fixtures import question_file


class CsvTests(unittest.TestCase):
    def test_fixed_order_and_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            game = JeopardyGame(str(path.with_suffix("")))
            self.assertEqual(game.getJeopardyRound(), [f"Category {i}" for i in range(6)])
            self.assertEqual(game.getDoubleJeopardyRound(), [f"Category {i}" for i in range(6, 12)])
            self.assertEqual(game.getQuestionsByCategory("Category 0")[0], ("Question 0-0", "Answer 0-0"))
            self.assertEqual(game.getQuestionValue("Category 6", 4), 1000)

    def test_random_games_have_distinct_categories_and_clues(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory, fixed=False)
            game = JeopardyGame(str(path.with_suffix("")))
            categories = game.getJeopardyRound() + game.getDoubleJeopardyRound()
            self.assertEqual(len(set(categories)), 12)
            for category in categories:
                self.assertEqual(len(set(game.getQuestionsByCategory(category))), 5)

    def test_invalid_input_fails_instead_of_looping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream))
            with path.open("w", encoding="utf-8", newline="") as stream:
                csv.writer(stream).writerows(rows[:5])
            with self.assertRaisesRegex(ValueError, "12 categories"):
                JeopardyQuestions(str(path.with_suffix("")))

    def test_rejects_invalid_fixed_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            path.write_text(path.read_text(encoding="utf-8-sig").replace(",200,", ",invalid,", 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "numeric point value"):
                JeopardyQuestions(str(path.with_suffix("")))
