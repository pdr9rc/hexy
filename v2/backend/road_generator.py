"""
Road Generation System for The Dying Lands

This module implements Minimum Spanning Tree (MST) based road generation
that connects all settlements and cities with terrain-aware pathfinding.
Bridges are prioritized as existing road infrastructure.
"""

import heapq
from typing import List, Dict, Set, Tuple, Optional, Any


# Terrain movement costs (lower = preferred for road routing)
DEFAULT_TERRAIN_COSTS = {
    'bridge': 0.5,      # Highest priority - existing infrastructure
    'plains': 1.0,      # Easiest natural terrain
    'coast': 1.5,
    'river': 100.0,     # Impassable - must use bridges
    'forest': 2.0,
    'hills': 2.0,
    'desert': 2.5,
    'mountain': 4.0,    # Hardest
    'swamp': 4.0,
    'sea': 100.0,       # Impassable - must use bridges
    'deep_sea': 100.0,  # Impassable
    'sea_encounter': 100.0,  # Impassable
    'settlement': 1.0,  # Settlements are easy to traverse
    'city': 1.0,        # Cities are easy to traverse
    'dungeon': 2.0,
}


def parse_hex_code(hex_code: str) -> Tuple[int, int]:
    """Parse hex code (e.g., '0101') into (x, y) coordinates."""
    if isinstance(hex_code, str) and len(hex_code) == 4:
        x = int(hex_code[:2])
        y = int(hex_code[2:])
        return (x, y)
    raise ValueError(f"Invalid hex code format: {hex_code}")


def format_hex_code(x: int, y: int) -> str:
    """Format (x, y) coordinates into hex code (e.g., '0101')."""
    return f"{x:02d}{y:02d}"


def get_hex_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
    """Get all 6 neighbors of a hex in offset coordinates."""
    # In offset coordinates, odd rows are shifted right
    is_odd_row = y % 2 == 1
    
    if is_odd_row:
        # Odd row neighbors
        neighbors = [
            (x, y - 1),      # NW
            (x + 1, y - 1),  # NE
            (x + 1, y),      # E
            (x + 1, y + 1),  # SE
            (x, y + 1),      # SW
            (x - 1, y),      # W
        ]
    else:
        # Even row neighbors
        neighbors = [
            (x - 1, y - 1),  # NW
            (x, y - 1),      # NE
            (x + 1, y),      # E
            (x, y + 1),      # SE
            (x - 1, y + 1),  # SW
            (x - 1, y),      # W
        ]
    
    return neighbors


def hex_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calculate Manhattan-like distance between two hex positions."""
    x1, y1 = pos1
    x2, y2 = pos2
    
    # Simple Manhattan distance as heuristic
    return abs(x2 - x1) + abs(y2 - y1)


def astar_pathfind(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    hex_map: Dict[str, Dict[str, Any]],
    terrain_costs: Dict[str, float]
) -> List[Tuple[int, int]]:
    """
    Find optimal path between two hexes using A* algorithm.
    Returns list of (x, y) coordinates from start to goal.
    """
    # Priority queue: (f_score, counter, position, path)
    counter = 0
    heap = [(0, counter, start, [start])]
    visited = set()
    
    while heap:
        f_score, _, current, path = heapq.heappop(heap)
        
        if current in visited:
            continue
        
        visited.add(current)
        
        # Check if we reached the goal
        if current == goal:
            return path
        
        # Explore neighbors
        for neighbor in get_hex_neighbors(*current):
            if neighbor in visited:
                continue
            
            nx, ny = neighbor
            hex_code = format_hex_code(nx, ny)
            
            # Skip if hex doesn't exist
            if hex_code not in hex_map:
                continue
            
            # Get terrain cost
            terrain = hex_map[hex_code].get('terrain', 'plains')
            move_cost = terrain_costs.get(terrain, 2.0)
            
            # Calculate scores
            g_score = len(path) * move_cost  # Actual cost from start
            h_score = hex_distance(neighbor, goal)  # Heuristic to goal
            f = g_score + h_score
            
            counter += 1
            new_path = path + [neighbor]
            heapq.heappush(heap, (f, counter, neighbor, new_path))
    
    # No path found, return direct line (shouldn't happen in practice)
    return [start, goal]


def compute_mst_edges(
    settlements: List[Tuple[int, int]],
    hex_map: Dict[str, Dict[str, Any]],
    terrain_costs: Dict[str, float]
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Compute Minimum Spanning Tree edges connecting all settlements.
    Uses Prim's algorithm with terrain-aware edge weights.
    Returns list of (start, end) coordinate pairs.
    """
    if len(settlements) < 2:
        return []
    
    # Prim's algorithm
    mst_edges = []
    explored = {settlements[0]}
    unexplored = set(settlements[1:])
    
    while unexplored:
        # Find cheapest edge from explored to unexplored
        best_edge = None
        best_cost = float('inf')
        
        for start in explored:
            for end in unexplored:
                # Calculate path cost (simple distance heuristic)
                # We'll do actual pathfinding later, this is just for MST structure
                dist = hex_distance(start, end)
                
                # Factor in terrain between points (simplified)
                start_hex = format_hex_code(*start)
                end_hex = format_hex_code(*end)
                start_terrain = hex_map.get(start_hex, {}).get('terrain', 'plains')
                end_terrain = hex_map.get(end_hex, {}).get('terrain', 'plains')
                
                avg_cost = (terrain_costs.get(start_terrain, 2.0) + 
                           terrain_costs.get(end_terrain, 2.0)) / 2
                
                cost = dist * avg_cost
                
                if cost < best_cost:
                    best_cost = cost
                    best_edge = (start, end)
        
        if best_edge:
            mst_edges.append(best_edge)
            explored.add(best_edge[1])
            unexplored.remove(best_edge[1])
    
    return mst_edges


def generate_roads(
    hex_data_list: List[Dict[str, Any]],
    terrain_costs: Optional[Dict[str, float]] = None
) -> Set[str]:
    """
    Generate road network connecting all settlements and cities.
    
    Args:
        hex_data_list: List of hex data dictionaries
        terrain_costs: Optional custom terrain costs (lower = preferred)
    
    Returns:
        Set of hex codes that should have roads
    """
    if terrain_costs is None:
        terrain_costs = DEFAULT_TERRAIN_COSTS
    
    # Build hex map for lookups
    hex_map = {hex_data['hex_code']: hex_data for hex_data in hex_data_list}
    
    # Find all settlements and cities
    settlements = []
    road_hexes = set()
    
    for hex_data in hex_data_list:
        hex_code = hex_data['hex_code']
        terrain = hex_data.get('terrain', 'plains')
        
        # Automatically mark bridges as roads
        if terrain == 'bridge':
            road_hexes.add(hex_code)
        
        # Collect settlements and cities
        is_settlement = hex_data.get('is_settlement', False)
        is_major_city = hex_data.get('is_major_city', False)
        is_minor_city = hex_data.get('is_minor_city', False)
        is_lore_location = hex_data.get('is_lore_location', False)
        
        if is_settlement or is_major_city or is_minor_city:
            try:
                pos = parse_hex_code(hex_code)
                settlements.append(pos)
                # Settlements themselves should have roads
                road_hexes.add(hex_code)
            except ValueError:
                continue
    
    print(f"  Found {len(settlements)} settlements/cities to connect")
    print(f"  Found {len([h for h in road_hexes if hex_map.get(h, {}).get('terrain') == 'bridge'])} bridges")
    
    # If less than 2 settlements, no roads needed
    if len(settlements) < 2:
        return road_hexes
    
    # Compute MST edges
    mst_edges = compute_mst_edges(settlements, hex_map, terrain_costs)
    print(f"  MST computed with {len(mst_edges)} edges")
    
    # For each MST edge, find actual path and mark hexes
    for start, end in mst_edges:
        path = astar_pathfind(start, end, hex_map, terrain_costs)
        
        # Mark all hexes in path as roads
        for pos in path:
            hex_code = format_hex_code(*pos)
            if hex_code in hex_map:
                road_hexes.add(hex_code)
    
    return road_hexes


# Example usage for testing
if __name__ == "__main__":
    # Test hex coordinate functions
    test_code = "0101"
    x, y = parse_hex_code(test_code)
    print(f"Parsed {test_code} -> ({x}, {y})")
    print(f"Formatted back -> {format_hex_code(x, y)}")
    
    # Test neighbors
    neighbors = get_hex_neighbors(5, 5)
    print(f"\nNeighbors of (5, 5): {neighbors}")
    
    # Test distance
    dist = hex_distance((1, 1), (5, 5))
    print(f"\nDistance (1,1) to (5,5): {dist}")
