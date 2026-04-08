"""Forças: gravidade, arrasto 1D/2D, empuxo SL/vac, Cd(Mach)."""
from __future__ import annotations

import math

import numpy as np

_G0 = 9.80665
_EARTH_RADIUS_M = 6_371_000.0


def gravity_acceleration(altitude_m: float) -> float:
    """Aceleração gravitacional [m/s²] (esférico simples)."""
    r = _EARTH_RADIUS_M + float(altitude_m)
    return _G0 * (_EARTH_RADIUS_M / r) ** 2


def drag_force(
    rho: float,
    velocity_m_s: float,
    cd: float,
    area_m2: float,
) -> float:
    """Força de arrasto [N], oposta ao movimento (1D vertical)."""
    v = float(velocity_m_s)
    return 0.5 * rho * v * abs(v) * cd * area_m2


def thrust_at_altitude(
    pressure_pa: float,
    thrust_sl_n: float,
    thrust_vac_n: float,
    p0_pa: float = 101_325.0,
) -> float:
    """
    Empuxo interpolado entre nível do mar e vácuo (modelo linear em pressão).
    """
    p = max(float(pressure_pa), 0.0)
    w = np.clip(p / p0_pa, 0.0, 1.0)
    return thrust_vac_n + (thrust_sl_n - thrust_vac_n) * w


def cd_from_mach(mach: float, table: tuple[tuple[float, float], ...]) -> float:
    """
    Coeficiente de arrasto por interpolação linear em Mach.
    `table`: ((mach0, cd0), (mach1, cd1), ...), mach crescente.
    """
    m = float(abs(mach))
    if not table:
        raise ValueError("Tabela Cd(Mach) vazia.")
    if m <= table[0][0]:
        return float(table[0][1])
    if m >= table[-1][0]:
        return float(table[-1][1])
    for i in range(len(table) - 1):
        m0, c0 = table[i]
        m1, c1 = table[i + 1]
        if m0 <= m <= m1:
            if m1 == m0:
                return float(c0)
            t = (m - m0) / (m1 - m0)
            return float(c0 + t * (c1 - c0))
    return float(table[-1][1])


def aerodynamic_force_2d(
    rho: float,
    vx: float,
    vy: float,
    cd: float,
    area_m2: float,
) -> tuple[float, float]:
    """Vetor força de arrasto [N] (2D), oposto à velocidade."""
    vx, vy = float(vx), float(vy)
    speed = math.hypot(vx, vy)
    if speed < 1e-9:
        return 0.0, 0.0
    dyn = 0.5 * rho * speed * speed * cd * area_m2
    ux, uy = vx / speed, vy / speed
    return -dyn * ux, -dyn * uy
