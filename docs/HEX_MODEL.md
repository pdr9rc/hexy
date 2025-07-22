# Hex Model Documentation

## Overview
The Dying Lands uses a hex-based map system where each hex represents a distinct location with unique content. This document outlines the data model and content structure for hexes.

## Core Hex Structure

### Basic Hex Information
```json
{
  "hex_code": "1509",
  "terrain": "plains|forest|mountain|coast|swamp|desert|sea",
  "exists": true,
  "hex_type": "wilderness|settlement|dungeon|beast|npc|sea_encounter"
}
```

### Content Types

#### 1. Wilderness Hexes
Basic terrain hexes with minimal content.

#### 2. Settlement Hexes (⌂)
```json
{
  "is_settlement": true,
  "name": "Boar Creek",
  "description": "A 20-50 settlement in the plains.",
  "population": "20-50|51-100|101-500|501-1000",
  "atmosphere": "Open and exposed",
  "notable_feature": "Ancient standing stones",
  "local_tavern": "The Moldy Barrel",
  "local_power": "Religious fanatic|Bandit chief|Cult leader|Mad prophet|Undead noble|Mysterious hermit",
  "settlement_art": "ASCII art representation",
  "terrain": "plains|forest|mountain|coast|swamp|desert"
}
```

#### 3. Dungeon Hexes (▲)
```json
{
  "is_dungeon": true,
  "encounter": "▲ **Sacrificial chamber**",
  "dungeon_type": "Sacrificial chamber|Forgotten crypt|Underground warren|Ruined temple|Abandoned tower|Sunken cathedral|Bone pit|Cursed cellar|Twisted labyrinth|Plague house|Ancient tomb|Collapsed mine",
  "denizen": "Sacrificial chamber, overrun with vermin.",
  "danger": "Magical wards|Pit trap with spikes|Collapsing ceiling|Predatory creatures|Poisonous gas leak|Hidden blade traps|Disease-ridden corpses|Toxic mold|Cursed artifacts|Unstable floor|Aggressive scavengers|Ancient curses|Structural decay|Flooding chambers",
  "atmosphere": "Oppressive silence|Distant moaning|Echoing drips|Scratching sounds|Unnatural cold",
  "notable_feature": "Ancient sacrificial chamber",
  "treasure": "Forgotten tools|Precious gemstones|Ancient scrolls|Religious artifacts|Ornate containers|Carved idols|Lost books|Silver coins scattered about|Mysterious potions|Rare herbs and components|Jewelry from the dead|A rusted but valuable weapon|Rare metals|Old maps and documents",
  "loot": {
    "description": "Demon bottle (600 coins, contains something)",
    "full_description": "**Demon bottle (600 coins, contains something)**\n\n**Magical Effect:** Glimmers with dark energy",
    "item": "Demon bottle (600 coins, contains something)",
    "type": "valuable|armor|weapon|utility"
  },
  "scroll": {
    "content": "summoning circles",
    "description": "**Stone inscriptions** containing summoning circles that drives reader temporarily mad.",
    "effect": "drives reader temporarily mad",
    "type": "Stone inscriptions|Crumbling parchment|Blood-stained vellum|Skin manuscripts|Metal scrolls|Flesh pages|Wax tablets"
  }
}
```

#### 4. Beast Hexes (※)
```json
{
  "is_beast": true,
  "encounter": "※ **Void Spider Encounter**",
  "beast_type": "Void spider|Grave worm|Blood leech|Doom moth|Flesh wasp|Death adder|Blight bat|Acid toad|Sewer serpent|Rust beetle|Plague rat|Scream bird|Shadow wolf|Spine crawler|Bone spider|Corpse crow|Terror mole",
  "beast_feature": "glowing red eyes|translucent skin|rotting flesh|constantly bleeding|multiple heads|emits toxic fumes|exposed ribs|venomous bite|razor-sharp claws|acidic saliva|backwards joints|metallic scales|diseased fur",
  "beast_behavior": "screams before attacking|ambushes from shadows|phases through walls|hunts in packs|plays dead|drains blood|feeds on corpses|hangs from ceilings|spits acid|stalks silently|spreads disease|burrows underground|mimics voices",
  "denizen": "A Void spider with glowing red eyes that screams before attacking.",
  "territory": "This creature has claimed this area of plains as its hunting ground.",
  "threat_level": "High - approach with extreme caution.",
  "notable_feature": "Beast territory",
  "atmosphere": "Tense and dangerous",
  "loot": {
    "description": "Rusty chainmail (AC 14, noisy)",
    "full_description": "**Rusty chainmail (AC 14, noisy)**\n\n**Magical Effect:** Whispers ancient secrets",
    "item": "Rusty chainmail (AC 14, noisy)",
    "type": "armor"
  }
}
```

#### 5. NPC Hexes (☉)
```json
{
  "is_npc": true,
  "encounter": "☉ **Wandering Plains dweller**",
  "name": "Lost Crow",
  "denizen_type": "Plains dweller",
  "motivation": "seeks redemption for past sins|flees from terrible pursuers|hunts for forbidden knowledge|spreads word of the coming end|searches for lost family|trades in human misery|worships forgotten gods|prophesies doom and destruction|harvests organs for dark rituals|guards ancient secrets|seeks to break an ancient curse",
  "feature": "Bears holy symbols|Nervous tics and twitches|Carries strange implements|Teeth filed to points|Constantly muttering prayers|Wears tattered robes|Eyes clouded with cataracts|Moves with unnatural stiffness|Missing several fingers|Speaks in whispers|Unnaturally pale skin|Burns easily in sunlight",
  "demeanor": "Hostile|Desperate|Indifferent|Cryptic|Suspicious|Helpful",
  "notable_feature": "NPC territory",
  "atmosphere": "Mysterious and unpredictable",
  "loot": {
    "description": "Cursed helmet (AC +1, constant whispers)",
    "full_description": "**Cursed helmet (AC +1, constant whispers)**\n\n**Magical Effect:** Pulses with unholy power",
    "item": "Cursed helmet (AC +1, constant whispers)",
    "type": "armor"
  }
}
```

#### 6. Sea Encounter Hexes (≈)
```json
{
  "is_sea_encounter": true,
  "encounter": "≈ **Abyssal Nightmare Encounter**",
  "encounter_type": "Abyssal Nightmare",
  "denizen": "An entity that exists between dreams and reality, haunting the ocean's edge.",
  "territory": "This section of the sea has been claimed by the nightmare, its influence corrupting the very waters themselves.",
  "threat_level": "Catastrophic - this entity represents an existential threat to all who encounter it.",
  "notable_feature": "Waters that whisper of forgotten terrors|A spot where the sea seems to bleed darkness|A location where time itself seems to flow differently",
  "atmosphere": "The water seems to pulse with an unnatural rhythm",
  "loot": {
    "description": "Demon bottle (600 coins, contains something)",
    "full_description": "**Demon bottle (600 coins, contains something)**\n\n**Magical Effect:** Pulses with unholy power",
    "item": "Demon bottle (600 coins, contains something)",
    "type": "valuable"
  }
}
```

## Terrain ASCII Art

Each terrain type has specific ASCII art representation:

```javascript
const terrainArt = {
  'mountain': `    /\\   /\\   /\\
   /  \\_/  \\_/  \\
  /            \\
 /              \\`,
  'forest': `      /\\      /\\
     /  \\    /  \\
    /____\\  /____\\
      ||      ||`,
  'coast': `   ~   ~   ~   ~
 ~   ~   ~   ~
   ~   ~   ~   ~`,
  'plains': `  .  .  .  .  .
 .  .  .  .  .
  .  .  .  .  .`,
  'swamp': `  # # # # # #
 # # # # # # #
  # # # # # #`,
  'desert': `  ~~~~~~~~~~~
 ~~~~~.~~~~~
  ~~~~~~~~~~~`,
  'sea': `  ≈ ≈ ≈ ≈ ≈ ≈
 ≈ ≈ ≈ ≈ ≈ ≈
  ≈ ≈ ≈ ≈ ≈ ≈`
};
```

## Content Generation Patterns

### Loot Types
- **Valuable**: Demon bottles, Soul gems, Ancient tomes, Golden skull chalices, Cursed jewelry
- **Armor**: Rusty chainmail, Plague doctor's robes, Grave dirt coating, Cursed helmets, Thieves' leathers
- **Weapons**: Bone daggers, Rusted swords, Executioner's axes, Plague doctor's canes, Witch hunter's crossbows
- **Utility**: Lanterns with oil, Crowbars, Ropes, Smoke bombs, Healing potions, Holy water

### Magical Effects
- "Pulses with unholy power"
- "Whispers ancient secrets"
- "Glimmers with dark energy"
- "Radiates cold"

### Ancient Knowledge Effects
- "drives reader temporarily mad"
- "causes uncontrollable fear"
- "ages the reader rapidly"
- "burns the reader's hands"
- "grants dark knowledge"
- "inflicts temporary blindness"
- "causes nightmares when read"
- "summons malevolent spirits"
- "attracts undead"
- "curses the reader"
- "reveals hidden truths"
- "whispers dark secrets"

## Map Dimensions
- **Width**: 25 hexes
- **Height**: 30 hexes
- **Total**: 750 hexes

## File Structure
```
dying_lands_output/
├── hexes/
│   ├── hex_0101.md
│   ├── hex_0102.md
│   └── ... (750 files)
└── city_overlays/
    ├── galgenbeck_overlay.json
    └── bergen_chrypt_overlay.json
```

## API Endpoints

### Hex Information
- `GET /api/hex/{hex_code}` - Get hex content
- `POST /api/generate-hex` - Generate single hex
- `POST /api/generate-full-map` - Generate all hexes
- `POST /api/reset-continent` - Reset and regenerate all content

### Settlement Information
- `GET /api/settlement/{hex_code}` - Get settlement details

### City Information
- `GET /api/city/{hex_code}` - Get major city details
- `GET /api/city-overlays` - Get available city overlays
- `GET /api/city-overlay/{overlay_name}` - Get city overlay data

### Lore Information
- `GET /api/lore-overview` - Get world lore overview 