#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_ANALYSIS_DIR = Path.home() / "tcc-leo-ns3/analysis/dynamic_v3_campaign"


METRICS = [
    ("total_rx_mbps", "Total RX Throughput (Mbps)", "total_rx_mbps.png"),
    ("global_demand_satisfaction", "Global Demand Satisfaction", "global_demand_satisfaction.png"),
    ("global_loss_rate", "Global Loss Rate", "global_loss_rate.png"),
    ("global_mean_delay_ms", "Global Mean Delay (ms)", "global_mean_delay_ms.png"),
    ("avg_final_virtual_backlog_mb", "Average Final Virtual Backlog (MB)", "avg_final_backlog_mb.png"),
    ("max_final_virtual_backlog_mb", "Maximum Final Virtual Backlog (MB)", "max_final_backlog_mb.png"),
    ("jain_fairness_rx_mbps", "Jain Fairness over RX Mbps", "jain_fairness_rx_mbps.png"),
    ("hotspot_demand_satisfaction", "Hotspot Demand Satisfaction", "hotspot_demand_satisfaction.png"),
    ("hotspot_loss_rate", "Hotspot Loss Rate", "hotspot_loss_rate.png"),
    ("hotspot_final_backlog_mb", "Hotspot Final Backlog (MB)", "hotspot_final_backlog_mb.png"),
]


def plot_grouped_bar(summary_df: pd.DataFrame, metric: str, title: str, output_path: Path) -> None:
    if metric not in summary_df.columns:
        print(f"Skipping missing metric: {metric}")
        return

    pivot = summary_df.pivot_table(
        index="scenario",
        columns="policy",
        values=metric,
        aggfunc="mean",
    )

    ax = pivot.plot(kind="bar", figsize=(11, 6))

    ax.set_title(title)
    ax.set_xlabel("Scenario")
    ax.set_ylabel(metric)
    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()

    print(f"Saved: {output_path}")


def plot_hotspot_vs_normal(beam_df: pd.DataFrame, output_path: Path) -> None:
    required = {"scenario", "policy", "is_hotspot", "demand_satisfaction"}

    if not required.issubset(set(beam_df.columns)):
        print("Skipping hotspot vs normal plot because required columns are missing.")
        return

    grouped = (
        beam_df
        .assign(group=lambda df: df["is_hotspot"].map({True: "hotspot", False: "normal"}))
        .groupby(["scenario", "policy", "group"], as_index=False)["demand_satisfaction"]
        .mean()
    )

    for scenario in sorted(grouped["scenario"].unique()):
        scenario_df = grouped[grouped["scenario"] == scenario]
        pivot = scenario_df.pivot_table(
            index="policy",
            columns="group",
            values="demand_satisfaction",
            aggfunc="mean",
        )

        fig_path = output_path / f"hotspot_vs_normal_satisfaction_{scenario}.png"

        ax = pivot.plot(kind="bar", figsize=(11, 6))
        ax.set_title(f"Hotspot vs Normal Demand Satisfaction — {scenario}")
        ax.set_xlabel("Policy")
        ax.set_ylabel("Demand satisfaction")
        ax.grid(axis="y", alpha=0.3)

        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(fig_path, dpi=160)
        plt.close()

        print(f"Saved: {fig_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot NS-3 dynamic_v3 campaign results."
    )

    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_DIR,
        help="Directory containing consolidated CSV files.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    analysis_dir = args.analysis_dir.expanduser().resolve()
    figures_dir = analysis_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    summary_path = analysis_dir / "summary_by_policy.csv"
    beam_path = analysis_dir / "beam_results.csv"

    if not summary_path.exists():
        raise FileNotFoundError(f"Summary CSV not found: {summary_path}")

    summary_df = pd.read_csv(summary_path)

    for metric, title, filename in METRICS:
        plot_grouped_bar(
            summary_df=summary_df,
            metric=metric,
            title=title,
            output_path=figures_dir / filename,
        )

    if beam_path.exists():
        beam_df = pd.read_csv(beam_path)
        plot_hotspot_vs_normal(beam_df, figures_dir)

    print(f"\nFigures saved under: {figures_dir}")


if __name__ == "__main__":
    main()
