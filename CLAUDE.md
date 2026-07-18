# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

GTA Online vehicle equivalencies database: a single React/Vite app for browsing,
filtering, and exporting 795 vehicles, plus a Python data pipeline that produces
the CSV the app consumes. Everything runs client-side — there is no backend.

- Repo branch: `master`. Remote: `github.com/reynaldoivory/gta-online-database`.
- This repo also sits at `apps/gta-vehicle-database/` inside the `~/projects`
  npm-workspaces monorepo (matched by its `apps/*` glob), but it syncs through
  its **own** remote. The inner React app (`GTA-Vehicle-Database-App/`) is
  **not** a workspace — it needs its own `npm install` inside that directory.

## Commands

### React app (`GTA-Vehicle-Database-App/`)

```bash
cd GTA-Vehicle-Database-App
npm install        # first time — the app is not part of any npm workspace
npm run dev        # Vite dev server on http://localhost:3000 (vite.config.js)
npm run build      # production build → dist/
npm run preview    # serve the production build
npm run lint       # ESLint 9 flat config — 0 errors (2 complexity warnings tolerated)
```

ESLint (`eslint.config.js`, flat config) covers `src/**` (React 18 JSX,
browser globals, react-hooks + react-refresh + jsx-uses-vars) and the
`*.config.js` files (Node globals). It is a **hard CI gate** — keep it at 0
errors. Inner components must be declared at module scope, not inside render
(`react-hooks/static-components`).

The root `package.json` scripts (`npm run dev` / `build` / `preview` /
`install:app` from the repo root) just `cd GTA-Vehicle-Database-App` and run
the same commands.

### Python data scripts (`scripts/`)

```bash
pip install -r requirements.txt   # requests, beautifulsoup4, pandas, openpyxl
python scripts/gta_vehicle_scraper.py        # scrape GTABase.com (slow, rate-limited)
python scripts/vehicle_merger.py data/a.csv data/b.csv   # merge/dedupe, renumbers Vehicle_ID
python scripts/vehicle_entry_helper.py       # interactive manual entry
python scripts/convert_to_xlsx.py            # CSV → Excel
```

CI runs the data-validation job on **Python 3.11**.

## Architecture

### Data flow

1. `GTA-Vehicle-Database-App/public/gta_vehicles_complete.csv` is a full
   795-row copy of `data/gta_vehicles_complete.csv` (the master dataset).
   When the master changes, re-copy it into the app's `public/` dir.
2. At runtime `src/App.jsx` fetches `/gta_vehicles_complete.csv` and parses it
   with PapaParse, normalizing rows into the field names the components use
   (`ID`, `Make`, `Model`, `Real_World`, boolean flags, …).
3. React state + `useMemo` handle filtering/sorting; components live in
   `src/components/` (FilterPanel, VehicleTable, StatsChart, DetailModal,
   ExportButton).

### CSV schema (single source of truth)

```
Vehicle_ID,GTA_Make,GTA_Model,Class,Real_World_Make,Real_World_Model,
Price,Drivetrain,Shop,Top_Speed_MPH,Lap_Time,Weaponized,HSW,Imani,Bennys,Arena,Notes
```

- Booleans are `TRUE`/`FALSE` (all caps). The app also accepts `Yes`/`No`
  case-insensitively for robustness.
- `Vehicle_ID` is zero-padded 3 digits; `vehicle_merger.py` renumbers it.
- Price is numeric only (no `$` or commas).

### Styling

Tailwind CSS 3 with custom component classes in `src/index.css` (`.card`,
`.btn-primary`, `.btn-secondary`, `.input-dark`, `.select-dark`, `.badge`,
`.badge-hsw`, `.badge-imani`, `.badge-wpn`).

## CI (.github/workflows/ci.yml)

Triggers on push/PR to `master`. Jobs: install → lint → build (uploads
`dist/` artifact), plus a data-validation job that loads every `data/*.csv`
with pandas on Python 3.11 (empty-file, column, and duplicate checks). The
lint job runs the app's ESLint and now **fails** on lint errors (previously a
`|| echo` swallowed them — harmless when no lint script existed, a gap once
one does).
Renovate manages dependency updates (`renovate.json`).

## Conventions

- Semantic commit prefixes (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`).
- `package-lock.json` files are tracked (CI uses `npm ci`).
- Husky + lint-staged run on pre-commit (currently only a CSV-change echo).

## Legacy files (do not build on these)

The root-level Python generators — `build_app.py`, `create_gta_app.py`,
`master_deploy.py`, `setup_project.py` — are historical one-shot scaffolding
tools from the project's origin. `LEGACY_TOOLKIT_README.md` documents that
era. Prefer `scripts/` for all data work.
