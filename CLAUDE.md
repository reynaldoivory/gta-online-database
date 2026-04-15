# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a GTA Online vehicle database — a data management toolkit (Python scripts) paired with a React/Vite frontend for browsing, filtering, and exporting vehicle data. The primary data source is CSV files that are loaded at runtime by the frontend.

## Commands

### Frontend (Active App — `app/GTA-Vehicle-App/`)

```bash
# Install dependencies (first time)
npm run install:app          # from root, OR:
cd app/GTA-Vehicle-App && npm install

# Development server (runs on http://localhost:5173)
npm run dev                  # from root

# Production build
npm run build                # from root

# Preview production build
npm run preview              # from root
```

The root `package.json` scripts all delegate to `app/GTA-Vehicle-App/`.

### Python Data Scripts (`scripts/`)

```bash
# Scrape vehicle data from GTABase.com (~30-40 min, 2s rate limit)
pip install requests beautifulsoup4 lxml
python scripts/gta_vehicle_scraper.py

# Merge/deduplicate CSV files (deduplicates on GTA_Model, renumbers Vehicle_ID)
python scripts/vehicle_merger.py data/file1.csv data/file2.csv ...

# Interactive manual entry CLI
python scripts/vehicle_entry_helper.py

# Check which vehicles have livery options
python scripts/livery_vehicle_checker.py

# Convert database to Excel
python scripts/convert_to_xlsx.py
```

## Architecture

### Two React Apps (Important)

There are **two separate React apps** in this repo with different schemas and feature sets:

| App | Location | Dev Port | Features |
|-----|----------|----------|----------|
| Simple (active) | `app/GTA-Vehicle-App/` | 5173 | Pagination (100/page), livery filter, single-file component |
| Feature-rich | `GTA-Vehicle-Database-App/` | 3000 | Filters panel, stats charts (Recharts), detail modal, CSV/ZIP export |

The root `package.json` `dev`/`build`/`preview` scripts point to `app/GTA-Vehicle-App/`. The `GTA-Vehicle-Database-App/` is a more complete standalone version but is not wired to the root scripts.

### Data Flow

CSV files live in `public/data/` within each app (served as static assets). At runtime:
1. `App.jsx` fetches `/data/gta_vehicles_complete.csv` via the browser `fetch` API
2. PapaParse parses CSV → JavaScript objects
3. React state manages the full dataset, with `useMemo` for filtered/sorted views
4. No backend — everything runs client-side

The `app/GTA-Vehicle-App` also loads `vehicles_with_liveries.json` from `public/data/` to show a livery filter toggle.

### Two CSV Schemas

The two apps use **different column names** for the same data:

| `data/gta_vehicles_complete.csv` (Python scripts output) | `data/final_database.csv` (feature-rich app) |
|---|---|
| `Vehicle_ID`, `GTA_Make`, `GTA_Model` | `ID`, `Make`, `Model` |
| `Real_World_Make`, `Real_World_Model` | `Real_World` (combined) |
| Booleans: `TRUE`/`FALSE` | Booleans: `Yes`/`No` |
| `Lap_Time`, `Bennys`, `Arena` fields | `Acceleration`, `Handling`, `Tags` fields |

The Python `vehicle_merger.py` outputs to the `gta_vehicles_complete.csv` schema. The `GTA-Vehicle-Database-App/App.jsx` reads using the `final_database.csv` schema (field names like `Make`, `Model`, `Real_World`).

### Styling

Tailwind CSS with custom component classes defined in `src/index.css`:
- `.card` — dark frosted-glass panel
- `.btn-primary` / `.btn-secondary` — purple/gray buttons
- `.input-dark` / `.select-dark` — dark-themed inputs
- `.badge`, `.badge-hsw`, `.badge-imani`, `.badge-wpn` — colored pill badges

Custom Tailwind color palette under `gta.*` (dark, purple, blue, orange, green, red, gold) in `tailwind.config.js`.

## Data Validation Rules

When editing or generating CSV data, these rules must be followed:

- **Price**: Numeric only (`2765000`, not `$2,765,000`)
- **Booleans**: `TRUE`/`FALSE` (all caps) in `gta_vehicles_complete.csv` format; `Yes`/`No` in `final_database.csv` format
- **Drivetrain**: `AWD`, `RWD`, `FWD`, or `N/A` (uppercase)
- **Shop**: `Legendary`, `Southern`, `Warstock`, `Bennys`, `Arena`, `Reward`, `Pegasus` (capitalize first letter)
- **Tags** (final_database format): semicolon-separated, e.g. `Hypercar;Classic`
- **Vehicle_ID**: Zero-padded 3 digits (`001`–`792`); `vehicle_merger.py` auto-renumbers

Valid vehicle classes: Super, Sports, Sports Classic, Muscle, Sedan, Coupe, Compact, SUV, Off-Road, Motorcycle, Plane, Helicopter, Boat, Emergency, Commercial, Industrial, Service, Military, Arena, Open Wheel, Utility, Van

## Data Sources & Attribution

- **GTABase.com** — vehicle specs, pricing, shop locations
- **Broughy1322** — standardized top speed and lap time testing
- **GTA Wiki (Fandom)** — real-world vehicle counterparts

When publishing the database, credit all three sources.

## Root-Level Python Scripts (Legacy)

The files `create_gta_app.py`, `build_app.py`, `setup_project.py`, `master_deploy.py`, and the root-level copies of `gta_vehicle_scraper.py`, `vehicle_entry_helper.py`, `vehicle_merger.py` are older versions. Prefer the versions in `scripts/` for data work.
