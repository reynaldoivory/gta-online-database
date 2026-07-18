# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

GTA Online vehicle database: a Python data pipeline (`scripts/`) that maintains a 795-vehicle
CSV, and a single React/Vite frontend (`GTA-Vehicle-Database-App/`) that loads it at runtime
with PapaParse. Everything runs client-side; there is no backend.

The old second app (`app/GTA-Vehicle-App/`) was deleted in the 2026 cleanup. If documentation
or scripts reference it, they are stale.

## Commands

### Frontend (`GTA-Vehicle-Database-App/`)

```bash
npm run install:app     # install app dependencies (from repo root)
npm run dev             # dev server on http://localhost:3000 (opens browser)
npm run build           # production build -> GTA-Vehicle-Database-App/dist/
npm run preview         # preview the production build
```

All root `package.json` scripts delegate to `GTA-Vehicle-Database-App/`. There is no test
suite and no lint script in the app (root/CI tolerate this with a fallback echo).

### Python data scripts (`scripts/`)

```bash
pip install requests beautifulsoup4 lxml

python scripts/gta_vehicle_scraper.py    # scrape GTABase (destructive: overwrites master CSV)
python scripts/vehicle_merger.py a.csv b.csv   # merge/dedupe on GTA_Model, renumber Vehicle_ID
python scripts/livery_vehicle_checker.py # cross-check livery JSON vs DB
python scripts/convert_to_xlsx.py        # CSV -> Excel (run from repo root)
python scripts/fix_data_quality.py       # targeted row fixes + livery JSON fixes; re-syncs app CSV

# Mod stack (run in order; NOT yet run against the current data)
python scripts/mod_scraper.py --limit 5  # smoke test first
python scripts/mod_scraper.py            # full run (~45-60 min, adds Top_Mod_* columns in place)
python scripts/mod_match_report.py       # mod vs DB comparison -> data/mod_match_report.csv
```

**Warning:** `gta_vehicle_scraper.py` and `wiki_api_scraper.py` overwrite
`data/gta_vehicles_complete.csv` in place and use relative paths (run them only from where
their `../data/` resolves into the repo). Do not run them casually — see "Data sources" below;
the scraped sites now block non-browser clients.

## Architecture

- `App.jsx` fetches `/gta_vehicles_complete.csv` (served from
  `GTA-Vehicle-Database-App/public/`, no `data/` subfolder) and parses it with PapaParse.
- The Papa.parse mapper normalizes the pipeline CSV schema to the app's internal fields:
  `Vehicle_ID→ID`, `GTA_Make→Make`, `GTA_Model→Model`,
  `Real_World_Make + Real_World_Model → Real_World`, and booleans accept both `TRUE` and `Yes`.
  Missing numeric fields (`Acceleration`, `Handling`) default to 0 and their UI hides itself.
- Components: `VehicleTable` (sortable table, class chips, badges), `FilterPanel`
  (class/shop/make dropdowns, toggles, clamped price sliders), `StatsChart` (Recharts class
  distribution + price-vs-speed scatter), `DetailModal` (accessible dialog with stats and
  notes), `ExportButton` (RFC-4180 CSV export).
- The `Top_Mod_*` UI (table column, filter dropdown, modal section, export columns) is
  **dormant**: it renders only when the data actually contains mod columns, which happens after
  `mod_scraper.py` + `mod_match_report.py` have been run. Until then the UI hides itself.

## Data: SSOT and flow

`data/gta_vehicles_complete.csv` is the master (795 vehicles, 17 columns):

```
Vehicle_ID,GTA_Make,GTA_Model,Class,Real_World_Make,Real_World_Model,Price,Drivetrain,Shop,
Top_Speed_MPH,Lap_Time,Weaponized,HSW,Imani,Bennys,Arena,Notes
```

- `GTA-Vehicle-Database-App/public/gta_vehicles_complete.csv` is a **copy of the master** —
  never edit it directly; edit the master and re-copy (`fix_data_quality.py` does this
  automatically). Scripts must never treat a `public/` copy as input.
- `data/final_database.csv` is a separate hand-curated 80-vehicle set with a different schema
  (`ID/Make/Model/Real_World`, Yes/No booleans). Keep it; do not confuse the two.
- `data/vehicles_with_liveries.json` lists the 41 vehicles with livery support.

### Validation rules

- **Price**: numeric only (`2765000`); **Booleans**: `TRUE`/`FALSE` all caps
- **Drivetrain**: `AWD`, `RWD`, `FWD`, or `N/A`; **Vehicle_ID**: zero-padded `001`–`795`
- **Shop**: `Legendary`, `Southern`, `Warstock`, `Bennys`, `Arena`, `Reward`, `Pegasus`

### Known data issues (do not "fix" without a real source)

- `Weaponized` is TRUE for 794/795 rows and `HSW` is TRUE for 757/795 — both columns are
  junk/unpopulated. The UI suppresses their badges. `Bennys` is FALSE for every row.
  `Imani` (20 TRUE) and `Arena` (134 TRUE) are real.
- `Top_Speed_MPH` and `Drivetrain` are mostly empty; `Lap_Time` is populated.
- `Class` values are plural (`Sedans`, `Coupes`, …) with some comma-joined multi-class rows
  (`Sports,Tuners`). The frontend splits them; do not mass-rename the taxonomy without also
  updating `classColors` (VehicleTable) and `SKIP_CLASSES` (mod_scraper).
- `GTA_Model` is not a unique key (e.g. `Cruiser` ×5); joins should prefer `Vehicle_ID`.

## Data sources (as of July 2026)

| Data | Source | Status |
|---|---|---|
| Vehicle list | GTABase.com | site live, but serves HTTP 403 to non-browser clients |
| Real-world mappings | GTA Wiki (Fandom) | same 403/bot-protection concern |
| Performance | Broughy1322 via GTABase | Broughy still active; prefer GTACars.net or his Google Sheet |
| Top PC mods | gta5-mods.com | 403 to non-browser clients |

The plain `requests`+BeautifulSoup scrapers likely no longer work against these sites without
browser-grade headers (`curl_cffi`/`cloudscraper`). Better structured alternatives:

- **DurtyFree/gta-v-data-dumps** (GitHub) — machine-readable `vehicles.json` per DLC; best
  canonical vehicle list source.
- **GTACars.net** / Broughy's master Google Sheet — structured lap time / top speed data.
- **gta.wiki** — community mirror of the Fandom wiki, more scraper-friendly.

Game context: GTA Online is still updated (Money Fronts 6/2025, A Safehouse in the Hills
12/2025, The Kortz Center Heist 7/2026 — likely the final storyline DLC). GTA VI releases
Nov 19, 2026; expect the vehicle count (~795 here, ~800+ after Kortz drip-feed) to grow slowly
and then plateau. When publishing, credit GTABase.com, Broughy1322, and GTA Wiki (Fandom).

## CI & tooling

- `.github/workflows/ci.yml` (triggers on `master`): install → lint (tolerated no-op) → build
  (uploads `dist/` artifact) → Python validation of every `data/*.csv`.
- Husky pre-commit runs lint-staged; Renovate manages dependency PRs.
- Lockfiles are committed (root and app); `npm ci` depends on them.

## Gotchas

- Two copies of the vehicle CSV must stay in sync (master + app public copy) — always edit the
  master and re-run `python scripts/fix_data_quality.py` (or copy manually).
- The price-vs-speed scatter is sparse because most `Top_Speed_MPH` values are empty.
- Root-level `build_app.py`, `create_gta_app.py`, `master_deploy.py`, `setup_project.py` are
  legacy one-shot generators — do not use them for data work.
