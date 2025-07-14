#!/usr/bin/env python3
"""
Test script for Sandbox Generator Integration
Demonstrates the enhanced hex generation with faction systems, settlements, and castles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sandbox_generator import sandbox_generator
from sandbox_integration import sandbox_integration
from terrain_system import terrain_system
import json

def test_sandbox_generator():
    """Test the sandbox generator with various hex types."""
    print("🧪 Testing Sandbox Generator Integration")
    print("=" * 50)
    
    # Test hexes in different terrain types
    test_hexes = [
        ('0808', 'forest'),    # Central forest
        ('1505', 'mountain'),  # Eastern mountains
        ('0505', 'coast'),     # Western coast
        ('1010', 'plains'),    # Central plains
        ('0818', 'swamp'),     # Southern swamp
    ]
    
    for hex_code, expected_terrain in test_hexes:
        print(f"\n📍 Testing Hex {hex_code} ({expected_terrain})")
        print("-" * 30)
        
        # Get actual terrain from system
        actual_terrain = terrain_system.get_terrain_for_hex(hex_code)
        print(f"Terrain: {actual_terrain} (expected: {expected_terrain})")
        
        # Generate enhanced content
        enhanced_content = sandbox_integration.generate_enhanced_hex_content(
            hex_code, actual_terrain, 'en'
        )
        
        # Display results
        print(f"Content Type: {enhanced_content['content_type']}")
        print(f"Summary: {enhanced_content['summary']}")
        
        # Show sandbox data
        sandbox_data = enhanced_content['sandbox_data']
        
        if sandbox_data['factions']:
            print(f"Factions: {len(sandbox_data['factions'])} present")
            for faction in sandbox_data['factions']:
                print(f"  - {faction['name']} ({faction['type']}) - Power: {faction['power_level']}")
        
        if sandbox_data['settlements']:
            print(f"Settlements: {len(sandbox_data['settlements'])} present")
            for settlement in sandbox_data['settlements']:
                print(f"  - {settlement['name']} ({settlement['type']}) - Pop: {settlement['population']}")
        
        if sandbox_data['castles']:
            print(f"Castles: {len(sandbox_data['castles'])} present")
            for castle in sandbox_data['castles']:
                print(f"  - {castle['name']} - {castle['condition']}")
        
        if sandbox_data['conflicts']:
            print(f"Conflicts: {len(sandbox_data['conflicts'])} active")
            for conflict in sandbox_data['conflicts']:
                print(f"  - {conflict['type']} between {', '.join(conflict['factions'])}")
        
        if sandbox_data['plot_hooks']:
            print(f"Plot Hooks: {len(sandbox_data['plot_hooks'])} available")
            for hook in sandbox_data['plot_hooks'][:2]:  # Show first 2
                print(f"  - {hook}")

def test_region_generation():
    """Test region generation around a center hex."""
    print("\n\n🗺️ Testing Region Generation")
    print("=" * 50)
    
    center_hex = '1010'  # Central plains
    radius = 3
    
    print(f"Generating region around hex {center_hex} (radius {radius})")
    
    # Generate enhanced region
    enhanced_region = sandbox_integration.generate_enhanced_region(center_hex, radius)
    
    # Display region summary
    summary = enhanced_region['summary']
    print(f"\nRegion Summary:")
    print(f"Total Hexes: {summary['total_hexes']}")
    print(f"Factions: {summary['faction_count']}")
    print(f"Settlements: {summary['settlement_count']}")
    print(f"Castles: {summary['castle_count']}")
    print(f"Conflicts: {summary['conflict_count']}")
    
    print(f"\nTerrain Distribution:")
    for terrain, count in summary['terrain_distribution'].items():
        print(f"  {terrain}: {count}")
    
    print(f"\nContent Distribution:")
    for content_type, count in summary['content_distribution'].items():
        print(f"  {content_type}: {count}")
    
    print(f"\nNotable Features:")
    for feature in summary['notable_features']:
        print(f"  - {feature}")

def test_api_data():
    """Test API data generation."""
    print("\n\n🌐 Testing API Data Generation")
    print("=" * 50)
    
    hex_code = '0808'  # Forest hex
    terrain = terrain_system.get_terrain_for_hex(hex_code)
    
    # Get API data
    api_data = sandbox_integration.get_enhanced_api_data(hex_code, 'en')
    
    print(f"Hex: {api_data['hex_code']}")
    print(f"Terrain: {api_data['terrain']}")
    print(f"Summary: {api_data['summary']}")
    print(f"Enhanced Encounter: {api_data['enhanced_encounter']}")
    
    print(f"\nSandbox Data:")
    print(f"  Factions: {len(api_data['sandbox']['factions'])}")
    print(f"  Settlements: {len(api_data['sandbox']['settlements'])}")
    print(f"  Castles: {len(api_data['sandbox']['castles'])}")
    print(f"  Conflicts: {len(api_data['sandbox']['conflicts'])}")
    print(f"  Plot Hooks: {len(api_data['sandbox']['plot_hooks'])}")

def test_biome_modifiers():
    """Test biome-specific modifiers."""
    print("\n\n🌍 Testing Biome Modifiers")
    print("=" * 50)
    
    terrain_types = ['mountain', 'forest', 'coast', 'plains', 'swamp', 'desert']
    
    for terrain in terrain_types:
        print(f"\n{terrain.upper()}:")
        modifiers = sandbox_generator.biome_modifiers.get(terrain, {})
        
        print(f"  Settlement Types: {modifiers.get('settlement_types', [])}")
        print(f"  Faction Types: {modifiers.get('faction_types', [])}")
        print(f"  Population Modifier: {modifiers.get('population_modifier', 0)}")

def test_faction_system():
    """Test faction generation and relationships."""
    print("\n\n⚔️ Testing Faction System")
    print("=" * 50)
    
    # Generate factions in different terrain types
    test_terrains = ['mountain', 'forest', 'coast']
    
    for terrain in test_terrains:
        print(f"\n{terrain.upper()} Terrain:")
        
        # Create multiple factions
        factions = []
        for i in range(3):
            hex_code = f"10{i+10}"
            faction = sandbox_generator._create_faction(hex_code, terrain)
            if faction:
                factions.append(faction)
                print(f"  Created: {faction['name']} ({faction['type']})")
        
        # Test faction relationships
        if len(factions) >= 2:
            conflict = sandbox_generator._create_conflict(factions[0], factions[1])
            if conflict:
                print(f"  Conflict: {conflict['type']} between {conflict['factions'][0]} and {conflict['factions'][1]}")

def main():
    """Run all tests."""
    print("🚀 Starting Sandbox Generator Integration Tests")
    print("=" * 60)
    
    try:
        test_sandbox_generator()
        test_region_generation()
        test_api_data()
        test_biome_modifiers()
        test_faction_system()
        
        print("\n\n✅ All tests completed successfully!")
        print("\n🎯 Sandbox Generator Integration Features:")
        print("  - Biome-aware faction generation")
        print("  - Detailed settlement creation")
        print("  - Castle and fortification system")
        print("  - Faction conflict generation")
        print("  - Economic and political dynamics")
        print("  - Plot hook generation")
        print("  - Integration with existing terrain system")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 