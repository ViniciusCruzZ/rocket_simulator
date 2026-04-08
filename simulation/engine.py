"""Motor de simulação — trajetória 2D, ISA, empuxo×tempo, Cd(Mach), costa entre estágios."""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from core.environment import Environment, isa_speed_of_sound
from core.physics import (
    aerodynamic_force_2d,
    cd_from_mach,
    gravity_acceleration,
    thrust_at_altitude,
)
from core.rocket import MissionEvent, RocketConfig, SimulationHistory, Stage
from core.schedules import LinearSchedule1D
from simulation.integrator import integrate_ivp


def default_pitch_falcon_demo() -> LinearSchedule1D:
    """Arfagem (graus a partir da vertical em direção ao alcance +x), estilo rampa de lançamento."""
    return LinearSchedule1D(
        (
            (0.0, 0.0),
            (45.0, 0.0),
            (85.0, 6.0),
            (160.0, 14.0),
            (350.0, 24.0),
            (2500.0, 32.0),
        )
    )


@dataclass
class MissionParameters:
    coast_between_stages_s: float = 6.0
    rtol: float = 1e-9
    atol: float = 1e-12
    max_step_burn_s: float = 0.25
    max_step_coast_s: float = 1.0
    pitch_schedule: LinearSchedule1D = field(default_factory=default_pitch_falcon_demo)


def _burn_rhs(
    stage: Stage,
    env: Environment,
    cfg: RocketConfig,
    m0: float,
    mdot: float,
    t_ignition: float,
    mission: MissionParameters,
) -> Callable[[float, np.ndarray], np.ndarray]:
    cd_table = cfg.resolved_cd_mach_table()

    def fun(t: float, y: np.ndarray) -> np.ndarray:
        x, h, vx, vy = float(y[0]), float(y[1]), float(y[2]), float(y[3])
        dt_loc = t - t_ignition
        m = m0 - mdot * dt_loc
        m = max(m, m0 * 1e-6)

        p = env.pressure(h)
        rho = env.density(h)
        t_base = thrust_at_altitude(p, stage.thrust_sl_n, stage.thrust_vac_n)
        f_t = stage.thrust_schedule.eval_at(dt_loc)
        t_mag = t_base * f_t

        phi_deg = mission.pitch_schedule.eval_at(t)
        phi_rad = math.radians(phi_deg)
        tx = t_mag * math.sin(phi_rad)
        ty = t_mag * math.cos(phi_rad)

        a_sound = isa_speed_of_sound(h)
        speed = math.hypot(vx, vy)
        mach = speed / a_sound if a_sound > 1e-9 else 0.0
        cd = cd_from_mach(mach, cd_table)
        fx, fy = aerodynamic_force_2d(rho, vx, vy, cd, cfg.reference_area_m2)
        g = gravity_acceleration(h)
        ax = (tx + fx) / m
        ay = (ty + fy) / m - g
        return np.array([vx, vy, ax, ay], dtype=float)

    return fun


def _coast_rhs(
    env: Environment,
    cfg: RocketConfig,
    mass_kg: float,
) -> Callable[[float, np.ndarray], np.ndarray]:
    cd_table = cfg.resolved_cd_mach_table()

    def fun(t: float, y: np.ndarray) -> np.ndarray:
        m = float(mass_kg)
        _x, h, vx, vy = float(y[0]), float(y[1]), float(y[2]), float(y[3])
        rho = env.density(h)
        a_sound = isa_speed_of_sound(h)
        speed = math.hypot(vx, vy)
        mach = speed / a_sound if a_sound > 1e-9 else 0.0
        cd = cd_from_mach(mach, cd_table)
        fx, fy = aerodynamic_force_2d(rho, vx, vy, cd, cfg.reference_area_m2)
        g = gravity_acceleration(h)
        ax = fx / m
        ay = fy / m - g
        return np.array([vx, vy, ax, ay], dtype=float)

    return fun


def _append_segment(
    hist: SimulationHistory,
    t_seg: np.ndarray,
    sol_y: np.ndarray,
    m_seg: np.ndarray,
    cfg: RocketConfig,
) -> None:
    cd_table = cfg.resolved_cd_mach_table()
    for i in range(len(t_seg)):
        x, h, vx, vy = float(sol_y[0, i]), float(sol_y[1, i]), float(sol_y[2, i]), float(sol_y[3, i])
        speed = math.hypot(vx, vy)
        a_sound = isa_speed_of_sound(h)
        mach = speed / a_sound if a_sound > 1e-9 else 0.0
        cd = cd_from_mach(mach, cd_table)
        hist.time_s.append(float(t_seg[i]))
        hist.range_m.append(x)
        hist.altitude_m.append(h)
        hist.vx_m_s.append(vx)
        hist.vy_m_s.append(vy)
        hist.velocity_m_s.append(speed)
        hist.mach.append(mach)
        hist.cd_aero.append(cd)
        hist.mass_kg.append(float(m_seg[i]))


def _mass_during_burn(m0: float, mdot: float, t_local: np.ndarray) -> np.ndarray:
    return m0 - mdot * t_local


def run_mission(
    rocket_cfg: RocketConfig,
    env: Environment | None = None,
    mission: MissionParameters | None = None,
) -> SimulationHistory:
    """
    Ascensão 2D (x = alcance, y = altitude): estágios em sequência, costa opcional.
    Empuxo: SL/vac × agenda de fração; arrasto: Cd(Mach); atitude: agenda de arfagem.
    """
    env = env or Environment()
    mp = mission or MissionParameters()

    hist = SimulationHistory()
    y = np.array([0.0, 0.0, 0.0, 0.0], dtype=float)
    t_global = 0.0
    m_current = rocket_cfg.total_mass_at_liftoff_kg()

    for idx, stage in enumerate(rocket_cfg.stages):
        mdot = stage.mdot_kg_s()
        if mdot <= 0:
            raise ValueError(f"Estágio {stage.name}: vazão mássica inválida.")
        t_burn = stage.burn_time_s
        m0 = m_current

        sol = integrate_ivp(
            _burn_rhs(stage, env, rocket_cfg, m0, mdot, t_global, mp),
            (t_global, t_global + t_burn),
            y,
            rtol=mp.rtol,
            atol=mp.atol,
            max_step=mp.max_step_burn_s,
            dense_output=True,
        )

        if not sol.success:
            raise RuntimeError(f"Falha na integração ({stage.name}): {sol.message}")

        t_seg = sol.t
        t_loc = t_seg - t_global
        m_seg = _mass_during_burn(m0, mdot, t_loc)
        _append_segment(hist, t_seg, sol.y, m_seg, rocket_cfg)

        ev_name = "MECO" if idx == 0 and len(rocket_cfg.stages) > 1 else "SECO"
        if len(rocket_cfg.stages) == 1:
            ev_name = "burnout"
        hist.events.append(MissionEvent(float(t_seg[-1]), f"{stage.name} — {ev_name}"))

        y = np.array(
            [sol.y[0, -1], sol.y[1, -1], sol.y[2, -1], sol.y[3, -1]],
            dtype=float,
        )
        m_after_burn = m0 - stage.propellant_kg
        m_current = m_after_burn - stage.dry_mass_kg

        is_last = idx == len(rocket_cfg.stages) - 1
        if is_last:
            break

        if mp.coast_between_stages_s > 0:
            t_end = t_global + t_burn + mp.coast_between_stages_s
            sol_c = integrate_ivp(
                _coast_rhs(env, rocket_cfg, m_current),
                (t_global + t_burn, t_end),
                y,
                rtol=mp.rtol,
                atol=mp.atol,
                max_step=mp.max_step_coast_s,
                dense_output=True,
            )
            if not sol_c.success:
                raise RuntimeError(f"Falha na costa: {sol_c.message}")

            t_c = sol_c.t
            m_c = np.full_like(t_c, m_current, dtype=float)
            _append_segment(hist, t_c, sol_c.y, m_c, rocket_cfg)

            hist.events.append(
                MissionEvent(float(t_c[0]), "Costa entre estágios (aprox.)"),
            )

            y = np.array(
                [
                    sol_c.y[0, -1],
                    sol_c.y[1, -1],
                    sol_c.y[2, -1],
                    sol_c.y[3, -1],
                ],
                dtype=float,
            )

        t_global = t_global + t_burn + mp.coast_between_stages_s

    return hist
