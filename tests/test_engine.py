"""Smoke test do motor de simulação."""
from core.rocket import RocketConfig, Stage
from simulation.engine import MissionParameters, run_mission


def _tiny_two_stage() -> RocketConfig:
    s1 = Stage(
        name="S1",
        dry_mass_kg=100.0,
        propellant_kg=900.0,
        thrust_sl_n=50_000.0,
        thrust_vac_n=55_000.0,
        isp_s=280.0,
    )
    s2 = Stage(
        name="S2",
        dry_mass_kg=50.0,
        propellant_kg=150.0,
        thrust_sl_n=10_000.0,
        thrust_vac_n=12_000.0,
        isp_s=320.0,
    )
    return RocketConfig(payload_kg=10.0, stages=(s1, s2), reference_area_m2=1.0, cd=0.4)


def test_run_mission_smoke():
    hist = run_mission(_tiny_two_stage(), mission=MissionParameters(coast_between_stages_s=2.0))
    t, h, v, m = hist.as_arrays()
    full = hist.as_arrays_full()
    assert len(t) == len(h) == len(v) == len(m)
    assert len(full["range_m"]) == len(t)
    assert h[0] == 0.0
    assert full["range_m"][-1] >= 0.0
    assert len(hist.events) >= 2
