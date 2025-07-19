#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from ascii_map_viewer import extract_hex_data

# Test content from a hex file
content = '''# Hex 2025

**Terrain:** Mountain

## Encounter
▲ **Ancient Ruins**

## Denizen
Tax collection dungeon, littered with ancient bones.

**Danger:** Toxic mold
**Atmosphere:** Scratching sounds

**Treasure Found:** Broken shield (AC +1, once magnificent)

```
      /\\  /\\  /\\
     /  \\/  \\/  \\
    [    ][    ]
    | ?? || ?? |
    [____][____]
        ```

## Notable Feature
Ancient tax collection dungeon

## Atmosphere
Scratching sounds'''

result = extract_hex_data(content, '2025')
print('TERRAIN:', result['terrain'])
print('ENCOUNTER:', result['encounter'])
print('DENIZEN:', result['denizen'])
print('TREASURE:', result['treasure'])
print('DANGER:', result['danger'])
print('ATMOSPHERE:', result['atmosphere'])
print('NOTABLE FEATURE:', result['notable_feature']) 