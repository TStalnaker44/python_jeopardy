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

    def test_interleaved_categories_follow_their_csv_round(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream))
            # Deliberately place Double Jeopardy first, then interleave both rounds.
            reordered = [rows[0]]
            for category in range(6):
                reordered.extend(rows[1 + (category + 6) * 5:1 + (category + 7) * 5])
                reordered.extend(rows[1 + category * 5:1 + (category + 1) * 5])
            reordered.append(rows[-1])
            with path.open("w", encoding="utf-8", newline="") as stream:
                csv.writer(stream).writerows(reordered)
            game = JeopardyGame(str(path.with_suffix("")))
            self.assertEqual(game.getJeopardyRound(), [f"Category {i}" for i in range(6)])
            self.assertEqual(game.getDoubleJeopardyRound(), [f"Category {i}" for i in range(6, 12)])

    def test_fixed_category_cannot_span_rounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            text = path.read_text(encoding="utf-8-sig")
            path.write_text(text.replace("Jeopardy!,Category 0,200", "Double Jeopardy!,Category 0,200", 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "multiple regular rounds"):
                JeopardyQuestions(str(path.with_suffix("")))

    def test_fixed_game_requires_six_categories_per_round(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            text = path.read_text(encoding="utf-8-sig")
            path.write_text(text.replace("Double Jeopardy!,Category 6", "Jeopardy!,Category 6"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "six categories"):
                JeopardyQuestions(str(path.with_suffix("")))

    def test_fixed_game_rejects_unknown_round(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            path.write_text(path.read_text(encoding="utf-8-sig").replace("Double Jeopardy!", "Typo round"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid regular round"):
                JeopardyQuestions(str(path.with_suffix("")))

    def test_duplicate_clues_do_not_count_as_five_distinct_clues(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory, fixed=False)
            text = path.read_text(encoding="utf-8-sig").replace("Question 0-4,Answer 0-4", "Question 0-0,Answer 0-0")
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "12 categories"):
                JeopardyQuestions(str(path.with_suffix("")))

    def test_missing_final_and_malformed_rows_fail_fast(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            text = path.read_text(encoding="utf-8-sig")
            path.write_text("\n".join(text.splitlines()[:-1]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Final Jeopardy"):
                JeopardyQuestions(str(path.with_suffix("")))
            path.write_text("not,a,complete,row", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "seven columns"):
                JeopardyQuestions(str(path.with_suffix("")))

    def test_windows_encoding_fallback_clears_partial_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = question_file(directory)
            text = path.read_text(encoding="utf-8-sig").replace("Final answer", "Café answer")
            path.write_bytes(text.encode("cp1252"))
            game = JeopardyGame(str(path.with_suffix("")))
            self.assertEqual(game.getFinalJeopardyAnswer(), "Café answer")
            self.assertEqual(len(game.getQuestionsByCategory("Category 0")), 5)
