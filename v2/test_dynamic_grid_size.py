#!/usr/bin/env python3
"""
Test script to verify dynamic grid sizing from image dimensions.
"""

import sys
from pathlib import Path

# Add v2/backend to path
backend_path = Path(__file__).parent / "v2" / "backend"
sys.path.insert(0, str(backend_path))

from backend.terrain_system import TerrainSystem
from backend.utils.image_size_calculator import calculate_grid_size_from_image, calculate_ideal_image_size

def test_dynamic_sizing():
    """Test that TerrainSystem calculates grid size from image."""
    
    # Test with a known image size - try both .png and .jpg
    data_dir = Path(__file__).parent.parent / "data"
    test_image_path = data_dir / "mork_borg_official_map.png"
    if not test_image_path.exists():
        test_image_path = data_dir / "_mork_borg_official_map.jpg"
    
    if not test_image_path.exists():
        print(f"⚠️  Test image not found in {data_dir}")
        print("   Available files:")
        for f in data_dir.glob("*.png"):
            print(f"     {f.name}")
        for f in data_dir.glob("*.jpg"):
            print(f"     {f.name}")
        print("   Skipping dynamic sizing test")
        return
    
    # Calculate what the ideal grid should be for this image
    from PIL import Image
    img = Image.open(test_image_path)
    img_width, img_height = img.size
    img.close()
    
    print(f"Test image: {img_width} x {img_height} pixels")
    
    # Calculate expected grid size (targeting ~1800 hexes like default 30x60)
    expected_width, expected_height = calculate_grid_size_from_image(
        img_width, img_height, target_total_hexes=1800
    )
    print(f"Expected grid: {expected_width} x {expected_height} hexes")
    
    # Create TerrainSystem with auto-sizing enabled
    terrain = TerrainSystem(
        map_width=30,  # This will be overridden
        map_height=60,  # This will be overridden
        image_path=str(test_image_path),
        auto_size_from_image=True,
        debug=True
    )
    
    actual_width, actual_height = terrain.get_map_dimensions()
    print(f"Actual grid: {actual_width} x {actual_height} hexes")
    
    # Verify they match
    if actual_width == expected_width and actual_height == expected_height:
        print("✅ Dynamic sizing works correctly!")
    else:
        print(f"⚠️  Mismatch: expected {expected_width}x{expected_height}, got {actual_width}x{actual_height}")
    
    # Verify the reverse: calculate ideal image size for the calculated grid
    ideal_w, ideal_h = calculate_ideal_image_size(actual_width, actual_height)
    ideal_aspect = ideal_w / ideal_h
    img_aspect = img_width / img_height
    aspect_diff = abs(ideal_aspect - img_aspect) / img_aspect
    
    print(f"\nAspect ratio verification:")
    print(f"  Image aspect: {img_aspect:.4f}")
    print(f"  Ideal aspect: {ideal_aspect:.4f}")
    print(f"  Difference: {aspect_diff * 100:.2f}%")
    
    if aspect_diff < 0.01:  # Less than 1% difference
        print("✅ Aspect ratios match!")
    else:
        print("⚠️  Aspect ratio mismatch")

if __name__ == "__main__":
    test_dynamic_sizing()
