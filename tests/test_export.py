"""Exportação CSV / figura."""
import tempfile
from pathlib import Path

from core.rocket import falcon9_class_demo_config
from simulation.engine import run_mission
from simulation.export_results import export_history_csv, save_mission_figure


def test_export_csv_roundtrip_rows():
    hist = run_mission(falcon9_class_demo_config())
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.csv"
        export_history_csv(hist, p)
        text = p.read_text(encoding="utf-8")
        lines = text.strip().splitlines()
        assert lines[0].startswith("time_s")
        assert len(lines) == len(hist.time_s) + 1


def test_save_figure_png():
    hist = run_mission(falcon9_class_demo_config())
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "m.png"
        save_mission_figure(hist, p, theme="light")
        assert p.is_file()
        assert p.stat().st_size > 1000
