# Assets

Versioned images for the main **README** and docs.

| File | Description |
|------|---------------|
| `dashboard_preview.png` | Light-theme dashboard (GitHub-friendly). |
| `dashboard_preview_dark.png` | Same simulation, dark theme. |

**Regenerate** (from repo root, venv activated):

```bash
python scripts/generate_docs_assets.py
```

Requires `MPLBACKEND=Agg` for headless runs (the script sets it).
