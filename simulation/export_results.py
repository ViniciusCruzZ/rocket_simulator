"""Exportação CSV e figuras (PNG/PDF)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from core.rocket import SimulationHistory
    from visualization.plot import Theme


def export_history_csv(history: SimulationHistory, path: str | Path) -> Path:
    """Grava telemetria em CSV (UTF-8)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = history.as_arrays_full()
    n = len(data["time_s"])
    fieldnames = [
        "time_s",
        "range_km",
        "altitude_km",
        "vx_m_s",
        "vy_m_s",
        "speed_m_s",
        "mach",
        "cd",
        "mass_kg",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for i in range(n):
            w.writerow(
                {
                    "time_s": f"{float(data['time_s'][i]):.6f}",
                    "range_km": f"{float(data['range_m'][i]) / 1000.0:.6f}",
                    "altitude_km": f"{float(data['altitude_m'][i]) / 1000.0:.6f}",
                    "vx_m_s": f"{float(data['vx_m_s'][i]):.6f}",
                    "vy_m_s": f"{float(data['vy_m_s'][i]):.6f}",
                    "speed_m_s": f"{float(data['speed_m_s'][i]):.6f}",
                    "mach": f"{float(data['mach'][i]):.6f}",
                    "cd": f"{float(data['cd'][i]):.6f}",
                    "mass_kg": f"{float(data['mass_kg'][i]):.6f}",
                }
            )
    return path


FigureFormat = Literal["png", "pdf", "svg"]


def save_mission_figure(
    history: SimulationHistory,
    path: str | Path,
    *,
    theme: "Theme" = "light",
    title: str = "Telemetria de ascensão (2D)",
    fmt: FigureFormat | None = None,
) -> Path:
    """Salva o dashboard em arquivo (formato inferido pela extensão ou `fmt`)."""
    from visualization.plot import plot_ascent_profile

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower().lstrip(".")
    if fmt is not None:
        out_fmt: FigureFormat = fmt
        if suffix not in ("png", "pdf", "svg"):
            path = path.with_suffix("." + out_fmt)
    elif suffix in ("png", "pdf", "svg"):
        out_fmt = suffix  # type: ignore[assignment]
    else:
        out_fmt = "png"
        path = path.with_suffix(".png")

    fig, _axes = plot_ascent_profile(history, title=title, show=False, theme=theme)
    fig.savefig(path, format=out_fmt, dpi=150, bbox_inches="tight")
    import matplotlib.pyplot as plt

    plt.close(fig)
    return path
