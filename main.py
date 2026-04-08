"""Entrada: simulação 2D tipo Falcon 9 (2 estágios), ISA, Cd(Mach), exportação opcional."""
from __future__ import annotations

import argparse
from pathlib import Path

from core.rocket import falcon9_class_demo_config
from simulation.engine import MissionParameters, run_mission
from simulation.export_results import export_history_csv, save_mission_figure
from visualization.plot import plot_ascent_profile


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulador de ascensão 2D (preset Falcon-like): empuxo×tempo, Cd(Mach), arfagem.",
    )
    parser.add_argument(
        "--theme",
        choices=("light", "dark"),
        default="light",
        help="Tema dos gráficos (claro ou escuro).",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        metavar="PATH",
        help="Exportar telemetria para CSV (UTF-8).",
    )
    parser.add_argument(
        "--figure",
        type=str,
        default=None,
        metavar="PATH",
        help="Salvar dashboard em PNG/PDF/SVG (extensão define o formato).",
    )
    parser.add_argument(
        "--figure-format",
        choices=("png", "pdf", "svg"),
        default=None,
        help="Formato da figura se --figure não tiver extensão reconhecida.",
    )
    args = parser.parse_args()

    rocket_cfg = falcon9_class_demo_config()
    mission = MissionParameters(coast_between_stages_s=6.0)
    history = run_mission(rocket_cfg, mission=mission)

    for ev in history.events:
        print(f"{ev.time_s:10.2f} s — {ev.name}")

    d = history.as_arrays_full()
    t = d["time_s"]
    h = d["altitude_m"]
    imax = int(h.argmax())
    r_at_max = float(d["range_m"][imax])
    print(f"\nApogeu: {h[imax]/1e3:.1f} km em t = {t[imax]:.1f} s (alcance horizontal ≈ {r_at_max/1e3:.1f} km)")

    if args.csv:
        out = export_history_csv(history, args.csv)
        print(f"\nCSV gravado: {out.resolve()}")

    if args.figure:
        path = Path(args.figure)
        fmt = args.figure_format
        if fmt is None and path.suffix.lower().lstrip(".") not in ("png", "pdf", "svg"):
            fmt = "png"
        out = save_mission_figure(
            history,
            path,
            theme=args.theme,
            title="Telemetria de ascensão (2D)",
            fmt=fmt,
        )
        print(f"Figura gravada: {out.resolve()}")

    if not args.csv and not args.figure:
        plot_ascent_profile(history, theme=args.theme)


if __name__ == "__main__":
    main()
