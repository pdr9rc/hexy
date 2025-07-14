# Sandbox Generator by Atelier Clandestin - Biome Integration Research

## Executive Summary

This research document explores how to integrate the **Sandbox Generator by Atelier Clandestin** with biome-aware generation and adapt it to the Hexy - Dying Lands hexcrawl generator codebase. The Sandbox Generator is a 156-page OSR (Old School Renaissance) supplement that provides comprehensive table-based methods for generating sandbox worlds, perfectly suited for enhancing your existing hex-based system.

## What is the Sandbox Generator by Atelier Clandestin?

### Core Description
- **Format:** 156-page PDF supplement available on DriveThruRPG
- **System:** OSR and system-neutral (works with any RPG system)
- **Focus:** Complete sandbox world generation from scratch
- **Scale:** Generates 19-hex areas at a time (perfect for hex-based systems)
- **Publisher:** Atelier Clandestin (French audiovisual production company)

### Key Features
1. **Terrain Generation:** Land and sea area creation
2. **Settlement Generation:** Villages, towns, cities, and castles
3. **Faction Systems:** Relationship mapping and conflict generation
4. **Dungeon Creation:** Unique layout system with underground connections
5. **Detailed Elements:** Monster lairs, coats of arms, treasure distribution
6. **Interconnected Systems:** All dungeons in an area can be linked underground

## Current Hexy System Analysis

### Your Existing Strengths
Based on your codebase, you already have:
```python
# From terrain_system.py
class TerrainType(Enum):
    MOUNTAIN = "mountain"
    FOREST = "forest"
    COAST = "coast"
    PLAINS = "plains"
    SWAMP = "swamp"
    DESERT = "desert"
    UNKNOWN = "unknown"

# 25x30 map (750 hexes total)
# 6 Major Mörk Borg cities with canonical placement
# Terrain-aware content generation
# Web-based interface
```

### Integration Opportunities
The Sandbox Generator's methods can enhance your system by adding:
- **Faction relationships and conflicts**
- **Detailed settlement generation**
- **Castle and fortification systems**
- **Connected dungeon networks**
- **Economic and political dynamics**

## Adaptation Strategy

### Phase 1: Table Conversion and Biome Integration

**Convert Sandbox Generator Tables to Python:**
```python
# sandbox_generator.py
class SandboxGenerator:
    def __init__(self, terrain_system, lore_database):
        self.terrain_system = terrain_system
        self.lore_db = lore_database
        self.faction_tables = self._load_faction_tables()
        self.settlement_tables = self._load_settlement_tables()
        self.castle_tables = self._load_castle_tables()
    
    def generate_region(self, center_hex, radius=9):
        """Generate a 19-hex region using Sandbox Generator methods."""
        region_hexes = self._get_region_hexes(center_hex, radius)
        
        # Apply biome-specific modifiers to generation tables
        biome_modifiers = self._get_biome_modifiers(region_hexes)
        
        return {
            'factions': self._generate_factions(region_hexes, biome_modifiers),
            'settlements': self._generate_settlements(region_hexes, biome_modifiers),
            'castles': self._generate_castles(region_hexes, biome_modifiers),
            'dungeons': self._generate_linked_dungeons(region_hexes),
            'conflicts': self._generate_faction_conflicts()
        }
```

**Biome-Aware Table Modifications:**
```python
BIOME_SETTLEMENT_MODIFIERS = {
    'mountain': {
        'fortress_chance': +2,
        'mining_settlement': +3,
        'population_modifier': -1
    },
    'forest': {
        'druid_grove': +2,
        'logging_camp': +3,
        'ranger_outpost': +2
    },
    'swamp': {
        'hermit_chance': +3,
        'witch_hut': +2,
        'population_modifier': -2
    },
    'coast': {
        'port_town': +4,
        'fishing_village': +3,
        'lighthouse': +2
    },
    'plains': {
        'farming_settlement': +3,
        'trade_route': +2,
        'population_modifier': +1
    },
    'desert': {
        'oasis_settlement': +4,
        'nomad_camp': +3,
        'population_modifier': -2
    }
}
```

### Phase 2: Faction System Integration

**Core Faction Structure (adapted from OSR research):**
```python
class Faction:
    def __init__(self, name, faction_type, territory, relationships):
        self.name = name
        self.type = faction_type  # Noble, Religious, Mercantile, Criminal, etc.
        self.territory = territory  # List of hex codes they control
        self.relationships = relationships  # Dict of other faction relationships
        self.power_level = self._calculate_power()
        self.goals = self._generate_goals()
        self.resources = self._calculate_resources()
    
    def get_relationship(self, other_faction):
        """Returns: Allied, Neutral, Hostile, or Rival"""
        return self.relationships.get(other_faction.name, 'Neutral')

FACTION_GENERATION_TABLES = {
    'noble_factions': [
        'Local Baron seeking expansion',
        'Exiled noble planning return',
        'Knight-Commander of military order',
        'Merchant prince with political ambitions'
    ],
    'religious_factions': [
        'Orthodox temple maintaining tradition',
        'Heretical cult spreading influence',
        'Monastic order preserving knowledge',
        'Death cult preparing for apocalypse'
    ],
    'criminal_factions': [
        'Thieves guild controlling trade routes',
        'Bandit clan raiding settlements',
        'Smugglers moving contraband',
        'Assassins guild accepting contracts'
    ]
}
```

### Phase 3: Enhanced Settlement Generation

**Settlement Generator with Biome Integration:**
```python
class SettlementGenerator:
    def __init__(self, sandbox_generator):
        self.sandbox = sandbox_generator
        
    def generate_settlement(self, hex_code, terrain_type, faction_influence=None):
        """Generate detailed settlement using Sandbox Generator methods."""
        base_settlement = self._roll_settlement_type(terrain_type)
        
        # Apply biome-specific characteristics
        biome_features = self._get_biome_settlement_features(terrain_type)
        
        # Apply faction influence if present
        if faction_influence:
            base_settlement = self._apply_faction_influence(base_settlement, faction_influence)
        
        return {
            'type': base_settlement['type'],
            'population': self._calculate_population(base_settlement, terrain_type),
            'government': self._determine_government(base_settlement),
            'defenses': self._generate_defenses(base_settlement, terrain_type),
            'economy': self._generate_economy(base_settlement, terrain_type),
            'notable_locations': self._generate_notable_locations(base_settlement),
            'npcs': self._generate_key_npcs(base_settlement),
            'rumors': self._generate_rumors(base_settlement),
            'faction_presence': faction_influence
        }
```

### Phase 4: Castle and Fortification System

**Adapted from the Sandbox Generator's castle example:**
```python
CASTLE_GENERATION_TABLES = {
    'condition': [
        'Pristine - Well maintained',
        'Good - Minor repairs needed', 
        'Fair - Some structural damage',
        'Poor - Major repairs required',
        'Ruined - Partially collapsed',
        'Abandoned - Overgrown ruins'
    ],
    'defensive_features': [
        'High stone walls with towers',
        'Deep moat with drawbridge',
        'Murder holes and portcullis',
        'Concentric wall design',
        'Natural cliff protection',
        'Magical ward stones'
    ],
    'garrison_composition': {
        'small': {'total': 20, 'cavalry': 2, 'archers': 6, 'infantry': 12},
        'medium': {'total': 50, 'cavalry': 8, 'archers': 15, 'infantry': 27},
        'large': {'total': 100, 'cavalry': 15, 'archers': 30, 'infantry': 55}
    }
}

def generate_castle(hex_code, terrain_type, faction_owner=None):
    """Generate castle using Sandbox Generator methodology."""
    castle_data = {
        'hex_code': hex_code,
        'name': generate_castle_name(terrain_type, faction_owner),
        'condition': random.choice(CASTLE_GENERATION_TABLES['condition']),
        'defenses': random.sample(CASTLE_GENERATION_TABLES['defensive_features'], random.randint(2, 4)),
        'garrison': generate_garrison(terrain_type),
        'lord': generate_castle_lord(faction_owner),
        'treasury': generate_treasury(),
        'special_features': generate_special_features(terrain_type),
        'strategic_importance': calculate_strategic_value(hex_code)
    }
    return castle_data
```

## Technical Implementation Plan

### 1. New Python Modules to Create

```
src/
├── sandbox_generator.py          # Main sandbox generation engine
├── faction_system.py             # Faction management and relationships
├── settlement_generator.py       # Enhanced settlement creation
├── castle_generator.py           # Castle and fortification generation
├── dungeon_connector.py          # Underground dungeon linking system
├── conflict_generator.py         # Faction conflict and plot hooks
└── sandbox_tables.py             # All generation tables and data
```

### 2. Enhanced API Endpoints

**New Flask Routes:**
```python
@app.route('/api/sandbox/generate-region/<hex_code>')
def generate_sandbox_region(hex_code):
    """Generate a 19-hex sandbox region around the specified hex."""
    sandbox = SandboxGenerator(terrain_system, lore_db)
    region_data = sandbox.generate_region(hex_code)
    return jsonify(region_data)

@app.route('/api/sandbox/factions/<hex_code>')
def get_faction_influence(hex_code):
    """Get faction influence and relationships for a hex."""
    factions = faction_system.get_local_factions(hex_code)
    return jsonify({
        'active_factions': factions,
        'conflicts': faction_system.get_active_conflicts(hex_code),
        'plot_hooks': conflict_generator.generate_plot_hooks(factions)
    })

@app.route('/api/sandbox/settlement/<hex_code>/detailed')
def get_detailed_settlement(hex_code):
    """Get comprehensive settlement details using Sandbox Generator methods."""
    terrain = terrain_system.get_terrain_for_hex(hex_code)
    factions = faction_system.get_local_factions(hex_code)
    
    settlement = settlement_generator.generate_settlement(
        hex_code, terrain, factions
    )
    return jsonify(settlement)
```

### 3. Database Schema Extensions

**New Tables for Enhanced Data:**
```sql
-- Factions table
CREATE TABLE factions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    faction_type TEXT NOT NULL,
    power_level INTEGER,
    goals TEXT,
    territory TEXT, -- JSON array of hex codes
    relationships TEXT -- JSON object of faction relationships
);

-- Settlements table (enhanced)
CREATE TABLE settlements (
    hex_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    settlement_type TEXT NOT NULL,
    population INTEGER,
    government_type TEXT,
    defenses TEXT, -- JSON array
    economy TEXT, -- JSON object
    faction_influence TEXT, -- JSON object
    notable_locations TEXT, -- JSON array
    key_npcs TEXT -- JSON array
);

-- Castles table
CREATE TABLE castles (
    hex_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    condition TEXT,
    defenses TEXT, -- JSON array
    garrison TEXT, -- JSON object
    lord_name TEXT,
    treasury TEXT, -- JSON object
    faction_owner TEXT,
    strategic_value INTEGER
);
```

## Integration with Current Features

### Enhanced Hex Generation
```python
# Modified hex_generator.py
def generate_enhanced_hex_content(hex_code, terrain_type, language='en'):
    """Enhanced hex generation using Sandbox Generator methods."""
    base_content = generate_basic_hex_content(hex_code, terrain_type, language)
    
    # Add sandbox elements
    sandbox_data = sandbox_generator.enhance_hex(hex_code, terrain_type)
    
    enhanced_content = {
        **base_content,
        'factions': sandbox_data.get('factions', []),
        'detailed_settlements': sandbox_data.get('settlements', []),
        'castles': sandbox_data.get('castles', []),
        'dungeon_connections': sandbox_data.get('dungeon_connections', []),
        'plot_hooks': sandbox_data.get('plot_hooks', []),
        'political_situation': sandbox_data.get('political_situation', {}),
        'economic_data': sandbox_data.get('economy', {})
    }
    
    return enhanced_content
```

### Web Interface Enhancements
```javascript
// Enhanced map interface
class SandboxMapViewer {
    constructor() {
        this.mapViewer = new ASCIIMapViewer();
        this.factionOverlay = new FactionOverlay();
        this.conflictMarkers = new ConflictMarkers();
    }
    
    showFactionInfluence(hexCode) {
        fetch(`/api/sandbox/factions/${hexCode}`)
            .then(response => response.json())
            .then(data => {
                this.factionOverlay.displayFactions(data.active_factions);
                this.conflictMarkers.displayConflicts(data.conflicts);
                this.updatePlotHooks(data.plot_hooks);
            });
    }
    
    generateSandboxRegion(centerHex) {
        fetch(`/api/sandbox/generate-region/${centerHex}`)
            .then(response => response.json())
            .then(data => {
                this.updateRegionalView(data);
                this.displayFactionMap(data.factions);
                this.highlightConflictZones(data.conflicts);
            });
    }
}
```

## Example Implementation: Faction Conflict Generation

**Based on OSR Research Methods:**
```python
class ConflictGenerator:
    def __init__(self, faction_system):
        self.factions = faction_system
        
    def generate_regional_conflicts(self, hex_list):
        """Generate faction conflicts using Sandbox Generator principles."""
        active_factions = self.factions.get_factions_in_region(hex_list)
        conflicts = []
        
        for faction_a in active_factions:
            for faction_b in active_factions:
                if faction_a != faction_b:
                    relationship = faction_a.get_relationship(faction_b)
                    if relationship in ['Hostile', 'Rival']:
                        conflict = self._generate_conflict(faction_a, faction_b)
                        conflicts.append(conflict)
        
        return conflicts
    
    def _generate_conflict(self, faction_a, faction_b):
        """Generate specific conflict between two factions."""
        conflict_types = [
            'Territory Dispute',
            'Resource Competition', 
            'Ideological Opposition',
            'Personal Vendetta',
            'Economic Rivalry',
            'Religious Schism'
        ]
        
        conflict_type = random.choice(conflict_types)
        intensity = random.randint(1, 5)
        
        return {
            'type': conflict_type,
            'factions': [faction_a.name, faction_b.name],
            'intensity': intensity,
            'description': self._generate_conflict_description(
                conflict_type, faction_a, faction_b
            ),
            'plot_hooks': self._generate_conflict_plot_hooks(
                conflict_type, faction_a, faction_b
            ),
            'potential_outcomes': self._generate_potential_outcomes(
                conflict_type, intensity
            )
        }
```

## Biome-Specific Sandbox Features

### Terrain-Aware Generation Tables

**Mountain Regions:**
```python
MOUNTAIN_SANDBOX_FEATURES = {
    'settlements': {
        'mining_camp': 30,
        'dwarven_hold': 15,
        'mountain_monastery': 10,
        'trading_post': 20,
        'bandit_stronghold': 15,
        'hermit_retreat': 10
    },
    'factions': {
        'mining_guild': 25,
        'mountain_clan': 30,
        'religious_order': 15,
        'bandit_gang': 20,
        'merchant_company': 10
    },
    'conflicts': [
        'Mining rights disputes',
        'Clan territorial wars',
        'Bandit raids on trade routes',
        'Religious zealots vs. secular miners'
    ]
}
```

**Forest Regions:**
```python
FOREST_SANDBOX_FEATURES = {
    'settlements': {
        'logging_camp': 25,
        'druid_grove': 15,
        'ranger_outpost': 20,
        'hidden_village': 15,
        'bandit_camp': 15,
        'witch_hut': 10
    },
    'factions': {
        'druid_circle': 30,
        'ranger_company': 20,
        'logging_guild': 15,
        'forest_bandits': 20,
        'nature_cult': 15
    },
    'special_features': [
        'Ancient tree with magical properties',
        'Hidden fairy ring portals',
        'Abandoned elven ruins',
        'Sacred grove protected by spirits'
    ]
}
```

## Integration Timeline

### Phase 1 (Week 1-2): Foundation
- [ ] Research and adapt core Sandbox Generator tables
- [ ] Create basic faction system
- [ ] Implement simple settlement enhancement
- [ ] Test integration with existing hex generation

### Phase 2 (Week 3-4): Core Features  
- [ ] Implement castle generation system
- [ ] Add faction relationship mapping
- [ ] Create conflict generation engine
- [ ] Enhance web interface with faction overlays

### Phase 3 (Week 5-6): Advanced Features
- [ ] Add dungeon connection system
- [ ] Implement economic modeling
- [ ] Create plot hook generation
- [ ] Add biome-specific specializations

### Phase 4 (Week 7-8): Polish and Testing
- [ ] Comprehensive testing and debugging
- [ ] Performance optimization
- [ ] Documentation creation
- [ ] User interface refinement

## Benefits of Integration

### For Game Masters
1. **Rich Political Landscape:** Factions with clear motivations and conflicts
2. **Detailed Settlements:** Every town has personality and purpose
3. **Connected World:** Underground dungeons link regions meaningfully
4. **Plot Hook Generation:** Automatic adventure seeds from faction conflicts
5. **Scalable Complexity:** Can be as simple or detailed as needed

### For Players
1. **Meaningful Choices:** Political decisions have consequences
2. **Dynamic World:** Faction relationships evolve based on player actions
3. **Exploration Rewards:** Discovering faction secrets and alliances
4. **Multiple Story Threads:** Various faction conflicts to engage with
5. **Economic Opportunities:** Trade routes and resource control

### For the Codebase
1. **Modular Design:** New systems integrate cleanly with existing code
2. **API Expansion:** New endpoints for enhanced functionality
3. **Data Richness:** More detailed world state tracking
4. **Extensibility:** Framework for future sandbox features
5. **Backwards Compatibility:** Existing features remain unchanged

## Conclusion

The Sandbox Generator by Atelier Clandestin provides excellent table-based methods that can be directly adapted to enhance your Hexy hexcrawl generator. By converting its OSR tables to Python code and integrating them with your existing biome system, you can create a much richer, more dynamic sandbox world.

The key insight is that the Sandbox Generator's strength lies in its systematic approach to creating interconnected elements (factions, settlements, conflicts) that make the world feel alive and reactive to player choices. This perfectly complements your existing terrain generation and Mörk Borg lore integration.

The proposed implementation maintains your current Flask/web architecture while adding powerful new sandbox generation capabilities that will make each hex feel like part of a living, breathing world with political intrigue, economic relationships, and ongoing conflicts that players can discover and influence.

## Resources and References

1. **The Sandbox Generator by Atelier Clandestin** - DriveThruRPG
2. **OSR Sandbox Generation Methods** - Various blog sources
3. **Bat in the Attic Random Village Generation** - Detailed OSR examples
4. **Ground Rules Generator** - PBE Games hex crawl system
5. **Medieval Economics Research** - Historical accuracy for economic modeling
6. **Faction Relationship Matrices** - OSR community best practices

## Next Steps

1. **Acquire the Sandbox Generator PDF** from DriveThruRPG to access complete tables
2. **Plan table conversion priorities** based on your campaign needs
3. **Design database schema** for new faction and settlement data
4. **Create prototype implementation** of core faction system
5. **Test integration** with existing Mörk Borg cities and lore