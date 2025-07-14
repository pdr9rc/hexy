#!/usr/bin/env python3
"""
Test script for sandbox integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/src')

from generation_engine import GenerationEngine
from main_map_generator import MainMapGenerator

def test_sandbox_integration():
    """Test the sandbox integration with the generation engine."""
    print("🧪 Testing Sandbox Integration")
    print("=" * 50)
    
    # Initialize the generation engine
    print("1. Initializing Generation Engine...")
    engine = GenerationEngine()
    print("✅ Generation Engine initialized")
    
    # Test enhanced content generation
    print("\n2. Testing Enhanced Content Generation...")
    test_hex = "1508"
    test_terrain = "forest"
    test_language = "en"
    
    context = {
        'hex_code': test_hex,
        'terrain': test_terrain,
        'language': test_language
    }
    
    # Test different content types
    content_types = ['settlement', 'dungeon', 'beast', 'npc']
    
    for content_type in content_types:
        print(f"\n   Testing {content_type} generation...")
        try:
            content = engine.generate_content(content_type, context)
            
            print(f"   ✅ {content_type} generated successfully")
            print(f"   📍 Hex: {content.get('hex_code', 'N/A')}")
            print(f"   🏔️ Terrain: {content.get('terrain', 'N/A')}")
            print(f"   🎯 Content Type: {content.get('content_type', 'N/A')}")
            
            # Check for sandbox data
            if 'sandbox_data' in content:
                sandbox = content['sandbox_data']
                print(f"   🏰 Sandbox Data:")
                print(f"      - Factions: {len(sandbox.get('factions', []))}")
                print(f"      - Castles: {len(sandbox.get('castles', []))}")
                print(f"      - Conflicts: {len(sandbox.get('conflicts', []))}")
                print(f"      - Economic Data: {'Yes' if sandbox.get('economic_data') else 'No'}")
            
            # Check for enhanced encounter
            if 'enhanced_encounter' in content:
                print(f"   🎭 Enhanced Encounter: {content['enhanced_encounter'][:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error generating {content_type}: {e}")
    
    # Test main map generator integration
    print("\n3. Testing Main Map Generator Integration...")
    try:
        generator = MainMapGenerator({'language': 'en'})
        print("✅ Main Map Generator initialized")
        
        # Test single hex generation
        print("\n   Testing single hex generation...")
        hex_data = generator.generate_hex_content(test_hex, test_terrain)
        
        print(f"   ✅ Hex {test_hex} generated successfully")
        print(f"   📍 Content Type: {hex_data.get('content_type', 'N/A')}")
        
        if 'sandbox_data' in hex_data:
            sandbox = hex_data['sandbox_data']
            print(f"   🏰 Sandbox Integration:")
            print(f"      - Factions: {len(sandbox.get('factions', []))}")
            print(f"      - Castles: {len(sandbox.get('castles', []))}")
            print(f"      - Conflicts: {len(sandbox.get('conflicts', []))}")
        
    except Exception as e:
        print(f"   ❌ Error with Main Map Generator: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Sandbox Integration Test Complete!")

if __name__ == "__main__":
    test_sandbox_integration() 