"""Synthetic clues for tests; no user question banks are required."""
import csv
import json
from pathlib import Path


def question_file(directory, fixed=True):
    path = Path(directory) / "synthetic.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Show Number", "Air Date", "Round", "Category", "Value", "Question", "Answer"])
        for category in range(12):
            for row in range(5):
                writer.writerow(["x", "x", "Jeopardy!" if category < 6 else "Double Jeopardy!",
                                 f"Category {category}", (row + 1) * 200,
                                 f"Question {category}-{row}", f"Answer {category}-{row}"])
        writer.writerow(["x", "x", "Final Jeopardy!", "Final category", "x", "Final question", "Final answer"])
    if fixed:
        path.with_suffix(".layout.json").write_text(json.dumps({"title": "Synthetic game", "preserve_layout": True}), encoding="utf-8")
    return path
