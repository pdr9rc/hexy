#!/usr/bin/env python3
"""
City Overlay Analyzer for The Dying Lands
Processes city overlay images and generates round hex grids with random content.
Supports matrix-based district placement from city JSON files.
"""

import os
import random
import json
import math
from typing import Dict, List, Tuple, Optional, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.mork_borg_lore_database import MorkBorgLoreDatabase
from backend.database_manager import database_manager

class CityOverlayAnalyzer:
    """Generates round hex grids for city overlays using matrix-based district placement and random content generation."""
    
    def __init__(self):
        self.lore_db = MorkBorgLoreDatabase()
        self.output_directory = 'dying_lands_output/city_overlays'
        os.makedirs(self.output_directory, exist_ok=True)
        self.content_tables = database_manager.load_tables('en')
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
        city_db_path = f'databases/cities/{city_key}.json'
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
        overlays = self.get_available_overlays()
        print(f"DEBUG: Requested overlay: '{overlay_name}'")
        print(f"DEBUG: Available overlays: {[o['name'] for o in overlays]}")
        
        overlay_info = next((o for o in overlays if o['name'] == overlay_name), None)
        
        if not overlay_info:
            print(f"DEBUG: No exact match found for '{overlay_name}'")
            # Try case-insensitive match
            overlay_info = next((o for o in overlays if o['name'].lower() == overlay_name.lower()), None)
            if overlay_info:
                print(f"DEBUG: Found case-insensitive match: {overlay_info['name']}")
        
        if not overlay_info:
            print(f"DEBUG: Still no match found. Available overlay details:")
            for overlay in overlays:
                print(f"  - Name: '{overlay['name']}', Filename: '{overlay['filename']}'")
            raise ValueError(f"City overlay '{overlay_name}' not found")
        
        # Load city data
        city_data = self._load_city_database(overlay_name.lower())
        
        # Generate round hex grid
        hex_grid = self._generate_round_hex_grid(overlay_name, city_data)
        
        # Calculate grid radius
        radius = self._calculate_grid_radius(hex_grid)
        
        # Create overlay data structure
        overlay_data = {
            'name': overlay_name,
            'display_name': self._format_overlay_name(overlay_name),
            'filename': f"{overlay_name}_overlay.json",
            'grid_type': 'round',
            'radius': radius,
            'hex_grid': hex_grid,
            'total_hexes': len(hex_grid)
        }
        
        print(f"DEBUG: Final hex grid has {len(hex_grid)} hexes")
        print(f"DEBUG: Final hex grid keys: {list(hex_grid.keys())}")
        
        # Save overlay data
        self._save_overlay_data(overlay_name, overlay_data)
        
        return overlay_data
    
    def _generate_round_hex_grid(self, overlay_name: str, city_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a round hex grid with district matrix support."""
        hex_grid = {}
        
        print(f"DEBUG: Generating round hex grid for {overlay_name}")
        
        # Check if city has a district matrix defined
        district_matrix = self._get_district_matrix(city_data)
        
        if district_matrix:
            print(f"DEBUG: Using predefined district matrix")
            # Use the predefined district matrix
            hex_grid = self._apply_district_matrix(district_matrix, overlay_name, city_data)
        else:
            print(f"DEBUG: No district matrix found, generating default round grid")
            # Generate a default round grid
            hex_grid = self._generate_default_round_grid(overlay_name, city_data)
        
        print(f"DEBUG: Final hex grid has {len(hex_grid)} hexes")
        return hex_grid
    
    def _get_district_matrix(self, city_data: Optional[Dict[str, Any]]) -> Optional[List[List[str]]]:
        """Get the district matrix from city data if it exists."""
        print(f"DEBUG: Checking for district matrix in city data")
        if city_data:
            print(f"DEBUG: City data keys: {list(city_data.keys())}")
            if 'district_matrix' in city_data:
                matrix = city_data['district_matrix']
                print(f"DEBUG: Found district matrix: {matrix}")
                return matrix
            else:
                print(f"DEBUG: No district_matrix found in city data")
        else:
            print(f"DEBUG: No city data provided")
        return None
    
    def _apply_district_matrix(self, matrix: List[List[str]], overlay_name: str, city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply a predefined district matrix to generate hex content."""
        hex_grid = {}
        
        print(f"DEBUG: Applying district matrix for {overlay_name}")
        print(f"DEBUG: Matrix dimensions: {len(matrix)}x{len(matrix[0]) if matrix else 0}")
        
        # Fill the entire matrix with hexes (visible or invisible)
        for row_idx, row in enumerate(matrix):
            for col_idx, district_name in enumerate(row):
                hex_id = f"{row_idx}_{col_idx}"
                hex_position = f"Row {row_idx+1}, Col {col_idx+1}"
                
                if district_name and district_name.strip():  # Has content
                    print(f"DEBUG: Processing hex {hex_id} with district '{district_name}'")
                    
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
                    
                    print(f"DEBUG: Generated content for {hex_id}: {hex_content.get('name', 'Unknown')}")
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
        
        print(f"DEBUG: Generated {len(hex_grid)} hexes total (including empty ones)")
        return hex_grid
    
    def _generate_default_round_grid(self, overlay_name: str, city_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a default round hex grid when no matrix is provided."""
        hex_grid = {}
        
        # Create a 10x10 grid (100 hexes total) - changed from radius 3 round grid
        grid_size = 10
        center_row, center_col = 5, 5  # Center point for 10x10 grid
        
        for row in range(grid_size):
            for col in range(grid_size):
                hex_id = f"{row}_{col}"
                hex_position = f"Row {row+1}, Col {col+1}"
                
                # Calculate distance from center for content generation
                distance = self._hex_distance(center_row, center_col, row, col)
                
                # Generate content based on position in the grid
                hex_content = self._generate_position_based_content(
                        row, col, distance, grid_size // 2, overlay_name, city_data
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
            content_type = self._select_district_content_type(district_data)
            content = self._generate_content_by_type(content_type, row, col, overlay_name, city_data, district_data)
            
            # Add fallback if content is None
            if content is None:
                content = {
                    'name': f'Unknown {district_name}',
                    'type': 'unknown',
                    'description': f'A mysterious area in {district_name}',
                    'encounter': 'Strange activities',
                    'atmosphere': 'Mysterious and foreboding'
                }
            
            return content
        else:
            # Fallback to generic district content
            fallback_districts = [
                "The Corpse Quarter", "Merchant's Decay", "The Bone Markets", "Plague Ward",
                "The Hanging Gardens", "Scholar's Ruin", "Thieves' Paradise", "The Bleeding Streets",
                "Noble's Decay", "The Cursed Commons"
            ]
            fallback_encounters = [
                "Plague-ridden beggars seeking alms", "Corrupt city guards demanding bribes",
                "Mysterious figures in black robes", "Mad prophet screaming prophecies",
                "Pack of starving dogs", "Lost soul wandering aimlessly"
            ]
            fallback_atmospheres = [
                "Thick with the stench of decay", "Perpetual twilight shrouds the streets",
                "Whispers echo from empty buildings", "Shadows move where no one walks",
                "The air tastes of copper and fear", "Strange lights flicker in windows"
            ]
            
            districts = self._get_city_content_list(city_data, 'districts', fallback_districts)
            encounters = self._get_city_encounters(city_data, 'district', fallback_encounters)
            atmospheres = self._get_city_atmospheres(city_data, fallback_atmospheres)
            random_table = self._get_city_random_table(city_data, 'district', self._generate_district_random_table)
            
            name = random.choice(districts)
            encounter = random.choice(encounters) if encounters else "Mysterious activities in the district"
            atmosphere = random.choice(atmospheres) if atmospheres else "Dark and foreboding"
            
            return {
                'name': name,
                'description': f"A district where {random.choice(['the wealthy once lived', 'merchants once thrived', 'scholars once studied', 'the poor struggle to survive'])}.",
                'encounter': encounter,
                'atmosphere': atmosphere,
                'random_table': random_table,
                'notable_features': [
                    random.choice(["Crumbling mansions", "Narrow alleyways", "Ancient statues", "Broken fountains"]),
                    random.choice(["Abandoned shops", "Boarded windows", "Graffiti-covered walls", "Overgrown gardens"])
                ]
            }
    
    def _find_district_data(self, district_name: str, city_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find district data by name in city data."""
        if not city_data or 'districts' not in city_data:
            print(f"DEBUG: No city data or districts found for '{district_name}'")
            return None
        
        print(f"DEBUG: Looking for district '{district_name}' in {len(city_data['districts'])} districts")
        available_districts = [d.get('name', 'Unknown') for d in city_data['districts']]
        print(f"DEBUG: Available districts: {available_districts}")
        
        for district in city_data['districts']:
            if district.get('name', '').lower() == district_name.lower():
                print(f"DEBUG: Found district '{district_name}'")
                return district
        
        print(f"DEBUG: District '{district_name}' not found")
        return None
    
    def _select_district_content_type(self, district_data: Dict[str, Any]) -> str:
        """Select content type based on district data."""
        # Weight content types based on what's available in the district
        content_weights = {}
        
        if 'buildings' in district_data and district_data['buildings']:
            content_weights['building'] = 0.3
        if 'streets' in district_data and district_data['streets']:
            content_weights['street'] = 0.2
        if 'landmarks' in district_data and district_data['landmarks']:
            content_weights['landmark'] = 0.2
        if 'markets' in district_data and district_data['markets']:
            content_weights['market'] = 0.15
        if 'temples' in district_data and district_data['temples']:
            content_weights['temple'] = 0.15
        
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
        """Generate specific content based on type."""
        # Base content structure
        content = {
            'type': content_type,
            'name': '',
            'description': '',
            'encounter': '',
            'atmosphere': '',
            'random_table': [],
            'notable_features': [],
            'threats': [],
            'treasures': [],
            'npcs': []
        }
        
        # Generate content based on type
        if content_type == 'district':
            content.update(self._generate_district_content(city_data, district_data))
        elif content_type == 'building':
            content.update(self._generate_building_content(city_data, district_data))
        elif content_type == 'street':
            content.update(self._generate_street_content(city_data, district_data))
        elif content_type == 'landmark':
            content.update(self._generate_landmark_content(city_data, district_data))
        elif content_type == 'market':
            content.update(self._generate_market_content(city_data, district_data))
        elif content_type == 'temple':
            content.update(self._generate_temple_content(city_data, district_data))
        elif content_type == 'tavern':
            content.update(self._generate_tavern_content(city_data, district_data))
        elif content_type == 'guild':
            content.update(self._generate_guild_content(city_data, district_data))
        elif content_type == 'residence':
            content.update(self._generate_residence_content(city_data, district_data))
        elif content_type == 'ruins':
            content.update(self._generate_ruins_content(city_data, district_data))
        
        return content
    
    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Choose an item based on weighted probabilities."""
        items = list(weights.keys())
        weights_list = list(weights.values())
        return random.choices(items, weights=weights_list)[0]
    
    def _load_city_database(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Load city-specific database if available."""
        city_db_path = f'databases/cities/{city_name}.json'
        if os.path.exists(city_db_path):
            try:
                with open(city_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load city database for {city_name}: {e}")
        return None
    

    
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
        if district_data:
            # Use specific district data
            name = district_data.get('name', 'Unknown District')
            description = district_data.get('description', f"A district where {random.choice(['the wealthy once lived', 'merchants once thrived', 'scholars once studied', 'the poor struggle to survive'])}.")
            
            # Get encounters from district data
            encounters = district_data.get('encounters', [])
            if encounters:
                encounter = random.choice(encounters)
            else:
                encounter = "Mysterious activities in the district"
            
            # Get atmosphere from district data
            atmospheres = district_data.get('atmosphere_modifiers', [])
            if atmospheres:
                atmosphere = random.choice(atmospheres)
            else:
                atmosphere = "Dark and foreboding"
            
            # Get random table from district data
            random_tables = district_data.get('random_tables', {})
            if 'district' in random_tables:
                random_table = random_tables['district']
            else:
                random_table = self._generate_district_random_table()
            
            # Get notable features from district data
            notable_features = []
            for content_type in ['buildings', 'streets', 'landmarks']:
                if content_type in district_data and district_data[content_type]:
                    notable_features.append(random.choice(district_data[content_type]))
            
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
        else:
            # Fallback to generic district content
            fallback_districts = [
                "The Corpse Quarter", "Merchant's Decay", "The Bone Markets", "Plague Ward",
                "The Hanging Gardens", "Scholar's Ruin", "Thieves' Paradise", "The Bleeding Streets",
                "Noble's Decay", "The Cursed Commons"
            ]
        fallback_encounters = [
            "Plague-ridden beggars seeking alms", "Corrupt city guards demanding bribes",
            "Mysterious figures in black robes", "Mad prophet screaming prophecies",
            "Pack of starving dogs", "Lost soul wandering aimlessly"
        ]
        fallback_atmospheres = [
            "Thick with the stench of decay", "Perpetual twilight shrouds the streets",
            "Whispers echo from empty buildings", "Shadows move where no one walks",
            "The air tastes of copper and fear", "Strange lights flicker in windows"
        ]
        
        districts = self._get_city_content_list(city_data, 'districts', fallback_districts)
        encounters = self._get_city_encounters(city_data, 'district', fallback_encounters)
        atmospheres = self._get_city_atmospheres(city_data, fallback_atmospheres)
        random_table = self._get_city_random_table(city_data, 'district', self._generate_district_random_table)
        
        name = random.choice(districts)
        encounter = random.choice(encounters) if encounters else "Mysterious activities in the district"
        atmosphere = random.choice(atmospheres) if atmospheres else "Dark and foreboding"
        
        return {
            'name': name,
            'description': f"A district where {random.choice(['the wealthy once lived', 'merchants once thrived', 'scholars once studied', 'the poor struggle to survive'])}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'notable_features': [
                random.choice(["Crumbling mansions", "Narrow alleyways", "Ancient statues", "Broken fountains"]),
                random.choice(["Abandoned shops", "Boarded windows", "Graffiti-covered walls", "Overgrown gardens"])
            ]
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
            buildings = [
                "The Moldering Manor",
                "House of Broken Dreams",
                "The Weeping Tower",
                "Crimson Archives",
                "The Bone Foundry",
                "House of Whispers",
                "The Iron Sanctuary",
                "Tower of Screams",
                "The Bloody Library",
                "Chamber of Echoes"
            ]
        
        purposes = [
            "abandoned residence of a fallen noble",
            "mysterious workshop of unknown purpose",
            "forgotten library with forbidden knowledge",
            "ancient temple to a forgotten god",
            "guild hall for secretive organization",
            "warehouse filled with strange artifacts"
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
            encounter = f"The building {random.choice(['seems abandoned but sounds come from within', 'is guarded by strange creatures', 'pulses with unnatural energy', 'draws visitors like moths to flame'])}."
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"The air around the building {random.choice(['crackles with dark energy', 'feels unnaturally cold', 'whispers forgotten secrets', 'reeks of ancient death'])}."
        
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
            'description': f"An imposing structure that once served as a {purpose}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'treasures': [random.choice(["Hidden vault", "Secret passage", "Cursed artifact", "Ancient tome"])]
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
            streets = [
                "Corpse Alley",
                "Bleeding Way", 
                "The Bone Road",
                "Sorrow Street",
                "Plague Path",
                "The Withered Walk",
                "Death's Door Lane",
                "The Screaming Steps",
                "Tomb Street",
                "The Cursed Crossing"
            ]
        
        conditions = [
            "cracked cobblestones stained with old blood",
            "ankle-deep mud mixed with unidentifiable substances",
            "broken glass that crunches underfoot",
            "patches of strange, glowing moss",
            "deep potholes that seem to lead nowhere",
            "slippery stones covered in mysterious slime"
        ]
        
        name = random.choice(streets)
        condition = random.choice(conditions)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'street', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            encounter = f"The street {random.choice(['is haunted by spectral figures', 'echoes with the sounds of long-past events', 'seems to change direction when not watched', 'is patrolled by something unseen'])}."
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"Walking here feels {random.choice(['like being watched by unseen eyes', 'as if the very stones remember violence', 'heavy with the weight of forgotten sorrows', 'charged with malevolent energy'])}."
        
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
            'description': f"A winding thoroughfare with {condition}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'threats': [random.choice(["Unstable buildings", "Roving gangs", "Supernatural manifestations", "Poisonous vapors"])]
        }
    
    def _generate_landmark_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate landmark content."""
        # Get landmarks from district data first, then city data, then fallback
        landmarks = []
        if district_data and 'landmarks' in district_data:
            landmarks = district_data['landmarks']
        elif city_data and 'landmarks' in city_data:
            landmarks = city_data['landmarks']
        
        if not landmarks:
            landmarks = [
                "The Weeping Obelisk",
                "Fountain of Bones",
                "The Iron Gallows",
                "Cathedral of Screams",
                "The Bleeding Monument",
                "Tower of the Damned",
                "The Corpse Clock",
                "Throne of Skulls",
                "The Wailing Gate",
                "Pillar of Sorrows"
            ]
        
        significances = [
            "marks the site of an ancient atrocity",
            "serves as a meeting place for cultists",
            "is said to grant visions to those who touch it",
            "bleeds real blood on certain nights",
            "whispers the names of the dead",
            "grows larger with each passing year"
        ]
        
        name = random.choice(landmarks)
        significance = random.choice(significances)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'landmark', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            encounter = f"The landmark {random.choice(['draws crowds of pilgrims and madmen', 'is avoided by all sane inhabitants', 'pulses with otherworldly power', 'seems to watch those who approach'])}."
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"The area around it {random.choice(['feels sacred and terrible', 'thrums with ancient power', 'whispers with voices of the past', 'radiates an aura of dread'])}."
        
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
            'description': f"An imposing monument that {significance}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'notable_features': [
                random.choice(["Strange inscriptions", "Supernatural phenomena", "Ritual markings", "Offerings from visitors"]),
                random.choice(["Guardian spirits", "Temporal anomalies", "Prophetic visions", "Cursed ground"])
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
            markets = [
                "The Bone Bazaar",
                "Corpse Market",
                "The Bleeding Stalls",
                "Plague Merchant's Square",
                "The Soul Exchange",
                "Market of Whispers",
                "The Cursed Commerce",
                "Death's Trading Post",
                "The Flesh Fair",
                "Sorrow's Marketplace"
            ]
        
        specialties = [
            "forbidden artifacts and cursed relics",
            "body parts and alchemical ingredients", 
            "souls and memories of the dead",
            "weapons forged from unholy metals",
            "maps to places that shouldn't exist",
            "services that violate natural law"
        ]
        
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
            encounter = f"The market {random.choice(['operates only during certain hours', 'requires payment in strange currencies', 'attracts customers from other realms', 'exists in multiple dimensions simultaneously'])}."
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"The air {random.choice(['shimmers with dark magic', 'carries whispers in unknown languages', 'feels heavy with desperate desires', 'crackles with forbidden transactions'])}."
        
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
            'description': f"A bustling marketplace specializing in {specialty}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'npcs': [
                random.choice(["Mysterious merchant", "Soul broker", "Flesh trader", "Curse dealer"]),
                random.choice(["Desperate customer", "Pickpocket", "Market guard", "Information seller"])
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
            temples = [
                "Temple of the Dying God",
                "Shrine of Bones",
                "The Blood Cathedral",
                "Chapel of Screams",
                "The Corpse Sanctuary",
                "House of Final Prayers",
                "The Weeping Altar",
                "Cathedral of Endings",
                "Shrine of Forgotten Names",
                "The Last Church"
            ]
        
        deities = [
            "a god of death and decay",
            "the patron of lost souls",
            "a forgotten deity of suffering",
            "the lord of final moments",
            "an ancient god of bones",
            "the goddess of beautiful endings"
        ]
        
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
            encounter = f"The temple {random.choice(['holds services at midnight', 'requires blood offerings', 'grants dark blessings to supplicants', 'echoes with otherworldly chants'])}."
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"The sacred space {random.choice(['feels both holy and profane', 'pulses with divine corruption', 'whispers with the voice of god', 'radiates transcendent horror'])}."
        
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
            'description': f"A sacred place dedicated to {deity}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'npcs': [
                random.choice(["Mad priest", "Death cultist", "Heretical cleric", "Divine prophet"]),
                random.choice(["Faithful pilgrim", "Desperate supplicant", "Temple guard", "Sacred witness"])
            ]
        }
    
    def _generate_tavern_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate tavern content."""
        # Get taverns from district data first, then city data, then fallback
        taverns = []
        if district_data and 'taverns' in district_data:
            taverns = district_data['taverns']
        elif city_data and 'taverns' in city_data:
            taverns = city_data['taverns']
        
        if not taverns:
            taverns = [
                "The Rotting Corpse",
                "The Weeping Wound",
                "The Last Call",
                "The Bone and Barrel",
                "The Screaming Goat",
                "The Coffin Nail",
                "The Dying Light",
                "The Blood and Brew",
                "The Final Hour",
                "The Corpse's Rest"
            ]
        
        atmospheres = [
            "thick with smoke and despair",
            "filled with the laughter of the damned", 
            "heavy with the scent of cheap ale and cheaper lives",
            "vibrant with dark energy and darker secrets",
            "oppressive with the weight of broken dreams",
            "alive with dangerous possibilities"
        ]
        
        name = random.choice(taverns)
        atmosphere = random.choice(atmospheres)
        
        # Get encounters from district data if available
        encounters = []
        if district_data and 'encounters' in district_data:
            encounters = district_data['encounters']
        elif city_data:
            encounters = self._get_city_encounters(city_data, 'tavern', [])
        
        if encounters:
            encounter = random.choice(encounters)
        else:
            encounter = f"The tavern {random.choice(['serves drinks that grant visions', 'is a front for illegal activities', 'hosts fights to the death', 'welcomes both living and dead'])}."
        
        # Get atmosphere from district data if available
        district_atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            district_atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            district_atmospheres = self._get_city_atmospheres(city_data, [])
        
        if district_atmospheres:
            final_atmosphere = random.choice(district_atmospheres)
        else:
            final_atmosphere = atmosphere
        
        # Get random table from district data if available
        random_table = []
        if district_data and 'random_tables' in district_data and 'tavern' in district_data['random_tables']:
            random_table = district_data['random_tables']['tavern']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'tavern', self._generate_tavern_random_table)
        else:
            random_table = self._generate_tavern_random_table()
        
        return {
            'name': name,
            'description': f"A drinking establishment where {random.choice(['the lost come to forget', 'deals are made in shadows', 'songs are sung for the dead', 'strangers become enemies'])}.",
            'encounter': encounter,
            'atmosphere': final_atmosphere,
            'random_table': random_table,
            'npcs': [
                random.choice(["Grizzled barkeep", "Mysterious stranger", "Drunk prophet", "Scarred mercenary"]),
                random.choice(["Tavern wench", "Regular patron", "Traveling bard", "Local gossip"])
            ]
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
            guilds = [
                "The Corpse Collectors",
                "Brotherhood of the Final Cut",
                "The Soul Merchants",
                "Order of the Bleeding Hand",
                "The Bone Workers Union",
                "Guild of Sacred Executioners",
                "The Death Dealers",
                "Fraternity of Forgotten Names",
                "The Last Rites Society",
                "Order of Beautiful Endings"
            ]
        
        purposes = [
            "maintains the city's dark secrets",
            "controls trade in forbidden goods",
            "performs services for the dead",
            "enforces supernatural law",
            "preserves ancient traditions",
            "guards sacred knowledge"
        ]
        
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
            encounter = f"The guild {random.choice(['recruits only the desperate', 'demands terrible oaths of loyalty', 'operates from hidden chambers', 'controls vital city functions'])}."
        
        # Get atmosphere from district data if available
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"The guild hall {random.choice(['feels like a tomb', 'hums with organized menace', 'whispers with professional secrets', 'radiates quiet authority'])}."
        
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
            'description': f"A professional organization that {purpose}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'npcs': [
                random.choice(["Guild master", "Senior member", "Initiate", "Guild enforcer"]),
                random.choice(["Client", "Rival guild member", "Informant", "Potential recruit"])
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
            residences = [
                "The Mourning House",
                "Widow's Manor",
                "The Corpse Cottage",
                "House of Broken Hearts",
                "The Weeping Residence",
                "Manor of Lost Souls",
                "The Dying Estate",
                "House of Final Breaths",
                "The Sorrow Mansion",
                "Tomb Home"
            ]
        inhabitants = [
            "the ghost of its former owner",
            "a family cursed by tragedy",
            "a reclusive scholar of dark arts",
            "servants who refuse to leave their dead master",
            "multiple families who don't know about each other",
            "something that was once human"
        ]
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
            encounter = f"The residence {random.choice(['seems normal from outside but holds dark secrets', 'shifts and changes when not observed', 'exists in multiple time periods simultaneously', 'draws the lonely and desperate'])}."
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"The home {random.choice(['feels alive with memories', 'whispers with domestic tragedy', 'aches with profound loneliness', 'pulses with family secrets'])}."
        random_table = []
        if district_data and 'random_tables' in district_data and 'residence' in district_data['random_tables']:
            random_table = district_data['random_tables']['residence']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'residence', self._generate_residence_random_table)
        else:
            random_table = self._generate_residence_random_table()
        return {
            'name': name,
            'description': f"A dwelling inhabited by {inhabitant}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'treasures': [random.choice(["Family heirloom", "Hidden vault", "Personal diary", "Secret passage"])]
        }
    
    def _generate_ruins_content(self, city_data: Optional[Dict[str, Any]] = None, district_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate ruins content."""
        ruins = []
        if district_data and 'ruins' in district_data:
            ruins = district_data['ruins']
        elif city_data and 'ruins' in city_data:
            ruins = city_data['ruins']
        if not ruins:
            ruins = [
                "The Fallen Spire",
                "Ruins of the Old Palace",
                "The Collapsed Cathedral",
                "Broken Tower of Memory",
                "The Shattered Archive",
                "Ruins of the First Church",
                "The Fallen Monument",
                "Wreckage of the Golden Age",
                "The Crumbling Fortress",
                "Bones of Better Times"
            ]
        histories = [
            "destroyed during the great catastrophe",
            "abandoned when its purpose was forgotten",
            "collapsed under the weight of accumulated sin",
            "shattered by divine wrath",
            "consumed by otherworldly forces",
            "left empty when hope finally died"
        ]
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
            encounter = f"The ruins {random.choice(['are haunted by echoes of the past', 'hide secrets in their depths', 'attract treasure hunters and scholars', 'serve as lairs for dangerous creatures'])}."
        atmospheres = []
        if district_data and 'atmosphere_modifiers' in district_data:
            atmospheres = district_data['atmosphere_modifiers']
        elif city_data:
            atmospheres = self._get_city_atmospheres(city_data, [])
        if atmospheres:
            atmosphere = random.choice(atmospheres)
        else:
            atmosphere = f"The broken stones {random.choice(['whisper with forgotten glory', 'ache with profound loss', 'pulse with residual power', 'weep for better days'])}."
        random_table = []
        if district_data and 'random_tables' in district_data and 'ruins' in district_data['random_tables']:
            random_table = district_data['random_tables']['ruins']
        elif city_data:
            random_table = self._get_city_random_table(city_data, 'ruins', self._generate_ruins_random_table)
        else:
            random_table = self._generate_ruins_random_table()
        return {
            'name': name,
            'description': f"Ancient ruins {history}.",
            'encounter': encounter,
            'atmosphere': atmosphere,
            'random_table': random_table,
            'treasures': [
                random.choice(["Ancient artifact", "Forgotten knowledge", "Hidden treasure", "Lost relic"]),
                random.choice(["Historical document", "Valuable material", "Cursed item", "Sacred object"])
            ]
        }
    
    def _add_position_modifiers(self, content: Dict[str, Any], row: int, col: int) -> Dict[str, Any]:
        """Add position-specific modifiers to content."""
        # Edge positions (outer ring)
        if row == 0 or row == 4 or col == 0 or col == 4:
            content['position_type'] = 'edge'
            content['notable_features'].append("At the city's edge, less developed")
            
        # Corner positions
        elif (row == 0 and col == 0) or (row == 0 and col == 4) or (row == 4 and col == 0) or (row == 4 and col == 4):
            content['position_type'] = 'corner'
            content['notable_features'].append("At a corner, often fortified")
            
        # Center position
        elif row == 2 and col == 2:
            content['position_type'] = 'center'
            content['notable_features'].append("At the city's heart, most important")
            
        # Inner positions
        else:
            content['position_type'] = 'inner'
            content['notable_features'].append("Within the city proper, well developed")
        
        return content
    
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
            "5-6: Rooms appear and disappear mysteriously",
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
        os.makedirs(self.output_directory, exist_ok=True)
        filename = os.path.join(self.output_directory, f"{overlay_name}_overlay.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(overlay_data, f, indent=2, ensure_ascii=False)
    
    def load_overlay_data(self, overlay_name: str) -> Optional[Dict[str, Any]]:
        """Load overlay data from cache or file."""
        # Check cache first
        if overlay_name in self.overlays_cache:
            return self.overlays_cache[overlay_name]
        
        # Try to load from file
        filename = os.path.join(self.output_directory, f"{overlay_name}_overlay.json")
        if os.path.exists(filename):
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
                lines.append(f"Type: {content.get('type', 'Unknown').title()}")
                lines.append(f"Description: {content.get('description', 'No description')}")
                
                if content.get('encounter'):
                    lines.append(f"Encounter: {content.get('encounter')}")
                
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

# Global instance
city_overlay_analyzer = CityOverlayAnalyzer()