# Report

The Data Innovation Challenge report for team DIC005 and what it is built from.

| File | What it is |
|---|---|
| `DataChallenge_Team DIC005_Report.docx` | The report in the organiser's format (A4, Calibri, team number and page in header and footer). Export to PDF as `DataChallenge_Team DIC005_Report.pdf` for submission. |
| `DataChallenge_Team DIC005_Report.md` | The same text in Markdown; every number is read from `data/out/` and `docs/FINDINGS.md`. |
| `drafts/DataChallenge_Team DIC005_Report_team-draft.md` | The team's first draft, kept for reference. |
| `figures/` | Figure 1 (verdicts per service) and Figure 2 (where to act first), with the scripts that draw them. |

Redraw the figures after the pipeline changes:

```
uv run python docs/report/figures/Crosscheck_figure_services.py
uv run python docs/report/figures/Crosscheck_figure_where_to_act.py
```
