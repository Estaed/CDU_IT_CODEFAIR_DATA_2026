"""Join the lane outputs into one capability row per community and score each service.

Inputs (all keyed on bushtel_id, 96 rows each): spike/communities.csv, spike/out/nbn.csv,
spike/out/accc.csv, spike/out/rrl.csv, spike/out/ntg.csv, spike/out/bushtel.csv,
spike/thresholds.csv. A missing lane file is reported and its columns left empty, so the
table can be inspected before every lane has finished.

Verdict rules are provisional spike rules, written down here so the report can quote them:

  fixed_latency_ms      SATELLITE_RESIDUAL -> 664.9 (ACCC MBA); FIXED_LINE / FIXED_WIRELESS
                        -> "<100 (TBD)" (no sourced figure yet, see thresholds.csv)
  mobile_sources_covered  count over four publishers that say "mobile coverage here":
                        ACCC 2025 any-carrier 4G polygon contains the point;
                        NT Government 2022 list names the community;
                        ACMA RRL has a carrier cellular-band transmit site within 5 km (NTG's own
                        small-cell radius; 40 km, NTG's macro radius, is true for 96/96 and so
                        carries no information -- measured 2026-09-12);
                        BushTel "Mobile phone" service = Y.
  telehealth_video      needs latency <= 100 ms. GREEN if fixed line/wireless; AMBER if satellite
                        but an ACCC 4G polygon covers the point (call could ride 4G, capacity and
                        cost unverified); RED if satellite and no 4G polygon. n/a without a
                        health centre.
  school_video_meeting  bandwidth minimum cleared by every technology; latency requirement TBD,
                        so satellite = AMBER, fixed line/wireless = GREEN. n/a without a school.
  mygov_text            GREEN wherever any link exists (no published requirement; text-first).
  voice_sms             GREEN if ACCC 4G polygon or NTG 2022 listing; AMBER if only public WiFi;
                        RED otherwise.

Run from the project root: PYTHONUTF8=1 .venv/Scripts/python.exe spike/merge.py
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SPIKE = ROOT / "spike"
OUT = SPIKE / "out" / "capability_table.csv"

SAT_LATENCY_MS = 664.9  # ACCC MBA release 147/24, see thresholds.csv


def load(name: str) -> pd.DataFrame | None:
    path = SPIKE / "out" / name
    if not path.exists():
        print(f"MISSING lane output: {path.relative_to(ROOT)}", file=sys.stderr)
        return None
    df = pd.read_csv(path, dtype=str).fillna("")
    df["bushtel_id"] = df["bushtel_id"].astype(int)
    if len(df) != 96:
        print(f"WARNING {name}: {len(df)} rows, expected 96", file=sys.stderr)
    return df.drop(columns=[c for c in ("name",) if c in df.columns])


def as_int(series: pd.Series, default: int = 0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default).astype(int)


def main() -> None:
    table = pd.read_csv(SPIKE / "communities.csv", dtype=str).fillna("")
    table["bushtel_id"] = table["bushtel_id"].astype(int)
    present = {}
    for name in ("nbn.csv", "accc.csv", "rrl.csv", "ntg.csv", "bushtel.csv"):
        df = load(name)
        present[name] = df is not None
        if df is not None:
            table = table.merge(df, on="bushtel_id", how="left")
    table = table.fillna("")

    # --- fixed access --------------------------------------------------------------
    if present["nbn.csv"]:
        table["fixed_latency_ms"] = table["nbn_technology"].map(
            lambda t: SAT_LATENCY_MS if t == "SATELLITE_RESIDUAL" else "<100 (TBD)"
        )
    else:
        table["nbn_technology"] = ""
        table["fixed_latency_ms"] = ""

    # --- mobile: four publishers ---------------------------------------------------
    accc_any = as_int(table["carriers_4g_count"]) >= 1 if present["accc.csv"] else pd.Series(False, index=table.index)
    ntg_listed = as_int(table["ntg2022_listed"]) == 1 if present["ntg.csv"] else pd.Series(False, index=table.index)
    rrl_5 = as_int(table["any_within_5km"]) >= 1 if present["rrl.csv"] else pd.Series(False, index=table.index)
    bushtel_mobile = table["svc_mobile_phone"].eq("Y") if present["bushtel.csv"] else pd.Series(False, index=table.index)
    publishers = [k for k, ok in (("accc", present["accc.csv"]), ("ntg2022", present["ntg.csv"]),
                                  ("rrl5", present["rrl.csv"]), ("bushtel", present["bushtel.csv"])) if ok]
    table["mobile_publishers_available"] = len(publishers)
    table["mobile_sources_covered"] = accc_any.astype(int) + ntg_listed.astype(int) + rrl_5.astype(int) + bushtel_mobile.astype(int)
    table["mobile_sources_disagree"] = ((table["mobile_sources_covered"] > 0) & (table["mobile_sources_covered"] < len(publishers))).astype(int)
    table["mobile_says"] = (
        "accc=" + accc_any.astype(int).astype(str) + ";ntg2022=" + ntg_listed.astype(int).astype(str)
        + ";rrl5=" + rrl_5.astype(int).astype(str) + ";bushtel=" + bushtel_mobile.astype(int).astype(str)
    )

    # --- service verdicts ------------------------------------------------------------
    sat = table["nbn_technology"].eq("SATELLITE_RESIDUAL")
    fixed_ok = table["nbn_technology"].isin(["FIXED_LINE", "FIXED_WIRELESS"])
    has = lambda col: table[col].eq("Y") if col in table.columns else pd.Series(False, index=table.index)  # noqa: E731

    def verdict(applies, green, amber):
        out = pd.Series("RED", index=table.index)
        out[amber] = "AMBER"
        out[green] = "GREEN"
        out[~applies] = "n/a"
        out[table["nbn_technology"].eq("")] = "no data"
        return out

    table["telehealth_video"] = verdict(has("svc_health_centre"), fixed_ok, sat & accc_any)
    table["telehealth_reason"] = table.apply(
        lambda r: "" if r["telehealth_video"] in ("n/a", "no data")
        else f"fixed={r['nbn_technology']} latency={r['fixed_latency_ms']} vs 100 ms required; accc_4g={int(accc_any[r.name])}",
        axis=1,
    )
    table["school_video_meeting"] = verdict(has("svc_school"), fixed_ok, sat)
    table["mygov_text"] = verdict(pd.Series(True, index=table.index), fixed_ok | sat, pd.Series(False, index=table.index))
    wifi_only = has("svc_wifi") & ~(accc_any | ntg_listed)
    table["voice_sms"] = verdict(pd.Series(True, index=table.index), accc_any | ntg_listed, wifi_only)
    services = ["telehealth_video", "school_video_meeting", "mygov_text", "voice_sms"]
    table["services_failing"] = table[services].isin(["RED"]).sum(axis=1)
    table["services_degraded"] = table[services].isin(["AMBER"]).sum(axis=1)

    # --- fragility (what exists today) ----------------------------------------------
    if present["ntg.csv"]:
        table["backhaul_2019"] = table["ntg2019_backhaul"]
    table["road_seasonal_cut"] = table.get("road_seasonal_cut", "")

    table = table.sort_values("bushtel_id")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT, index=False, lineterminator="\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(table)} rows, {table.shape[1]} columns; lanes present: {present}")

    # --- variation report (the kill criterion) --------------------------------------
    def dist(col, frame):
        return dict(frame[col].value_counts(dropna=False).sort_index())

    s20 = table[table["spike20"] == "1"]
    print("\n== 96 Major/Minor ==")
    for col in ("nbn_technology", "mobile_sources_covered", "mobile_sources_disagree", "telehealth_video",
                "school_video_meeting", "voice_sms", "services_failing", "services_degraded"):
        print(f"{col:26s} {dist(col, table)}")
    print("\n== 20 spike communities ==")
    for col in ("nbn_technology", "mobile_sources_covered", "mobile_sources_disagree", "telehealth_video",
                "school_video_meeting", "voice_sms", "services_failing", "services_degraded"):
        print(f"{col:26s} {dist(col, s20)}")
    combo = table[["nbn_technology", "mobile_sources_covered", "telehealth_video", "voice_sms"]].astype(str).agg("|".join, axis=1)
    print(f"\ndistinct (fixed, mobile_count, telehealth, voice) combinations over 96: {combo.nunique()}")
    print(combo.value_counts().to_string())


if __name__ == "__main__":
    main()
