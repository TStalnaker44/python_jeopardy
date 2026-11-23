# Contributing

Install `requirements.txt` and run `python -m unittest discover -s tests -v`
from the repository root before submitting a change. Tests use generated clues,
headless SDL drivers, and temporary user data. Keep runtime paths relative to the
checkout or executable, and preserve the existing MIT license.

Do not commit personal question banks, progress databases, local settings,
compiled executables, or build output. Use synthetic questions for regression tests.

## Desktop contribution branch sequence

The desktop features are split into the following cumulative branches. Each branch
includes the preceding branches; compare it to its predecessor to review one area.
The final branch is the upstream integration candidate.

1. `feature/csv-layout-validation` — CSV validation, preserved ordering and values.
2. `fix/fit-long-clue-text` — automatic clue/answer text fitting.
3. `feature/desktop-settings` — volume settings, window modes, icon and dark caption.
4. `feature/local-players-and-wagers` — players, solo mode, scoring and wagers.
5. `feature/library-progress-and-resume` — library, history, deletion and saved games.
6. `build/portable-desktop-package` — launcher, portable packaging, tests and documentation.

Each area has a separate commit so maintainers can review or extract changes while
the upstream pull request provides a complete working application.
