# GTA Online Vehicle Database - Project Structure

## Root Directory Organization

```
GTA_ONLINE_DATABASE/
│
├── app/
│   └── GTA-Vehicle-App/              # Main React application
│       ├── src/
│       │   ├── App.jsx               # Main application component
│       │   ├── main.jsx              # React entry point
│       │   └── index.css             # Global styles (Tailwind)
│       ├── public/
│       │   └── data/
│       │       ├── gta_vehicles_complete.csv
│       │       └── final_database.csv
│       ├── index.html                # HTML template
│       ├── package.json              # Node dependencies
│       ├── vite.config.js            # Vite configuration
│       ├── tailwind.config.js        # Tailwind CSS config
│       └── postcss.config.js         # PostCSS config
│
├── data/                              # Source data files
│   ├── gta_vehicles_complete.csv
│   ├── final_database.csv
│   └── generate_data.py              # Data generation script
│
├── scripts/                           # Python utility scripts
│   ├── gta_vehicle_scraper.py        # Web scraper for vehicle data
│   ├── vehicle_merger.py             # CSV merger utility
│   └── vehicle_entry_helper.py       # Helper for manual entries
│
├── README.md                          # Main project documentation
└── PROJECT_STRUCTURE.md              # This file
```

## Application Architecture

### Frontend (React/Vite)
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Data Loading**: PapaParse for CSV parsing
- **Icons**: Lucide React

### Data Flow
1. CSV files stored in `public/data/`
2. App loads CSV via fetch API
3. PapaParse parses CSV to JSON
4. React state manages filtered/sorted data
5. Pagination handles large datasets

### Key Features
- Real-time search across all vehicle fields
- Sortable columns with visual indicators
- Pagination (100 rows per page)
- Responsive design
- Dark theme UI

## Development Workflow

1. **Data Updates**: Place CSV files in `public/data/`
2. **Development**: Run `npm run dev` in `app/GTA-Vehicle-App/`
3. **Build**: Run `npm run build` for production
4. **Data Scripts**: Use Python scripts in `scripts/` for data management

## File Naming Conventions

- **CSV Files**: `gta_vehicles_complete.csv`, `final_database.csv`
- **Components**: PascalCase (e.g., `App.jsx`)
- **Scripts**: snake_case (e.g., `vehicle_merger.py`)
