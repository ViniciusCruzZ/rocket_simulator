"""Gráficos de telemetria — dashboard 2D (alcance, Mach, trajetória)."""
from __future__ import annotations

from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects as pe
from matplotlib.patches import FancyBboxPatch

from core.rocket import SimulationHistory

Theme = Literal["light", "dark"]

_COLORS = {
    "altitude": "#2563eb",
    "range": "#7c3aed",
    "velocity": "#0891b2",
    "mass": "#c2410c",
    "mach": "#db2777",
    "event_line": "#94a3b8",
    "event_line_dark": "#64748b",
    "track": "#0d9488",
}


def _rc_context(theme: Theme) -> dict:
    if theme == "dark":
        return {
            "figure.facecolor": "#0f1117",
            "axes.facecolor": "#161b22",
            "axes.edgecolor": "#30363d",
            "axes.labelcolor": "#e6edf3",
            "axes.titlecolor": "#f0f6fc",
            "text.color": "#e6edf3",
            "xtick.color": "#8b949e",
            "ytick.color": "#8b949e",
            "grid.color": "#30363d",
            "grid.linewidth": 0.9,
            "grid.alpha": 0.9,
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Segoe UI",
                "Inter",
                "DejaVu Sans",
                "Helvetica Neue",
                "Arial",
            ],
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "figure.titlesize": 15,
            "figure.titleweight": "600",
        }
    return {
        "figure.facecolor": "#f0f2f5",
        "axes.facecolor": "#ffffff",
        "axes.edgecolor": "#e2e8f0",
        "axes.labelcolor": "#334155",
        "axes.titlecolor": "#0f172a",
        "text.color": "#334155",
        "xtick.color": "#64748b",
        "ytick.color": "#64748b",
        "grid.color": "#e2e8f0",
        "grid.linewidth": 0.9,
        "grid.alpha": 1.0,
        "font.family": "sans-serif",
        "font.sans-serif": [
            "Segoe UI",
            "Inter",
            "DejaVu Sans",
            "Helvetica Neue",
            "Arial",
        ],
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.titlesize": 15,
        "figure.titleweight": "600",
    }


def _spines_clean(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(ax.xaxis.label.get_color())
    ax.spines["bottom"].set_color(ax.xaxis.label.get_color())


def _summary_lines(
    t_s: np.ndarray,
    alt_m: np.ndarray,
    range_m: np.ndarray,
    v_m_s: np.ndarray,
    m_kg: np.ndarray,
    mach: np.ndarray,
) -> tuple[str, ...]:
    imax = int(np.argmax(alt_m))
    t_end = float(t_s[-1])
    r_max = float(np.max(range_m)) if len(range_m) else 0.0
    mach_max = float(np.max(mach)) if len(mach) else 0.0
    lines = (
        f"Apogeu: {alt_m[imax] / 1_000.0:.1f} km  ·  Alcance @ apogeu: {range_m[imax] / 1_000.0:.1f} km",
        f"|v| máx: {np.max(v_m_s):.0f} m/s  ·  Mach máx: {mach_max:.2f}",
        f"Duração sim.: {t_end:.0f} s  ·  Alcance final: {r_max / 1_000.0:.1f} km  ·  Massa final: {m_kg[-1] / 1_000.0:.2f} t",
    )
    return lines


def plot_ascent_profile(
    history: SimulationHistory,
    *,
    title: str = "Telemetria de ascensão (modelo 2D)",
    show: bool = True,
    theme: Theme = "light",
):
    """
    Dashboard: resumo, altitude, alcance, |v| + Mach, massa, trajetória (x–y).
    """
    d = history.as_arrays_full()
    t_s = d["time_s"]
    alt_m = d["altitude_m"]
    range_m = d["range_m"]
    v_m_s = d["speed_m_s"]
    m_kg = d["mass_kg"]
    mach = d["mach"]

    ev_line = _COLORS["event_line_dark"] if theme == "dark" else _COLORS["event_line"]

    with plt.rc_context(_rc_context(theme)):
        fig = plt.figure(figsize=(11, 13))
        gs = fig.add_gridspec(
            6,
            1,
            height_ratios=[0.11, 1.0, 1.0, 1.0, 1.0, 0.95],
            hspace=0.24,
            left=0.09,
            right=0.94,
            top=0.94,
            bottom=0.05,
        )
        ax_card = fig.add_subplot(gs[0, 0])
        ax_h = fig.add_subplot(gs[1, 0])
        ax_r = fig.add_subplot(gs[2, 0], sharex=ax_h)
        ax_v = fig.add_subplot(gs[3, 0], sharex=ax_h)
        ax_m = fig.add_subplot(gs[4, 0], sharex=ax_h)
        ax_tr = fig.add_subplot(gs[5, 0])

        fig.suptitle(title, y=0.98)

        ax_card.set_axis_off()
        card_bg = "#1e293b" if theme == "dark" else "#ffffff"
        card_edge = "#334155" if theme == "dark" else "#e2e8f0"
        summary = _summary_lines(t_s, alt_m, range_m, v_m_s, m_kg, mach)
        card = FancyBboxPatch(
            (0.01, 0.1),
            0.98,
            0.8,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            transform=ax_card.transAxes,
            facecolor=card_bg,
            edgecolor=card_edge,
            linewidth=1,
            zorder=0,
        )
        ax_card.add_patch(card)
        txt_color = "#e2e8f0" if theme == "dark" else "#1e293b"
        ax_card.text(
            0.04,
            0.58,
            "  ·  ".join(summary[:2]),
            transform=ax_card.transAxes,
            fontsize=9.5,
            va="center",
            color=txt_color,
            linespacing=1.35,
        )
        ax_card.text(
            0.04,
            0.22,
            summary[2],
            transform=ax_card.transAxes,
            fontsize=8.8,
            va="center",
            color="#94a3b8" if theme == "dark" else "#64748b",
        )

        alt_km = alt_m / 1_000.0
        rng_km = range_m / 1_000.0
        mass_t = m_kg / 1_000.0

        ax_h.fill_between(t_s, 0, alt_km, alpha=0.12, color=_COLORS["altitude"], linewidth=0)
        (line_h,) = ax_h.plot(t_s, alt_km, color=_COLORS["altitude"], lw=2.0, solid_capstyle="round")
        if theme == "light":
            line_h.set_path_effects([pe.withStroke(linewidth=3.5, foreground="white", alpha=0.35)])
        ax_h.set_title("Altitude", loc="left", fontweight="600", pad=8)
        ax_h.set_ylabel("km")
        ax_h.grid(True, axis="y", linestyle="-", alpha=0.95)
        _spines_clean(ax_h)
        ax_h.tick_params(labelbottom=False)

        ax_r.fill_between(t_s, 0, rng_km, alpha=0.1, color=_COLORS["range"], linewidth=0)
        ax_r.plot(t_s, rng_km, color=_COLORS["range"], lw=2.0, solid_capstyle="round")
        ax_r.set_title("Alcance (downrange)", loc="left", fontweight="600", pad=8)
        ax_r.set_ylabel("km")
        ax_r.grid(True, axis="y", linestyle="-", alpha=0.95)
        _spines_clean(ax_r)
        ax_r.tick_params(labelbottom=False)

        (line_v,) = ax_v.plot(t_s, v_m_s, color=_COLORS["velocity"], lw=2.0, solid_capstyle="round")
        if theme == "light":
            line_v.set_path_effects([pe.withStroke(linewidth=3.5, foreground="white", alpha=0.35)])
        ax_v.set_title("Velocidade (módulo)", loc="left", fontweight="600", pad=8)
        ax_v.set_ylabel("|v| (m/s)")
        ax_v.grid(True, axis="y", linestyle="-", alpha=0.95)
        _spines_clean(ax_v)
        ax_v.tick_params(labelbottom=False)

        ax_mach = ax_v.twinx()
        ax_mach.plot(t_s, mach, color=_COLORS["mach"], lw=1.4, ls="-", alpha=0.9)
        ax_mach.set_ylabel("Mach", color=_COLORS["mach"])
        ax_mach.tick_params(axis="y", labelcolor=_COLORS["mach"])
        ax_mach.spines["top"].set_visible(False)

        ax_m.plot(t_s, mass_t, color=_COLORS["mass"], lw=2.0, solid_capstyle="round")
        ax_m.set_title("Massa", loc="left", fontweight="600", pad=8)
        ax_m.set_ylabel("t")
        ax_m.set_xlabel("Tempo de missão (s)")
        ax_m.grid(True, axis="y", linestyle="-", alpha=0.95)
        _spines_clean(ax_m)

        ax_tr.plot(
            rng_km,
            alt_km,
            color=_COLORS["track"],
            lw=1.8,
            solid_capstyle="round",
        )
        ax_tr.set_aspect("equal", adjustable="datalim")
        ax_tr.set_title("Trajetória (alcance × altitude)", loc="left", fontweight="600", pad=8)
        ax_tr.set_xlabel("Alcance (km)")
        ax_tr.set_ylabel("Altitude (km)")
        ax_tr.grid(True, linestyle="-", alpha=0.4)
        _spines_clean(ax_tr)

        time_axes = (ax_h, ax_r, ax_v, ax_m)
        legend_handles = []
        for ev in history.events:
            for ax in time_axes:
                ax.axvline(
                    ev.time_s,
                    color=ev_line,
                    ls=(0, (4, 4)),
                    lw=1.15,
                    alpha=0.85,
                    zorder=1,
                )
            (dummy,) = ax_h.plot([], [], color=ev_line, ls=(0, (4, 4)), lw=1.15, label=ev.name)
            legend_handles.append(dummy)

        if legend_handles:
            leg = ax_h.legend(
                handles=legend_handles,
                loc="upper left",
                frameon=True,
                fancybox=True,
                framealpha=0.92 if theme == "light" else 0.88,
                fontsize=8,
                title="Eventos",
                title_fontsize=9,
                borderaxespad=0.6,
            )
            leg.get_frame().set_edgecolor(card_edge)

        if show:
            plt.show()

        axes = (ax_h, ax_r, ax_v, ax_m, ax_tr)
        return fig, axes
