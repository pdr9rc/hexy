#!/usr/bin/env python3
"""
Utility to calculate ideal image dimensions for a given hex grid size,
and vice versa: calculate grid dimensions from image size.
"""

from typing import Tuple, Optional


def calculate_ideal_image_size(map_width: int, map_height: int) -> Tuple[int, int]:
    """
    Calculate the ideal image dimensions for a hex grid.
    
    Uses the same formulas as TerrainSystem to ensure perfect aspect ratio matching.
    This prevents letterboxing/cropping when using the image for terrain analysis.
    
    Args:
        map_width: Number of hexes horizontally
        map_height: Number of hexes vertically
        
    Returns:
        Tuple of (ideal_image_width, ideal_image_height) in pixels
    """
    # Hex dimensions (flat-topped hexes, matching frontend CSS)
    w = 40.0  # px, from --hex-width-base
    h = 35.0  # px, from --hex-height-base
    
    # Calculate grid pixel dimensions
    grid_px_width = w * (map_width + 0.5)
    grid_px_height = h * (map_height * 0.75 + 0.25)
    
    # Round to nearest integer
    ideal_width = int(round(grid_px_width))
    ideal_height = int(round(grid_px_height))
    
    return ideal_width, ideal_height


def calculate_aspect_ratio(map_width: int, map_height: int) -> float:
    """
    Calculate the aspect ratio for a given grid size.
    
    Args:
        map_width: Number of hexes horizontally
        map_height: Number of hexes vertically
        
    Returns:
        Aspect ratio (width / height)
    """
    ideal_width, ideal_height = calculate_ideal_image_size(map_width, map_height)
    return ideal_width / ideal_height


def calculate_grid_size_from_image(
    img_width: int, 
    img_height: int, 
    target_width: Optional[int] = None,
    target_total_hexes: Optional[int] = None
) -> Tuple[int, int]:
    """
    Calculate ideal grid dimensions (map_width, map_height) from image dimensions.
    
    This reverses the calculation: given an image size, determine what grid
    dimensions would best fit it without letterboxing/cropping.
    
    Args:
        img_width: Image width in pixels
        img_height: Image height in pixels
        target_width: Optional target width in hexes. If provided, calculates height to match.
        target_total_hexes: Optional target total hex count. If provided, calculates both dimensions
                          to match aspect ratio while approximating this total.
        
    Returns:
        Tuple of (map_width, map_height) in hexes
        
    Examples:
        # Calculate from image with target width of 30
        width, height = calculate_grid_size_from_image(1220, 1584, target_width=30)
        # Returns: (30, 60)
        
        # Calculate from image targeting ~1800 total hexes
        width, height = calculate_grid_size_from_image(1220, 1584, target_total_hexes=1800)
        # Returns dimensions that match aspect ratio and approximate 1800 hexes
    """
    # Hex dimensions (flat-topped hexes, matching frontend CSS)
    w = 40.0  # px, from --hex-width-base
    h = 35.0  # px, from --hex-height-base
    
    img_aspect = img_width / img_height
    
    if target_width is not None:
        # Calculate height to match aspect ratio given a target width
        # (w * (map_width + 0.5)) / (h * (map_height * 0.75 + 0.25)) = img_aspect
        # Solving for map_height:
        # map_height = ((w * (map_width + 0.5)) / (img_aspect * h) - 0.25) / 0.75
        map_width = target_width
        map_height = int(round(((w * (map_width + 0.5)) / (img_aspect * h) - 0.25) / 0.75))
    elif target_total_hexes is not None:
        # Calculate both dimensions to match aspect ratio while approximating target total
        # We have: map_width * map_height ≈ target_total_hexes
        # And: (w * (map_width + 0.5)) / (h * (map_height * 0.75 + 0.25)) = img_aspect
        # 
        # Rearranging the aspect ratio equation:
        # (map_width + 0.5) / (map_height * 0.75 + 0.25) = img_aspect * h / w
        # Let k = img_aspect * h / w
        # Then: map_width + 0.5 = k * (map_height * 0.75 + 0.25)
        #       map_width = k * (map_height * 0.75 + 0.25) - 0.5
        #
        # And: map_width * map_height ≈ target_total_hexes
        # So: (k * (map_height * 0.75 + 0.25) - 0.5) * map_height ≈ target_total_hexes
        # This is a quadratic: 0.75*k*map_height^2 + (0.25*k - 0.5)*map_height - target_total_hexes ≈ 0
        
        k = img_aspect * h / w
        # Solve quadratic: 0.75*k*x^2 + (0.25*k - 0.5)*x - target_total_hexes = 0
        a = 0.75 * k
        b = 0.25 * k - 0.5
        c = -target_total_hexes
        
        # Quadratic formula: x = (-b ± sqrt(b^2 - 4ac)) / 2a
        discriminant = b * b - 4 * a * c
        if discriminant >= 0:
            map_height = int(round((-b + (discriminant ** 0.5)) / (2 * a)))
            map_height = max(10, map_height)
            map_width = int(round(k * (map_height * 0.75 + 0.25) - 0.5))
            map_width = max(10, map_width)
        else:
            # Fallback to simpler approximation
            map_width = int(round((target_total_hexes * img_aspect * h / (w * 0.75)) ** 0.5))
            map_width = max(10, map_width)
            map_height = int(round(((w * (map_width + 0.5)) / (img_aspect * h) - 0.25) / 0.75))
            map_height = max(10, map_height)
        
        # Fine-tune to get closer to target total while prioritizing aspect ratio match
        current_total = map_width * map_height
        best_width, best_height = map_width, map_height
        best_aspect_diff = abs((w * (map_width + 0.5)) / (h * (map_height * 0.75 + 0.25)) - img_aspect) / img_aspect
        best_total_diff = abs(current_total - target_total_hexes)
        
        # Try small adjustments around the calculated values
        # Prioritize aspect ratio match (within 1%) over total hex count
        for width_adj in range(-5, 6):
            for height_adj in range(-5, 6):
                test_width = map_width + width_adj
                test_height = map_height + height_adj
                if test_width < 10 or test_height < 10:
                    continue
                # Calculate aspect ratio difference
                test_aspect = (w * (test_width + 0.5)) / (h * (test_height * 0.75 + 0.25))
                aspect_diff = abs(test_aspect - img_aspect) / img_aspect
                # Only consider if aspect ratio is within 1% (tighter than before)
                if aspect_diff > 0.01:
                    continue
                test_total = test_width * test_height
                test_total_diff = abs(test_total - target_total_hexes)
                # Prioritize aspect ratio match: if aspect is better, prefer it even if total is slightly worse
                # If aspect is similar (within 0.1%), then prefer better total
                if aspect_diff < best_aspect_diff - 0.001:
                    # Significantly better aspect ratio
                    best_width, best_height = test_width, test_height
                    best_aspect_diff = aspect_diff
                    best_total_diff = test_total_diff
                elif abs(aspect_diff - best_aspect_diff) < 0.001 and test_total_diff < best_total_diff:
                    # Similar aspect ratio, better total
                    best_width, best_height = test_width, test_height
                    best_aspect_diff = aspect_diff
                    best_total_diff = test_total_diff
        
        map_width, map_height = best_width, best_height
    else:
        # Default: use a reasonable starting width (30) and calculate height
        map_width = 30
        map_height = int(round(((w * (map_width + 0.5)) / (img_aspect * h) - 0.25) / 0.75))
    
    # Ensure minimum dimensions
    map_width = max(10, map_width)
    map_height = max(10, map_height)
    
    return map_width, map_height


if __name__ == "__main__":
    # Example: Default grid size
    default_width, default_height = calculate_ideal_image_size(30, 60)
    aspect = calculate_aspect_ratio(30, 60)
    
    print(f"Default grid (30x60 hexes):")
    print(f"  Ideal image size: {default_width} x {default_height} pixels")
    print(f"  Aspect ratio: {aspect:.4f} ({aspect:.2f}:1)")
    print()
    
    # Example: Square grid
    square_width, square_height = calculate_ideal_image_size(30, 30)
    square_aspect = calculate_aspect_ratio(30, 30)
    
    print(f"Square grid (30x30 hexes):")
    print(f"  Ideal image size: {square_width} x {square_height} pixels")
    print(f"  Aspect ratio: {square_aspect:.4f} ({square_aspect:.2f}:1)")
    print()
    
    # Example: Wide grid
    wide_width, wide_height = calculate_ideal_image_size(60, 30)
    wide_aspect = calculate_aspect_ratio(60, 30)
    
    print(f"Wide grid (60x30 hexes):")
    print(f"  Ideal image size: {wide_width} x {wide_height} pixels")
    print(f"  Aspect ratio: {wide_aspect:.4f} ({wide_aspect:.2f}:1)")
    print()
    print("=" * 60)
    print("REVERSE CALCULATION: Grid size from image size")
    print("=" * 60)
    print()
    
    # Test reverse calculation with the default grid's ideal image size
    calc_width, calc_height = calculate_grid_size_from_image(default_width, default_height, target_total_hexes=1800)
    print(f"Image size: {default_width} x {default_height} pixels")
    print(f"  Calculated grid: {calc_width} x {calc_height} hexes")
    print(f"  Original grid: 30 x 60 hexes")
    print(f"  Match: {'✓' if calc_width == 30 and calc_height == 60 else '✗'}")
    print()
    
    # Test with a different image size
    test_img_w, test_img_h = 2000, 1500
    calc_w, calc_h = calculate_grid_size_from_image(test_img_w, test_img_h, target_width=40)
    ideal_w, ideal_h = calculate_ideal_image_size(calc_w, calc_h)
    print(f"Image size: {test_img_w} x {test_img_h} pixels (target width: 40)")
    print(f"  Calculated grid: {calc_w} x {calc_h} hexes")
    print(f"  Ideal image for this grid: {ideal_w} x {ideal_h} pixels")
    print(f"  Aspect ratio match: {abs((test_img_w/test_img_h) - (ideal_w/ideal_h)) < 0.01}")
