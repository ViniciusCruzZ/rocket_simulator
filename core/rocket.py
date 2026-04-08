"""Foguete multiestágio — massas, empuxo, agendas e histórico."""
from __future__ import annotations

from dataclasses import dataclass, field

from core.schedules import LinearSchedule1D, thrust_flat

_G0 = 9.80665

# Tabela Cd(Mach) genérica (foguete alongado — pico transônico, queda supersônica)
DEFAULT_CD_MACH_TABLE: tuple[tuple[float, float], ...] = (
    (0.0, 0.32),
    (0.5, 0.38),
    (0.9, 0.72),
    (1.1, 0.82),
    (1.8, 0.55),
    (3.5, 0.42),
    (8.0, 0.38),
    (25.0, 0.38),
)


@dataclass
class Stage:
    """Um estágio (ex.: booster, segundo estágio)."""

    name: str
    dry_mass_kg: float
    propellant_kg: float
    thrust_sl_n: float
    thrust_vac_n: float
    isp_s: float
    thrust_schedule: LinearSchedule1D = field(default_factory=thrust_flat)

    def mdot_kg_s(self) -> float:
        return self.thrust_vac_n / (self.isp_s * _G0)

    @property
    def burn_time_s(self) -> float:
        m = self.mdot_kg_s()
        return self.propellant_kg / m if m > 0 else 0.0


@dataclass
class RocketConfig:
    """Configuração completa (payload + estágios em ordem de queima)."""

    payload_kg: float
    stages: tuple[Stage, ...]
    reference_area_m2: float = 10.5
    cd: float = 0.35
    cd_mach_table: tuple[tuple[float, float], ...] | None = None

    def __post_init__(self) -> None:
        if not self.stages:
            raise ValueError("Pelo menos um estágio é necessário.")

    def resolved_cd_mach_table(self) -> tuple[tuple[float, float], ...]:
        if self.cd_mach_table is not None:
            return self.cd_mach_table
        c = float(self.cd)
        return ((0.0, c), (30.0, c))

    def total_mass_at_liftoff_kg(self) -> float:
        return self.payload_kg + sum(s.dry_mass_kg + s.propellant_kg for s in self.stages)


def falcon9_class_demo_config() -> RocketConfig:
    """
    Ordem de grandeza compatível com Falcon 9 (valores públicos aproximados / didáticos).
    Inclui agenda de empuxo no S1 (rampa + plateau + redução próximo ao MECO) e Cd(Mach).
    """
    s1_thrust = LinearSchedule1D(
        (
            (0.0, 0.94),
            (4.0, 1.0),
            (125.0, 1.0),
            (132.0, 0.38),
            (1_000.0, 0.38),
        )
    )
    first = Stage(
        name="S1 (booster)",
        dry_mass_kg=22_200.0,
        propellant_kg=395_700.0,
        thrust_sl_n=7_607_000.0,
        thrust_vac_n=8_227_000.0,
        isp_s=282.0,
        thrust_schedule=s1_thrust,
    )
    second = Stage(
        name="S2",
        dry_mass_kg=4_000.0,
        propellant_kg=107_500.0,
        thrust_sl_n=845_000.0,
        thrust_vac_n=934_000.0,
        isp_s=348.0,
        thrust_schedule=thrust_flat(),
    )
    return RocketConfig(
        payload_kg=15_000.0,
        stages=(first, second),
        reference_area_m2=10.5,
        cd=0.32,
        cd_mach_table=DEFAULT_CD_MACH_TABLE,
    )


@dataclass
class MissionEvent:
    time_s: float
    name: str


@dataclass
class SimulationHistory:
    time_s: list[float] = field(default_factory=list)
    altitude_m: list[float] = field(default_factory=list)
    range_m: list[float] = field(default_factory=list)
    velocity_m_s: list[float] = field(default_factory=list)
    vx_m_s: list[float] = field(default_factory=list)
    vy_m_s: list[float] = field(default_factory=list)
    mach: list[float] = field(default_factory=list)
    cd_aero: list[float] = field(default_factory=list)
    mass_kg: list[float] = field(default_factory=list)
    events: list[MissionEvent] = field(default_factory=list)

    def as_arrays(self):
        import numpy as np

        return (
            np.array(self.time_s),
            np.array(self.altitude_m),
            np.array(self.velocity_m_s),
            np.array(self.mass_kg),
        )

    def as_arrays_full(self):
        """Séries completas para exportação e análise 2D."""
        import numpy as np

        return {
            "time_s": np.array(self.time_s),
            "range_m": np.array(self.range_m),
            "altitude_m": np.array(self.altitude_m),
            "vx_m_s": np.array(self.vx_m_s),
            "vy_m_s": np.array(self.vy_m_s),
            "speed_m_s": np.array(self.velocity_m_s),
            "mach": np.array(self.mach),
            "cd": np.array(self.cd_aero),
            "mass_kg": np.array(self.mass_kg),
        }
