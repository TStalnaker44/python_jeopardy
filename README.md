# Python Jeopardy

A version of the classic Jeopardy game show programmed in Python and Pygame.
The game includes questions from previous Jeopardy games and supports custom CSV games.
This version adds a game library, local players, scoring, wagers, study history,
and saved-game recovery.

## Installation and launch

Install Python and the runtime dependency, then launch from the repository root:

```bash
python -m pip install -r requirements.txt
python launcher.py
```

The library opens first. Choose a question set, then enter up to six player or team
names or select **Play solo**. The game starts in a maximized normal window.
Windows uses a dark native title bar; other platforms keep their native caption.

## Library and study history

- **Add CSV** imports a question file. The native file picker requires Tkinter,
  which is included in standard Windows Python installations.
- The library also discovers CSV files in `questions/`.
- Select a game to see its play count, completion count, and correct, incorrect,
  and skipped totals.
- **Review answers** shows recorded questions, answers, player names, and result
  counts, with filters and scrolling.
- **Delete game** removes an entry from the library. Its CSV and study history
  remain available. Re-importing the file restores the entry and history.
- Visible game numbers update when an entry is removed or restored.

Game identity is based on the CSV contents. Editing those contents creates a new
history identity. A large question bank randomly selects 60 regular clues and a
Final Jeopardy clue per game. A complete fixed-layout game uses all 60 regular
clues and its Final clue.

## Players, scoring, and wagers

Play solo or with up to six local players or teams on one computer. After revealing
an answer, mark it **Correct**, **Incorrect**, or **Skip**. Correct and incorrect
results add or subtract the clue value; skipping leaves the score unchanged.
Turns advance after each regular clue. Click a player on the board to change turns.

Daily Doubles collect a wager before the clue is shown. The minimum is 5 and the
maximum is the greater of the player's score and the highest clue value on the
current board. Final Jeopardy collects a separate wager for every player before
revealing the question. Each player's own wager is used when their answer is
judged. Final wagers range from zero to the player's nonnegative balance;
players with zero or negative scores may continue with a zero wager.

## Save, resume, and restart

An active game saves automatically, including its selected questions, used tiles,
round, players, scores, turn, timer, clue stage, and wager entry. Select the game in
the library after reopening the app:

- **Resume game** continues the existing run without increasing the play count.
- **Restart game** resets the same selected board and opens player setup again.
  Choose player names or Solo before a new play is counted. Existing answer history
  is retained.

Completed games leave the resume list and retain their results in study history.
Save/result transactions prevent partially recorded grading, and stale game
instances cannot overwrite a newer saved state. If saving fails, the game displays
an error and allows a retry.

Settings, library selection, and the SQLite progress database are stored under
`%LOCALAPPDATA%/PythonJeopardy` on Windows. On other platforms the app uses
`$XDG_DATA_HOME/PythonJeopardy`, falling back to `~/.local/share/PythonJeopardy`.
These user files are separate from the source and packaged resources.

## Controls

| Control | Action |
| --- | --- |
| Escape / window close | Exit and save the active game; Escape closes an open menu first |
| M | Toggle mute |
| F1 / Settings | Adjust volume and maximized-window mode |
| F2 / Library | Open the library and pause the current clue |
| F11 | Switch between maximized and resizable windows |
| Click a clue | Reveal that clue, or enter its Daily Double wager |
| Space | Reveal the answer or advance; advancing an unjudged answer records a skip |
| C / W / S | Correct / incorrect / skip after revealing an answer |
| Enter | Confirm a wager or start/resume the selected library game |

The timer pauses during player setup, wager entry, settings, and the library.
Long question and answer text automatically shrinks to fit the clue card.

## Custom question CSVs

CSV files have seven columns:

```text
Show Number,Air Date,Round,Category,Value,Question,Answer
```

Use `Jeopardy!`, `Double Jeopardy!`, or `Final Jeopardy!` for the round. The game
needs at least 12 categories containing five different regular clues each, plus
at least one Final Jeopardy clue. A header row is optional. UTF-8 (including BOM)
and Windows-1252 files are supported. Empty required fields, malformed rows, and
insufficient categories produce validation messages.

For the default randomized layout, `x` may be used for Show Number, Air Date,
and Value. Place the CSV in `questions/` or import it through the library.

To preserve a complete game's category order, clue order, and point values, add a
sidecar with the same stem. For `my_game.csv`, create `my_game.layout.json`:

```json
{
  "title": "My custom game",
  "preserve_layout": true
}
```

A preserved layout requires exactly 12 categories with five different clues each
and five distinct positive numeric values in each category. The first six
categories form Jeopardy and the next six form Double Jeopardy. The displayed
point values come from the CSV.

## Command-line options

```bash
python launcher.py --questions my_game --timer 30 --dims "(1200,800)"
python launcher.py --help
python launcher.py --controls
```

`--questions` accepts a CSV stem or path, with or without `.csv`, and preselects
that game in the library. `--timer` sets regular-clue answer time in seconds.
`--fullscreen` requests the maximized window mode. The default logical board
size is 1200 by 800; Pygame scales it with the window.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests use synthetic question files and SDL's dummy video/audio drivers.
They isolate their settings and databases in temporary directories and do not
require a personal question bank or a visible desktop. CI runs on Linux and Windows.

## Build a desktop executable

```bash
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --noconfirm Jeopardy.spec
```

On Windows the result is `dist/Jeopardy.exe`. Build on the target operating system.
The launcher locates bundled resources when started from another directory.
To keep imported CSVs outside a one-file bundle, place them in a `questions/`
folder beside the executable or use **Add CSV**. A Windows desktop shortcut can
point to the executable and use its embedded Jeopardy icon.

## License and credits

Original game copyright (c) 2021 TStalnaker44. Desktop study features contributed
by Carter Howell. Distributed under the existing [MIT license](LICENSE).
