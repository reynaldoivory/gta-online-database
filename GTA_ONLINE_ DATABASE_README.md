# GTA Online Vehicle Database - Auto-Population Toolkit

## Overview
Complete toolkit for populating your GTA Online vehicle database from 65 to 792 vehicles using automated scraping, manual entry, and data validation.

## Scripts Included

### 1. `gta_vehicle_scraper.py` - Automatic Web Scraper
**Purpose:** Scrapes GTABase.com and GTA Wiki to auto-populate vehicle data

**Features:**
- Fetches all 792 vehicles from GTABase
- Extracts pricing, drivetrain, shop location
- Pulls top speed and lap times (Broughy1322 data)
- Cross-references real-world counterparts from GTA Wiki
- Implements 2-second rate limiting (polite scraping)
- Progress checkpoints every 50 vehicles

**Usage:**
```bash
pip install requests beautifulsoup4 lxml
python gta_vehicle_scraper.py
```

**Output:** `gta_vehicles_complete.csv` (727 new vehicles, IDs 066-792)

**Runtime:** ~30-40 minutes

**Limitations:**
- May break if website structure changes
- Real-world counterparts need manual verification
- Boolean flags require human judgment

---

### 2. `vehicle_entry_helper.py` - Interactive Manual Entry
**Purpose:** Efficiently enter vehicle data manually with validation

**Features:**
- Interactive command-line interface
- Auto-suggest real-world manufacturers
- Built-in data validation
- Batch paste mode (copy from GTABase)
- Quick reference guide for manufacturers/classes

**Usage:**
```bash
python vehicle_entry_helper.py
```

**Modes:**
1. **Interactive Entry** - One vehicle at a time with prompts
2. **Batch Entry** - Paste multiple vehicles from GTABase
3. **Quick Reference** - Manufacturer and class lookup

**Output:** `new_vehicles.csv`

**Best for:** 
- When web scraping fails
- Adding new DLC vehicles
- Correcting specific entries

---

### 3. `vehicle_merger.py` - CSV Combiner & Validator
**Purpose:** Merge multiple CSV files and validate data integrity

**Features:**
- Combines any number of CSV files
- Removes duplicate entries
- Validates required fields
- Checks boolean format (TRUE/FALSE)
- Validates price format
- Validates drivetrain values (AWD/RWD/FWD/N/A)
- Renumbers Vehicle_IDs sequentially
- Generates comprehensive statistics report

**Usage:**
```bash
python vehicle_merger.py existing_65.csv scraped_data.csv manual_entries.csv
```

**Output:** `gta_vehicles_complete.csv` + statistics report

**Report includes:**
- Total unique vehicles
- Class distribution
- Top manufacturers
- Special features count (HSW, Imani, etc.)
- Duplicate warnings
- Validation errors

---

## Recommended Workflow

### Phase 1: Automatic Scraping
```bash
# Install dependencies
pip install requests beautifulsoup4 lxml

# Run scraper
python gta_vehicle_scraper.py

# Wait ~30-40 minutes
# Output: gta_vehicles_complete.csv (727 vehicles)
```

### Phase 2: Manual Entry (if needed)
```bash
# For vehicles that failed to scrape
python vehicle_entry_helper.py

# Select mode 1 (interactive) or 2 (batch)
# Output: new_vehicles.csv
```

### Phase 3: Merge & Validate
```bash
# Combine all data sources
python vehicle_merger.py \
    your_existing_65.csv \
    gta_vehicles_complete.csv \
    new_vehicles.csv

# Output: gta_vehicles_complete.csv (merged & validated)
```

### Phase 4: Manual Review
1. Open `gta_vehicles_complete.csv` in Google Sheets
2. Apply conditional formatting (your recommendations)
3. Set up filter views
4. Cross-reference real-world counterparts
5. Verify boolean flags (HSW, Imani, Benny's, Arena)
6. Check Arena War variants (3 per base vehicle)

---

## Data Attribution & Sources

### Primary Sources
1. **GTABase.com**
   - Vehicle specifications
   - Pricing information
   - Shop locations
   - Release dates

2. **Broughy1322**
   - Top speed testing (standardized method)
   - Lap time testing (consistent track)
   - Performance rankings

3. **GTA Wiki (Fandom)**
   - Real-world vehicle counterparts
   - Design inspiration details
   - Historical vehicle information

### Attribution Requirements
Always credit these sources when sharing or publishing the database:
- "Vehicle data sourced from GTABase.com"
- "Performance testing by Broughy1322"
- "Real-world references from GTA Wiki"

---

## Database Schema

### Required Fields
- `Vehicle_ID` - Unique identifier (001-792)
- `GTA_Make` - In-game manufacturer
- `GTA_Model` - In-game model name
- `Class` - Vehicle class (Super, Sports, Muscle, etc.)

### Core Data Fields
- `Real_World_Make` - Real manufacturer
- `Real_World_Model` - Real model name
- `Price` - Base purchase price (no trade price)
- `Drivetrain` - AWD, RWD, FWD, or N/A
- `Shop` - Legendary, Southern, Warstock, Bennys, Arena, Reward

### Performance Fields (Optional)
- `Top_Speed_MPH` - Broughy1322 tested
- `Lap_Time` - Standardized track time
- `Seats` - Passenger capacity

### Boolean Flags
- `Weaponized` - Has weapons (TRUE/FALSE)
- `HSW` - Hao's Special Works compatible (TRUE/FALSE)
- `Imani` - Imani Tech compatible (TRUE/FALSE)
- `Bennys` - Benny's custom available (TRUE/FALSE)
- `Arena` - Arena War vehicle (TRUE/FALSE)

### Additional Fields
- `Notes` - Special features, variants, etc.

---

## Data Validation Rules

### Price Format
- Numeric only (no $ or commas in CSV)
- Example: `2765000` not `$2,765,000`

### Boolean Format
- Use `TRUE` or `FALSE` (all caps)
- Never use: Yes/No, 1/0, T/F, true/false

### Drivetrain Values
- Only: `AWD`, `RWD`, `FWD`, `N/A`
- Must be uppercase

### Shop Values
- Legendary, Southern, Warstock, Bennys, Arena, Reward, Pegasus
- Capitalize first letter

### Class Values
Valid classes:
- Super, Sports, Sports Classic, Muscle, Sedan
- Coupe, Compact, SUV, Off-Road, Motorcycle
- Plane, Helicopter, Boat, Emergency, Commercial
- Industrial, Service, Military, Arena, Open Wheel
- Utility, Van

---

## Troubleshooting

### Scraper Not Working
**Problem:** Website structure changed

**Solutions:**
1. Check GTABase.com is accessible
2. Update HTML selectors in script
3. Use manual entry helper instead
4. Check for API alternatives

### Duplicate Entries
**Problem:** Same vehicle appears twice

**Solutions:**
1. Run merger script with validation
2. Check for variant names (e.g., "Ignus" vs "Weaponized Ignus")
3. Manually review duplicates list in report

### Invalid Data Formats
**Problem:** Validation errors in merger

**Solutions:**
1. Check boolean fields are TRUE/FALSE
2. Verify prices are numeric only
3. Confirm drivetrains are AWD/RWD/FWD/N/A
4. Review error list in merger report

### Missing Real-World Data
**Problem:** Real-world counterpart unknown

**Solutions:**
1. Search GTA Wiki: `https://gta.fandom.com/wiki/[Vehicle_Name]`
2. Search GTABase individual vehicle page
3. Check community resources (r/gtaonline)
4. Leave blank and mark for later review

---

## Google Sheets Formatting (Your Recommendations)

### 1. Filter Views
```
Data > Create a Filter
```
Click arrows on headers to filter by:
- Class (show only Super cars)
- Shop (show only Legendary Motorsport)
- HSW (show only TRUE)
- Real_World_Make (show only Toyota)

### 2. Conditional Formatting
```
Format > Conditional Formatting
```
**Color coding by Class:**
- Super → Purple background
- Sports → Blue background
- Muscle → Orange background
- Arena → Red background

**Highlight special features:**
- HSW = TRUE → Purple text
- Imani = TRUE → Blue text
- Weaponized = TRUE → Red text

### 3. Data Validation
```
Data > Data Validation
```
Create dropdown lists for:
- Class (from master list)
- Drivetrain (AWD, RWD, FWD, N/A)
- Shop (Legendary, Southern, Warstock, etc.)

Prevents typos and ensures consistency

### 4. Slicers (Dashboard View)
```
Data > Add Slicer
```
Add slicers for:
- Real_World_Make (filter by manufacturer)
- Class (filter by vehicle type)
- Shop (filter by store)

Creates visual filtering buttons

### 5. Freeze Panes
```
View > Freeze > 1 row
```
Keeps header row visible when scrolling

### 6. Named Ranges
```
Select column > Right-click > Define named range
```
Name important columns:
- "ClassRange" for Class column
- "PriceRange" for Price column
- Enables easier formulas

---

## Advanced Features

### Add Statistics Dashboard
Create second sheet tab with formulas:

```excel
=COUNTIF(Database!C:C,"Super")
→ Counts Super cars

=AVERAGE(IF(Database!C:C="Super",Database!G:G))
→ Average Super car price

=QUERY(Database!A:N,"SELECT B, C, G WHERE M='TRUE'",1)
→ Lists all Imani Tech vehicles with prices
```

### Performance Analysis
Add calculations:
```excel
Price_Per_MPH: =G2/J2
Value_Rating: =IF(AND(J2>190,G2<2000000),"Excellent","Fair")
```

### Racing Meta Filter
Create view showing:
- Top 10 fastest by class
- Best AWD vehicles for rain
- Cheapest competitive options

---

## Maintenance & Updates

### New DLC Releases
When Rockstar releases new vehicles:

1. Use manual entry helper for new vehicles
2. Start Vehicle_ID at next available (793+)
3. Merge with existing database
4. Renumber IDs sequentially

### Performance Updates
Broughy1322 updates testing data:

1. Download updated spreadsheet
2. Match by vehicle name
3. Update Top_Speed_MPH and Lap_Time fields
4. Keep old data in Notes field

### Real-World Corrections
Community identifies better counterparts:

1. Update Real_World_Make and Real_World_Model
2. Add old value to Notes: "Previously: [old data]"
3. Track changes in version history

---

## Community Contributions

### GitHub Repository (Recommended)
Host on GitHub for:
- Version control
- Community pull requests
- Issue tracking
- Public collaboration

### Reddit Sharing
Post to r/gtaonline with:
- Proper attribution
- Usage instructions
- Request for corrections
- Link to Google Sheets (view-only)

### Updates Schedule
- Weekly: New DLC vehicles
- Monthly: Performance data updates
- Quarterly: Real-world counterpart verification

---

## Known Limitations

### Web Scraping
- Fragile (breaks if site changes)
- Rate limited (slow)
- Requires manual verification

### Real-World Data
- Subjective (design inspiration varies)
- Multiple sources (vehicles inspired by multiple cars)
- Community debate (no official data)

### Boolean Flags
- Requires judgment calls
- Some vehicles have partial features
- HSW/Imani compatibility changes with updates

---

## FAQ

**Q: How long to complete 792 vehicles?**
A: Automatic: 30-40 min. Manual: ~40 hours. Hybrid: ~5 hours.

**Q: Can I skip web scraping?**
A: Yes, use manual entry helper or copy from GTABase directly.

**Q: How to handle Arena War variants?**
A: Each base vehicle has 3 variants (Apocalypse, Future Shock, Nightmare). Create separate entries with Arena=TRUE.

**Q: What about HSW vehicles?**
A: HSW upgrades are performance mods, not separate vehicles. Use HSW=TRUE flag. PS5/Xbox Series X|S exclusive.

**Q: How to handle trade prices?**
A: Use base price in Price field. Note trade price in Notes: "Trade: $2,073,750"

**Q: Vehicle ID numbering?**
A: Use 001-792 sequential. Merger script auto-renumbers.

---

## Support & Resources

### Documentation
- GTABase: https://www.gtabase.com/grand-theft-auto-v/vehicles/
- GTA Wiki: https://gta.fandom.com/wiki/Vehicles_in_GTA_Online
- Broughy1322: https://broughy.com/

### Community
- r/gtaonline - General discussion
- r/gtavcustoms - Vehicle customization
- GTA Forums - Technical details

### Performance Testing
- Broughy1322 YouTube - Testing methodology
- Broughy1322 Spreadsheet - Performance data

---

## Version History

**v1.0** - January 2026
- Initial release
- 3 core scripts (scraper, helper, merger)
- 792 vehicle capacity
- Complete documentation

---

## License & Attribution

**Scripts:** Educational use, modify freely
**Data:** Must credit GTABase, Broughy1322, GTA Wiki
**Sharing:** Encourage attribution and community contributions

---

**Created:** January 2026
**For:** GTA Online Vehicle Database Project
**By:** GTA Community Contributors
