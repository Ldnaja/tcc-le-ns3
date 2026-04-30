#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

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


def pct(series: pd.Series) -> pd.Series:
    return series * 100.0


def prepare_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["Cenário"] = out["scenario"].map(SCENARIO_LABELS).fillna(out["scenario"])
    out["Política"] = out["policy"].map(POLICY_LABELS).fillna(out["policy"])

    table = pd.DataFrame(
        {
            "Cenário": out["Cenário"],
            "Política": out["Política"],
            "Vazão total (Mbps)": out["total_rx_mbps"],
            "Satisfação global (%)": pct(out["global_demand_satisfaction"]),
            "Perda global (%)": pct(out["global_loss_rate"]),
            "Atraso médio global (ms)": out["global_mean_delay_ms"],
            "Backlog médio final (MB)": out["avg_final_virtual_backlog_mb"],
            "Backlog máximo final (MB)": out["max_final_virtual_backlog_mb"],
            "Fairness Jain": out["jain_fairness_rx_mbps"],
            "Satisfação hotspot (%)": pct(out["hotspot_demand_satisfaction"]),
            "Perda hotspot (%)": pct(out["hotspot_loss_rate"]),
            "Backlog hotspot final (MB)": out["hotspot_final_backlog_mb"],
        }
    )

    table["Cenário"] = pd.Categorical(table["Cenário"], categories=SCENARIO_ORDER, ordered=True)
    table["Política"] = pd.Categorical(table["Política"], categories=POLICY_ORDER, ordered=True)

    table = table.sort_values(["Cenário", "Política"]).reset_index(drop=True)

    numeric_cols = table.select_dtypes(include="number").columns
    table[numeric_cols] = table[numeric_cols].round(3)

    return table


def prepare_ranking(table: pd.DataFrame) -> pd.DataFrame:
    ranking = table.copy()

    ranking["rank_satisfacao"] = (
        ranking.groupby("Cenário", observed=True)["Satisfação global (%)"]
        .rank(ascending=False, method="min")
    )

    ranking["rank_perda"] = (
        ranking.groupby("Cenário", observed=True)["Perda global (%)"]
        .rank(ascending=True, method="min")
    )

    ranking["rank_atraso"] = (
        ranking.groupby("Cenário", observed=True)["Atraso médio global (ms)"]
        .rank(ascending=True, method="min")
    )

    ranking["score_composto"] = (
        ranking["rank_satisfacao"] + ranking["rank_perda"] + ranking["rank_atraso"]
    )

    ranking = ranking.sort_values(["Cenário", "score_composto", "rank_satisfacao"]).reset_index(drop=True)

    ranking = ranking[
        [
            "Cenário",
            "Política",
            "Vazão total (Mbps)",
            "Satisfação global (%)",
            "Perda global (%)",
            "Atraso médio global (ms)",
            "Backlog máximo final (MB)",
            "Satisfação hotspot (%)",
            "Backlog hotspot final (MB)",
            "score_composto",
        ]
    ]

    numeric_cols = ranking.select_dtypes(include="number").columns
    ranking[numeric_cols] = ranking[numeric_cols].round(3)

    return ranking


def save_table(df: pd.DataFrame, output_dir: Path, stem: str) -> None:
    csv_path = output_dir / f"{stem}.csv"
    md_path = output_dir / f"{stem}.md"
    tex_path = output_dir / f"{stem}.tex"

    df.to_csv(csv_path, index=False)
    md_path.write_text(df.to_markdown(index=False), encoding="utf-8")

    latex = df.to_latex(
        index=False,
        escape=True,
        longtable=True,
        caption=stem.replace("_", " ").title(),
        label=f"tab:{stem}",
    )
    tex_path.write_text(latex, encoding="utf-8")

    print(f"Saved: {csv_path}")
    print(f"Saved: {md_path}")
    print(f"Saved: {tex_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate publication-ready tables for dynamic_v3 NS-3 campaign."
    )

    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_DIR,
        help="Directory containing summary_by_policy.csv.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    analysis_dir = args.analysis_dir.expanduser().resolve()
    summary_path = analysis_dir / "summary_by_policy.csv"
    tables_dir = analysis_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    if not summary_path.exists():
        raise FileNotFoundError(f"File not found: {summary_path}")

    summary_df = pd.read_csv(summary_path)

    table = prepare_summary(summary_df)
    ranking = prepare_ranking(table)

    save_table(table, tables_dir, "tabela_resumo_metricas")
    save_table(ranking, tables_dir, "tabela_ranking_cenarios")

    print("\n=== Tabela resumo ===")
    print(table.to_string(index=False))

    print("\n=== Ranking ===")
    print(ranking.to_string(index=False))


if __name__ == "__main__":
    main()
