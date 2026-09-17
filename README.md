# Data Innovation Challenge 2026 — CDU IT Code Fair

**Theme: Remote Connectivity.**
Official page: <https://itcodefair.cdu.edu.au/data-innovation-challenge/>
Datasets page: <https://itcodefair.cdu.edu.au/datasciencechalllenge_datasets/>
Report format: <https://itcodefair.cdu.edu.au/data-innovation-challenge-requirement/>

Transcribed 11 September 2026. Re-check the live pages before any deadline.

---

## The problem

Many remote communities across Australia do not have reliable internet or mobile coverage.
That makes it harder for people to reach essential digital services such as education,
healthcare and government support, and it feeds the ongoing digital divide.

The organisers name a second, subtler problem on top of the first one, and it is the part
that makes this a *data* challenge rather than an engineering one:

> Connectivity gaps are not always clearly understood or consistently represented, making it
> difficult for communities, governments, and industry to prioritise action and investment
> effectively.

So the gap is not only in the network. It is in the map of the network. Coverage maps are
published by the carriers that sell the coverage, they describe predicted signal rather than
lived experience, and they are not consistent between sources. An entry that reconciles those
sources, or that shows where they disagree, is answering the brief directly.

## The five tasks

The page lists these as aims, "but not limited to":

1. **Find the gaps.** Identify and analyse areas of limited or unreliable connectivity using
   available data.
2. **Make it understandable.** Communicate connectivity gaps clearly to support communities,
   governments and service providers in making informed decisions.
3. **Consider multiple data sources.** Show how data can be integrated from several sources to
   give clearer insight into connectivity challenges and opportunities.
4. **Impacts.** Show that you have considered the ethical, cultural and community effects of
   how you use, explain and present data.
5. **Solutions.** Design solutions that remain usable in low-connectivity or offline contexts,
   such as through offline-first functionality.

Task 5 is the one most teams will get wrong. A dashboard that needs a live connection to
explain where there is no connection is self-defeating, and the organisers wrote
"offline-first" into the brief on purpose. Building the artefact so it works on a phone with
no signal is both a requirement and an easy point of differentiation.

Task 4 has real weight in this specific context. The subject matter is remote and heavily
First Nations communities in the Northern Territory. Data about those communities carries
Indigenous Data Sovereignty obligations, and presenting a community as a deficit on a map is
itself a decision with consequences. Address that in the report rather than hoping it does not
come up in Q&A.

## Data and tools

Full list with commentary in [`docs/datasets.md`](docs/datasets.md). The organisers name eight
sources: NT Remote Areas Mobile Coverage, the Australian Digital Inclusion Index dashboard,
the National Broadband Network dataset, the ACCC Mobile Infrastructure Report data release,
tropical cyclone reports, the First Nations Connectivity Mapping Tool, the ACMA Site Location
Map, and ABS TableBuilder. Other public datasets on connectivity, geography or community
demographics are allowed.

Tools: Python and related data analysis libraries, AI and machine learning libraries, public
data APIs, and other development, visualisation and mapping tools.

The presence of **tropical cyclone reports** in a connectivity dataset list is a hint, not
filler. In the NT, connectivity is not a static property; it is a thing that fails exactly
when a cyclone makes it matter most. Crossing coverage with cyclone exposure is a resilience
story the judges have effectively pre-seeded.

## Eligibility

Teams of **2–4** enrolled CDU IT coursework students (undergraduate, postgraduate, TAFE and
short courses). Higher Degree by Research students are not eligible.

## What must be handed in

The challenge page and the requirement page give different lists. Build for the union of both,
detailed in [`docs/report-requirements.md`](docs/report-requirements.md):

1. **Data analysis report and background research** — PDF, max 8 pages excluding title page,
   references and appendices, ~2,500 words, A4, Calibri or Arial, team number and page number
   in header and footer, named `DataChallenge_Team xx(number)_Report.pdf`.
2. **Presentation slide deck** — the requirement page says 5 minutes; Challenge Day gives a
   10-minute slot plus 5 minutes of Q&A. Prepare the 10-minute version and keep a 5-minute
   cut.
3. **Interactive prototype solution.**
4. **Python-based solution** — `.py` files or Jupyter Notebooks, no restrictions on packages,
   with remarks on the key steps and a README containing reproduction instructions.

All of it in a **zip file, emailed to itcodefair@cdu.edu.au**, with this subject line format:

```
Data Innovation Challenge Submission – [Group] – IT Code Fair 2026
```

The report structure is prescribed: Title page, Summary of 150–250 words, then Introduction,
Methodology, Findings, Discussion (defined as ethical, cultural and community impacts),
Recommendations, References, and Appendices including an AI usage declaration.

## Dates

| Milestone | Date |
|---|---|
| Registration closes | Tuesday 15 September 2026 |
| Final submission deadline | Wednesday 30 September 2026 |
| Challenge Presentation Day | Wednesday 7 October 2026, 09:00–17:00 |
| Winners announced | Thursday 5 November 2026 |

Venue for Challenge Day: Festival Learning Space 1.12, Danala | ECP, Darwin, Charles Darwin
University. Format: 10-minute pitch plus 5-minute Q&A per team, face to face with industry
judges.

**This is the earliest submission deadline of all six competitions.** Roughly nineteen days
separate the transcription date from the hand-in.

## How it is judged

Six criteria, no published weightings: **datasets**, **overall creativity and originality**,
**technical sophistication**, **contextual relevance and practicality**, **ethical
considerations**, **presentation**. First winner and runner-up.

Judging panel:

| Judge | Role |
|---|---|
| Sandeep Rasali | Department of Corporate and Digital Development, NT Government |
| Sarah Strzelecki | Department of Corporate and Digital Development, NT Government |
| Mohammad Aurangzeb Khan | Department of Corporate and Digital Development, NT Government |
| Dr Cat Kutay | Senior Lecturer in Information Technology, Charles Darwin University |

Three of the four judges work for the NT Government department that would actually act on
these recommendations. That shapes what wins: the "Recommendations" section of the report is
being read by the people it is addressed to, so it should name who does what, not gesture at
"further investment".

Note also that **datasets is listed first among the criteria**. Breadth and honest handling of
sources is being scored on its own, separately from the modelling.

## Scaffolding in this folder

This folder is a Project Ignition clone. `CLAUDE.md` and its Codex twin `AGENTS.md` carry the
workflow: dump raw thinking into `notes.md`, then `create-prd`, then `create-architecture` to
write Blueprint, then `generate-tasks`, then `verify-task` per task. `.codex/hooks.json` has been
generated for this path. Blueprint of `CLAUDE.md` is still the placeholder and must be written
before any task is generated.

## Reproduce

Every command below runs from this folder (the project root) and was run once while writing
this section. Commands are copied verbatim from `CLAUDE.md` Blueprint "Entry points" and "Quality
gate"; if the two ever disagree, `CLAUDE.md` is the source of truth.

### Prerequisites

- Python 3.13 and [uv](https://docs.astral.sh/uv/) (this project was built against Python
  3.13.5 and uv 0.12.13).
- An environment at `.venv/`, created and kept in sync with:

  ```
  uv sync
  ```

  This installs both the runtime dependencies in `pyproject.toml` and the `dev` group
  (`pytest`, `ruff`, `playwright`). Playwright also needs its Chromium build once:
  `.venv/Scripts/python -m playwright install chromium`.

### Raw data: committed vs re-fetched

`data/raw/` is entirely gitignored — a clone of this repository starts with no raw snapshots
and no committed ones exist to unpack (BushTel's reuse terms are still an open question, so no
raw file from any source is committed). Every source is re-fetched by hand with one script per
publisher, each writing `data/raw/<source>_<today>.*`:

```
PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.bushtel
PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.nbn
PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.accc
PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.rrl
PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.ntg
PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.abs_boundary
```

The pipeline always reads the **newest** file matching each source's pattern under
`data/raw/`, so a fresh fetch does not need the old snapshot removed first — a re-fetch today
produces new BushTel and ACMA RRL files, for example, dated with today's date, sitting next
to whatever was already there.

### Run the pipeline

```
PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py
```

Reads only `data/raw/`, writes only `data/out/`: `capability_table.csv`/`.xlsx`,
`data_pack.json`, `PROVENANCE.md`, and the figures. No network access.

The ACCC source is the slow part: on its first run it parses the raw KML files and writes a
290 MB cache to `data/out/cache/` (gitignored); that cold parse took 3,531 seconds on
2026-09-13. Every run after that reads the cache and takes seconds, until a raw ACCC file
changes.

### Build the app

```
PYTHONUTF8=1 .venv/Scripts/python scripts/build_app.py
```

Inlines the design tokens, `app/app.css`, `app/app.js` and `data/out/data_pack.json` into
`app/index.html`, writing `dist/index.html`, and copies `app/sw.js` and
`app/manifest.webmanifest` next to it for the host. `dist/` is gitignored and rebuilt from
source every time.

### Quality gate

```
PYTHONUTF8=1 .venv/Scripts/python scripts/gate.py
```

Runs, in order, stopping at the first failure: lint (`ruff check --no-cache .`), the unit
tests, the app build above, the size check (`dist/index.html` under 1 MiB, `data_pack.json`
under 300 KiB), then the Playwright browser smoke test. That last step is also the offline
claim's verification: it opens `dist/index.html` from `file://` and asserts zero requests
left the page. Run it on its own with:

```
PYTHONUTF8=1 .venv/Scripts/python -m pytest -m browser
```

### Package the submission

```
PYTHONUTF8=1 .venv/Scripts/python scripts/package_submission.py
```

Builds `dist/DataChallenge_Team <team number>_Submission.zip` (team number read from
`constants.md`) from `dist/index.html`, this README, `pyproject.toml`, `uv.lock`, `pipeline/`,
`scripts/`, `tests/`, `data/out/`, and any committed raw snapshot. It also picks up the report
PDF and slide deck from `submission/` if present there under their expected names, and warns
without failing if either is missing.
