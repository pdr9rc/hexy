# 🏰 City Overlays Refactor Documentation

## Overview

This document outlines the refactoring changes made to the city overlay system to properly integrate with the Mörk Borg database and provide city-specific content generation.

## Changes Made

### 1. Image Mapping
- **Change**: `image1.jpg` now maps to Galgenbeck city overlay
- **Implementation**: Updated `_format_overlay_name()` to map `image1` → `galgenbeck`
- **Files**: Renamed `data/city_overlays/image1.jpg` → `data/city_overlays/galgenbeck.jpg`

### 2. City Name Resolution
- **Change**: Overlay names now fetch from Mörk Borg database
- **Implementation**: 
  - Check `lore_db.major_cities` for canonical names
  - Fallback to city-specific database files
  - Final fallback to formatted filename
- **Method**: `_format_overlay_name()` in `src/city_overlay_analyzer.py`

### 3. City-Specific Content Databases

Created comprehensive city-specific content databases:

#### Database Structure
```
databases/cities/
├── galgenbeck.json       # Complete Galgenbeck lore
├── bergen_chrypt.json    # Complete Bergen Chrypt lore
└── [city_name].json      # Future cities
```

#### Content Structure Per City
Each city database includes:
- **Basic Info**: `city_name`, `display_name`, `description`, `theme`
- **Content Lists**: `districts`, `buildings`, `streets`, `landmarks`, `markets`, `temples`, `taverns`, `guilds`, `residences`, `ruins`
- **Encounters**: Specific encounter text per content type
- **Random Tables**: Custom d12 tables per content type
- **Atmosphere Modifiers**: City-specific atmospheric descriptions

### 4. Content Generation Refactor

#### Method Signature Updates
All content generation methods now accept `city_data` parameter:
```python
def _generate_district_content(self, city_data: Optional[Dict[str, Any]] = None)
def _generate_building_content(self, city_data: Optional[Dict[str, Any]] = None)
# ... etc for all content types
```

#### Helper Methods Added
- `_load_city_database()`: Load city-specific JSON data
- `_get_city_content_list()`: Get city-specific content or fallback
- `_get_city_encounters()`: Get city-specific encounters or fallback
- `_get_city_random_table()`: Get city-specific random tables or fallback
- `_get_city_atmospheres()`: Get city-specific atmospheres or fallback

#### Content Flow
1. Map overlay name to city name (`image1` → `galgenbeck`)
2. Load city-specific database if available
3. Generate content using city data or fallback to generic
4. Use city-specific names, encounters, and random tables

### 5. Galgenbeck City Content

#### Lore Integration
All content reflects canonical Galgenbeck lore:
- **Soul-based economy** (Ministry of Wealth & Taxes)
- **Corpse processing industry** (Bone Mill, Corpse Quarter)
- **Schleswig demon district** integration
- **Hanging Gardens** execution site
- **Council rule** and **Catacomb** connections
- **Heptalith** magical elements

#### Example Content
- **Districts**: "Schleswig District", "Ministry of Wealth District", "The Corpse Quarter"
- **Buildings**: "Ministry of Wealth & Taxes", "The City (Bone) Mill", "Demon Embassy (Schleswig)"
- **Encounters**: Soul tax collection, corpse processing, demon negotiations
- **Random Tables**: City-specific events tied to lore elements

### 6. Bergen Chrypt City Content

#### Lore Integration
- **Undead nobility** and **Crypt Lord** authority
- **Preservation magic** and **eternal winter** themes
- **Nordic heritage** and **ancient traditions**
- **Glacier-carved architecture** and **ice magic**

#### Example Content
- **Districts**: "Noble Undead Quarter", "Frozen Battlements", "The Glacier Heart"
- **Buildings**: "Crypt Lord's Ice Palace", "The Eternal Throne Room"
- **Encounters**: Undead court proceedings, preservation ceremonies
- **Random Tables**: Ice magic effects, ancient Nordic manifestations

## Technical Implementation

### Backend Changes

#### File Structure
```
src/
├── city_overlay_analyzer.py    # Updated with city-specific logic
└── ascii_map_viewer.py         # No changes needed

databases/cities/
├── galgenbeck.json            # New city database
├── bergen_chrypt.json         # New city database
└── [future_cities].json      # Template for expansion

data/city_overlays/
├── galgenbeck.jpg            # Renamed from image1.jpg
└── [city_images]             # Future city images
```

#### Core Logic Changes
```python
# OLD: Generic content generation
def _generate_district_content(self):
    districts = ["Generic District 1", "Generic District 2"]
    
# NEW: City-specific content generation  
def _generate_district_content(self, city_data=None):
    districts = self._get_city_content_list(city_data, 'districts', fallback_list)
```

### Frontend Compatibility

#### No Frontend Changes Required
The existing frontend interface remains fully functional:
- Same API endpoints (`/api/city-overlays`, `/api/city-overlay/{name}`)
- Same data structure returned
- Same interactive grid and ASCII views
- Same hex detail display

#### Enhanced User Experience
- City names now show proper canonical names
- Content is lore-appropriate and immersive
- Random tables reflect specific city themes
- Encounters reference actual lore elements

## Benefits of Refactor

### 1. Lore Accuracy
- Content now reflects canonical Mörk Borg city lore
- Encounters and locations match established themes
- Names and descriptions are lore-appropriate

### 2. Immersion
- Players experience authentic city atmosphere
- Random events tie to established city elements
- Content feels integrated with the broader world

### 3. Modularity
- Easy to add new cities by creating JSON databases
- Fallback system ensures stability
- Generic content still available for unknown cities

### 4. Maintainability
- City data separated from code logic
- Easy to update lore without code changes
- Clear structure for content organization

## Future Expansion

### Adding New Cities

1. **Create City Database**:
   ```json
   {
     "city_name": "New City",
     "display_name": "New City - The Description",
     "districts": [...],
     "buildings": [...],
     // ... other content arrays
     "encounters": {...},
     "random_tables": {...}
   }
   ```

2. **Add City Image**: Place image in `data/city_overlays/new_city.jpg`

3. **Automatic Integration**: System will automatically detect and use new city data

### Potential Enhancements

- **Multi-language support** for city databases
- **Seasonal variations** in content
- **NPC placement** and **faction influence** integration
- **District-specific** content weighting
- **Historical timeline** content variations

## Testing

### Verification Steps
1. **City Detection**: Galgenbeck properly detected from `galgenbeck.jpg`
2. **Content Generation**: City-specific content used over generic
3. **Fallback System**: Generic content used when city data unavailable
4. **API Compatibility**: Existing endpoints return expected data structure
5. **Frontend Function**: Interactive grid and ASCII views work unchanged

### Example Output
```
Available overlays: 1
  - Galgenbeck (galgenbeck.jpg)

Generated 25 hexes for Galgenbeck
Center hex content:
Name: The Corpse Sanctuary
Type: temple
Description: A sacred place dedicated to the patron of lost souls...
```

## Summary

The refactor successfully transforms the city overlay system from generic fantasy content to lore-accurate Mörk Borg city generation while maintaining full backward compatibility and providing a framework for easy expansion to additional cities.

---

**Implementation Status**: ✅ Complete  
**Frontend Impact**: ✅ No changes required  
**Backward Compatibility**: ✅ Maintained  
**Testing**: ✅ Verified functional