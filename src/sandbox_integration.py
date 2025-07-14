#!/usr/bin/env python3
"""
Sandbox Generator Integration Module
Integrates the Sandbox Generator with the existing Hexy generation engine.
"""

import random
from typing import Dict, List, Optional, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generation_engine import GenerationEngine
from sandbox_generator import SandboxGenerator, sandbox_generator
from terrain_system import terrain_system
from database_manager import database_manager

class SandboxIntegration:
    """Integrates Sandbox Generator with existing Hexy systems."""
    
    def __init__(self):
        """Initialize the integration layer."""
        self.generation_engine = GenerationEngine()
        self.sandbox_generator = sandbox_generator
        self.terrain_system = terrain_system
        self.db_manager = database_manager
        
        # Enhanced generation rules that include sandbox elements
        self.enhanced_rules = {
            **self.generation_engine.default_rules,
            'sandbox_enabled': True,
            'faction_influence': True,
            'detailed_settlements': True,
            'castle_generation': True,
            'conflict_generation': True
        }
    
    def generate_enhanced_hex_content(self, hex_code: str, terrain_type: str, language: str = 'en') -> Dict[str, Any]:
        """Generate enhanced hex content combining existing and sandbox systems."""
        # Get base content from existing generation engine
        base_content = self._get_base_content(hex_code, terrain_type, language)
        
        # Get sandbox enhancements
        sandbox_content = self.sandbox_generator.generate_enhanced_hex_content(
            hex_code, terrain_type, language
        )
        
        # Combine content intelligently
        enhanced_content = self._combine_content(base_content, sandbox_content)
        
        return enhanced_content
    
    def _get_base_content(self, hex_code: str, terrain_type: str, language: str) -> Dict[str, Any]:
        """Get base content from existing generation engine."""
        # Determine content type using existing logic
        content_type = self.generation_engine.determine_content_type(hex_code, terrain_type)
        
        # Generate base content
        context = {
            'hex_code': hex_code,
            'terrain': terrain_type,
            'language': language
        }
        
        base_content = self.generation_engine.generate_content(content_type, context)
        
        return {
            'hex_code': hex_code,
            'terrain': terrain_type,
            'content_type': content_type,
            'base_content': base_content,
            'language': language
        }
    
    def _combine_content(self, base_content: Dict[str, Any], sandbox_content: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently combine base and sandbox content."""
        combined = {
            'hex_code': base_content['hex_code'],
            'terrain': base_content['terrain'],
            'language': base_content['language'],
            'content_type': base_content['content_type'],
            
            # Base content (existing system)
            'base_content': base_content['base_content'],
            
            # Sandbox enhancements
            'sandbox_data': sandbox_content['sandbox_data'],
            'terrain_info': sandbox_content['terrain_info'],
            
            # Combined summary
            'summary': self._generate_combined_summary(base_content, sandbox_content),
            
            # Enhanced encounter description
            'enhanced_encounter': self._generate_enhanced_encounter(base_content, sandbox_content)
        }
        
        return combined
    
    def _generate_combined_summary(self, base_content: Dict[str, Any], sandbox_content: Dict[str, Any]) -> str:
        """Generate a combined summary of the hex."""
        summary_parts = []
        
        # Add base content summary
        if 'base_content' in base_content and 'encounter' in base_content['base_content']:
            summary_parts.append(base_content['base_content']['encounter'])
        
        # Add sandbox elements
        sandbox_data = sandbox_content['sandbox_data']
        
        # Add settlements
        if sandbox_data.get('settlements'):
            for settlement in sandbox_data['settlements']:
                summary_parts.append(f"🏘️ {settlement['name']} ({settlement['type']})")
        
        # Add castles
        if sandbox_data.get('castles'):
            for castle in sandbox_data['castles']:
                summary_parts.append(f"🏰 {castle['name']} ({castle['condition']})")
        
        # Add factions
        if sandbox_data.get('factions'):
            faction_names = [f['name'] for f in sandbox_data['factions']]
            summary_parts.append(f"⚔️ Factions: {', '.join(faction_names)}")
        
        # Add conflicts
        if sandbox_data.get('conflicts'):
            conflict_count = len(sandbox_data['conflicts'])
            summary_parts.append(f"🔥 {conflict_count} active conflicts")
        
        return " | ".join(summary_parts) if summary_parts else "Empty hex"
    
    def _generate_enhanced_encounter(self, base_content: Dict[str, Any], sandbox_content: Dict[str, Any]) -> str:
        """Generate an enhanced encounter description."""
        encounter_parts = []
        
        # Start with base encounter
        if 'base_content' in base_content and 'encounter' in base_content['base_content']:
            encounter_parts.append(base_content['base_content']['encounter'])
        
        # Add sandbox context
        sandbox_data = sandbox_content['sandbox_data']
        
        # Add faction context
        if sandbox_data.get('factions'):
            faction = sandbox_data['factions'][0]  # Primary faction
            encounter_parts.append(f"Under {faction['name']} influence")
        
        # Add conflict context
        if sandbox_data.get('conflicts'):
            conflict = sandbox_data['conflicts'][0]  # Primary conflict
            encounter_parts.append(f"Tension: {conflict['type']}")
        
        # Add economic context
        if sandbox_data.get('economic_data', {}).get('trade_routes'):
            encounter_parts.append("Trade route present")
        
        return " | ".join(encounter_parts)
    
    def generate_enhanced_region(self, center_hex: str, radius: int = 9) -> Dict[str, Any]:
        """Generate an enhanced region with both base and sandbox content."""
        # Get sandbox region data
        sandbox_region = self.sandbox_generator.generate_region(center_hex, radius)
        
        # Generate base content for each hex
        enhanced_hexes = {}
        for hex_code in sandbox_region['hexes']:
            terrain = self.terrain_system.get_terrain_for_hex(hex_code)
            enhanced_content = self.generate_enhanced_hex_content(hex_code, terrain)
            enhanced_hexes[hex_code] = enhanced_content
        
        # Combine into region data
        enhanced_region = {
            'center_hex': center_hex,
            'radius': radius,
            'hexes': enhanced_hexes,
            'sandbox_data': sandbox_region,
            'summary': self._generate_region_summary(enhanced_hexes, sandbox_region)
        }
        
        return enhanced_region
    
    def _generate_region_summary(self, enhanced_hexes: Dict[str, Any], sandbox_region: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the enhanced region."""
        # Count content types
        content_counts = {}
        terrain_counts = {}
        faction_count = len(sandbox_region.get('factions', []))
        settlement_count = len(sandbox_region.get('settlements', []))
        castle_count = len(sandbox_region.get('castles', []))
        conflict_count = len(sandbox_region.get('conflicts', []))
        
        for hex_code, hex_data in enhanced_hexes.items():
            content_type = hex_data.get('content_type', 'unknown')
            terrain = hex_data.get('terrain', 'unknown')
            
            content_counts[content_type] = content_counts.get(content_type, 0) + 1
            terrain_counts[terrain] = terrain_counts.get(terrain, 0) + 1
        
        return {
            'total_hexes': len(enhanced_hexes),
            'content_distribution': content_counts,
            'terrain_distribution': terrain_counts,
            'faction_count': faction_count,
            'settlement_count': settlement_count,
            'castle_count': castle_count,
            'conflict_count': conflict_count,
            'notable_features': self._identify_notable_features(enhanced_hexes, sandbox_region)
        }
    
    def _identify_notable_features(self, enhanced_hexes: Dict[str, Any], sandbox_region: Dict[str, Any]) -> List[str]:
        """Identify notable features in the region."""
        features = []
        
        # Check for major settlements
        settlements = sandbox_region.get('settlements', [])
        if settlements:
            largest_settlement = max(settlements, key=lambda s: s.get('population', 0))
            features.append(f"Major settlement: {largest_settlement['name']}")
        
        # Check for castles
        castles = sandbox_region.get('castles', [])
        if castles:
            features.append(f"Castles: {len(castles)} fortifications")
        
        # Check for major conflicts
        conflicts = sandbox_region.get('conflicts', [])
        if conflicts:
            high_intensity_conflicts = [c for c in conflicts if c.get('intensity', 0) >= 4]
            if high_intensity_conflicts:
                features.append(f"High-intensity conflicts: {len(high_intensity_conflicts)}")
        
        # Check for unique terrain
        terrain_counts = {}
        for hex_data in enhanced_hexes.values():
            terrain = hex_data.get('terrain', 'unknown')
            terrain_counts[terrain] = terrain_counts.get(terrain, 0) + 1
        
        rare_terrains = [t for t, count in terrain_counts.items() if count <= 2]
        if rare_terrains:
            features.append(f"Rare terrain: {', '.join(rare_terrains)}")
        
        return features
    
    def get_enhanced_api_data(self, hex_code: str, language: str = 'en') -> Dict[str, Any]:
        """Get enhanced API data for a hex."""
        terrain = self.terrain_system.get_terrain_for_hex(hex_code)
        enhanced_content = self.generate_enhanced_hex_content(hex_code, terrain, language)
        
        # Format for API response
        api_data = {
            'hex_code': hex_code,
            'terrain': terrain,
            'content': enhanced_content['base_content'],
            'sandbox': {
                'factions': enhanced_content['sandbox_data']['factions'],
                'settlements': enhanced_content['sandbox_data']['settlements'],
                'castles': enhanced_content['sandbox_data']['castles'],
                'conflicts': enhanced_content['sandbox_data']['conflicts'],
                'economic_data': enhanced_content['sandbox_data']['economic_data'],
                'plot_hooks': enhanced_content['sandbox_data']['plot_hooks']
            },
            'summary': enhanced_content['summary'],
            'enhanced_encounter': enhanced_content['enhanced_encounter']
        }
        
        return api_data
    
    def get_region_api_data(self, center_hex: str, radius: int = 9) -> Dict[str, Any]:
        """Get enhanced region data for API."""
        enhanced_region = self.generate_enhanced_region(center_hex, radius)
        
        # Format for API response
        api_data = {
            'center_hex': center_hex,
            'radius': radius,
            'summary': enhanced_region['summary'],
            'hexes': {},
            'factions': enhanced_region['sandbox_data']['factions'],
            'settlements': enhanced_region['sandbox_data']['settlements'],
            'castles': enhanced_region['sandbox_data']['castles'],
            'conflicts': enhanced_region['sandbox_data']['conflicts']
        }
        
        # Add hex data (simplified for API)
        for hex_code, hex_data in enhanced_region['hexes'].items():
            api_data['hexes'][hex_code] = {
                'terrain': hex_data['terrain'],
                'content_type': hex_data['content_type'],
                'summary': hex_data['summary'],
                'factions': len(hex_data['sandbox_data']['factions']),
                'settlements': len(hex_data['sandbox_data']['settlements']),
                'castles': len(hex_data['sandbox_data']['castles'])
            }
        
        return api_data

# Create global instance
sandbox_integration = SandboxIntegration() 