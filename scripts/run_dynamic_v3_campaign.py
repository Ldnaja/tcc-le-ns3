#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List


DEFAULT_NS3_DIR = Path.home() / "simulators/ns-allinone-3.47/ns-3.47"
DEFAULT_RESULTS_ROOT = Path.home() / "tcc-leo-ns3/results/dynamic_v3_campaign"

POLICIES = [
    "equal",
    "round_robin",
    "longest_queue_first",
    "greedy_backlog",
    "proportional_fair",
]


@dataclass(frozen=True)
class Scenario:
    name: str
    base_user_rate_mbps: float
    hotspot_user_rate_mbps: float
    description: str


SCENARIOS: Dict[str, Scenario] = {
    "light": Scenario(
        name="light",
        base_user_rate_mbps=0.3,
        hotspot_user_rate_mbps=1.0,
        description="Carga leve, com folga de capacidade.",
    ),
    "medium": Scenario(
        name="medium",
        base_user_rate_mbps=0.5,
        hotspot_user_rate_mbps=2.0,
        description="Cenário principal, com hotspot moderado.",
    ),
    "heavy_controlled": Scenario(
        name="heavy_controlled",
        base_user_rate_mbps=0.6,
        hotspot_user_rate_mbps=2.5,
        description="Carga pesada controlada, levemente acima da capacidade nominal.",
    ),
    "extreme": Scenario(
        name="extreme",
        base_user_rate_mbps=0.8,
        hotspot_user_rate_mbps=3.0,
        description="Teste extremo de limite, não recomendado como cenário principal.",
    ),
}


COMMON_ARGS = {
    "nBeams": 19,
    "nUsersPerBeam": 4,
    "simTime": 120,
    "hotspotBeam": 0,
    "totalChannels": 48,
    "maxChannelsPerBeam": 6,
    "minChannelsPerActiveBeam": 1,
    "channelCapacityMbps": 1.1,
}


def run_command(command: List[str], cwd: Path, dry_run: bool) -> None:
    printable = " ".join(command)
    print(f"\n$ {printable}")

    if dry_run:
        return

    subprocess.run(command, cwd=cwd, check=True)


def build_ns3(ns3_dir: Path, dry_run: bool) -> None:
    run_command(["./ns3", "build"], cwd=ns3_dir, dry_run=dry_run)


def copy_required_outputs(ns3_dir: Path, output_dir: Path, policy: str, dry_run: bool) -> None:
    files = {
        "leo-multibeam-dynamic-history.csv": f"history_{policy}.csv",
        "leo-multibeam-dynamic-final.csv": f"final_{policy}.csv",
        "leo-multibeam-dynamic-summary.txt": f"summary_{policy}.txt",
    }

    for src_name, dst_name in files.items():
        src = ns3_dir / src_name
        dst = output_dir / dst_name

        print(f"Copying {src} -> {dst}")

        if dry_run:
            continue

        if not src.exists():
            raise FileNotFoundError(f"Expected output not found: {src}")

        shutil.copy2(src, dst)


def run_policy(
    ns3_dir: Path,
    results_root: Path,
    scenario: Scenario,
    policy: str,
    dry_run: bool,
) -> None:
    scenario_dir = results_root / scenario.name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    run_args = [
        "scratch/leo-multibeam-dynamic",
        f"--policy={policy}",
        f"--nBeams={COMMON_ARGS['nBeams']}",
        f"--nUsersPerBeam={COMMON_ARGS['nUsersPerBeam']}",
        f"--simTime={COMMON_ARGS['simTime']}",
        f"--hotspotBeam={COMMON_ARGS['hotspotBeam']}",
        f"--baseUserRateMbps={scenario.base_user_rate_mbps}",
        f"--hotspotUserRateMbps={scenario.hotspot_user_rate_mbps}",
        f"--totalChannels={COMMON_ARGS['totalChannels']}",
        f"--maxChannelsPerBeam={COMMON_ARGS['maxChannelsPerBeam']}",
        f"--minChannelsPerActiveBeam={COMMON_ARGS['minChannelsPerActiveBeam']}",
        f"--channelCapacityMbps={COMMON_ARGS['channelCapacityMbps']}",
    ]

    ns3_run_arg = " ".join(run_args)

    print("\n" + "=" * 80)
    print(f"Scenario: {scenario.name}")
    print(f"Policy:   {policy}")
    print("=" * 80)

    run_command(["./ns3", "run", ns3_run_arg], cwd=ns3_dir, dry_run=dry_run)
    copy_required_outputs(ns3_dir, scenario_dir, policy, dry_run=dry_run)


def write_campaign_metadata(
    results_root: Path,
    scenarios: List[Scenario],
    policies: List[str],
    dry_run: bool,
) -> None:
    metadata = {
        "version": "dynamic_v3",
        "common_args": COMMON_ARGS,
        "policies": policies,
        "scenarios": [asdict(s) for s in scenarios],
        "notes": (
            "Cenários light, medium e heavy_controlled são recomendados para análise principal. "
            "O cenário extreme é teste de limite."
        ),
    }

    path = results_root / "campaign_metadata.json"

    print(f"\nWriting campaign metadata: {path}")

    if dry_run:
        print(json.dumps(metadata, indent=2))
        return

    results_root.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run NS-3 dynamic_v3 LEO multibeam campaigns."
    )

    parser.add_argument(
        "--ns3-dir",
        type=Path,
        default=Path(os.environ.get("NS3_DIR", DEFAULT_NS3_DIR)),
        help="Path to the ns-3 root directory.",
    )

    parser.add_argument(
        "--results-root",
        type=Path,
        default=DEFAULT_RESULTS_ROOT,
        help="Directory where campaign results will be stored.",
    )

    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["light", "medium", "heavy_controlled"],
        choices=list(SCENARIOS.keys()),
        help="Scenarios to run.",
    )

    parser.add_argument(
        "--policies",
        nargs="+",
        default=POLICIES,
        choices=POLICIES,
        help="Policies to run.",
    )

    parser.add_argument(
        "--include-extreme",
        action="store_true",
        help="Also include the extreme stress scenario.",
    )

    parser.add_argument(
        "--build",
        action="store_true",
        help="Run ./ns3 build before the campaign.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ns3_dir = args.ns3_dir.expanduser().resolve()
    results_root = args.results_root.expanduser().resolve()

    if not ns3_dir.exists():
        raise FileNotFoundError(f"NS-3 directory not found: {ns3_dir}")

    scenario_names = list(args.scenarios)

    if args.include_extreme and "extreme" not in scenario_names:
        scenario_names.append("extreme")

    scenarios = [SCENARIOS[name] for name in scenario_names]
    policies = list(args.policies)

    print(f"NS-3 dir:      {ns3_dir}")
    print(f"Results root:  {results_root}")
    print(f"Scenarios:     {scenario_names}")
    print(f"Policies:      {policies}")
    print(f"Dry run:       {args.dry_run}")

    results_root.mkdir(parents=True, exist_ok=True)

    write_campaign_metadata(results_root, scenarios, policies, dry_run=args.dry_run)

    if args.build:
        build_ns3(ns3_dir, dry_run=args.dry_run)

    for scenario in scenarios:
        for policy in policies:
            run_policy(
                ns3_dir=ns3_dir,
                results_root=results_root,
                scenario=scenario,
                policy=policy,
                dry_run=args.dry_run,
            )

    print("\nCampaign finished.")
    print(f"Results saved under: {results_root}")


if __name__ == "__main__":
    main()
