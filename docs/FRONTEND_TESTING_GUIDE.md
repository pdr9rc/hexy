# 🏰 Frontend Testing Guide - City Overlays

## Overview

The city overlays functionality has been moved to the city details view as requested. Here's how to test the new interface.

## Changes Made

### 1. **Moved City Overlays Button**
- ❌ **Removed**: City Overlays button from main control panel
- ✅ **Added**: City Overlays button in city details view next to "RETURN TO MAP"

### 2. **New Navigation Flow**
```
Main Map → Click Major City → City Details → 🏰 CITY OVERLAYS → Interactive Grid
                                                     ↓
                                              📜 ASCII VIEW
```

### 3. **Left-Right Layout**
- **Left Side**: City overlay map/grid (where main map normally shows)
- **Right Side**: Hex encounter details (when clicking grid hexes)

## Testing Steps

### Prerequisites
1. Install Flask: `pip install flask`
2. Start server: `cd src && python3 ascii_map_viewer.py`
3. Open browser: `http://localhost:5000`

### Test Sequence

#### 1. Navigate to City Details
1. Click on a major city hex (should show as ◆ symbol)
2. City details should display in the left panel
3. Verify you see two buttons:
   - **RETURN TO MAP** (existing)
   - **🏰 CITY OVERLAYS** (new)

#### 2. Enter City Overlay Mode
1. Click **🏰 CITY OVERLAYS** button
2. Left panel should show:
   - **← RETURN TO CITY** button
   - **📜 ASCII VIEW** button  
   - 5x5 interactive hex grid
   - Legend explaining symbols

#### 3. Test Interactive Grid
1. Click any hex in the 5x5 grid
2. Right panel should display hex encounter details:
   - Hex name and position
   - Content type and description
   - Encounter details
   - Random events table
   - NPCs, treasures, threats (if any)

#### 4. Test ASCII View
1. Click **📜 ASCII VIEW** button
2. Left panel should show complete ASCII representation
3. Buttons should be:
   - **← BACK TO GRID**
   - **🏰 RETURN TO CITY**

#### 5. Test Navigation
1. From ASCII view: **← BACK TO GRID** → Returns to interactive grid
2. From grid view: **← RETURN TO CITY** → Returns to city details
3. From city details: **RETURN TO MAP** → Returns to main map

## Expected Results

### Galgenbeck Content
When testing with Galgenbeck city, you should see lore-accurate content:

- **Districts**: "Schleswig District", "Ministry of Wealth District", "The Corpse Quarter"
- **Buildings**: "Ministry of Wealth & Taxes", "The City (Bone) Mill", "Demon Embassy (Schleswig)"
- **Encounters**: References to soul taxation, corpse processing, demon negotiations
- **Random Tables**: Events tied to Galgenbeck lore (soul taxes, bone grinding, etc.)

### Grid Layout Example
```
[R] [R] [S] [B] [R]
[R] [T] [T] [B] [S]
[B] [M] [G] [M] [S]
[B] [R] [M] [B] [R]
[B] [D] [D] [D] [S]

Legend:
D=District, B=Building, S=Street, L=Landmark, M=Market
T=Temple, V=Tavern, G=Guild, R=Residence, U=Ruins
```

## Troubleshooting

### Issue: "No city overlay images found"
**Cause**: Server can't find `data/city_overlays/galgenbeck.jpg`
**Solution**: 
1. Verify file exists: `ls -la data/city_overlays/`
2. Should show `galgenbeck.jpg` (not `image1.jpg`)
3. Restart server if file was just added

### Issue: City name not mapping correctly
**Cause**: City detection logic not finding proper city name
**Solution**:
1. Check console for error messages
2. Verify city is in `lore_db.major_cities` 
3. Check `databases/cities/galgenbeck.json` exists

### Issue: Generic content instead of city-specific
**Cause**: City database not loading properly
**Solution**:
1. Verify `databases/cities/galgenbeck.json` exists
2. Check JSON syntax is valid
3. Check console for loading errors

### Issue: Buttons not working
**Cause**: JavaScript function not found
**Solution**:
1. Check browser console for JavaScript errors
2. Verify all new functions are present:
   - `showCityOverlayInMap()`
   - `showCityOverlayGridInMap()`
   - `showCityOverlayAsciiInMap()`
   - `showCityHexDetailsInMap()`

## File Verification

Ensure these files exist:
```
data/city_overlays/
├── galgenbeck.jpg              # Main city image
└── galgenbeck.txt              # Can be removed

databases/cities/
├── galgenbeck.json            # City-specific content
└── bergen_chrypt.json         # Additional city (optional)

web/templates/
└── main_map.html              # Updated with new functions
```

## API Testing

Test API endpoints directly:
```bash
# List available overlays
curl "http://localhost:5000/api/city-overlays"

# Get Galgenbeck overlay data  
curl "http://localhost:5000/api/city-overlay/galgenbeck"

# Get ASCII view
curl "http://localhost:5000/api/city-overlay/galgenbeck/ascii"

# Get specific hex details
curl "http://localhost:5000/api/city-overlay/galgenbeck/hex/2_2"
```

Expected response format:
```json
{
  "success": true,
  "overlays": [
    {
      "name": "galgenbeck",
      "filename": "galgenbeck.jpg", 
      "display_name": "Galgenbeck"
    }
  ]
}
```

## Implementation Status

✅ **Backend Changes**: Complete and tested
- City overlay analyzer updated
- City-specific databases created
- API endpoints functional

✅ **Frontend Changes**: Complete
- City overlays button moved to city details
- Left-right layout implemented
- Interactive grid with hex details
- ASCII view with proper navigation

✅ **Integration**: Complete
- City name mapping from lore database
- Galgenbeck-specific content loading
- Fallback system for unknown cities

---

The interface now provides a seamless city exploration experience with lore-accurate content and intuitive navigation! 🏰💀