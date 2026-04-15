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

### Mod Stack Pipeline (run in order)

```bash
pip install requests beautifulsoup4

# Step 1: Scrape top replace mod per vehicle from gta5-mods.com (~45-60 min)
#         Adds Top_Mod_Title/Make/Model/Downloads/URL columns to main CSV.
#         Supports --limit N for smoke tests and auto-resumes from checkpoint.
python scripts/mod_scraper.py --limit 5   # smoke test
python scripts/mod_scraper.py             # full run

# Step 2: Compare mod community choices vs DB real-world mappings.
#         Outputs data/mod_match_report.csv and enriches the app CSV.
python scripts/mod_match_report.py
```

The feature-rich app (`GTA-Vehicle-Database-App/`) auto-picks up the new columns once `mod_match_report.py` has run.

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

## Data Sources, SSOT Chain & Mod Mismatches

### Primary SSOT per data type

| Data | Source | Script |
|---|---|---|
| Vehicle list (792 vehicles) | GTABase.com | `scripts/gta_vehicle_scraper.py` |
| Real-world car mappings | GTA Wiki Fandom API | `scripts/wiki_api_scraper.py` |
| Mapping corrections | Manual overrides | `scripts/fix_make_model_issues.py`, `scripts/fix_empty_makes.py` |
| Performance (speed, lap time) | Broughy1322 (embedded in GTABase pages) | `scripts/gta_vehicle_scraper.py` |
| Top PC mod per vehicle | gta5-mods.com (highest-downloaded replace mod) | `scripts/mod_scraper.py` |
| Mod vs DB match analysis | Derived from above two | `scripts/mod_match_report.py` |

**Important:** `GTA-Vehicle-Database-App/public/gta_vehicles_complete.csv` is a **hand-curated 80-vehicle subset** with a different schema (`ID/Make/Model/Real_World` instead of `Vehicle_ID/GTA_Make/GTA_Model/Real_World_Make/Real_World_Model`). It is **not** auto-generated from the Python pipeline. The `mod_match_report.py` script syncs the 5 mod columns into it by matching on `GTA_Model == Model`.

When publishing the database, credit: GTABase.com, Broughy1322, GTA Wiki (Fandom).

### Why the top mod often disagrees with the DB's Real_World mapping

This is expected and not a data error. Five structural reasons:

1. **Multi-inspiration design.** Most GTA cars blend 2–4 real vehicles. GTA Wiki records one primary inspiration; modders may pick a different car from the same blend (e.g., Zentorno = Lamborghini Veneno per Wiki, but Ferrari LaFerrari is the most-downloaded replace mod because it looks closer).
2. **Community consensus drift.** Over years the community settles on a different "correct" car than what the Wiki originally noted. The DB reflects editorial Wiki accuracy; mods reflect current player preference.
3. **Slot popularity over accuracy.** Modders choose the most desirable car that fits a slot, not the documented inspiration. The Adder slot gets Bugatti Chiron mods even though the Veyron is the official basis — because the Chiron is more current.
4. **Many-to-one slots.** Generic tuner templates like Sultan and Elegy can fit dozens of real JDM cars. Whichever high-quality 3D model is available wins.
5. **Add-On vs Replace distinction.** Most top-downloaded mods are Add-On (new slot) not Replace. Only Replace mods indicate which specific GTA vehicle the modder associates with a real car.

Use `data/mod_match_report.csv` (column `Suggested_DB_Update = review`) to identify high-confidence mismatches worth manual review.

## Root-Level Python Scripts (Legacy)

The files `create_gta_app.py`, `build_app.py`, `setup_project.py`, `master_deploy.py`, and the root-level copies of `gta_vehicle_scraper.py`, `vehicle_entry_helper.py`, `vehicle_merger.py` are older versions. Prefer the versions in `scripts/` for data work.
