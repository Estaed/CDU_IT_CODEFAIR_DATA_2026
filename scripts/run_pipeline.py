"""The pipeline entry point: frozen snapshots in, capability table and data pack out.

Run from the project root:

    PYTHONUTF8=1 .venv/Scripts/python scripts/run_pipeline.py

Reads only ``data/raw/`` and writes only ``data/out/``. Nothing here touches the network:
the ``pipeline.fetch`` modules are run by hand and their results are recorded in
``data/out/PROVENANCE.md``. A missing snapshot stops the run with the command that re-fetches
it, rather than a half-filled table.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import figures, merge, pack, provenance, rules  # noqa: E402
from pipeline.sources import accc, audit, bushtel, nbn, ntg, rrl  # noqa: E402

RAW = ROOT / "data/raw"
OUT = ROOT / "data/out"
CACHE = OUT / "cache"
THRESHOLDS = ROOT / "pipeline/thresholds.csv"
TABLE_CSV = OUT / "capability_table.csv"
TABLE_XLSX = OUT / "capability_table.xlsx"
PROVENANCE = OUT / "PROVENANCE.md"
AUDIT_TABLE = OUT / "tables/audit_within_5km.csv"


def newest(pattern: str, fetch_command: str) -> Path:
    """The newest raw file matching ``pattern``, or a stop naming the fetch command."""
    found = sorted(RAW.glob(pattern))
    if not found:
        raise SystemExit(
            f"missing raw snapshot: no file matches {pattern} under "
            f"{RAW.relative_to(ROOT).as_posix()}. Fetch it with: {fetch_command}"
        )
    return found[-1]


def main() -> None:
    thresholds = rules.load_thresholds(THRESHOLDS)

    communities = bushtel.load(
        newest("bushtel_community_detail_*.json", bushtel.FETCH_COMMAND)
    )
    print(f"bushtel: {len(communities)} communities")

    nbn_frame = nbn.load(
        newest("nbn_coverage_fixedline_*.zip", nbn.FETCH_COMMAND),
        newest("nbn_coverage_wireless_*.zip", nbn.FETCH_COMMAND),
        communities,
    )
    print(f"nbn: {len(nbn_frame)} rows")

    accc_frame = accc.load(RAW, communities, CACHE)
    print(f"accc: {len(accc_frame)} rows")

    rrl_frame = rrl.load(newest("spectra_rrl_*.zip", rrl.FETCH_COMMAND), communities)
    print(f"rrl: {len(rrl_frame)} rows")

    audit_frame = audit.load(
        newest("audit_non_alignment_*.csv", audit.FETCH_COMMAND), communities
    )
    print(f"audit: {len(audit_frame)} rows, {(audit_frame['audit5'] == '1').sum()} within 5 km")

    ntg_frame = ntg.load(
        newest("ntg_2019.xlsx", ntg.FETCH_COMMAND),
        newest("ntg_2021.xlsx", ntg.FETCH_COMMAND),
        newest("ntg_2022.xlsx", ntg.FETCH_COMMAND),
        newest("ntg_smallcell.xlsx", ntg.FETCH_COMMAND),
        communities,
    )
    print(f"ntg: {len(ntg_frame)} rows")

    table = merge.merge(
        communities, nbn_frame, accc_frame, rrl_frame, ntg_frame, audit_frame, thresholds
    )
    OUT.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLE_CSV, index=False, lineterminator="\n", encoding="utf-8")
    table.to_excel(TABLE_XLSX, index=False, engine="openpyxl")
    print(f"{TABLE_CSV.relative_to(ROOT).as_posix()}: {len(table)} rows, {table.shape[1]} columns")

    audit.write_table(audit_frame, communities, AUDIT_TABLE)
    print(f"{AUDIT_TABLE.relative_to(ROOT).as_posix()}: written")

    provenance.write(PROVENANCE, RAW)
    print(f"{PROVENANCE.relative_to(ROOT).as_posix()}: written")

    pack.main()
    figures.main()


if __name__ == "__main__":
    main()
