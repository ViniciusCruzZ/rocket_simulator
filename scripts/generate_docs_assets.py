"""Regenerate README screenshots (run from repo root with venv activated)."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("MPLBACKEND", "Agg")

from core.rocket import falcon9_class_demo_config
from simulation.engine import MissionParameters, run_mission
from simulation.export_results import save_mission_figure


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(root, "assets")
    os.makedirs(assets, exist_ok=True)

    history = run_mission(
        falcon9_class_demo_config(),
        mission=MissionParameters(coast_between_stages_s=6.0),
    )
    save_mission_figure(
        history,
        os.path.join(assets, "dashboard_preview.png"),
        theme="light",
        title="Rocket Simulator — telemetry dashboard (2D)",
    )
    save_mission_figure(
        history,
        os.path.join(assets, "dashboard_preview_dark.png"),
        theme="dark",
        title="Rocket Simulator — telemetry dashboard (2D)",
    )
    print("Wrote assets/dashboard_preview.png and assets/dashboard_preview_dark.png")


if __name__ == "__main__":
    main()
