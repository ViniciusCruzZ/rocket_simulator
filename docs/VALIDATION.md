# Validation & benchmarks

This document describes **what is verified** in code and how **order-of-magnitude** checks relate to public launch vehicle data. The simulator is **not** flight-certified software.

## Automated sanity checks (`pytest`)

| Check | Meaning |
|-------|---------|
| ISA density at sea level | ~1.225 kg/m³ (standard atmosphere) |
| Drag at zero speed | Zero force |
| Gravity vs altitude | Decreases with altitude |
| SL/vac thrust blend | Sea level → SL thrust; vacuum → vac thrust |
| Cd(Mach) table | Linear interpolation; clamp outside range |
| Speed of sound (ISA) | ~331–343 m/s near sea level |
| 2D drag | Opposes velocity vector |
| Mission smoke (toy rocket) | Integrated trajectory; non-negative range; events recorded |
| Full preset export | CSV rows match history length; PNG non-empty |

Run: `python -m pytest tests -q`

## Mission-level checks (`tests/test_validation.py`)

For the bundled **Falcon 9–like** preset, tests assert coarse physical plausibility:

- Apogee altitude and max speed are positive and finite.
- At least two flight events (e.g. staging-related).
- Max Mach exceeds transonic threshold (model exercises Cd(Mach) table).

These are **regression guards**, not guarantees of realism versus a real mission.

## Order-of-magnitude comparison (public data)

Real **Falcon 9** ascent timelines depend on payload, trajectory, and throttle — values below are **illustrative** from open sources and **must not** be interpreted as targets for this 2D educational model.

| Milestone (typical order) | Public ballpark | This repo’s preset (simulated) |
|---------------------------|-----------------|--------------------------------|
| First-stage burnout / MECO | ~2–3+ min | Similar order (depends on schedules) |
| Second-stage long burn | several minutes | Yes (2D coast + S2 burn) |
| Not modeled here | Orbit insertion, entry, landing | N/A |

**Why numbers differ:** the code uses a **planar point-mass** model, tabulated Cd(Mach), synthetic thrust and pitch schedules, and **no** official trajectory or mass properties. Use the comparison only to sanity-check that the simulation is “in the stadium,” not on the millimeter.

## How to add a stricter benchmark

1. Export CSV: `python main.py --csv out/flight.csv`
2. Overlay public **altitude vs time** or **velocity vs time** from a published plot (manually digitized) in Jupyter or another tool.
3. Document bias sources: 2D vs 3D, winds, thrust uncertainty, Cd table.

## Recording a GIF for the README (optional)

1. Run `python main.py` and interact with the matplotlib window, **or** open a saved `dashboard_preview.png` in an image viewer.
2. Use [ScreenToGif](https://www.screentogif.com/) (Windows) or `peek` (Linux) to capture a short loop.
3. Save as `assets/dashboard_demo.gif` and reference it in `README.md`.

Keep GIFs under ~2–5 MB for GitHub loading.
