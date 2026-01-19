# GTA Online Vehicle Equivalencies Database

A comprehensive database and web application for tracking vehicle equivalencies in Grand Theft Auto Online.

## Project Structure

```
GTA_ONLINE_DATABASE/
├── package.json                   # Root package.json with convenience scripts
├── app/
│   └── GTA-Vehicle-App/          # React/Vite frontend application
│       ├── src/
│       ├── public/
│       │   └── data/             # CSV data files
│       └── package.json
├── data/                          # Source data files
│   ├── gta_vehicles_complete.csv
│   └── final_database.csv
├── scripts/                       # Python utility scripts
│   ├── gta_vehicle_scraper.py
│   ├── vehicle_merger.py
│   └── vehicle_entry_helper.py
└── README.md
```

## Quick Start

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- Python 3.x (for data scripts)

### Running the Application

1. **Install dependencies (first time only):**
   ```bash
   npm run install:app
   ```
   Or manually:
   ```bash
   cd app/GTA-Vehicle-App
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   You can run this from the root directory - it will automatically navigate to the app folder.

3. **Open your browser:**
   Navigate to the URL shown in the terminal (typically `http://localhost:5173`)

### Building for Production

```bash
npm run build
npm run preview
```
You can run these commands from the root directory.

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

- **Vehicle Search**: Search by GTA make/model, real-world make/model, class, or ID
- **Sortable Columns**: Click column headers to sort
- **Pagination**: Browse through large datasets efficiently
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Modern dark UI optimized for extended use

## Technology Stack

- **Frontend**: React 18, Vite
- **Styling**: Tailwind CSS
- **Data Parsing**: PapaParse (CSV)
- **Icons**: Lucide React

## Development

The application uses:
- Vite for fast development and building
- React with modern hooks
- Tailwind CSS for styling
- PapaParse for CSV data loading
