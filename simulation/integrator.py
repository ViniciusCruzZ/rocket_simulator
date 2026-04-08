"""Integração de EDO — SciPy como motor principal; RK4 explícito para testes."""
from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.integrate import solve_ivp


def rk4_step(
    f: Callable[[float, np.ndarray], np.ndarray],
    t: float,
    y: np.ndarray,
    dt: float,
) -> np.ndarray:
    """Um passo RK4 (vetor estado arbitrário)."""
    k1 = f(t, y)
    k2 = f(t + 0.5 * dt, y + 0.5 * dt * k1)
    k3 = f(t + 0.5 * dt, y + 0.5 * dt * k2)
    k4 = f(t + dt, y + dt * k3)
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate_ivp(
    fun: Callable[[float, np.ndarray], np.ndarray],
    t_span: tuple[float, float],
    y0: np.ndarray,
    *,
    rtol: float = 1e-9,
    atol: float = 1e-12,
    max_step: float | None = None,
    dense_output: bool = True,
):
    """Wrapper em torno de `solve_ivp` (RK45)."""
    return solve_ivp(
        fun,
        t_span,
        y0,
        method="RK45",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        dense_output=dense_output,
    )
