# Rocket Simulator

**2D ascent** simulator (horizontal range × altitude) for multi-stage rockets: **ISA** atmosphere, **time-dependent thrust** (per-stage schedule) multiplied by **sea-level / vacuum** blending, tabulated **Cd(Mach)**, **pitch program** (angle from vertical vs mission time), and **SciPy** integration (`solve_ivp`).

**Disclaimer:** the “Falcon 9-like” preset uses **public, order-of-magnitude** numbers for education, not official flight data. The model is **planar 2D** (point mass), with no orbit or 6DOF attitude dynamics.

## Features

- **ISA atmosphere** — density, pressure, and **speed of sound** for Mach number.
- **Multi-stage** — sequential burn, dry-mass separation, and configurable **coast** (MECO → second-stage style).
- **Thrust** — **fraction × time relative to stage** (`LinearSchedule1D`) × instantaneous SL/vac thrust (local pressure).
- **Drag** — interpolated **Cd(Mach)**; force opposite the velocity vector in 2D.
- **Pitch** — mission time → degrees from vertical toward +x downrange (`MissionParameters.pitch_schedule`).
- **Visualization** — dashboard (altitude, range, |v| + Mach, mass, x–y trajectory), light/dark theme.
- **Export** — CSV and PNG/PDF/SVG figures (`simulation/export_results.py`).
- **Tests** — `pytest` under `tests/`.

## Project layout

| Path | Contents |
|------|----------|
| `core/schedules.py` | Linear schedules (thrust, pitch) |
| `core/physics.py` | Gravity, 2D drag, SL/vac thrust, Cd(Mach) |
| `core/environment.py` | ISA, density, speed of sound |
| `core/rocket.py` | Stages, Falcon-like preset, `SimulationHistory` |
| `simulation/engine.py` | `run_mission`, `MissionParameters` |
| `simulation/integrator.py` | `solve_ivp` + auxiliary RK4 |
| `simulation/export_results.py` | CSV and figure export |
| `visualization/plot.py` | 2D dashboard |
| `api/` | Placeholder for HTTP API (not implemented) |
| `main.py` | CLI: run, theme, `--csv`, `--figure` |
| `tests/` | Automated tests |

## Requirements

- Python 3.10+ recommended  
- Dependencies in `requirements.txt`: NumPy, SciPy, Matplotlib, Pytest

## Setup

```bash
python -m venv venv
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS:**

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

From the repo root (with `venv` activated):

```bash
python main.py
python main.py --theme dark
python main.py --csv out/telemetry.csv
python main.py --figure out/dashboard.png
python main.py --csv out/data.csv --figure out/dashboard.pdf --theme dark
```

Without `--csv` or `--figure`, the app opens the interactive dashboard. A figure file is only written when `--figure` is passed.

## Tests

```bash
python -m pytest tests -q
```

## Model limitations

- **Planar 2D** — no orbit, 3D body axis, or real attitude control.
- **Thrust** aligned with scalar pitch (no yaw/side force).
- **Cd(Mach)** and areas are generic; no wind-tunnel data.

Possible next steps: HTTP API in `api/main.py`, 6DOF, or thrust curves loaded from files.
