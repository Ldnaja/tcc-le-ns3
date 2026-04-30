#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd


DEFAULT_RESULTS_ROOT = Path.home() / "tcc-leo-ns3/results/dynamic_v3_campaign"
DEFAULT_ANALYSIS_DIR = Path.home() / "tcc-leo-ns3/analysis/dynamic_v3_campaign"


def parse_value(value: str) -> Any:
    value = value.strip()

    try:
        if "." in value or "e" in value.lower():
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_summary(path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or "=" not in line:
            continue

        key, value = line.split("=", 1)
        data[key.strip()] = parse_value(value)

    return data


def policy_from_summary_path(path: Path) -> str:
    name = path.stem

    if not name.startswith("summary_"):
        raise ValueError(f"Invalid summary filename: {path.name}")

    return name.replace("summary_", "", 1)


def load_final_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    numeric_cols = [
        "beam_id",
        "offered_payload_mbps",
        "offered_ip_mbps",
        "rx_mbps",
        "rx_mbps_observed_window",
        "measurement_window_s",
        "demand_satisfaction",
        "tx_packets",
        "rx_packets",
        "lost_packets",
        "delivery_ratio",
        "loss_rate",
        "mean_delay_ms",
        "final_virtual_backlog_mb",
        "last_allocated_channels",
        "last_beam_capacity_mbps",
        "ewma_served_mbps",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def summarize_beam_level(
    final_df: pd.DataFrame,
    hotspot_beam: int,
) -> Dict[str, Any]:
    hotspot = final_df[final_df["beam_id"] == hotspot_beam]
    normal = final_df[final_df["beam_id"] != hotspot_beam]

    out: Dict[str, Any] = {}

    if not hotspot.empty:
        h = hotspot.iloc[0]
        out.update(
            {
                "hotspot_rx_mbps": h.get("rx_mbps"),
                "hotspot_offered_ip_mbps": h.get("offered_ip_mbps"),
                "hotspot_demand_satisfaction": h.get("demand_satisfaction"),
                "hotspot_loss_rate": h.get("loss_rate"),
                "hotspot_mean_delay_ms": h.get("mean_delay_ms"),
                "hotspot_final_backlog_mb": h.get("final_virtual_backlog_mb"),
                "hotspot_last_allocated_channels": h.get("last_allocated_channels"),
            }
        )

    if not normal.empty:
        out.update(
            {
                "normal_avg_rx_mbps": normal["rx_mbps"].mean(),
                "normal_avg_demand_satisfaction": normal["demand_satisfaction"].mean(),
                "normal_avg_loss_rate": normal["loss_rate"].mean(),
                "normal_avg_delay_ms": normal["mean_delay_ms"].mean(),
                "normal_avg_final_backlog_mb": normal["final_virtual_backlog_mb"].mean(),
                "normal_min_demand_satisfaction": normal["demand_satisfaction"].min(),
                "normal_max_delay_ms": normal["mean_delay_ms"].max(),
            }
        )

    return out


def collect_results(results_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: List[Dict[str, Any]] = []
    beam_frames: List[pd.DataFrame] = []

    scenario_dirs = sorted([p for p in results_root.iterdir() if p.is_dir()])

    if not scenario_dirs:
        raise FileNotFoundError(f"No scenario directories found in: {results_root}")

    for scenario_dir in scenario_dirs:
        scenario_name = scenario_dir.name
        summary_files = sorted(scenario_dir.glob("summary_*.txt"))

        for summary_file in summary_files:
            policy = policy_from_summary_path(summary_file)
            final_file = scenario_dir / f"final_{policy}.csv"

            summary = parse_summary(summary_file)
            summary["scenario"] = scenario_name
            summary["policy"] = policy
            summary["summary_file"] = str(summary_file)

            hotspot_beam = int(summary.get("hotspotBeam", 0))

            if final_file.exists():
                final_df = load_final_csv(final_file)
                final_df["scenario"] = scenario_name
                final_df["policy"] = policy
                final_df["is_hotspot"] = final_df["beam_id"] == hotspot_beam
                beam_frames.append(final_df)

                summary.update(summarize_beam_level(final_df, hotspot_beam))
                summary["final_file"] = str(final_file)
            else:
                summary["final_file"] = ""

            summary_rows.append(summary)

    summary_df = pd.DataFrame(summary_rows)

    if beam_frames:
        beam_df = pd.concat(beam_frames, ignore_index=True)
    else:
        beam_df = pd.DataFrame()

    return summary_df, beam_df


def create_rankings(summary_df: pd.DataFrame) -> pd.DataFrame:
    ranking_cols = [
        "scenario",
        "policy",
        "total_rx_mbps",
        "global_demand_satisfaction",
        "global_loss_rate",
        "global_mean_delay_ms",
        "avg_final_virtual_backlog_mb",
        "max_final_virtual_backlog_mb",
        "jain_fairness_rx_mbps",
        "hotspot_demand_satisfaction",
        "hotspot_loss_rate",
        "hotspot_final_backlog_mb",
    ]

    available_cols = [c for c in ranking_cols if c in summary_df.columns]

    ranking = summary_df[available_cols].copy()

    sort_cols = []
    ascending = []

    if "scenario" in ranking.columns:
        sort_cols.append("scenario")
        ascending.append(True)

    if "global_demand_satisfaction" in ranking.columns:
        sort_cols.append("global_demand_satisfaction")
        ascending.append(False)

    if "global_loss_rate" in ranking.columns:
        sort_cols.append("global_loss_rate")
        ascending.append(True)

    if sort_cols:
        ranking = ranking.sort_values(sort_cols, ascending=ascending)

    return ranking


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect NS-3 dynamic_v3 campaign results."
    )

    parser.add_argument(
        "--results-root",
        type=Path,
        default=DEFAULT_RESULTS_ROOT,
        help="Root directory containing scenario result folders.",
    )

    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_DIR,
        help="Directory where consolidated analysis files will be saved.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    results_root = args.results_root.expanduser().resolve()
    analysis_dir = args.analysis_dir.expanduser().resolve()

    if not results_root.exists():
        raise FileNotFoundError(f"Results root not found: {results_root}")

    analysis_dir.mkdir(parents=True, exist_ok=True)

    summary_df, beam_df = collect_results(results_root)
    ranking_df = create_rankings(summary_df)

    summary_path = analysis_dir / "summary_by_policy.csv"
    beam_path = analysis_dir / "beam_results.csv"
    ranking_path = analysis_dir / "scenario_rankings.csv"

    summary_df.to_csv(summary_path, index=False)
    beam_df.to_csv(beam_path, index=False)
    ranking_df.to_csv(ranking_path, index=False)

    print(f"Saved summary:  {summary_path}")
    print(f"Saved beams:    {beam_path}")
    print(f"Saved rankings: {ranking_path}")

    print("\n=== Ranking preview ===")
    preview_cols = [
        "scenario",
        "policy",
        "total_rx_mbps",
        "global_demand_satisfaction",
        "global_loss_rate",
        "global_mean_delay_ms",
        "max_final_virtual_backlog_mb",
        "hotspot_demand_satisfaction",
    ]

    preview_cols = [c for c in preview_cols if c in ranking_df.columns]
    print(ranking_df[preview_cols].to_string(index=False))


if __name__ == "__main__":
    main()
