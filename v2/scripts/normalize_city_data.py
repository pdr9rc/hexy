#!/usr/bin/env python3
"""
Normalize city JSON files by moving city-level data into districts.
Distributes buildings, streets, landmarks, markets, temples, taverns, guilds, residences, ruins,
encounters, random_tables, and atmosphere_modifiers from root level into appropriate districts.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher

def similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_district_match(item: str, districts: List[Dict[str, Any]], item_type: str) -> Optional[int]:
    """Find the best matching district for an item based on name, theme, and description.
    Always returns a district index (never None) - uses balanced distribution if no strong match."""
    best_match_idx = None
    best_score = 0.0
    all_scores = []
    
    for idx, district in enumerate(districts):
        score = 0.0
        district_name = district.get('name', '').lower()
        district_theme = district.get('theme', '').lower()
        district_desc = district.get('description', '').lower()
        item_lower = item.lower()
        
        # Check name similarity
        name_sim = similarity(item, district_name)
        if name_sim > 0.3:
            score += name_sim * 0.4
        
        # Check if item name appears in district name or description
        if item_lower in district_name or district_name in item_lower:
            score += 0.3
        if item_lower in district_desc or any(word in district_desc for word in item_lower.split() if len(word) > 3):
            score += 0.2
        
        # Theme-based matching
        theme_keywords = {
            'temple': ['temple', 'cathedral', 'church', 'shrine', 'holy', 'sacred', 'religious'],
            'market': ['market', 'bazaar', 'trade', 'commerce', 'merchant'],
            'tavern': ['tavern', 'inn', 'bar', 'ale', 'drink'],
            'guild': ['guild', 'union', 'association', 'society', 'order'],
            'residence': ['residence', 'manor', 'house', 'palace', 'quarters', 'dwelling'],
            'ruins': ['ruin', 'collapsed', 'fallen', 'shattered', 'abandoned'],
            'building': ['building', 'warehouse', 'factory', 'hospital', 'prison'],
            'street': ['street', 'road', 'avenue', 'lane', 'path', 'way'],
            'landmark': ['landmark', 'fountain', 'tree', 'clock', 'well', 'bridge']
        }
        
        for keyword_type, keywords in theme_keywords.items():
            if keyword_type == item_type:
                for keyword in keywords:
                    if keyword in item_lower:
                        if keyword in district_theme or keyword in district_desc:
                            score += 0.1
        
        all_scores.append((idx, score))
        if score > best_score:
            best_score = score
            best_match_idx = idx
    
    # If we have a strong match (score > 0.2), use it
    if best_score > 0.2:
        return best_match_idx
    
    # Otherwise, return the district with the highest score (even if low)
    # This ensures we always return a district
    if best_match_idx is not None:
        return best_match_idx
    
    # Fallback: return first district
    return 0 if districts else None

def remove_duplicates(items: List[Any]) -> List[Any]:
    """Remove duplicate items from a list, preserving order."""
    seen = set()
    result = []
    for item in items:
        # Create a key for comparison
        if isinstance(item, dict):
            key = item.get('name', str(item))
        else:
            key = str(item)
        
        key_lower = key.lower().strip()
        if key_lower not in seen:
            seen.add(key_lower)
            result.append(item)
    return result

def balance_distribute_items(items: List[Any], districts: List[Dict[str, Any]], 
                            array_key: str, item_type: str) -> None:
    """Distribute items across districts in a balanced way, removing duplicates."""
    if not items or not districts:
        return
    
    # Remove duplicates first
    unique_items = remove_duplicates(items)
    
    # First pass: try to match items to districts by theme
    matched_items = []
    unmatched_items = []
    
    for item in unique_items:
        item_name = item.get('name', str(item)) if isinstance(item, dict) else str(item)
        match_idx = find_best_district_match(item_name, districts, item_type)
        
        if match_idx is not None and match_idx < len(districts):
            # Check if this is a strong match (score > 0.2)
            # We'll use a simple heuristic: if item name contains district name or vice versa
            district_name = districts[match_idx].get('name', '').lower()
            item_lower = item_name.lower()
            is_strong_match = (
                district_name in item_lower or 
                item_lower in district_name or
                similarity(item_name, district_name) > 0.3
            )
            
            if is_strong_match:
                # Strong match - add to this district
                districts[match_idx][array_key].append(item)
                matched_items.append(item)
            else:
                # Weak match - add to unmatched for balanced distribution
                unmatched_items.append((item, match_idx))
        else:
            unmatched_items.append((item, None))
    
    # Second pass: distribute unmatched items in a balanced way
    if unmatched_items:
        # Count current items per district for this array type
        district_counts = [len(d.get(array_key, [])) for d in districts]
        
        for item, preferred_idx in unmatched_items:
            if preferred_idx is not None and preferred_idx < len(districts):
                # Use preferred district if provided
                target_idx = preferred_idx
            else:
                # Find district with fewest items of this type
                target_idx = district_counts.index(min(district_counts))
            
            districts[target_idx][array_key].append(item)
            district_counts[target_idx] += 1

def normalize_city_file(city_path: Path) -> bool:
    """Normalize a single city JSON file."""
    print(f"Normalizing {city_path.name}...")
    
    try:
        with open(city_path, 'r', encoding='utf-8') as f:
            city_data = json.load(f)
    except Exception as e:
        print(f"Error loading {city_path}: {e}")
        return False
    
    # Check if already normalized (no city-level arrays)
    city_level_arrays = ['buildings', 'streets', 'landmarks', 'markets', 'temples', 
                        'taverns', 'guilds', 'residences', 'ruins']
    has_city_level = any(key in city_data for key in city_level_arrays)
    has_city_encounters = 'encounters' in city_data and isinstance(city_data['encounters'], dict)
    has_city_random_tables = 'random_tables' in city_data and isinstance(city_data['random_tables'], dict)
    has_city_atmosphere = 'atmosphere_modifiers' in city_data and isinstance(city_data['atmosphere_modifiers'], list)
    
    # Check if there are General districts that need redistribution
    districts = city_data.get('districts', [])
    has_general_district = any(
        d.get('name', '').lower() in ['general', 'city center', 'center'] 
        for d in districts
    )
    
    # If already normalized AND no General districts, skip
    if not (has_city_level or has_city_encounters or has_city_random_tables or has_city_atmosphere) and not has_general_district:
        print(f"  {city_path.name} already normalized, skipping...")
        return True
    
    # If has General district, we need to redistribute even if otherwise normalized
    if has_general_district:
        print(f"  {city_path.name} has General district(s), redistributing...")
    
    # districts already loaded above if checking for General
    if 'districts' not in locals():
        districts = city_data.get('districts', [])
    if not districts:
        print(f"  Warning: {city_path.name} has no districts, skipping...")
        return False
    
    # Ensure all districts have required structure
    for district in districts:
        if 'buildings' not in district:
            district['buildings'] = []
        if 'streets' not in district:
            district['streets'] = []
        if 'landmarks' not in district:
            district['landmarks'] = []
        if 'markets' not in district:
            district['markets'] = []
        if 'temples' not in district:
            district['temples'] = []
        if 'taverns' not in district:
            district['taverns'] = []
        if 'guilds' not in district:
            district['guilds'] = []
        if 'residences' not in district:
            district['residences'] = []
        if 'ruins' not in district:
            district['ruins'] = []
        # Encounters can be list or dict - normalize to dict
        if 'encounters' not in district:
            district['encounters'] = {}
        elif isinstance(district['encounters'], list):
            # Convert list to dict with 'district' key
            old_encounters = district['encounters']
            district['encounters'] = {'district': old_encounters}
        # Random tables can be list or dict - normalize to dict
        if 'random_tables' not in district:
            district['random_tables'] = {}
        elif isinstance(district['random_tables'], list):
            # Convert list to dict with 'district' key
            old_tables = district['random_tables']
            district['random_tables'] = {'district': old_tables}
        if 'atmosphere_modifiers' not in district:
            district['atmosphere_modifiers'] = []
    
    # Distribute city-level arrays with balanced distribution and duplicate removal
    array_types = {
        'buildings': 'building',
        'streets': 'street',
        'landmarks': 'landmark',
        'markets': 'market',
        'temples': 'temple',
        'taverns': 'tavern',
        'guilds': 'guild',
        'residences': 'residence',
        'ruins': 'ruins'
    }
    
    for array_key, item_type in array_types.items():
        if array_key in city_data:
            items = city_data[array_key]
            if isinstance(items, list) and items:
                # Remove duplicates and distribute in balanced way
                balance_distribute_items(items, districts, array_key, item_type)
                
                # Remove duplicates from each district after distribution
                for district in districts:
                    if array_key in district:
                        district[array_key] = remove_duplicates(district[array_key])
                
                print(f"  Distributed {len(items)} {array_key} (removed duplicates, balanced across districts)")
    
    # Distribute city-level encounters with balanced distribution
    if 'encounters' in city_data and isinstance(city_data['encounters'], dict):
        city_encounters = city_data['encounters']
        for encounter_type, encounters in city_encounters.items():
            if isinstance(encounters, list) and encounters:
                # Remove duplicates first
                unique_encounters = remove_duplicates(encounters)
                
                # Count current encounters per district for this type
                district_counts = []
                for district in districts:
                    count = len(district.get('encounters', {}).get(encounter_type, []))
                    district_counts.append(count)
                
                # Distribute encounters
                for encounter in unique_encounters:
                    match_idx = find_best_district_match(encounter, districts, encounter_type)
                    if match_idx is not None and match_idx < len(districts):
                        # Check for strong match
                        district_name = districts[match_idx].get('name', '').lower()
                        encounter_str = encounter.lower() if isinstance(encounter, str) else str(encounter).lower()
                        is_strong_match = (
                            district_name in encounter_str or 
                            encounter_str in district_name or
                            similarity(encounter_str, district_name) > 0.3
                        )
                        
                        if is_strong_match:
                            target_idx = match_idx
                        else:
                            # Balance: use district with fewest encounters of this type
                            target_idx = district_counts.index(min(district_counts))
                    else:
                        # Balance: use district with fewest encounters of this type
                        target_idx = district_counts.index(min(district_counts))
                    
                    if encounter_type not in districts[target_idx]['encounters']:
                        districts[target_idx]['encounters'][encounter_type] = []
                    districts[target_idx]['encounters'][encounter_type].append(encounter)
                    district_counts[target_idx] += 1
                
                # Remove duplicates from each district
                for district in districts:
                    if encounter_type in district.get('encounters', {}):
                        district['encounters'][encounter_type] = remove_duplicates(
                            district['encounters'][encounter_type]
                        )
        print(f"  Distributed encounters (removed duplicates, balanced across districts)")
    
    # Distribute city-level random_tables with balanced distribution
    if 'random_tables' in city_data and isinstance(city_data['random_tables'], dict):
        city_random_tables = city_data['random_tables']
        for table_type, table_entries in city_random_tables.items():
            if isinstance(table_entries, list) and table_entries:
                # Remove duplicates first
                unique_entries = remove_duplicates(table_entries)
                
                # Count current entries per district for this type
                district_counts = []
                for district in districts:
                    count = len(district.get('random_tables', {}).get(table_type, []))
                    district_counts.append(count)
                
                # Distribute entries
                for entry in unique_entries:
                    match_idx = find_best_district_match(entry, districts, table_type)
                    if match_idx is not None and match_idx < len(districts):
                        # Check for strong match
                        district_name = districts[match_idx].get('name', '').lower()
                        entry_str = entry.lower() if isinstance(entry, str) else str(entry).lower()
                        is_strong_match = (
                            district_name in entry_str or 
                            entry_str in district_name or
                            similarity(entry_str, district_name) > 0.3
                        )
                        
                        if is_strong_match:
                            target_idx = match_idx
                        else:
                            # Balance: use district with fewest entries of this type
                            target_idx = district_counts.index(min(district_counts))
                    else:
                        # Balance: use district with fewest entries of this type
                        target_idx = district_counts.index(min(district_counts))
                    
                    if table_type not in districts[target_idx]['random_tables']:
                        districts[target_idx]['random_tables'][table_type] = []
                    districts[target_idx]['random_tables'][table_type].append(entry)
                    district_counts[target_idx] += 1
                
                # Remove duplicates from each district
                for district in districts:
                    if table_type in district.get('random_tables', {}):
                        district['random_tables'][table_type] = remove_duplicates(
                            district['random_tables'][table_type]
                        )
        print(f"  Distributed random_tables (removed duplicates, balanced across districts)")
    
    # Distribute city-level atmosphere_modifiers (remove duplicates, add to all districts)
    if 'atmosphere_modifiers' in city_data and isinstance(city_data['atmosphere_modifiers'], list):
        atmosphere_items = city_data['atmosphere_modifiers']
        # Remove duplicates
        unique_atmosphere = remove_duplicates(atmosphere_items)
        # Add to all districts (shared atmosphere)
        for district in districts:
            # Remove duplicates from existing and new
            existing = district.get('atmosphere_modifiers', [])
            combined = existing + unique_atmosphere
            district['atmosphere_modifiers'] = remove_duplicates(combined)
        print(f"  Distributed {len(unique_atmosphere)} unique atmosphere_modifiers to all districts")
    
    # Remove city-level arrays
    for key in array_types.keys():
        city_data.pop(key, None)
    city_data.pop('encounters', None)
    city_data.pop('random_tables', None)
    city_data.pop('atmosphere_modifiers', None)
    
    # Find and redistribute "General" district if it exists
    general_districts = [d for d in districts if d.get('name', '').lower() in ['general', 'city center', 'center']]
    if general_districts:
        print(f"  Found {len(general_districts)} 'General' district(s), redistributing...")
        for general_dist in general_districts:
            # Redistribute all items from General district
            for array_key, item_type in array_types.items():
                if array_key in general_dist and general_dist[array_key]:
                    items = general_dist[array_key]
                    balance_distribute_items(items, districts, array_key, item_type)
                    # Remove duplicates from each district after redistribution
                    for district in districts:
                        if array_key in district:
                            district[array_key] = remove_duplicates(district[array_key])
                    print(f"    Redistributed {len(items)} {array_key} from General district")
            
            # Redistribute encounters
            if 'encounters' in general_dist and isinstance(general_dist['encounters'], dict):
                for encounter_type, encounters in general_dist['encounters'].items():
                    if isinstance(encounters, list) and encounters:
                        unique_encounters = remove_duplicates(encounters)
                        district_counts = [len(d.get('encounters', {}).get(encounter_type, [])) for d in districts]
                        for encounter in unique_encounters:
                            target_idx = district_counts.index(min(district_counts))
                            if encounter_type not in districts[target_idx]['encounters']:
                                districts[target_idx]['encounters'][encounter_type] = []
                            districts[target_idx]['encounters'][encounter_type].append(encounter)
                            district_counts[target_idx] += 1
                        print(f"    Redistributed {len(encounters)} {encounter_type} encounters from General district")
            
            # Redistribute random_tables
            if 'random_tables' in general_dist and isinstance(general_dist['random_tables'], dict):
                for table_type, entries in general_dist['random_tables'].items():
                    if isinstance(entries, list) and entries:
                        unique_entries = remove_duplicates(entries)
                        district_counts = [len(d.get('random_tables', {}).get(table_type, [])) for d in districts]
                        for entry in unique_entries:
                            target_idx = district_counts.index(min(district_counts))
                            if table_type not in districts[target_idx]['random_tables']:
                                districts[target_idx]['random_tables'][table_type] = []
                            districts[target_idx]['random_tables'][table_type].append(entry)
                            district_counts[target_idx] += 1
                        print(f"    Redistributed {len(entries)} {table_type} random_table entries from General district")
        
        # Remove General districts
        districts = [d for d in districts if d.get('name', '').lower() not in ['general', 'city center', 'center']]
        print(f"  Removed {len(general_districts)} General district(s)")
    
    # Update districts in city_data
    city_data['districts'] = districts
    
    # Save normalized file
    try:
        with open(city_path, 'w', encoding='utf-8') as f:
            json.dump(city_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Normalized {city_path.name}")
        return True
    except Exception as e:
        print(f"  Error saving {city_path}: {e}")
        return False

def main():
    """Normalize all city JSON files."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    cities_en_dir = repo_root / 'databases' / 'cities' / 'en'
    cities_pt_dir = repo_root / 'databases' / 'cities' / 'pt'
    
    if not cities_en_dir.exists():
        print(f"Error: {cities_en_dir} does not exist")
        return 1
    
    # Normalize English cities
    print("Normalizing English city files...")
    en_files = list(cities_en_dir.glob('*.json'))
    # Skip metadata files
    en_files = [f for f in en_files if f.name not in ['cities.json', 'major_cities.json']]
    
    success_count = 0
    for city_file in en_files:
        if normalize_city_file(city_file):
            success_count += 1
    
    print(f"\nNormalized {success_count}/{len(en_files)} English city files")
    
    # Normalize Portuguese cities if directory exists
    if cities_pt_dir.exists():
        print("\nNormalizing Portuguese city files...")
        pt_files = list(cities_pt_dir.glob('*.json'))
        pt_files = [f for f in pt_files if f.name not in ['cities.json', 'major_cities.json']]
        
        pt_success = 0
        for city_file in pt_files:
            if normalize_city_file(city_file):
                pt_success += 1
        
        print(f"\nNormalized {pt_success}/{len(pt_files)} Portuguese city files")
    
    print("\nNormalization complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())

