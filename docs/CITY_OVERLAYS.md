# 🏰 City Overlays - The Dying Lands

## Overview

The City Overlays feature allows you to generate detailed 5x5 hex grids from city images, with each hex containing randomly generated content based on the Mörk Borg database. This feature expands the existing terrain analyzer code to work with urban environments.

## Features

- **Image-based Overlays**: Process any city image to create hex grids
- **5x5 Hex Grid**: Each overlay generates exactly 25 hexes arranged in a 5x5 grid
- **Random Tables**: Each hex has its own random encounter table based on Mörk Borg lore
- **ASCII Map View**: Visual representation of the city layout in ASCII format
- **Interactive Interface**: Click hexes to explore detailed content
- **Position-based Content**: Content varies based on hex position (edge, center, corner, inner)

## How to Use

### 1. Adding City Images

1. Place city images in the `data/city_overlays/` directory
2. Supported formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`
3. Example files:
   - `image1.jpg` - Historical city map (provided as example)
   - `galgenbeck.jpg` - For the canonical Mörk Borg city

### 2. Accessing City Overlays

1. Start the server: `cd src && python3 ascii_map_viewer.py`
2. Open the web interface
3. Click the **🏰 CITY OVERLAYS** button in the control panel
4. Select an available city overlay

### 3. Viewing Overlay Content

#### ASCII View
- Displays the entire 5x5 grid in text format
- Shows all hex details with descriptions and encounters
- Perfect for printing or text-based reference

#### Interactive Grid
- Click **🎲 INTERACTIVE GRID** for the visual interface
- Click individual hexes to view detailed information
- Each hex shows:
  - Content type (District, Building, Street, etc.)
  - Description and encounter details
  - Random event tables
  - NPCs, treasures, and threats
  - Atmospheric details

## Content Types

### City Hex Content Types

| Symbol | Type | Description |
|--------|------|-------------|
| D | District | Large areas with thematic content |
| B | Building | Individual structures |
| S | Street | Thoroughfares and pathways |
| L | Landmark | Important monuments |
| M | Market | Trading areas |
| T | Temple | Religious sites |
| V | Tavern | Drinking establishments |
| G | Guild | Professional organizations |
| R | Residence | Homes and dwellings |
| U | Ruins | Destroyed or abandoned areas |

### Position-based Generation

- **Edge Hexes**: Less developed, more residential/ruined
- **Corner Hexes**: Often fortified or defensive
- **Center Hex**: Most important, usually landmarks/temples
- **Inner Hexes**: Well-developed commercial/civic areas

## Random Tables

Each hex type includes specific random encounter tables:

### Example - Temple Random Table
```
1-2: The altar demands a sacrifice for a blessing
3-4: Hear confessions that reveal dark secrets
5-6: A divine vision shows you a possible future
7-8: The sacred texts rewrite themselves
9-10: A miracle occurs, but at a terrible price
11-12: The deity speaks directly to you
```

### Example - Market Random Table
```
1-2: A vendor offers to buy your memories
3-4: Find an item that shouldn't exist here
5-6: Witness a transaction in souls rather than coin
7-8: A merchant recognizes you from a dream
9-10: Discover the market exists in multiple realms
11-12: A purchase comes with an unexpected curse
```

## API Endpoints

### GET /api/city-overlays
Returns list of available city overlay images.

### GET /api/city-overlay/{overlay_name}
Returns complete overlay data including all hex information.

### GET /api/city-overlay/{overlay_name}/ascii
Returns ASCII representation of the city overlay.

### GET /api/city-overlay/{overlay_name}/hex/{hex_id}
Returns detailed information for a specific hex.

## File Structure

```
data/city_overlays/              # City overlay images
├── image1.jpg                   # Example historical map
├── galgenbeck.jpg              # Galgenbeck city (add your image)
└── your_city.png               # Any additional city images

dying_lands_output/city_overlays/  # Generated overlay data
├── image1_overlay.json         # Cached overlay data
└── galgenbeck_overlay.json     # Generated when accessed

src/
├── city_overlay_analyzer.py    # Main overlay processing
└── ascii_map_viewer.py         # Web interface integration
```

## Technical Details

### Grid System
- 5x5 grid (25 hexes total)
- Hex IDs: `{row}_{col}` (0_0, 0_1, ..., 4_4)
- Position types: edge, corner, center, inner

### Content Generation
- Uses existing Mörk Borg database tables
- Weighted content selection based on position
- Random tables generated per content type
- Position-specific modifiers applied

### Data Storage
- JSON files for generated overlays
- Cached for performance
- Regenerated if image changes

## Examples

### Galgenbeck Example

Create a `galgenbeck.jpg` image in `data/city_overlays/` and the system will automatically generate:

```
🏰 GALGENBECK - THE CORPSE CITY
Grid Layout (5x5):
[R] [B] [S] [L] [R]
[D] [T] [M] [G] [D]
[B] [M] [L] [T] [S]
[R] [G] [M] [B] [R]
[U] [D] [S] [D] [U]
```

Each hex would contain detailed Mörk Borg-appropriate content like:
- **Temple of the Dying God** with blood offerings
- **The Bone Bazaar** trading in cursed relics
- **Corpse Quarter** district with plague-ridden inhabitants
- **Guild of Sacred Executioners** maintaining dark order

## Integration with Existing System

The city overlay system seamlessly integrates with:
- **Terrain System**: Uses same base infrastructure
- **Mörk Borg Database**: Draws from canonical lore
- **ASCII Map Viewer**: Shares interface patterns
- **Random Generation**: Uses existing table system

## Testing

Run the test script to verify functionality:

```bash
python3 test_city_overlays.py
```

This will test:
- Image detection
- Overlay generation
- ASCII view creation
- Individual hex content
- Grid summary display

## Future Enhancements

Potential expansions of the city overlay system:
- Variable grid sizes (3x3, 7x7, etc.)
- Image analysis for automatic content placement
- Custom content tables per city
- Multi-level city maps (underground, etc.)
- Integration with existing hex map system

---

**Created for The Dying Lands - Mörk Borg Hex Crawl Generator**