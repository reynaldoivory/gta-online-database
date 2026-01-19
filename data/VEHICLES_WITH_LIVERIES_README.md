# GTA Online Vehicles with Livery Options

This directory contains a comprehensive set of all GTA Online vehicles that support livery customization options.

## Files

- **`vehicles_with_liveries.json`** - Structured JSON format with metadata and vehicle details
- **`vehicles_with_liveries.csv`** - CSV format for easy import into spreadsheets or databases

## Overview

This set contains **42 vehicles** (as of January 2024) that have livery customization options in GTA Online. Liveries are special paint jobs and designs that can be applied to vehicles, often including:

- Racing liveries
- Branded liveries (Sprunk, eCola)
- Anime-style liveries
- Exclusive event liveries
- Drift tuning liveries
- Galaxy-themed liveries

## Categories

### Sports Cars
- Dinka Sugoi
- Maibatsu Penumbra FF
- Bravado Banshee
- Übermacht Sentinel Classic
- Pfister Comet Safari
- Benefactor Schlagen GT
- And more...

### Muscle Cars
- Vapid Dominator ASP
- Bravado Gauntlet Classic Custom
- Declasse Tampa GT
- Bravado Gauntlet Hellfire
- And more...

### Supercars
- Progen Itali GTB Custom
- Pegassi Torero XO
- Benefactor LM87
- Annis S80RR
- And more...

### Other Classes
- Motorcycles (Pegassi Bati 801RR)
- SUVs (Übermacht Rebla GTS)
- Compacts (Weeny Dynasty)
- Military vehicles (with Galaxy livery)
- And more...

## Special Livery Types

### Exclusive Event Liveries
- **Merry Cliquemas** - Vapid Clique (December 25, 2018)
- **For Queen and Country** - Ocelot Swinger (July 24-30, 2018)
- **eCola Exclusive** - Annis S80RR (Casino missions completion)

### Branded Liveries
- **Sprunk** - Available on multiple vehicles
- **eCola** - Available on select vehicles

### Drift Tuning Liveries
- **Painted n' Shaded** - Drift race completion reward
- **Drift Gorilla Green** - Drift race completion reward

### Galaxy Livery
Available on weaponized vehicles:
- TM-02 Khanjali Tank
- Mammoth Avenger
- Mammoth Thruster
- Ocelot Ardent
- Declasse Weaponized Tampa
- HVY Nightshark
- HVY Insurgent variants

## Usage

### JSON Format
```python
import json

with open('data/vehicles_with_liveries.json', 'r') as f:
    data = json.load(f)
    
vehicles = data['vehicles']
print(f"Total vehicles with liveries: {data['metadata']['total_vehicles']}")
```

### CSV Format
```python
import csv

with open('data/vehicles_with_liveries.csv', 'r') as f:
    reader = csv.DictReader(f)
    for vehicle in reader:
        print(f"{vehicle['GTA_Make']} {vehicle['GTA_Model']}")
```

## Notes

- Some liveries are **exclusive** and were only available during specific events
- Certain vehicles require upgrades at **Benny's Original Motorworks** to access all livery options
- **Drift Tuning liveries** require completing Drift Races
- The list is continuously updated as new vehicles and liveries are added to GTA Online

## Last Updated

January 13, 2024

## Sources

- GTA Online community resources
- Vehicle customization guides
- Official GTA Online updates and patch notes
