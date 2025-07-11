#!/usr/bin/env python3
"""
Test script to debug content generation issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_direct_generation():
    """Test content generation directly"""
    print("🧪 Testing direct content generation...")
    
    try:
        from dying_lands_generator import generate_hex_content
        print("✅ Successfully imported generate_hex_content from dying_lands_generator")
        
        # Test generation
        hex_data = generate_hex_content('0601', 'forest')
        print(f"✅ Generated content for hex 0601:")
        print(f"   Encounter: {hex_data.get('encounter', 'None')}")
        print(f"   Terrain: {hex_data.get('terrain', 'None')}")
        return True
        
    except Exception as e:
        print(f"❌ Error in direct generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ascii_viewer_imports():
    """Test the imports used in ascii_map_viewer"""
    print("\n🧪 Testing ascii_map_viewer imports...")
    
    try:
        from full_map_generator import generate_lore_hex_content
        print("✅ Successfully imported generate_lore_hex_content from full_map_generator")
        
        from dying_lands_generator import generate_hex_content, write_hex_file
        print("✅ Successfully imported generate_hex_content and write_hex_file from dying_lands_generator")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in ascii_viewer imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_hex_flow():
    """Test the complete single hex generation flow"""
    print("\n🧪 Testing complete single hex flow...")
    
    try:
        # Import what ascii_map_viewer needs
        from full_map_generator import generate_lore_hex_content
        from dying_lands_generator import generate_hex_content, write_hex_file, detect_terrain_from_hex
        from mork_borg_lore_database import MorkBorgLoreDatabase
        
        # Initialize lore database
        lore_db = MorkBorgLoreDatabase()
        
        hex_code = "0601"
        
        # Check for hardcoded lore locations
        hardcoded = lore_db.get_hardcoded_hex(hex_code)
        if hardcoded and hardcoded.get('locked', False):
            hex_data = generate_lore_hex_content(hex_code, hardcoded, 'en')
            print(f"✅ Generated lore-based content for {hex_code}")
        else:
            # Use the terrain detection from dying_lands_generator
            terrain = detect_terrain_from_hex(hex_code)
            hex_data = generate_hex_content(hex_code, terrain)
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
    
    success1 = test_direct_generation()
    success2 = test_ascii_viewer_imports() 
    success3 = test_single_hex_flow()
    
    print("\n📊 Test Results:")
    print(f"Direct generation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"ASCII viewer imports: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Complete flow: {'✅ PASS' if success3 else '❌ FAIL'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 All tests passed! Content generation should work.")
    else:
        print("\n💥 Some tests failed. Check errors above.") 