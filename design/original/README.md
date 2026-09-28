# The original design (before Tarik Base)

Kept on 2026-09-28, the day the app moved to Tarik Base (`design/deviations.md`).

- **Code:** git tag `design-original` (commit `78d49e3`, "Group Crosscheck priority actions"),
  the last commit with the original look: white canvas, black primary buttons, system sans for
  every heading, pill chips and tinted verdict badges, light only.
- **Rebuild it:** `git worktree add ../crosscheck-original design-original`, then in that folder
  `PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py` (needs its own `uv sync`).
- **Screenshots:** `shots/`, 390 × 844 at 2×, taken from that build (`original-<screen>.png` is
  the first screen; `-full` is the whole page for home, community and share, where the bottom
  navigation is drawn where the first screen ended, a capture artefact).
- The submission zip built on 2026-09-27 (`dist/DataChallenge_Team DIC005_Submission.zip`,
  gitignored) also carries this design.
