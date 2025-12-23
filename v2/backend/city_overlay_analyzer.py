#!/usr/bin/env python3
"""
City Overlay Analyzer for The Dying Lands
Processes city overlay images and generates round hex grids with random content.
Supports matrix-based district placement from city JSON files.
"""

import os
import random
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .lore_database import LoreDatabase
from .database_manager import database_manager
from .utils.city_helpers import create_fallback_district_data

class CityOverlayAnalyzer:
    """Generates round hex grids for city overlays using matrix-based district placement and random content generation."""
    
    def __init__(self, language='en', output_directory=None):
        self.lore_db = LoreDatabase()
        # Use provided output_directory, or honor HEXY_OUTPUT_DIR, or fallback to default
        if output_directory:
            self.output_directory = Path(output_directory) / 'city_overlays'
        else:
            base_root = os.getenv('HEXY_OUTPUT_DIR')
            if base_root:
                self.output_directory = Path(base_root) / 'city_overlays'
            else:
                # Fallback to default location (~/.local/share/hexy/dying_lands_output)
                from .config import _default_output_dir
                default_out = _default_output_dir()
                self.output_directory = default_out / 'city_overlays'
        self.output_directory = Path(self.output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.language = language
        self.content_tables = database_manager.load_tables(language)
        self.overlays_cache = {}
        self.overlay_fallbacks = self._load_overlay_fallbacks()

    def _load_overlay_fallbacks(self) -> Dict[str, Any]:
        """Load fallback overlay content from database tables."""
        data = database_manager.get_table("city_overlays", "fallbacks", self.language)
        if isinstance(data, dict):
            # Merge in shared descriptions tables if present
            data = dict(data)
            data["district_descriptions"] = data.get("district_descriptions", database_manager.get_table("descriptions", "district_descriptions", self.language) or [])
            data["market_specialties"] = data.get("market_specialties", database_manager.get_table("descriptions", "market_specialties", self.language) or [])
            data["temple_deities"] = data.get("temple_deities", database_manager.get_table("descriptions", "temple_deities", self.language) or [])
            data["tavern_descriptions"] = data.get("tavern_descriptions", database_manager.get_table("descriptions", "tavern_descriptions", self.language) or [])
            data["guild_purposes"] = data.get("guild_purposes", database_manager.get_table("descriptions", "guild_purposes", self.language) or [])
            data["residence_inhabitants"] = data.get("residence_inhabitants", database_manager.get_table("descriptions", "residence_inhabitants", self.language) or [])
            return data
        if isinstance(data, list) and data and isinstance(data[0], dict):
            merged = dict(data[0])
            merged["district_descriptions"] = merged.get("district_descriptions", database_manager.get_table("descriptions", "district_descriptions", self.language) or [])
            merged["market_specialties"] = merged.get("market_specialties", database_manager.get_table("descriptions", "market_specialties", self.language) or [])
            merged["temple_deities"] = merged.get("temple_deities", database_manager.get_table("descriptions", "temple_deities", self.language) or [])
            merged["tavern_descriptions"] = merged.get("tavern_descriptions", database_manager.get_table("descriptions", "tavern_descriptions", self.language) or [])
            merged["guild_purposes"] = merged.get("guild_purposes", database_manager.get_table("descriptions", "guild_purposes", self.language) or [])
            merged["residence_inhabitants"] = merged.get("residence_inhabitants", database_manager.get_table("descriptions", "residence_inhabitants", self.language) or [])
            return merged
        return {}

    def invalidate_cache(self) -> None:
        """Clear in-memory overlays cache after a reset."""
        try:
            self.overlays_cache.clear()
        except Exception:
            self.overlays_cache = {}

    def get_available_overlays(self) -> List[Dict[str, Any]]:
        """Get list of available city overlays by name only (no image files)."""
        overlays = []
        # Example: populate overlays from lore_db major cities
        for city_key, city_data in self.lore_db.major_cities.items():
            overlays.append({
                'name': city_key,
                'display_name': city_data['name'],
                'filename': None,
                'path': None
            })
        return overlays
    
    def _format_overlay_name(self, name: str) -> str:
        """Format overlay name for display using Mork Borg database."""
        # Map image1 to galgenbeck as requested
        if name.lower() == 'image1':
            name = 'galgenbeck'
        
        # Try to find city in Mork Borg database
        city_key = name.lower()
        if city_key in self.lore_db.major_cities:
            city_data = self.lore_db.major_cities[city_key]
            return city_data['name']
        
        # Try to load city-specific database
        city_db_path = f'databases/cities/en/{city_key}.json'
        if os.path.exists(city_db_path):
            try:
                with open(city_db_path, 'r', encoding='utf-8') as f:
                    city_data = json.load(f)
                    return city_data.get('display_name', city_data.get('city_name', name.title()))
            except Exception:
                pass
        
        # Fallback to formatted name
        return name.replace('_', ' ').title()
    
    def generate_city_overlay(self, overlay_name: str) -> Dict[str, Any]:
        """Generate a round hex grid overlay for a city image."""
        try:
            overlays = self.get_available_overlays()
        
            overlay_info = next((o for o in overlays if o['name'] == overlay_name), None)
        
            if not overlay_info:
                # Try case-insensitive match
                overlay_info = next((o for o in overlays if o['name'].lower() == overlay_name.lower()), None)
        
            if not overlay_info:
                raise ValueError(f"City overlay '{overlay_name}' not found")
        
            # Load city data
            city_data = self._load_city_database(overlay_name.lower())
        
            # Generate round hex grid
            hex_grid = self._generate_round_hex_grid(overlay_name, city_data)
        
            # Add cross-references between related hexes
            hex_grid = self._add_cross_references(hex_grid, city_data)
        
            # Calculate grid radius
            radius = self._calculate_grid_radius(hex_grid)
        
            # Create overlay data structure
            overlay_data = {
                'name': overlay_name,
                'display_name': self._format_overlay_name(overlay_name),
                'filename': None,
                'grid_type': 'round',
                'radius': radius,
                'hex_grid': hex_grid,
                'total_hexes': len(hex_grid)
            }
        
            # Save overlay data
            self._save_overlay_data(overlay_name, overlay_data)
        
            return overlay_data
            
        except Exception as e:
            import traceback
            error_msg = f"Error during loading city overlay: {str(e)}\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)  # Log the full error
            raise ValueError(error_msg)
    
    def _generate_round_hex_grid(self, overlay_name: str, city_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a round hex grid for city overlay."""
        try:
            hex_grid = {}
        
            # Get district matrix if available
            district_matrix = self._get_district_matrix(city_data)
        
            if district_matrix:
                # Use district matrix for content generation
                hex_grid = self._apply_district_matrix(district_matrix, overlay_name, city_data)
            else:
                # Generate default round grid
                hex_grid = self._generate_default_round_grid(overlay_name, city_data)
        
            return hex_grid
            
        except Exception as e:
            import traceback
            error_msg = f"Error in _generate_round_hex_grid for {overlay_name}: {str(e)}\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)  # Log the full error
            raise ValueError(error_msg)
    
    def _get_district_matrix(self, city_data: Optional[Dict[str, Any]]) -> Optional[List[List[str]]]:
        """Get the district matrix from city data if it exists."""
        if city_data and 'district_matrix' in city_data:
            return city_data['district_matrix']
        return None
    
    def _apply_district_matrix(self, matrix: List[List[str]], overlay_name: str, city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply a predefined district matrix to generate hex content."""
        hex_grid = {}
        
        # Fill the entire matrix with hexes (visible or invisible)
        for row_idx, row in enumerate(matrix):
            for col_idx, district_name in enumerate(row):
                hex_id = f"{row_idx}_{col_idx}"
                hex_position = f"Row {row_idx+1}, Col {col_idx+1}"
                
                if district_name and district_name.strip():  # Has content
                    
                    
                    # Generate content based on the specified district
                    hex_content = self._generate_district_based_content(
                        district_name, row_idx, col_idx, overlay_name, city_data
                    )
                    
                    hex_grid[hex_id] = {
                        'id': hex_id,
                        'row': row_idx,
                        'col': col_idx,
                        'position': hex_position,
                        'district': district_name,
                        'content': hex_content
                    }
                    
                    
                else:  # Empty cell - create invisible hex for proper formatting
                    hex_grid[hex_id] = {
                        'id': hex_id,
                        'row': row_idx,
                        'col': col_idx,
                        'position': hex_position,
                        'district': 'empty',
                        'content': {
                            'name': 'Empty',
                            'type': 'empty',
                            'description': 'Empty space',
                            'encounter': 'Nothing here',
                            'atmosphere': 'Silent emptiness'
                        }
                    }
        
        
        return hex_grid
    
    def _generate_default_round_grid(self, overlay_name: str, city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a default round hex grid when no matrix is provided."""
        hex_grid = {}
        
        # Create a small round grid (radius 3) to limit size and generation time
        radius = 3
        center_row = center_col = radius
        
        for row in range(radius * 2 + 1):
            for col in range(radius * 2 + 1):
                distance = self._hex_distance(center_row, center_col, row, col)
                if distance > radius:
                    continue
                hex_id = f"{row}_{col}"
                hex_position = f"Row {row+1}, Col {col+1}"
                
                hex_content = self._generate_position_based_content(
                        row, col, distance, radius, overlay_name, city_data
                    )
                
                hex_grid[hex_id] = {
                    'id': hex_id,
                    'row': row,
                    'col': col,
                    'position': hex_position,
                    'distance_from_center': distance,
                    'content': hex_content
                }
        
        return hex_grid
    
    def _hex_distance(self, row1: int, col1: int, row2: int, col2: int) -> int:
        """Calculate hex distance between two positions."""
        # Convert to cube coordinates for proper hex distance calculation
        q1 = col1
        r1 = row1 - (col1 - (col1 & 1)) // 2
        s1 = -q1 - r1
        
        q2 = col2
        r2 = row2 - (col2 - (col2 & 1)) // 2
        s2 = -q2 - r2
        
        return (abs(q1 - q2) + abs(r1 - r2) + abs(s1 - s2)) // 2
    
    def _generate_district_based_content(self, district_name: str, row: int, col: int, overlay_name: str, city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate content based on a specific district."""
        # Find the district data
        district_data = self._find_district_data(district_name, city_data)
        
        if district_data:
            # Generate content specific to this district
            content_type = self._select_district_content_type(district_data, city_data)
            content = self._generate_content_by_type(content_type, row, col, overlay_name, city_data, district_data)
            
            # Add fallback if content is None
            if content is None:
                content = create_fallback_district_data(
                    city_data,
                    self._get_city_content_list,
                    self._get_city_encounters,
                    self._get_city_atmospheres,
                    self._get_city_random_table,
                    self._generate_district_random_table,
                    fallback_content=self.overlay_fallbacks
                )
            
            # Integrate city-specific content
            content = self._integrate_city_specific_content(content, city_data)
            
            return content
        else:
            # Use centralized fallback district data
            return create_fallback_district_data(
                city_data,
                self._get_city_content_list,
                self._get_city_encounters,
                self._get_city_atmospheres,
                self._get_city_random_table,
                self._generate_district_random_table,
                fallback_content=self.overlay_fallbacks
            )
    
    def _find_district_data(self, district_name: str, city_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find district data by name in city data."""
        if not city_data or 'districts' not in city_data:
            
            return None
        
        
        available_districts = [d.get('name', 'Unknown') for d in city_data['districts']]
        
        
        for district in city_data['districts']:
            if district.get('name', '').lower() == district_name.lower():
                
                return district
        
        
        return None
    
    def _select_district_content_type(self, district_data: Dict[str, Any], city_data: Optional[Dict[str, Any]] = None) -> str:
        """Select content type based on district data and city data."""
        # Weight content types based on what's available in the district
        content_weights = {}
        
        if 'buildings' in district_data and district_data['buildings']:
            content_weights['building'] = 0.25
        if 'streets' in district_data and district_data['streets']:
            content_weights['street'] = 0.15
        if 'landmarks' in district_data and district_data['landmarks']:
            content_weights['landmark'] = 0.15
        if 'markets' in district_data and district_data['markets']:
            content_weights['market'] = 0.15
        if 'temples' in district_data and district_data['temples']:
            content_weights['temple'] = 0.15
        if 'taverns' in district_data and district_data['taverns']:
            content_weights['tavern'] = 0.1
        if 'guilds' in district_data and district_data['guilds']:
            content_weights['guild'] = 0.05
        
        # Also check city-level content if available
        if city_data:
            if 'markets' in city_data and city_data['markets'] and 'market' not in content_weights:
                content_weights['market'] = 0.15
            if 'temples' in city_data and city_data['temples'] and 'temple' not in content_weights:
                content_weights['temple'] = 0.15
            if 'taverns' in city_data and city_data['taverns'] and 'tavern' not in content_weights:
                content_weights['tavern'] = 0.1
            if 'guilds' in city_data and city_data['guilds'] and 'guild' not in content_weights:
                content_weights['guild'] = 0.05
        
        # If no specific content types, default to district
        if not content_weights:
            content_weights['district'] = 1.0
        
        return self._weighted_choice(content_weights)
    
    def _generate_position_based_content(self, row: int, col: int, distance: int, radius: int, overlay_name: str, city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate content based on position in the grid."""
        # Different content types based on distance from center for 10x10 grid
        if distance == 0:  # Center (5,5)
            content_weights = {
                'landmark': 0.4,
                'temple': 0.3,
                'market': 0.3
            }
        elif distance <= 2:  # Inner rings (distance 1-2)
            content_weights = {
                'building': 0.25,
                'market': 0.2,
                'temple': 0.2,
                'guild': 0.2,
                'tavern': 0.15
            }
        elif distance <= 4:  # Middle rings (distance 3-4)
            content_weights = {
                'building': 0.3,
                'tavern': 0.25,
                'residence': 0.2,
                'street': 0.15,
                'guild': 0.1
            }
        elif distance <= 6:  # Outer rings (distance 5-6)
            content_weights = {
                'district': 0.3,
                'building': 0.25,
                'street': 0.2,
                'residence': 0.15,
                'ruins': 0.1
            }
        else:  # Edge rings (distance 7+)
            content_weights = {
                'district': 0.4,
                'street': 0.25,
                'residence': 0.2,
                'ruins': 0.15
            }
        
        # Select content type
        content_type = self._weighted_choice(content_weights)
        
        # Generate content based on type
        content = self._generate_content_by_type(content_type, row, col, overlay_name, city_data)
        
        # Integrate city-specific content
        content = self._integrate_city_specific_content(content, city_data)
        
        return content
    
    def _calculate_grid_radius(self, hex_grid: Dict[str, Any]) -> int:
        """Calculate the radius of the hex grid."""
        if not hex_grid:
            return 0
        
        max_distance = 0
        center_row, center_col = 5, 5  # Center point for 10x10 grid (changed from 3,3)
        
        for hex_data in hex_grid.values():
            row = hex_data.get('row', 0)
            col = hex_data.get('col', 0)
            distance = self._hex_distance(center_row, center_col, row, col)
            max_distance = max(max_distance, distance)
        
        return max_distance
    
    def _generate_content_by_type(self, content_type: str, row: int, col: int, overlay_name: str, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate content based on type with detailed error reporting."""
        try:
            if content_type == 'district':
                    return self._generate_district_content(city_data, district_data)
            elif content_type == 'building':
                    return self._generate_building_content(city_data, district_data)
            elif content_type == 'street':
                    return self._generate_street_content(city_data, district_data)
            elif content_type == 'landmark':
                    return self._generate_landmark_content(city_data, district_data)
            elif content_type == 'market':
                    return self._generate_market_content(city_data, district_data)
            elif content_type == 'temple':
                    return self._generate_temple_content(city_data, district_data)
            elif content_type == 'tavern':
                    return self._generate_tavern_content(city_data, district_data)
            elif content_type == 'guild':
                    return self._generate_guild_content(city_data, district_data)
            elif content_type == 'residence':
                    return self._generate_residence_content(city_data, district_data)
            elif content_type == 'ruins':
                    return self._generate_ruins_content(city_data, district_data)
            else:
                # Default to district content
                return self._generate_district_content(city_data, district_data)
                
        except Exception as e:
            import traceback
            error_msg = f"Error in _generate_content_by_type for type '{content_type}' at position ({row}, {col}): {str(e)}\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)  # Log the full error
            raise ValueError(error_msg)
    
    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Choose an item based on weighted probabilities."""
        if not weights:
            raise ValueError("Cannot choose from empty weights dictionary")
        
        items = list(weights.keys())
        weights_list = list(weights.values())
        
        # Additional safety check for empty items list
        if not items:
            raise ValueError("Cannot choose from empty items list")
            
        return random.choices(items, weights=weights_list)[0]
    
    def _safe_random_choice(self, items: List[str], context: str = "unknown") -> str:
        """Safely choose a random item from a list, with fallback for empty lists."""
        if not items:
            return "Unknown"
        return random.choice(items)
    
    def _load_city_database(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Load city-specific database if available."""
        city_db_path = f'databases/cities/{self.language}/{city_name}.json'
        
        print(f"DEBUG: Loading city database from: {city_db_path}")
        print(f"DEBUG: File exists: {os.path.exists(city_db_path)}")
        
        if os.path.exists(city_db_path):
            try:
                with open(city_db_path, 'r', encoding='utf-8') as f:
                    city_data = json.load(f)
                    
                print(f"DEBUG: City data keys: {list(city_data.keys())}")
                
                # Load additional city-specific content from language database
                enriched_content = self._load_city_specific_content(city_name)
                print(f"DEBUG: Enriched content keys: {list(enriched_content.keys())}")
                
                city_data.update(enriched_content)
                print(f"DEBUG: Final city data keys: {list(city_data.keys())}")
                
                return city_data
            except Exception as e:
                print(f"Warning: Could not load city database for {city_name}: {e}")
        else:
            print(f"DEBUG: City database file not found: {city_db_path}")
        return None
    
    def _load_city_specific_content(self, city_name: str) -> Dict[str, Any]:
        """Load city-specific content from language database files."""
        content = {}
        
        # Load city events
        try:
            events_path = f'databases/city_events/{self.language}/city_events.json'
            if os.path.exists(events_path):
                with open(events_path, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                    # Extract data from tables structure
                    if 'tables' in events_data and 'city_events' in events_data['tables']:
                        city_events_data = events_data['tables']['city_events']
                        # Use all city events (no filtering for now)
                        content['city_events'] = city_events_data
        except Exception as e:
            print(f"Warning: Could not load city events: {e}")
        
        # Load weather conditions
        try:
            weather_path = f'databases/weather/{self.language}/weather.json'
            if os.path.exists(weather_path):
                with open(weather_path, 'r', encoding='utf-8') as f:
                    weather_data = json.load(f)
                    # Extract data from tables structure
                    if 'tables' in weather_data and 'weather_conditions' in weather_data['tables']:
                        content['weather_conditions'] = weather_data['tables']['weather_conditions']
                    else:
                        content['weather_conditions'] = weather_data
        except Exception as e:
            print(f"Warning: Could not load weather data: {e}")
        
        # Load NPC traits, concerns, wants, secrets
        for npc_type in ['npc_traits', 'npc_concerns', 'npc_wants', 'npc_secrets']:
            try:
                npc_path = f'databases/{npc_type}/{self.language}/{npc_type}.json'
                if os.path.exists(npc_path):
                    with open(npc_path, 'r', encoding='utf-8') as f:
                        npc_data = json.load(f)
                        # Extract data from tables structure
                        if 'tables' in npc_data and 'traits' in npc_data['tables']:
                            content[npc_type] = npc_data['tables']['traits']
                        elif 'tables' in npc_data and 'concerns' in npc_data['tables']:
                            content[npc_type] = npc_data['tables']['concerns']
                        elif 'tables' in npc_data and 'wants' in npc_data['tables']:
                            content[npc_type] = npc_data['tables']['wants']
                        elif 'tables' in npc_data and 'secrets' in npc_data['tables']:
                            content[npc_type] = npc_data['tables']['secrets']
                        else:
                            content[npc_type] = npc_data
            except Exception as e:
                print(f"Warning: Could not load {npc_type}: {e}")
        
        # Load tavern content
        for tavern_type in ['tavern_menu', 'tavern_innkeeper', 'tavern_patrons']:
            try:
                tavern_path = f'databases/{tavern_type}/{self.language}/{tavern_type}.json'
                if os.path.exists(tavern_path):
                    with open(tavern_path, 'r', encoding='utf-8') as f:
                        tavern_data = json.load(f)
                        # Extract data from tables structure
                        if tavern_type == 'tavern_menu' and 'tables' in tavern_data:
                            # For menu, combine select and budget menus
                            menu_items = []
                            if 'select_menu' in tavern_data['tables']:
                                menu_items.extend([item['name'] for item in tavern_data['tables']['select_menu']])
                            if 'budget_menu' in tavern_data['tables']:
                                menu_items.extend([item['name'] for item in tavern_data['tables']['budget_menu']])
                            content[tavern_type] = menu_items
                        elif tavern_type == 'tavern_innkeeper' and 'tables' in tavern_data and 'innkeeper_quirks' in tavern_data['tables']:
                            content[tavern_type] = tavern_data['tables']['innkeeper_quirks']
                        elif tavern_type == 'tavern_patrons' and 'tables' in tavern_data and 'patron_traits' in tavern_data['tables']:
                            content['tavern_patrons'] = tavern_data['tables']['patron_traits']
                        else:
                            content[tavern_type] = tavern_data
            except Exception as e:
                print(f"Warning: Could not load {tavern_type}: {e}")
        
        # Load market content (items, beasts, services)
        for market_type in ['items_prices', 'beasts_prices', 'services_prices']:
            try:
                market_path = f'databases/{market_type}/{self.language}/{market_type}.json'
                if os.path.exists(market_path):
                    with open(market_path, 'r', encoding='utf-8') as f:
                        market_data = json.load(f)
                        # Extract data from tables structure
                        if 'tables' in market_data:
                            # Use detailed entries (objects) so the UI can render name/price/currency/notes
                            if market_type == 'items_prices':
                                if 'items' in market_data['tables'] and isinstance(market_data['tables']['items'], list):
                                    content['items_sold'] = market_data['tables']['items']
                            elif self.language != 'en':
                                    # Fallback to English detailed items if local language lacks them
                                    try:
                                        fallback_path = f'databases/items_prices/en/items_prices.json'
                                        if os.path.exists(fallback_path):
                                            with open(fallback_path, 'r', encoding='utf-8') as ef:
                                                en_data = json.load(ef)
                                                if 'tables' in en_data and 'items' in en_data['tables']:
                                                    content['items_sold'] = en_data['tables']['items']
                                    except Exception:
                                        pass
                            elif market_type == 'beasts_prices':
                                if 'beasts' in market_data['tables'] and isinstance(market_data['tables']['beasts'], list):
                                    content['beast_prices'] = market_data['tables']['beasts']
                                elif self.language != 'en':
                                    # Fallback to English detailed beasts if local language lacks them
                                    try:
                                        fallback_path = f'databases/beasts_prices/en/beasts_prices.json'
                                        if os.path.exists(fallback_path):
                                            with open(fallback_path, 'r', encoding='utf-8') as ef:
                                                en_data = json.load(ef)
                                                if 'tables' in en_data and 'beasts' in en_data['tables']:
                                                    content['beast_prices'] = en_data['tables']['beasts']
                                    except Exception:
                                        pass
                            elif market_type == 'services_prices' and 'services' in market_data['tables']:
                                content['services'] = market_data['tables']['services']
                        else:
                            content[market_type] = market_data
            except Exception as e:
                print(f"Warning: Could not load {market_type}: {e}")
        
        # Load populations
        try:
            basic_path = f'databases/basic/{self.language}/basic.json'
            if os.path.exists(basic_path):
                with open(basic_path, 'r', encoding='utf-8') as f:
                    basic_data = json.load(f)
                    # Extract data from tables structure
                    if 'tables' in basic_data and 'populations' in basic_data['tables']:
                        content['populations'] = basic_data['tables']['populations']
        except Exception as e:
            print(f"Warning: Could not load populations: {e}")
        
        # Load NPC content (names, trades, affiliations)
        for npc_content_type in ['npc_names', 'npc_trades', 'affiliation']:
            try:
                npc_content_path = f'databases/{npc_content_type}/{self.language}/{npc_content_type}.json'
                print(f"DEBUG: Loading {npc_content_type} from: {npc_content_path}")
                print(f"DEBUG: File exists: {os.path.exists(npc_content_path)}")
                
                if os.path.exists(npc_content_path):
                    with open(npc_content_path, 'r', encoding='utf-8') as f:
                        npc_content_data = json.load(f)
                        # Extract data from tables structure
                        if 'tables' in npc_content_data:
                            if npc_content_type == 'npc_names' and 'first_names' in npc_content_data['tables']:
                                # Store the entire npc_names structure for tavern NPCs
                                content['npc_names'] = npc_content_data['tables']
                                print(f"DEBUG: Loaded npc_names with keys: {list(content['npc_names'].keys())}")
                            elif npc_content_type == 'npc_trades' and 'trades' in npc_content_data['tables']:
                                content['npc_trades'] = npc_content_data['tables']['trades']
                            elif npc_content_type == 'affiliation' and 'affiliations' in npc_content_data['tables']:
                                content['affiliations'] = npc_content_data['tables']['affiliations']
                        else:
                            content[npc_content_type] = npc_content_data
            except Exception as e:
                print(f"Warning: Could not load {npc_content_type}: {e}")
        
        # Load factions content
        try:
            factions_path = f'databases/factions/{self.language}/factions.json'
            if os.path.exists(factions_path):
                with open(factions_path, 'r', encoding='utf-8') as f:
                    factions_data = json.load(f)
                    # Extract data from tables structure
                    if 'tables' in factions_data:
                        content['factions'] = factions_data['tables']
                    else:
                        content['factions'] = factions_data
        except Exception as e:
            print(f"Warning: Could not load factions: {e}")
        
        # Load features content (buildings, landmarks, guilds, etc.)
        try:
            features_path = f'databases/features/{self.language}/features.json'
            if os.path.exists(features_path):
                with open(features_path, 'r', encoding='utf-8') as f:
                    features_data = json.load(f)
                    # Extract data from tables structure
                    if 'tables' in features_data:
                        content['features'] = features_data['tables']
                    else:
                        content['features'] = features_data
        except Exception as e:
            print(f"Warning: Could not load features: {e}")
        
        return content
    
    def get_city_context(self, city_name: str) -> Dict[str, Any]:
        """Get city context information for the left panel."""
        city_data = self._load_city_database(city_name)
        if not city_data:
            return {}
        
        # Load city-specific content
        enriched_content = self._load_city_specific_content(city_name)
        
        # Get city name and description from major cities data (with Portuguese support)
        city_name_final = city_name
        city_description = city_data.get('description', '')
        city_atmosphere = city_data.get('atmosphere', '')
        city_notable_features = city_data.get('notable_features', [])
        
        # Check if this is a major city and get data from database manager
        if city_name.lower() in self.lore_db.major_cities:
            # Load city data from database manager with current language
            from .database_manager import database_manager
            cities_table = database_manager.get_table('cities', 'major_cities', self.language)
            
            # Find the city data in the table
            major_city_data = {}
            for city in cities_table:
                if isinstance(city, dict) and city.get('key') == city_name.lower():
                    major_city_data = city
                    break
            
            if major_city_data:
                city_name_final = major_city_data.get('name', city_name)
                city_description = major_city_data.get('description', '')
                city_atmosphere = major_city_data.get('atmosphere', '')
                city_notable_features = major_city_data.get('notable_features', [])
        
        # Build city context
        context = {
            'name': city_name_final,
            'description': city_description,
            'atmosphere': city_atmosphere,
            'notable_features': city_notable_features,
            'districts': {},
            'major_landmarks': city_data.get('landmarks', []),
            'city_events': enriched_content.get('city_events', []),
            'weather_conditions': enriched_content.get('weather_conditions', []),
            'regional_npcs': city_data.get('regional_npcs', []),
            'factions': [],
            'atmosphere_modifiers': city_data.get('atmosphere_modifiers', [])
        }
        
        # Extract faction information from enriched content
        if 'factions' in enriched_content and isinstance(enriched_content['factions'], dict):
            factions_data = enriched_content['factions']
            
            # Select major factions for the city
            major_factions = factions_data.get('major_factions', [])
            if major_factions:
                num_major = random.randint(2, 4)
                selected_major = random.sample(major_factions, min(num_major, len(major_factions)))
                context['major_factions'] = selected_major
            
            # Select local factions for the city
            local_factions = factions_data.get('local_factions', [])
            if local_factions:
                num_local = random.randint(3, 6)
                selected_local = random.sample(local_factions, min(num_local, len(local_factions)))
                context['local_factions'] = selected_local
            
            # Select criminal factions for the city
            criminal_factions = factions_data.get('criminal_factions', [])
            if criminal_factions:
                num_criminal = random.randint(2, 4)
                selected_criminal = random.sample(criminal_factions, min(num_criminal, len(criminal_factions)))
                context['criminal_factions'] = selected_criminal
            
            # Get faction relationships
            faction_relationships = factions_data.get('faction_relationships', [])
            if faction_relationships:
                context['faction_relationships'] = faction_relationships[:5]  # Limit to 5 relationships
        
        # Legacy support - if no proper factions loaded, fall back to affiliations
        if not context.get('major_factions') and 'affiliations' in enriched_content:
            affiliations = enriched_content['affiliations']
            if 'faction_affiliations' in affiliations and isinstance(affiliations['faction_affiliations'], list):
                num_factions = random.randint(3, 6)
                selected_factions = random.sample(affiliations['faction_affiliations'], 
                                                min(num_factions, len(affiliations['faction_affiliations'])))
                
                faction_attitudes = affiliations.get('affiliation_attitudes', [])
                context['legacy_factions'] = []
                for faction in selected_factions:
                    faction_info = {
                        'name': faction,
                        'attitude': random.choice(faction_attitudes) if faction_attitudes else 'Unknown'
                    }
                    context['legacy_factions'].append(faction_info)
        
        # Add district information
        districts = city_data.get('districts', {})
        if isinstance(districts, dict):
            for district_name, district_data in districts.items():
                context['districts'][district_name] = {
                    'description': district_data.get('description', ''),
                    'buildings': district_data.get('buildings', []),
                    'streets': district_data.get('streets', []),
                    'landmarks': district_data.get('landmarks', []),
                    'markets': district_data.get('markets', []),
                    'temples': district_data.get('temples', []),
                    'taverns': district_data.get('taverns', []),
                    'guilds': district_data.get('guilds', [])
                }
        
        return context
    

    
    def _get_city_content_list(self, city_data: Optional[Dict[str, Any]], content_type: str, fallback: List[str]) -> List[str]:
        """Get city-specific content list or fallback to generic."""
        if city_data and content_type in city_data:
            return city_data[content_type]
        return fallback
    
    def _get_city_encounters(self, city_data: Optional[Dict[str, Any]], content_type: str, fallback: List[str]) -> List[str]:
        """Get city-specific encounters or fallback to generic."""
        if city_data and 'encounters' in city_data and content_type in city_data['encounters']:
            return city_data['encounters'][content_type]
        return fallback
    
    def _get_city_random_table(self, city_data: Optional[Dict[str, Any]], content_type: str, fallback_method) -> List[str]:
        """Get city-specific random table or fallback to generic."""
        if city_data and 'random_tables' in city_data and content_type in city_data['random_tables']:
            return city_data['random_tables'][content_type]
        return fallback_method()
    
    def _get_city_atmospheres(self, city_data: Optional[Dict[str, Any]], fallback: List[str]) -> List[str]:
        """Get city-specific atmosphere modifiers or fallback to generic."""
        if city_data and 'atmosphere_modifiers' in city_data:
            return city_data['atmosphere_modifiers']
        return fallback
    
    def _generate_district_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate district content."""
        if not district_data:
            district_data = {}

            name = district_data.get('name', 'Unknown District')

        # Compute description with safe fallback, regardless of errors
        try:
            district_descriptions = database_manager.get_table('descriptions', 'district_descriptions', self.language)
            if district_descriptions:
                description = random.choice(district_descriptions)
            else:
                description = district_data.get(
                    'description',
                    f"A district where {random.choice(['the wealthy once lived', 'merchants once thrived', 'scholars once studied', 'the poor struggle to survive'])}."
                )
        except Exception:
            description = district_data.get(
                'description',
                f"A district where {random.choice(['the wealthy once lived', 'merchants once thrived', 'scholars once studied', 'the poor struggle to survive'])}."
            )
            
        # Encounters
        encounters = district_data.get('encounters', [])
        encounter = random.choice(encounters) if encounters else "Unclear activity in the district"
            
        # Atmosphere
        atmospheres = district_data.get('atmosphere_modifiers', [])
        atmosphere = random.choice(atmospheres) if atmospheres else "Dark and foreboding"
            
        # Random table
        random_tables = district_data.get('random_tables', {})
        random_table = random_tables.get('district', self._generate_district_random_table())
            
        # Notable features
        notable_features: List[str] = []
        for content_type in ['buildings', 'streets', 'landmarks']:
            entries = district_data.get(content_type, [])
            if entries:
                notable_features.append(random.choice(entries))
            if not notable_features:
                notable_features = [
                    random.choice(["Crumbling mansions", "Narrow alleyways", "Ancient statues", "Broken fountains"]),
                    random.choice(["Abandoned shops", "Boarded windows", "Graffiti-covered walls", "Overgrown gardens"])
                ]
            
        return {
            'name': name,
            'description': description,
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'notable_features': notable_features
        }
    
    def _generate_building_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate building content."""
        # Get buildings from district data first, then city data, then fallback
        buildings = []
        if district_data and 'buildings' in district_data:
            buildings = district_data['buildings']
        elif city_data and 'buildings' in city_data:
            buildings = city_data['buildings']
        
        if not buildings:
            buildings = self._get_enhanced_fallback_content('buildings')
        
        # Get building features from city data
        purposes = []
        if city_data and 'features' in city_data:
            building_features = city_data['features'].get('building_features', [])
            if building_features:
                purposes = building_features
        else:
            # Fallback purposes
            purposes = [
                "residência abandonada de um nobre caído",
                "oficina misteriosa de propósito desconhecido",
                "biblioteca esquecida com conhecimento proibido",
                "templo antigo para um deus esquecido",
                "sede de guilda para organização secreta",
                "armazém cheio de artefatos estranhos"
            ]
        
        name = random.choice(buildings)
        purpose = random.choice(purposes)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'building', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                building_encounters = database_manager.get_table('encounters', 'building_encounters', self.language)
                if building_encounters:
                    encounter = random.choice(building_encounters)
                else:
                    raise ValueError("No building encounters available in database")
            except Exception:
                raise ValueError("No building encounters available in database")
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        
        # Get random table from district data if available
        random_table = []
        if district_data and 'random_tables' in district_data and 'building' in district_data['random_tables']:
            random_table = district_data['random_tables']['building']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'building', self._generate_building_random_table)
        else:
            random_table = self._generate_building_random_table()
        
        return {
            'name': name,
            'type': 'building',
            'description': f"Uma estrutura imponente que uma vez serviu como {purpose}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'treasures': [self._safe_random_choice(database_manager.get_table('loot', 'building_treasures', self.language) or [], "building_treasures")]
        }
    
    def _generate_street_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate street content."""
        # Get streets from district data first, then city data, then fallback
        streets = []
        if district_data and 'streets' in district_data:
            streets = district_data['streets']
        elif city_data and 'streets' in city_data:
            streets = city_data['streets']
        
        if not streets:
            streets = self._get_enhanced_fallback_content('streets')
        
        name = random.choice(streets)
        condition = self._safe_random_choice(database_manager.get_table('features', 'street_features', self.language) or [], "street_features")
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'street', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                street_encounters = database_manager.get_table('encounters', 'street_encounters', self.language)
                if street_encounters:
                    encounter = random.choice(street_encounters)
                else:
                    raise ValueError("No street encounters available in database")
            except Exception:
                raise ValueError("No street encounters available in database")
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        
        # Get random table from district data if available
        random_table = []
        if district_data and 'random_tables' in district_data and 'street' in district_data['random_tables']:
            random_table = district_data['random_tables']['street']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'street', self._generate_street_random_table)
        else:
            random_table = self._generate_street_random_table()
        
        return {
            'name': name,
            'type': 'street',
            'description': f"Uma via sinuosa com {condition}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'threats': [self._safe_random_choice(database_manager.get_table('encounters', 'street_threats', self.language) or [], "street_threats")]
        }
    
    def _generate_landmark_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate landmark content."""
        # Get landmarks from district data first, then city data, then fallback
        landmarks = []
        if district_data and 'landmarks' in district_data:
            landmarks = district_data['landmarks']
        elif city_data and 'landmarks' in city_data:
            landmarks = city_data['landmarks']
        
        name = random.choice(landmarks)
        
        # Get landmark features from city data
        significance = ""
        if city_data and 'features' in city_data:
            landmark_features = city_data['features'].get('landmark_features', [])
            if landmark_features:
                significance = random.choice(landmark_features)
            else:
                significance = self._safe_random_choice(database_manager.get_table('features', 'landmark_features', self.language) or [], "landmark_features")
        else:
            significance = self._safe_random_choice(database_manager.get_table('features', 'landmark_features', self.language) or [], "landmark_features")
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'landmark', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                landmark_encounters = database_manager.get_table('encounters', 'landmark_encounters', self.language)
                if landmark_encounters:
                    encounter = random.choice(landmark_encounters)
                else:
                    raise ValueError("No landmark encounters available in database")
            except Exception:
                raise ValueError("No landmark encounters available in database")
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        
        # Get random table from district data if available
        random_table = []
        if district_data and 'random_tables' in district_data and 'landmark' in district_data['random_tables']:
            random_table = district_data['random_tables']['landmark']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'landmark', self._generate_landmark_random_table)
        else:
            random_table = self._generate_landmark_random_table()
        
        return {
            'name': name,
            'type': 'landmark',
            'description': f"An imposing monument that {significance}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'notable_features': [
                self._safe_random_choice(city_data.get('features', {}).get('landmark_features', []) if city_data and 'features' in city_data else database_manager.get_table('features', 'landmark_features', self.language) or ["Strange inscriptions", "Supernatural phenomena", "Ritual markings", "Offerings from visitors"], "landmark_features"),
                self._safe_random_choice(city_data.get('features', {}).get('landmark_features', []) if city_data and 'features' in city_data else database_manager.get_table('features', 'landmark_features', self.language) or ["Guardian spirits", "Temporal anomalies", "Prophetic visions", "Cursed ground"], "landmark_features")
            ]
        }
    
    def _generate_market_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate market content."""
        # Get markets from district data first, then city data, then fallback
        markets = []
        if district_data and 'markets' in district_data:
            markets = district_data['markets']
        elif city_data and 'markets' in city_data:
            markets = city_data['markets']
        
        if not markets:
            # Try to get markets from database
                markets = database_manager.get_table('names', 'market_names', self.language)
                if not markets:
                    raise ValueError("No market names available in database")
        
        # Get market features from city data
        specialties = []
        if city_data and 'features' in city_data:
            market_features = city_data['features'].get('market_features', [])
            if market_features:
                specialties = market_features
        
        if not specialties:
        # Try to get specialties from database
            specialties = database_manager.get_table('descriptions', 'market_specialties', self.language)
            if not specialties:
                raise ValueError("No market specialties available in database")
        
        name = random.choice(markets)
        specialty = random.choice(specialties)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'market', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                market_encounters = database_manager.get_table('encounters', 'market_encounters', self.language)
                if market_encounters:
                    encounter = random.choice(market_encounters)
                else:
                    raise ValueError("No market encounters available in database")
            except Exception:
                raise ValueError("No market encounters available in database")
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        
        # Get random table from district data if available
        random_table = []
        if district_data and 'random_tables' in district_data and 'market' in district_data['random_tables']:
            random_table = district_data['random_tables']['market']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'market', self._generate_market_random_table)
        else:
            random_table = self._generate_market_random_table()
        
        return {
            'name': name,
            'type': 'market',
            'description': f"A bustling marketplace specializing in {specialty}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'npcs': [
                self._safe_random_choice(database_manager.get_table('npc_names', 'market_merchants', self.language) or ["Wary merchant", "Soul broker", "Flesh trader", "Curse dealer"], "market_merchants"),
                self._safe_random_choice(database_manager.get_table('npc_names', 'market_customers', self.language) or ["Desperate customer", "Pickpocket", "Market guard", "Information seller"], "market_customers")
            ]
        }
    
    def _generate_temple_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate temple content."""
        # Get temples from district data first, then city data, then fallback
        temples = []
        if district_data and 'temples' in district_data:
            temples = district_data['temples']
        elif city_data and 'temples' in city_data:
            temples = city_data['temples']
        
        if not temples:
            temples = database_manager.get_table('names', 'temple_names', self.language)
        if not temples:
            raise ValueError("No temple names available in database")
        
        # Get deities from database
        deities = database_manager.get_table('descriptions', 'temple_deities', self.language)
        if not deities:
            raise ValueError("No temple deities available in database")
        
        name = random.choice(temples)
        deity = random.choice(deities)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'temple', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                temple_encounters = database_manager.get_table('encounters', 'temple_encounters', self.language)
                if temple_encounters:
                    encounter = random.choice(temple_encounters)
                else:
                    raise ValueError("No temple encounters available in database")
            except Exception:
                raise ValueError("No temple encounters available in database")
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        
        # Get random table from district data if available
        random_table = []
        if district_data and 'random_tables' in district_data and 'temple' in district_data['random_tables']:
            random_table = district_data['random_tables']['temple']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'temple', self._generate_temple_random_table)
        else:
            random_table = self._generate_temple_random_table()
        
        return {
            'name': name,
            'type': 'temple',
            'description': f"A sacred place dedicated to {deity}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'npcs': [
                self._safe_random_choice(database_manager.get_table('npc_names', 'temple_npcs', self.language) or [], "temple_npcs"),
                self._safe_random_choice(database_manager.get_table('npc_names', 'temple_worshippers', self.language) or [], "temple_worshippers")
            ]
        }
    
    def _generate_tavern_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate tavern content."""
        # Get tavern names from district data first, then city data, then fallback
        taverns = []
        if district_data and 'taverns' in district_data:
            taverns = district_data['taverns']
        elif city_data and 'taverns' in city_data:
            taverns = city_data['taverns']
        
        if not taverns:
            taverns = database_manager.get_table('names', 'tavern_names', self.language)
            if not taverns:
                raise ValueError("No tavern names available in database")
        
        name = random.choice(taverns)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'tavern', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                tavern_encounters = database_manager.get_table('encounters', 'tavern_encounters', self.language)
                if tavern_encounters:
                    encounter = random.choice(tavern_encounters)
                else:
                    raise ValueError("No tavern encounters available in database")
            except Exception:
                raise ValueError("No tavern encounters available in database")
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        
        # Get tavern descriptions from database
        tavern_descriptions = database_manager.get_table('descriptions', 'tavern_descriptions', self.language)
        if not tavern_descriptions:
            raise ValueError("No tavern descriptions available in database")
        description = random.choice(tavern_descriptions)
        
        # Get tavern NPCs from city data if available, otherwise from database
        tavern_npcs = []
        tavern_customers = []
        
        if city_data and 'npc_names' in city_data:
            # Check if the city data has the specific tavern NPC tables
            if isinstance(city_data['npc_names'], dict):
                tavern_npcs = city_data['npc_names'].get('tavern_npcs', [])
                tavern_customers = city_data['npc_names'].get('tavern_customers', [])
        
        # Fallback to database if not found in city data
        if not tavern_npcs:
            tavern_npcs = database_manager.get_table('npc_names', 'tavern_npcs', self.language)
        if not tavern_customers:
            tavern_customers = database_manager.get_table('npc_names', 'tavern_customers', self.language)
            
        if not tavern_npcs or not tavern_customers:
            raise ValueError("No tavern NPCs available in database")
        npcs = [random.choice(tavern_npcs), random.choice(tavern_customers)]
        
        return {
            'name': name,
            'type': 'tavern',
            'description': description,
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': self._generate_tavern_random_table(),
            'npcs': npcs
        }
    
    def _generate_guild_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate guild content."""
        # Get guilds from district data first, then city data, then fallback
        guilds = []
        if district_data and 'guilds' in district_data:
            guilds = district_data['guilds']
        elif city_data and 'guilds' in city_data:
            guilds = city_data['guilds']
        
        if not guilds:
            guilds = database_manager.get_table('names', 'guild_names', self.language)
            if not guilds:
                raise ValueError("No guild names available in database")
        
        # Get guild features from city data
        purposes = []
        if city_data and 'features' in city_data:
            guild_features = city_data['features'].get('guild_features', [])
            if guild_features:
                purposes = guild_features
        
        if not purposes:
            purposes = database_manager.get_table('descriptions', 'guild_purposes', self.language)
            if not purposes:
                raise ValueError("No guild purposes available in database")
        
        name = random.choice(guilds)
        purpose = random.choice(purposes)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'guild', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                guild_encounters = database_manager.get_table('encounters', 'guild_encounters', self.language)
                if guild_encounters:
                    encounter = random.choice(guild_encounters)
                else:
                    raise ValueError("No guild encounters available in database")
            except Exception:
                raise ValueError("No guild encounters available in database")
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        
        # Get random table from district data if available
        random_table = []
        if district_data and 'random_tables' in district_data and 'guild' in district_data['random_tables']:
            random_table = district_data['random_tables']['guild']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'guild', self._generate_guild_random_table)
        else:
            random_table = self._generate_guild_random_table()
        
        return {
            'name': name,
            'type': 'guild',
            'description': f"A professional organization that {purpose}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'npcs': [
                            self._safe_random_choice(database_manager.get_table("npc_names", "guild_members", self.language) or [], "guild_members"),
            self._safe_random_choice(database_manager.get_table("npc_names", "guild_visitors", self.language) or [], "guild_visitors")
            ]
        }
    
    def _generate_residence_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate residence content."""
        residences = []
        if district_data and 'residences' in district_data:
            residences = district_data['residences']
        elif city_data and 'residences' in city_data:
            residences = city_data['residences']
        if not residences:
            residences = database_manager.get_table('names', 'residence_names', self.language)
            if not residences:
                raise ValueError("No residence names available in database")
        
        inhabitants = database_manager.get_table('descriptions', 'residence_inhabitants', self.language)
        if not inhabitants:
            raise ValueError("No residence inhabitants available in database")
        name = random.choice(residences)
        inhabitant = random.choice(inhabitants)
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'residence', [])
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                residence_encounters = database_manager.get_table('encounters', 'residence_encounters', self.language)
                if residence_encounters:
                    encounter = random.choice(residence_encounters)
                else:
                    raise ValueError("No residence encounters available in database")
            except Exception:
                raise ValueError("No residence encounters available in database")
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        random_table = []
        if district_data and 'random_tables' in district_data and 'residence' in district_data['random_tables']:
            random_table = district_data['random_tables']['residence']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'residence', self._generate_residence_random_table)
        else:
            random_table = self._generate_residence_random_table()
        return {
            'name': name,
            'type': 'residence',
            'description': f"A dwelling inhabited by {inhabitant}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'treasures': [self._safe_random_choice(database_manager.get_table("loot", "residence_treasures", self.language) or [], "residence_treasures")]
        }
    
    def _generate_ruins_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate ruins content."""
        ruins = []
        if district_data and 'ruins' in district_data:
            ruins = district_data['ruins']
        elif city_data and 'ruins' in city_data:
            ruins = city_data['ruins']
        if not ruins:
            ruins = database_manager.get_table('names', 'ruins_names', self.language)
            if not ruins:
                raise ValueError("No ruins names available in database")
        
        histories = database_manager.get_table('descriptions', 'ruins_histories', self.language)
        if not histories:
            raise ValueError("No ruins histories available in database")
        name = random.choice(ruins)
        history = random.choice(histories)
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'ruins', [])
        if encounters:
            encounter = random.choice(encounters)
        else:
            # Try to get encounters from database
            try:
                ruins_encounters = database_manager.get_table('encounters', 'ruins_encounters', self.language)
                if ruins_encounters:
                    encounter = random.choice(ruins_encounters)
                else:
                    raise ValueError("No ruins encounters available in database")
            except Exception:
                raise ValueError("No ruins encounters available in database")
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            # Try to get atmospheres from database
            try:
                atmospheres = database_manager.get_table('core', 'atmospheres', self.language)
                if atmospheres:
                    atmosphere = random.choice(atmospheres)
                else:
                    raise ValueError("No atmospheres available in database")
            except Exception:
                raise ValueError("No atmospheres available in database")
        random_table = []
        if district_data and 'random_tables' in district_data and 'ruins' in district_data['random_tables']:
            random_table = district_data['random_tables']['ruins']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'ruins', self._generate_ruins_random_table)
        else:
            random_table = self._generate_ruins_random_table()
        return {
            'name': name,
            'type': 'ruins',
            'description': f"Ancient ruins {history}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'treasures': [
                self._safe_random_choice(database_manager.get_table("loot", "ruins_treasures", self.language) or [], "ruins_treasures"),
                self._safe_random_choice(database_manager.get_table("loot", "ruins_artifacts", self.language) or [], "ruins_artifacts")
            ]
        }
    
    def _add_position_modifiers(self, content: Dict[str, Any], row: int, col: int) -> Dict[str, Any]:
        """Add position-specific modifiers to content."""
        # Edge positions (outer ring)
        if row == 0 or row == 4 or col == 0 or col == 4:
            content['position_type'] = 'edge'
        # Corner positions
        elif (row == 0 and col == 0) or (row == 0 and col == 4) or (row == 4 and col == 0) or (row == 4 and col == 4):
            content['position_type'] = 'corner'
        # Center position
        elif row == 2 and col == 2:
            content['position_type'] = 'center'
        # Inner positions
        else:
            content['position_type'] = 'inner'
        
        return content
    
    def _integrate_city_specific_content(self, content: Dict[str, Any], city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Integrate city-specific events, weather, and NPC content."""
        if not city_data:
            return content
        
        # Database-driven integration; no hardcoded fallbacks
        
        # Add city events
        if 'city_events' in city_data and city_data['city_events']:
            content['city_event'] = random.choice(city_data['city_events'])
        
        # Add weather conditions
        if 'weather_conditions' in city_data and isinstance(city_data['weather_conditions'], list) and len(city_data['weather_conditions']) > 0:
            content['weather'] = random.choice(city_data['weather_conditions'])
        
        # Add population
        if 'populations' in city_data and isinstance(city_data['populations'], list) and len(city_data['populations']) > 0:
            content['population'] = random.choice(city_data['populations'])
        
        # Add notable features for relevant content types
        if content.get('type') in ['landmark', 'building', 'street', 'district']:
            if 'features' in city_data and isinstance(city_data['features'], dict):
                features = city_data['features']
                feature_type = f"{content.get('type')}_features"
                if feature_type in features and isinstance(features[feature_type], list) and len(features[feature_type]) > 0:
                    content['notable_features'] = [random.choice(features[feature_type])]
                else:
                    # Fallback to general features
                    if 'landmark_features' in features and isinstance(features['landmark_features'], list) and len(features['landmark_features']) > 0:
                        content['notable_features'] = [random.choice(features['landmark_features'])]
        
        # Add NPC traits for relevant content types
        if content.get('type') in ['tavern', 'guild', 'temple', 'market', 'service', 'street', 'building', 'landmark', 'residence', 'ruins']:
            if 'npc_traits' in city_data and isinstance(city_data['npc_traits'], list) and len(city_data['npc_traits']) > 0:
                content['npc_trait'] = random.choice(city_data['npc_traits'])
            if 'npc_concerns' in city_data and isinstance(city_data['npc_concerns'], list) and len(city_data['npc_concerns']) > 0:
                content['npc_concern'] = random.choice(city_data['npc_concerns'])
            if 'npc_wants' in city_data and isinstance(city_data['npc_wants'], list) and len(city_data['npc_wants']) > 0:
                content['npc_want'] = random.choice(city_data['npc_wants'])
            if 'npc_secrets' in city_data and isinstance(city_data['npc_secrets'], list) and len(city_data['npc_secrets']) > 0:
                content['npc_secret'] = random.choice(city_data['npc_secrets'])
            
            # Add NPC name and trade (support dict structure with first/second names)
            if 'npc_names' in city_data:
                names_src = city_data['npc_names']
                if isinstance(names_src, dict):
                    first_names = names_src.get('first_names', [])
                    second_names = names_src.get('second_names', [])
                    if isinstance(first_names, list) and isinstance(second_names, list) and first_names and second_names:
                        content['npc_name'] = f"{random.choice(first_names)} {random.choice(second_names)}"
                elif isinstance(names_src, list) and names_src:
                    content['npc_name'] = random.choice(names_src)
            if 'npc_trades' in city_data and isinstance(city_data['npc_trades'], list) and len(city_data['npc_trades']) > 0:
                content['npc_trade'] = random.choice(city_data['npc_trades'])
            
            # Add affiliation
            if 'affiliations' in city_data and isinstance(city_data['affiliations'], dict):
                affiliations = city_data['affiliations']
                if 'npc_affiliations' in affiliations and isinstance(affiliations['npc_affiliations'], list) and len(affiliations['npc_affiliations']) > 0:
                    content['npc_affiliation'] = random.choice(affiliations['npc_affiliations'])
                if 'affiliation_attitudes' in affiliations and isinstance(affiliations['affiliation_attitudes'], list) and len(affiliations['affiliation_attitudes']) > 0:
                    content['npc_attitude'] = random.choice(affiliations['affiliation_attitudes'])
        
        # Add tavern-specific content
        if content.get('type') == 'tavern':
            if 'tavern_menu' in city_data and isinstance(city_data['tavern_menu'], list) and len(city_data['tavern_menu']) > 0:
                content['tavern_menu'] = random.choice(city_data['tavern_menu'])
            if 'tavern_innkeeper' in city_data and isinstance(city_data['tavern_innkeeper'], list) and len(city_data['tavern_innkeeper']) > 0:
                content['tavern_innkeeper'] = random.choice(city_data['tavern_innkeeper'])
            if 'tavern_patrons' in city_data and isinstance(city_data['tavern_patrons'], list) and len(city_data['tavern_patrons']) > 0:
                content['tavern_patron'] = random.choice(city_data['tavern_patrons'])
        
        # Add market-specific content
        if content.get('type') == 'market':
            if 'items_sold' in city_data and isinstance(city_data['items_sold'], list) and len(city_data['items_sold']) > 0:
                # Select 3-5 random items to sell
                num_items = random.randint(3, 5)
                selected_items = random.sample(city_data['items_sold'], min(num_items, len(city_data['items_sold'])))
                content['items_sold'] = selected_items
            if 'beast_prices' in city_data and isinstance(city_data['beast_prices'], list) and len(city_data['beast_prices']) > 0:
                # Select 2-3 random beasts to sell
                num_beasts = random.randint(2, 3)
                selected_beasts = random.sample(city_data['beast_prices'], min(num_beasts, len(city_data['beast_prices'])))
                content['beast_prices'] = selected_beasts
            if 'services' in city_data and isinstance(city_data['services'], list) and len(city_data['services']) > 0:
                # Select 2-4 random services to offer
                num_services = random.randint(2, 4)
                selected_services = random.sample(city_data['services'], min(num_services, len(city_data['services'])))
                content['services'] = selected_services
        
        # Add service-specific content (for service locations)
        if content.get('type') == 'service':
            if 'services' in city_data and isinstance(city_data['services'], list) and len(city_data['services']) > 0:
                # Select 3-6 random services to offer
                num_services = random.randint(3, 6)
                selected_services = random.sample(city_data['services'], min(num_services, len(city_data['services'])))
                content['services'] = selected_services
        
        # Add patrons for businesses (taverns, markets, guilds)
        if content.get('type') in ['tavern', 'market', 'guild']:
            patrons = []
            names_pool: list = []
            if 'npc_names' in city_data:
                names_src = city_data['npc_names']
                if isinstance(names_src, dict):
                    first_names = names_src.get('first_names', [])
                    second_names = names_src.get('second_names', [])
                    if isinstance(first_names, list) and isinstance(second_names, list) and first_names and second_names:
                        for _ in range(10):
                            names_pool.append(f"{random.choice(first_names)} {random.choice(second_names)}")
                elif isinstance(names_src, list):
                    names_pool = names_src[:]

            if names_pool:
                if 'npc_trades' in city_data and isinstance(city_data['npc_trades'], list) and len(city_data['npc_trades']) > 0:
                    num_patrons = random.randint(2, 4)
                    for _ in range(num_patrons):
                        name = random.choice(names_pool)
                        trade = random.choice(city_data['npc_trades'])
                        patrons.append(f"{name} ({trade})")
                else:
                    num_patrons = random.randint(2, 4)
                    patrons = random.sample(names_pool, min(num_patrons, len(names_pool)))
            
            if patrons:
                content['patrons'] = patrons
        
        # Add key NPCs for all content types
        if 'npc_names' in city_data:
            names_src = city_data['npc_names']
            names_pool: list = []
            if isinstance(names_src, dict):
                first_names = names_src.get('first_names', [])
                second_names = names_src.get('second_names', [])
                if isinstance(first_names, list) and isinstance(second_names, list) and first_names and second_names:
                    for _ in range(10):
                        names_pool.append(f"{random.choice(first_names)} {random.choice(second_names)}")
            elif isinstance(names_src, list):
                names_pool = names_src[:]

            if names_pool:
                num_key_npcs = random.randint(2, 3)
                key_npcs = []
                for _ in range(num_key_npcs):
                    name = random.choice(names_pool)
                    if 'npc_trades' in city_data and isinstance(city_data['npc_trades'], list) and len(city_data['npc_trades']) > 0:
                        trade = random.choice(city_data['npc_trades'])
                        key_npcs.append(f"{name} ({trade})")
                    else:
                        key_npcs.append(name)
                content['key_npcs'] = key_npcs
        
        # Add active factions
        if 'factions' in city_data and isinstance(city_data['factions'], dict):
            factions_data = city_data['factions']
            if 'faction_names' in factions_data and isinstance(factions_data['faction_names'], list) and len(factions_data['faction_names']) > 0:
                # Generate 1-3 active factions
                num_factions = random.randint(1, 3)
                selected_factions = random.sample(factions_data['faction_names'], min(num_factions, len(factions_data['faction_names'])))
                content['active_factions'] = selected_factions
        
        return content
    
    def _add_cross_references(self, hex_grid: Dict[str, Any], city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Add cross-references between related hexes."""
        for hex_id, hex_data in hex_grid.items():
            content = hex_data.get('content', {})
            content_type = content.get('type', '')
            
            # Find related hexes based on content type
            related_hexes = []
            
            # Find nearby hexes of the same type
            for other_id, other_data in hex_grid.items():
                if other_id != hex_id:
                    other_content = other_data.get('content', {})
                    other_type = other_content.get('type', '')
                    
                    # Same type hexes are related
                    if other_type == content_type:
                        related_hexes.append({
                            'hex_id': other_id,
                            'name': other_content.get('name', 'Unknown'),
                            'type': other_type,
                            'relationship': 'same_type'
                        })
                    
                    # Complementary types (e.g., tavern near market)
                    elif self._are_complementary_types(content_type, other_type):
                        related_hexes.append({
                            'hex_id': other_id,
                            'name': other_content.get('name', 'Unknown'),
                            'type': other_type,
                            'relationship': 'complementary'
                        })
            
            # Add cross-references to content
            if related_hexes:
                content['related_hexes'] = related_hexes[:3]  # Limit to 3 related hexes
                hex_data['content'] = content
        
        return hex_grid
    
    def _get_enhanced_fallback_content(self, content_type: str) -> List[str]:
        """Get enhanced fallback content for a specific type."""
        # Try to get content from database first
        if hasattr(self, 'content_tables') and self.content_tables:
            # Map content types to database table names
            table_mapping = {
                'buildings': 'buildings',
                'streets': 'streets', 
                'landmarks': 'landmarks',
                'markets': 'markets',
                'temples': 'temples',
                'taverns': 'taverns',
                'guilds': 'guilds',
                'residences': 'residences',
                'ruins': 'ruins'
            }
            
            table_name = table_mapping.get(content_type)
            if table_name and table_name in self.content_tables:
                return self.content_tables[table_name]
        
        # If no database content available, raise error instead of using hardcoded fallbacks
        raise ValueError(f"No {content_type} content available in database")
    
    def _are_complementary_types(self, type1: str, type2: str) -> bool:
        """Check if two content types are complementary."""
        complementary_pairs = [
            ('tavern', 'market'),
            ('tavern', 'guild'),
            ('temple', 'market'),
            ('guild', 'market'),
            ('building', 'street'),
            ('landmark', 'temple'),
            ('residence', 'market'),
            ('tavern', 'temple')
        ]
        
        return (type1, type2) in complementary_pairs or (type2, type1) in complementary_pairs
    
    def _generate_district_random_table(self) -> List[str]:
        """Generate random table for district encounters."""
        return [
            "1-2: Encounter corrupt guards demanding bribes",
            "3-4: Find a hidden entrance to the underground",
            "5-6: Witness a public execution or punishment",
            "7-8: Discover graffiti revealing district secrets",
            "9-10: Meet a desperate resident with information",
            "11-12: Find evidence of supernatural activity"
        ]
    
    def _generate_building_random_table(self) -> List[str]:
        """Generate random table for building encounters."""
        return [
            "1-2: The building shifts and changes when not watched",
            "3-4: Hear voices from within speaking in dead languages",
            "5-6: Find a window that shows different time periods",
            "7-8: Discover the entrance is sometimes not there",
            "9-10: Meet the building's ghostly caretaker",
            "11-12: Trigger an ancient security system"
        ]
    
    def _generate_street_random_table(self) -> List[str]:
        """Generate random table for street encounters."""
        return [
            "1-2: The street leads somewhere it shouldn't",
            "3-4: Footsteps echo yours, but no one is there",
            "5-6: Street performers display impossible acts",
            "7-8: A stranger offers to sell you directions",
            "9-10: The cobblestones spell out a message",
            "11-12: Time moves differently on this street"
        ]
    
    def _generate_landmark_random_table(self) -> List[str]:
        """Generate random table for landmark encounters."""
        return [
            "1-2: The landmark grants a prophetic vision",
            "3-4: Touching it reveals a hidden truth",
            "5-6: It demands an offering for safe passage",
            "7-8: Whispers reveal the location of treasure",
            "9-10: A guardian spirit manifests",
            "11-12: The landmark transforms before your eyes"
        ]
    
    def _generate_market_random_table(self) -> List[str]:
        """Generate random table for market encounters."""
        return [
            "1-2: A vendor offers to buy your memories",
            "3-4: Find an item that shouldn't exist here",
            "5-6: Witness a transaction in souls rather than coin",
            "7-8: A merchant recognizes you from a dream",
            "9-10: Discover the market exists in multiple realms",
            "11-12: A purchase comes with an unexpected curse"
        ]
    
    def _generate_temple_random_table(self) -> List[str]:
        """Generate random table for temple encounters."""
        return [
            "1-2: The altar demands a sacrifice for a blessing",
            "3-4: Hear confessions that reveal dark secrets",
            "5-6: A divine vision shows you a possible future",
            "7-8: The sacred texts rewrite themselves",
            "9-10: A miracle occurs, but at a terrible price",
            "11-12: The deity speaks directly to you"
        ]
    
    def _generate_tavern_random_table(self) -> List[str]:
        """Generate random table for tavern encounters."""
        return [
            "1-2: Overhear a conversation about hidden treasure",
            "3-4: A stranger challenges you to a deadly game",
            "5-6: The drinks reveal visions of the past",
            "7-8: A brawl breaks out over ancient grudges",
            "9-10: Meet someone who claims to know you",
            "11-12: The tavern exists in multiple time periods"
        ]
    
    def _generate_guild_random_table(self) -> List[str]:
        """Generate random table for guild encounters."""
        return [
            "1-2: Offered membership for a terrible price",
            "3-4: Witness an initiation ritual",
            "5-6: Discover the guild's true purpose",
            "7-8: A member offers you a dangerous job",
            "9-10: Learn of a rival guild's plans",
            "11-12: The guild master requests a private audience"
        ]
    
    def _generate_residence_random_table(self) -> List[str]:
        """Generate random table for residence encounters."""
        return [
            "1-2: The house remembers its former inhabitants",
            "3-4: Find a diary revealing family secrets",
            "5-6: Rooms appear and disappear unexpectedly",
            "7-8: Meet a resident who doesn't know they're dead",
            "9-10: Discover a passage to another house",
            "11-12: The building tries to keep you inside"
        ]
    
    def _generate_ruins_random_table(self) -> List[str]:
        """Generate random table for ruins encounters."""
        return [
            "1-2: Find an intact room with ancient treasures",
            "3-4: Trigger a magical trap or ward",
            "5-6: Encounter the ghost of a former inhabitant",
            "7-8: Discover clues to the site's destruction",
            "9-10: Find a passage to active underground areas",
            "11-12: The ruins briefly restore to their former glory"
        ]
    
    def _save_overlay_data(self, overlay_name: str, overlay_data: Dict[str, Any]):
        """Save overlay data to a JSON file."""
        # Ensure the output directory exists
        self.output_directory.mkdir(parents=True, exist_ok=True)
        filename = self.output_directory / f"{overlay_name}_overlay.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(overlay_data, f, indent=2, ensure_ascii=False)
    
    def load_overlay_data(self, overlay_name: str) -> Optional[Dict[str, Any]]:
        """Load overlay data from cache or file."""
        # Check cache first
        if overlay_name in self.overlays_cache:
            return self.overlays_cache[overlay_name]
        
        # Try to load from file
        filename = self.output_directory / f"{overlay_name}_overlay.json"
        if filename.exists():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    overlay_data = json.load(f)
                    self.overlays_cache[overlay_name] = overlay_data
                    return overlay_data
            except Exception as e:
                print(f"Error loading overlay data: {e}")
        
        return None
    
    def get_overlay_ascii_view(self, overlay_name: str) -> str:
        """Generate ASCII representation of the city overlay."""
        overlay_data = self.load_overlay_data(overlay_name)
        if not overlay_data:
            overlay_data = self.generate_city_overlay(overlay_name)
        
        lines = []
        lines.append(f"🏰 {overlay_data['display_name'].upper()}")
        lines.append("=" * 50)
        lines.append("")
        lines.append("City Overlay - Hex Grid")
        lines.append("-" * 30)
        lines.append("")
        
        # Generate grid representation
        hex_grid = overlay_data['hex_grid']
        
        # Determine grid dimensions from hex data
        if hex_grid:
            rows = set()
            cols = set()
            for hex_id in hex_grid.keys():
                if '_' in hex_id:
                    row, col = hex_id.split('_')
                    rows.add(int(row))
                    cols.add(int(col))
            
            if rows and cols:
                max_row = max(rows)
                max_col = max(cols)
                grid_size = max(max_row, max_col) + 1
            else:
                grid_size = 5  # Default fallback
        else:
            grid_size = 5  # Default fallback
        
        # Header row
        lines.append("   " + " ".join([f"Col{i+1:2}" for i in range(grid_size)]))
        lines.append("")
        
        # Data rows
        for row in range(grid_size):
            row_line = f"Row{row+1} "
            for col in range(grid_size):
                hex_id = f"{row}_{col}"
                hex_data = hex_grid.get(hex_id, {})
                content = hex_data.get('content', {})
                
                # Use first letter of content type as symbol
                symbol = content.get('type', 'unknown')[0].upper()
                row_line += f" [{symbol}] "
            
            lines.append(row_line)
        
        lines.append("")
        lines.append("Legend:")
        lines.append("D=District B=Building S=Street L=Landmark M=Market")
        lines.append("T=Temple V=Tavern G=Guild R=Residence U=Ruins")
        lines.append("")
        
        # Add detailed hex descriptions
        lines.append("Hex Details:")
        lines.append("-" * 20)
        
        for row in range(grid_size):
            for col in range(grid_size):
                hex_id = f"{row}_{col}"
                hex_data = hex_grid.get(hex_id, {})
                content = hex_data.get('content', {})
                
                lines.append(f"")
                lines.append(f"[{row+1},{col+1}] {content.get('name', 'Unknown')}")
                # Use translation system if available
                try:
                    from .translation_system import translation_system
                    type_label = translation_system.t('type')
                    description_label = translation_system.t('description')
                    encounter_label = translation_system.t('encounter')
                except ImportError:
                    type_label = 'Type'
                    description_label = 'Description'
                    encounter_label = 'Encounter'
                
                lines.append(f"{type_label}: {content.get('type', 'Unknown').title()}")
                lines.append(f"{description_label}: {content.get('description', 'No description')}")
                
                if content.get('encounter'):
                    lines.append(f"{encounter_label}: {content.get('encounter')}")
                
                if content.get('random_table'):
                    lines.append("Random Events:")
                    for event in content.get('random_table', [])[:3]:  # Show first 3
                        lines.append(f"  {event}")
        
        return "\n".join(lines)

    def load_city_database(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Public wrapper for _load_city_database."""
        return self._load_city_database(city_name)
    
    def generate_district_based_content(self, district_name: str, row: int, col: int, overlay_name: str, city_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Public wrapper for _generate_district_based_content."""
        return self._generate_district_based_content(district_name, row, col, overlay_name, city_data)
    
    def generate_position_based_content(self, row: int, col: int, distance: int, radius: int, overlay_name: str, city_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Public wrapper for _generate_position_based_content."""
        return self._generate_position_based_content(row, col, distance, radius, overlay_name, city_data)
    
    def hex_distance(self, row1: int, col1: int, row2: int, col2: int) -> int:
        """Public wrapper for _hex_distance."""
        return self._hex_distance(row1, col1, row2, col2)
    
    def save_overlay_data(self, overlay_name: str, overlay_data: Dict[str, Any]):
        """Public wrapper for _save_overlay_data."""
        return self._save_overlay_data(overlay_name, overlay_data)
    
    def clear_overlay_cache(self, overlay_name: str):
        """Clear the cache for a specific overlay."""
        if overlay_name in self.overlays_cache:
            del self.overlays_cache[overlay_name]
            print(f"Cleared cache for overlay: {overlay_name}")
        
        # Also delete the file if it exists
        filename = os.path.join(self.output_directory, f"{overlay_name}_overlay.json")
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted overlay file: {filename}")
    
    def regenerate_overlay(self, overlay_name: str) -> Dict[str, Any]:
        """Clear cache and regenerate overlay data."""
        self.clear_overlay_cache(overlay_name)
        return self.generate_city_overlay(overlay_name)

# Global instance
# Initialize with default language, will be updated by routes.py
city_overlay_analyzer = CityOverlayAnalyzer('en')