"""Atmosfera padrão ISA (1976), condições de voo e propriedades aerodinâmicas."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Ar seco — constantes ISA para troposfera / estratosfera inferior
_R_DRY_AIR = 287.05  # J/(kg·K)
_G0 = 9.80665
_T0 = 288.15  # K
_P0 = 101_325.0  # Pa
_LAPSE_TROP = 0.0065  # K/m


def _temperature_isa(h_m: float) -> float:
    """Temperatura [K] até ~32 km (segmentos usuais para ascensão)."""
    h = float(h_m)
    if h < 11_000.0:
        return _T0 - _LAPSE_TROP * h
    if h < 20_000.0:
        return 216.65
    if h < 32_000.0:
        return 216.65 + 0.001 * (h - 20_000.0)
    if h < 47_000.0:
        return 228.65 + 0.0028 * (h - 32_000.0)
    # Acima: retorno suave para evitar singularidades em simulações longas
    return 270.65


def _pressure_isa(h_m: float) -> float:
    """Pressão estática [Pa] — ISA por segmentos (0–47 km)."""
    h = float(np.clip(h_m, 0.0, 86_000.0))

    if h <= 11_000.0:
        t = _T0 - _LAPSE_TROP * h
        return _P0 * (t / _T0) ** (_G0 / (_R_DRY_AIR * _LAPSE_TROP))

    p11 = _pressure_isa(11_000.0)
    t11 = 216.65
    if h <= 20_000.0:
        return p11 * np.exp(-_G0 * (h - 11_000.0) / (_R_DRY_AIR * t11))

    p20 = _pressure_isa(20_000.0)
    if h <= 32_000.0:
        t = 216.65 + 0.001 * (h - 20_000.0)
        # lapse linear + integração log p
        t20 = 216.65
        return p20 * (t / t20) ** (-_G0 / (_R_DRY_AIR * 0.001))

    p32 = _pressure_isa(32_000.0)
    if h <= 47_000.0:
        t = 228.65 + 0.0028 * (h - 32_000.0)
        t32 = 228.65
        return p32 * (t / t32) ** (-_G0 / (_R_DRY_AIR * 0.0028))

    p47 = _pressure_isa(47_000.0)
    t47 = 270.65
    return p47 * np.exp(-_G0 * (h - 47_000.0) / (_R_DRY_AIR * t47))


def isa_density(h_m: float) -> float:
    """Densidade do ar [kg/m³] (ISA)."""
    h = max(0.0, float(h_m))
    t = _temperature_isa(h)
    p = _pressure_isa(h)
    return p / (_R_DRY_AIR * t)


_GAMMA_AIR = 1.4


def isa_speed_of_sound(h_m: float) -> float:
    """Velocidade do som [m/s] no ar seco (ISA), a = sqrt(gamma R T)."""
    t = _temperature_isa(max(0.0, float(h_m)))
    return float(np.sqrt(_GAMMA_AIR * _R_DRY_AIR * t))


@dataclass
class Environment:
    """Ambiente de voo: arrasto e funções de estado atmosférico."""

    cd: float = 0.35
    reference_area_m2: float = 10.5  # ~Ø3,7 m (Falcon 9)

    def density(self, altitude_m: float) -> float:
        return isa_density(altitude_m)

    def pressure(self, altitude_m: float) -> float:
        return _pressure_isa(altitude_m)
