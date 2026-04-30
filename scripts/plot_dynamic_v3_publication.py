#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_ANALYSIS_DIR = Path.home() / "tcc-leo-ns3/analysis/dynamic_v3_campaign"


SCENARIO_LABELS = {
    "light": "Leve",
    "medium": "Médio",
    "heavy_controlled": "Pesado Controlado",
    "extreme": "Extremo",
}

SCENARIO_ORDER = [
    "Leve",
    "Médio",
    "Pesado Controlado",
    "Extremo",
]

POLICY_LABELS = {
    "equal": "Equal",
    "round_robin": "Round Robin",
    "longest_queue_first": "Longest Queue First",
    "greedy_backlog": "Greedy Backlog",
    "proportional_fair": "Proportional Fair",
}

POLICY_ORDER = [
    "Equal",
    "Round Robin",
    "Longest Queue First",
    "Greedy Backlog",
    "Proportional Fair",
]


PLOTS = [
    {
        "metric": "total_rx_mbps",
        "title": "Vazão total recebida por cenário",
        "ylabel": "Vazão total (Mbps)",
        "filename": "01_vazao_total_mbps.png",
        "scale": 1.0,
        "fmt": "{:.1f}",
    },
    {
        "metric": "global_demand_satisfaction",
        "title": "Satisfação global da demanda",
        "ylabel": "Satisfação global (%)",
        "filename": "02_satisfacao_global_demanda.png",
        "scale": 100.0,
        "fmt": "{:.0f}",
    },
    {
        "metric": "global_loss_rate",
        "title": "Taxa global de perda",
        "ylabel": "Perda global (%)",
        "filename": "03_taxa_perda_global.png",
        "scale": 100.0,
        "fmt": "{:.0f}",
    },
    {
        "metric": "global_mean_delay_ms",
        "title": "Atraso médio global",
        "ylabel": "Atraso médio (ms)",
        "filename": "04_atraso_medio_global_ms.png",
        "scale": 1.0,
        "fmt": "{:.0f}",
    },
    {
        "metric": "avg_final_virtual_backlog_mb",
        "title": "Backlog virtual médio final",
        "ylabel": "Backlog médio final (MB)",
        "filename": "05_backlog_medio_final_mb.png",
        "scale": 1.0,
        "fmt": "{:.1f}",
    },
    {
        "metric": "max_final_virtual_backlog_mb",
        "title": "Backlog virtual máximo final",
        "ylabel": "Backlog máximo final (MB)",
        "filename": "06_backlog_maximo_final_mb.png",
        "scale": 1.0,
        "fmt": "{:.1f}",
    },
    {
        "metric": "hotspot_demand_satisfaction",
        "title": "Satisfação de demanda do hotspot",
        "ylabel": "Satisfação do hotspot (%)",
        "filename": "07_satisfacao_hotspot.png",
        "scale": 100.0,
        "fmt": "{:.0f}",
    },
    {
        "metric": "hotspot_loss_rate",
        "title": "Taxa de perda do hotspot",
        "ylabel": "Perda do hotspot (%)",
        "filename": "08_perda_hotspot.png",
        "scale": 100.0,
        "fmt": "{:.0f}",
    },
    {
        "metric": "hotspot_final_backlog_mb",
        "title": "Backlog final do hotspot",
        "ylabel": "Backlog final do hotspot (MB)",
        "filename": "09_backlog_hotspot_mb.png",
        "scale": 1.0,
        "fmt": "{:.1f}",
    },
    {
        "metric": "jain_fairness_rx_mbps",
        "title": "Índice de justiça de Jain sobre vazão",
        "ylabel": "Fairness de Jain",
        "filename": "10_fairness_jain.png",
        "scale": 1.0,
        "fmt": "{:.2f}",
    },
]


def normalize_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["scenario_label"] = out["scenario"].map(SCENARIO_LABELS).fillna(out["scenario"])
    out["policy_label"] = out["policy"].map(POLICY_LABELS).fillna(out["policy"])

    out["scenario_label"] = pd.Categorical(
        out["scenario_label"],
        categories=SCENARIO_ORDER,
        ordered=True,
    )

    out["policy_label"] = pd.Categorical(
        out["policy_label"],
        categories=POLICY_ORDER,
        ordered=True,
    )

    return out.sort_values(["scenario_label", "policy_label"])


def add_bar_labels(ax, fmt: str) -> None:
    for container in ax.containers:
        labels = []

        for bar in container:
            height = bar.get_height()

            if pd.isna(height):
                labels.append("")
            else:
                labels.append(fmt.format(height))

        ax.bar_label(container, labels=labels, fontsize=8, padding=2, rotation=90)


def plot_metric(summary_df: pd.DataFrame, spec: dict, output_dir: Path) -> None:
    metric = spec["metric"]

    if metric not in summary_df.columns:
        print(f"Skipping missing metric: {metric}")
        return

    df = summary_df.copy()
    df["_value"] = df[metric] * spec["scale"]

    pivot = df.pivot_table(
        index="scenario_label",
        columns="policy_label",
        values="_value",
        aggfunc="mean",
        observed=False,
    )

    pivot = pivot.reindex(index=SCENARIO_ORDER)
    pivot = pivot[[p for p in POLICY_ORDER if p in pivot.columns]]

    ax = pivot.plot(kind="bar", figsize=(12, 6))

    ax.set_title(spec["title"])
    ax.set_xlabel("Cenário")
    ax.set_ylabel(spec["ylabel"])
    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=0)

    ax.legend(
        title="Política",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0,
    )

    add_bar_labels(ax, spec["fmt"])

    plt.tight_layout(rect=(0, 0, 0.82, 1))

    path = output_dir / spec["filename"]
    plt.savefig(path, dpi=180)
    plt.close()

    print(f"Saved: {path}")


def plot_hotspot_vs_normal(beam_df: pd.DataFrame, output_dir: Path) -> None:
    required = {"scenario", "policy", "is_hotspot", "demand_satisfaction"}

    if not required.issubset(set(beam_df.columns)):
        print("Skipping hotspot vs normal plots; required columns are missing.")
        return

    df = beam_df.copy()
    df["scenario_label"] = df["scenario"].map(SCENARIO_LABELS).fillna(df["scenario"])
    df["policy_label"] = df["policy"].map(POLICY_LABELS).fillna(df["policy"])
    df["Grupo"] = df["is_hotspot"].map({True: "Hotspot", False: "Beams normais"})
    df["Satisfação (%)"] = df["demand_satisfaction"] * 100.0

    df["scenario_label"] = pd.Categorical(df["scenario_label"], categories=SCENARIO_ORDER, ordered=True)
    df["policy_label"] = pd.Categorical(df["policy_label"], categories=POLICY_ORDER, ordered=True)

    grouped = (
        df.groupby(["scenario_label", "policy_label", "Grupo"], observed=True)["Satisfação (%)"]
        .mean()
        .reset_index()
    )

    for scenario in SCENARIO_ORDER:
        scenario_df = grouped[grouped["scenario_label"] == scenario]

        if scenario_df.empty:
            continue

        pivot = scenario_df.pivot_table(
            index="policy_label",
            columns="Grupo",
            values="Satisfação (%)",
            aggfunc="mean",
            observed=False,
        )

        pivot = pivot.reindex(index=POLICY_ORDER)

        ax = pivot.plot(kind="bar", figsize=(12, 6))

        ax.set_title(f"Satisfação de demanda: hotspot vs beams normais — {scenario}")
        ax.set_xlabel("Política")
        ax.set_ylabel("Satisfação de demanda (%)")
        ax.grid(axis="y", alpha=0.3)

        plt.xticks(rotation=25, ha="right")

        ax.legend(
            title="Grupo",
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            borderaxespad=0,
        )

        add_bar_labels(ax, "{:.0f}")

        plt.tight_layout(rect=(0, 0, 0.82, 1))

        file_stem = (
            scenario.lower()
            .replace(" ", "_")
            .replace("é", "e")
            .replace("á", "a")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )

        path = output_dir / f"11_hotspot_vs_normal_{file_stem}.png"
        plt.savefig(path, dpi=180)
        plt.close()

        print(f"Saved: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate publication-style plots for NS-3 dynamic_v3 results."
    )

    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_DIR,
        help="Directory containing summary_by_policy.csv and beam_results.csv.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    analysis_dir = args.analysis_dir.expanduser().resolve()
    summary_path = analysis_dir / "summary_by_policy.csv"
    beam_path = analysis_dir / "beam_results.csv"

    if not summary_path.exists():
        raise FileNotFoundError(f"File not found: {summary_path}")

    output_dir = analysis_dir / "figures_publication"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_df = normalize_summary(pd.read_csv(summary_path))

    for spec in PLOTS:
        plot_metric(summary_df, spec, output_dir)

    if beam_path.exists():
        beam_df = pd.read_csv(beam_path)
        plot_hotspot_vs_normal(beam_df, output_dir)

    print(f"\nPublication figures saved under: {output_dir}")


if __name__ == "__main__":
    main()
