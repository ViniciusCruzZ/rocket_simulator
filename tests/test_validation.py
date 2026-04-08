"""Mission-level plausibility checks for the bundled Falcon-like preset."""
import numpy as np

from core.rocket import falcon9_class_demo_config
from simulation.engine import MissionParameters, run_mission


def test_falcon_preset_physical_plausibility():
    hist = run_mission(
        falcon9_class_demo_config(),
        mission=MissionParameters(coast_between_stages_s=6.0),
    )
    d = hist.as_arrays_full()
    alt = d["altitude_m"]
    v = d["speed_m_s"]
    mach = d["mach"]

    assert np.isfinite(alt).all()
    assert np.max(alt) > 1_000.0
    assert np.max(v) > 100.0
    assert np.max(mach) > 0.3
    assert len(hist.events) >= 2
