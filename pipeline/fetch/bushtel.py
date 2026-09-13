"""Re-fetch the BushTel snapshots that ``pipeline.sources.bushtel`` reads.

The only module in the repository that talks to bushtel.nt.gov.au. Run by hand, never by a
test or the gate:

    PYTHONUTF8=1 .venv/Scripts/python -m pipeline.fetch.bushtel

Writes ``data/raw/bushtel_communities_<today>.json`` (the full community list) and
``data/raw/bushtel_community_detail_<today>.json`` (one detail record per community
that is not a Family Outstation), each a JSON list, in the same shape as the 2026-09-12 snapshots.

Source: https://bushtel.nt.gov.au/api/Community (undocumented public API, (c) Northern
Territory Government, licence TBD).
"""

from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
LIST_URL = "https://bushtel.nt.gov.au/api/Community?community=&boundary=0"
DETAIL_URL = "https://bushtel.nt.gov.au/api/Community/{id}"
# Every type except Family Outstation, so a re-fetch has the shape of the 2026-09-12 snapshot
# (162 records); pipeline.sources.bushtel narrows to Major and Minor.
COMMUNITY_TYPES = ("Major", "Minor", "Town Camp", "Village", "Town", "City")
HEADERS = {"User-Agent": "Crosscheck-research/0.1 (CDU IT Code Fair 2026; one-off snapshot)"}
TIMEOUT_SECONDS = 60
DELAY_SECONDS = 0.3


def get_json(url: str) -> object:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    communities = get_json(LIST_URL)
    write(RAW / f"bushtel_communities_{today}.json", communities)

    wanted = [c for c in communities if c["CommunityTypeName"] in COMMUNITY_TYPES]
    print(f"fetching detail for {len(wanted)} communities")
    details = []
    for community in wanted:
        details.append(get_json(DETAIL_URL.format(id=int(community["Id"]))))
        time.sleep(DELAY_SECONDS)
    write(RAW / f"bushtel_community_detail_{today}.json", details)


if __name__ == "__main__":
    main()
