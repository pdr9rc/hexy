# The Dying Lands API Documentation

## Overview
This document describes the main API endpoints for accessing hex, city, and settlement data in The Dying Lands project. It details the expected request and response structures, field types, and provides example responses.

---

## Endpoints

### 1. Get Hex Data
**Endpoint:** `/api/hex/<hex_code>`
**Method:** `GET`

**Response:**
```json
{
  "hex_code": "1513",
  "terrain": "plains",
  "exists": true,
  "hex_type": "settlement",
  "is_settlement": true,
  "name": "Galgenbeck",
  "description": "A sprawling metropolis built atop the bones...",
  "population": "1000+",
  "atmosphere": "Urban decay, perpetual twilight...",
  "notable_feature": "Hanging Gardens of Corpses...",
  "local_tavern": "Major city establishment",
  "local_power": "City authority",
  "settlement_art": "Major city layout",
  "encounter": "Major City: Galgenbeck (Population: 1000+)",
  "denizen": {
    "raw": "Galgenbeck - Major City...",
    "fields": { "key_npcs": ["Josilfa Migol", "The Galgenbeck Council"] },
    "ascii_art": []
  },
  "loot": null,
  ...
}
```

**Field Types:**
- `terrain`: string (e.g., "plains", "mountain", "forest", ...)
- `hex_type`: string (e.g., "settlement", "dungeon", "beast", ...)
- `encounter`, `denizen`, `notable_feature`, `atmosphere`: string or object with `raw`, `fields`, `ascii_art`
- `loot`: object, array, or null
- `exists`: boolean

---

### 2. Get City Details
**Endpoint:** `/api/city/<hex_code>`
**Method:** `GET`

**Response:**
```json
{
  "success": true,
  "city": {
    "name": "Galgenbeck",
    "description": "A sprawling metropolis built atop the bones...",
    "population": "1000+",
    "region": "Central",
    "atmosphere": "Urban decay, perpetual twilight...",
    "notable_features": [
      "Hanging Gardens of Corpses",
      "Secretive ruling council",
      "Labyrinthine sewers"
    ],
    "key_npcs": ["Josilfa Migol", "The Galgenbeck Council"]
  },
  "regional_npcs": ["NPC1", "NPC2"],
  "factions": [
    { "name": "Faction1", "influence": "High", "description": "..." }
  ]
}
```

**Field Types:**
- `notable_features`, `key_npcs`, `regional_npcs`: array of strings
- `factions`: array of objects

---

### 3. Get Settlement Details
**Endpoint:** `/api/settlement/<hex_code>`
**Method:** `GET`

**Response:**
```json
{
  "success": true,
  "settlement": {
    "name": "Small Village",
    "description": "A quiet settlement...",
    "population": "200",
    "atmosphere": "Peaceful",
    "notable_feature": "Ancient well",
    "local_tavern": "The Rusty Mug",
    "local_power": "Village Elder",
    "terrain": "plains"
  }
}
```

**Field Types:**
- All fields are strings except `population` (string or number) and `terrain` (string).

---

## Notes
- All endpoints return JSON.
- If a hex does not exist, the response will include `{ "exists": false, "hex_code": <hex_code> }`.
- For structured fields (e.g., `denizen`, `notable_feature`), the object may include `raw` (string), `fields` (object), and `ascii_art` (array of strings).
- The API is subject to change; for breaking changes, versioning will be introduced. 