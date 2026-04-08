"""Testes de forças e modelo atmosférico."""
import numpy as np

from core.environment import isa_density, isa_speed_of_sound
from core.physics import (
    aerodynamic_force_2d,
    cd_from_mach,
    drag_force,
    gravity_acceleration,
    thrust_at_altitude,
)


def test_isa_sea_level_density():
    rho = isa_density(0.0)
    assert 1.2 < rho < 1.23


def test_drag_zero_at_rest():
    assert drag_force(1.225, 0.0, 0.5, 10.0) == 0.0


def test_gravity_decreases_with_altitude():
    g0 = gravity_acceleration(0.0)
    g100 = gravity_acceleration(100_000.0)
    assert g100 < g0


def test_thrust_blend_sea_to_vacuum():
    t_sl = 1_000_000.0
    t_vac = 1_200_000.0
    at_sl = thrust_at_altitude(101_325.0, t_sl, t_vac)
    at_vac = thrust_at_altitude(0.0, t_sl, t_vac)
    assert np.isclose(at_sl, t_sl)
    assert np.isclose(at_vac, t_vac)


def test_isa_speed_of_sound_positive():
    a0 = isa_speed_of_sound(0.0)
    assert 330 < a0 < 345


def test_cd_from_mach_interpolation():
    table = ((0.0, 0.3), (1.0, 0.6), (2.0, 0.5))
    assert np.isclose(cd_from_mach(0.0, table), 0.3)
    assert np.isclose(cd_from_mach(1.0, table), 0.6)
    assert cd_from_mach(3.0, table) == 0.5


def test_aero_force_2d_opposes_velocity():
    fx, fy = aerodynamic_force_2d(1.2, 100.0, 0.0, 0.5, 2.0)
    assert fx < 0 and fy == 0.0
