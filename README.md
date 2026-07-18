# GTA Online Vehicle Equivalencies Database

A comprehensive database and web application for tracking vehicle equivalencies in Grand Theft Auto Online.

**Database Status**: 795 vehicles catalogued with real-world equivalents, performance stats, and specifications.

## Project Structure

```
vehicle-database/
├── GTA-Vehicle-Database-App/     # React/Vite frontend application
│   ├── src/                      # React components and application code
│   │   ├── App.jsx              # Main application component
│   │   └── components/          # Reusable UI components
│   ├── public/                   # Static assets
│   │   └── gta_vehicles_complete.csv  # Primary dataset (795 vehicles)
│   └── package.json
├── data/                          # Source data files and documentation
│   ├── gta_vehicles_complete.csv # Master dataset (795 vehicles)
│   ├── final_database.csv        # Legacy dataset
│   ├── vehicles_with_liveries.csv
│   └── vehicles_with_liveries.json
├── scripts/                       # Python utility scripts
│   ├── gta_vehicle_scraper.py    # Web scraper for vehicle data
│   ├── vehicle_merger.py         # CSV merger and validator
│   ├── vehicle_entry_helper.py   # Helper for manual data entry
│   ├── fix_make_model_issues.py  # Data cleanup utilities
│   └── wiki_api_scraper.py       # Wikipedia API scraper
├── package.json                   # Root package.json with convenience scripts
└── README.md
```

## Quick Start

### Prerequisites
- Node.js (v20 or higher)
- npm or yarn
- Python 3.x (for data scripts)

### Running the Application

1. **Install dependencies (first time only):**
   ```bash
   cd GTA-Vehicle-Database-App
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to the URL shown in the terminal (typically `http://localhost:3000`)

### Building for Production

```bash
cd GTA-Vehicle-Database-App
npm run build
npm run preview
```

## Data Management

### Generate Sample Data
```bash
python data/generate_data.py
```

### Scrape Live Vehicle Data
```bash
python scripts/gta_vehicle_scraper.py
```

### Merge CSV Files
```bash
python scripts/vehicle_merger.py data/gta_vehicles_complete.csv
```

## Features

- **Comprehensive Database**: 795 vehicles with real-world equivalents and specifications
- **Advanced Filtering**: Filter by class, shop, make, HSW availability, Imani Tech, and weaponization
- **Vehicle Search**: Search by GTA make/model, real-world make/model, class, or ID
- **Sortable Columns**: Click column headers to sort by any attribute
- **Statistics Dashboard**: Visual charts showing vehicle distribution and pricing trends
- **Export Functionality**: Export filtered data to CSV or Excel
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Theme**: Modern dark UI optimized for extended use

## Technology Stack

- **Frontend**: React 18, Vite
- **Styling**: Tailwind CSS
- **Data Parsing**: PapaParse (CSV)
- **Charts**: Recharts
- **Export**: JSZip, FileSaver
- **Icons**: Lucide React

## Data Schema

The primary dataset (`gta_vehicles_complete.csv`) contains 795 vehicles with the following fields:

- `Vehicle_ID`: Unique identifier
- `GTA_Make`: Vehicle manufacturer in GTA Online
- `GTA_Model`: Vehicle model name in GTA Online
- `Class`: Vehicle class (Super, Sports, Off-Road, etc.)
- `Real_World_Make`: Real-world manufacturer equivalent
- `Real_World_Model`: Real-world model equivalent
- `Price`: In-game purchase price
- `Drivetrain`: AWD, RWD, FWD, 6WD
- `Shop`: Purchase location (Legendary Motorsport, etc.)
- `Top_Speed_MPH`: Maximum speed
- `Lap_Time`: Lap time performance metric
- `Weaponized`: Boolean - has weapons
- `HSW`: Boolean - HSW upgrade available
- `Imani`: Boolean - Imani Tech available
- `Bennys`: Boolean - Benny's customization available
- `Arena`: Boolean - Arena War vehicle
- `Notes`: Additional information

## Development

The application uses:
- Vite for fast development and building
- React with modern hooks for state management
- Tailwind CSS for utility-first styling
- PapaParse for efficient CSV parsing
- Recharts for data visualization

## Recent Updates (2026-04-11)

Project structure has been consolidated and optimized:
- Removed duplicate app directory (`app/GTA-Vehicle-App/`)
- Consolidated Python utility scripts into `scripts/` directory
- Updated primary dataset to 795 vehicles (previously 80 in production)
- Removed legacy JSX assessment files
- Updated documentation to reflect current structure
