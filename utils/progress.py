"""Transactional, persistent play counts and question results."""

import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import uuid4


def question_key(category, question, answer):
    return hashlib.sha256("\0".join((category, question, answer)).encode("utf-8")).hexdigest()


class ProgressStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, timeout=5)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA journal_mode=WAL")
        with self.connection:
            self.connection.executescript("""
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, total_questions INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
                    started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    completed_at TEXT, players TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS results (
                    run_id TEXT NOT NULL REFERENCES runs(id), question_id TEXT NOT NULL,
                    respondent TEXT NOT NULL, player_name TEXT NOT NULL,
                    category TEXT NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL,
                    result TEXT NOT NULL CHECK(result IN ('correct','incorrect','skip')),
                    recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    PRIMARY KEY (run_id, question_id, respondent)
                );
                CREATE TABLE IF NOT EXISTS saved_games (
                    game_id TEXT PRIMARY KEY REFERENCES games(id),
                    run_id TEXT NOT NULL REFERENCES runs(id), state TEXT NOT NULL,
                    revision INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS runs_by_game ON runs(game_id);
                CREATE TABLE IF NOT EXISTS hidden_library_games (
                    library_key TEXT PRIMARY KEY
                );
            """)

    def hidden_games(self):
        return {row["library_key"] for row in self.connection.execute("SELECT library_key FROM hidden_library_games")}

    def hide_game(self, library_key):
        with self.connection:
            self.connection.execute("INSERT INTO hidden_library_games(library_key) VALUES (?) ON CONFLICT(library_key) DO NOTHING", (library_key,))

    def restore_game(self, library_key):
        with self.connection:
            self.connection.execute("DELETE FROM hidden_library_games WHERE library_key=?", (library_key,))

    def start_game(self, game_id, title, total_questions, players):
        run_id = str(uuid4())
        with self.connection:
            self.connection.execute("""
                INSERT INTO games(id,title,total_questions) VALUES (?,?,?)
                ON CONFLICT(id) DO UPDATE SET title=excluded.title, total_questions=excluded.total_questions
            """, (game_id, title, total_questions))
            self.connection.execute("INSERT INTO runs(id,game_id,players) VALUES (?,?,?)", (run_id, game_id, json.dumps(players)))
        return run_id

    def record_answer(self, run_id, category, question, answer, respondent, player_name, result, complete=False, checkpoint=None):
        key = question_key(category, question, answer)
        with self.connection:
            self.connection.execute("""
                INSERT INTO results
                (run_id,question_id,respondent,player_name,category,question,answer,result)
                VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(run_id,question_id,respondent) DO NOTHING
            """, (run_id, key, respondent, player_name, category, question, answer, result))
            if complete:
                self.connection.execute("UPDATE runs SET completed_at=COALESCE(completed_at,strftime('%Y-%m-%dT%H:%M:%fZ','now')) WHERE id=?", (run_id,))
            saved = self.connection.execute("SELECT result FROM results WHERE run_id=? AND question_id=? AND respondent=?", (run_id, key, respondent)).fetchone()
            if checkpoint is not None:
                state = checkpoint(saved["result"])
                if state is not None:
                    self._write_checkpoint(state)
            if complete:
                self.connection.execute("DELETE FROM saved_games WHERE run_id=?", (run_id,))
        return saved["result"]

    def saved_games(self):
        return {row["game_id"]: row["run_id"] for row in self.connection.execute("SELECT game_id,run_id FROM saved_games")}

    def load_checkpoint(self, game_id):
        row = self.connection.execute("SELECT state,revision FROM saved_games WHERE game_id=?", (game_id,)).fetchone()
        if row is None:
            return None
        state = json.loads(row["state"])
        state["revision"] = row["revision"]
        return state

    def _write_checkpoint(self, state):
        game_id, run_id, revision = state["game_id"], state["session_id"], state["revision"]
        payload = json.dumps(state)
        if revision == 0:
            row = self.connection.execute("SELECT run_id FROM saved_games WHERE game_id=?", (game_id,)).fetchone()
            if row is not None and row["run_id"] == run_id:
                raise sqlite3.OperationalError("This game has a newer save.")
            self.connection.execute("INSERT INTO saved_games VALUES (?,?,?,1) ON CONFLICT(game_id) DO UPDATE SET run_id=excluded.run_id,state=excluded.state,revision=1", (game_id, run_id, payload))
        else:
            changed = self.connection.execute("UPDATE saved_games SET state=?,revision=revision+1 WHERE game_id=? AND run_id=? AND revision=?", (payload, game_id, run_id, revision))
            if changed.rowcount != 1:
                raise sqlite3.OperationalError("This game has a newer save.")

    def save_checkpoint(self, state):
        with self.connection:
            self._write_checkpoint(state)

    def summary(self, game_id):
        runs = self.connection.execute("SELECT COUNT(*) AS played, COUNT(completed_at) AS completed FROM runs WHERE game_id=?", (game_id,)).fetchone()
        answers = self.connection.execute("""
            SELECT COUNT(DISTINCT question_id) AS seen,
                COALESCE(SUM(result='correct'),0) AS correct,
                COALESCE(SUM(result='incorrect'),0) AS incorrect,
                COALESCE(SUM(result='skip'),0) AS skipped
            FROM results JOIN runs ON runs.id=results.run_id WHERE runs.game_id=?
        """, (game_id,)).fetchone()
        return dict(runs) | dict(answers)

    def review(self, game_id, result_filter="all"):
        condition = "" if result_filter == "all" else "HAVING SUM(results.result=?)>0"
        parameters = (game_id,) if result_filter == "all" else (game_id, result_filter)
        rows = self.connection.execute(f"""
            SELECT question_id, category, question, answer,
                SUM(result='correct') AS correct, SUM(result='incorrect') AS incorrect,
                SUM(result='skip') AS skipped, MAX(recorded_at) AS last_played,
                GROUP_CONCAT(DISTINCT player_name) AS players
            FROM results JOIN runs ON runs.id=results.run_id WHERE runs.game_id=?
            GROUP BY question_id {condition}
            ORDER BY last_played DESC, question_id
        """, parameters).fetchall()
        return [dict(row) for row in rows]

    def close(self):
        self.connection.close()
