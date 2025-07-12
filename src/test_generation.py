#!/usr/bin/env python3
"""
Test script to debug content generation issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_hex_generator():
    """Test the new unified hex generator"""
    print("🧪 Testing unified hex generator...")
    
    try:
        from hex_generator import HexGenerator
        print("✅ Successfully imported HexGenerator")
        
        # Test generation
        generator = HexGenerator('en')
        hex_data = generator.generate_hex_content('0601', 'forest')
        print(f"✅ Generated content for hex 0601:")
        print(f"   Encounter: {hex_data.get('encounter', 'None')}")
        print(f"   Terrain: {hex_data.get('terrain', 'None')}")
        return True
        
    except Exception as e:
        print(f"❌ Error in hex generator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_terrain_system():
    """Test the terrain system"""
    print("\n🧪 Testing terrain system...")
    
    try:
        from terrain_system import terrain_system
        print("✅ Successfully imported terrain_system")
        
        # Test terrain detection
        terrain = terrain_system.get_terrain_for_hex('0601')
        print(f"✅ Detected terrain for hex 0601: {terrain}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in terrain system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_map_generator():
    """Test the map generator"""
    print("\n🧪 Testing map generator...")
    
    try:
        from map_generator import map_generator
        print("✅ Successfully imported map_generator")
        
        # Test map generation
        result = map_generator.generate_map('en', ['0601', '0602'])
        print(f"✅ Generated map with {len(result)} hexes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in map generator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lore_database():
    """Test the lore database"""
    print("\n🧪 Testing lore database...")
    
    try:
        from mork_borg_lore_database import MorkBorgLoreDatabase
        print("✅ Successfully imported MorkBorgLoreDatabase")
        
        # Test lore database
        lore_db = MorkBorgLoreDatabase()
        hardcoded = lore_db.get_hardcoded_hex('0601')
        print(f"✅ Retrieved hardcoded data for hex 0601: {hardcoded is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in lore database: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_flow():
    """Test the complete content generation flow"""
    print("\n🧪 Testing complete content generation flow...")
    
    try:
        from hex_generator import HexGenerator
        from terrain_system import terrain_system
        from mork_borg_lore_database import MorkBorgLoreDatabase
        
        # Initialize components
        generator = HexGenerator('en')
        lore_db = MorkBorgLoreDatabase()
        
        hex_code = "0601"
        
        # Check for hardcoded lore locations
        hardcoded = lore_db.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('locked', False):
            hex_data = generator.generate_hex_content(hex_code, lore_db=lore_db)
            print(f"✅ Generated lore-based content for {hex_code}")
        else:
            # Use terrain detection
            terrain = terrain_system.get_terrain_for_hex(hex_code, lore_db)
            hex_data = generator.generate_hex_content(hex_code, terrain, lore_db)
            print(f"✅ Generated terrain-based content for {hex_code} (terrain: {terrain})")
        
        print(f"   Encounter: {hex_data.get('encounter', 'None')}")
        print(f"   Terrain: {hex_data.get('terrain', 'None')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in complete flow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 Content Generation Debug Test")
    print("=" * 50)
    
    success1 = test_hex_generator()
    success2 = test_terrain_system()
    success3 = test_map_generator()
    success4 = test_lore_database()
    success5 = test_complete_flow()
    
    print("\n📊 Test Results:")
    print(f"Hex generator: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Terrain system: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Map generator: {'✅ PASS' if success3 else '❌ FAIL'}")
    print(f"Lore database: {'✅ PASS' if success4 else '❌ FAIL'}")
    print(f"Complete flow: {'✅ PASS' if success5 else '❌ FAIL'}")
    
    if all([success1, success2, success3, success4, success5]):
        print("\n🎉 All tests passed! Content generation should work.")
    else:
        print("\n💥 Some tests failed. Check errors above.") 