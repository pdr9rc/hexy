import type { WorldGrid, WorldHex, HexCoordinate } from '@/models/types';
import { apiClient } from '@/api/client';

export class WorldGridService {
  private grid: WorldGrid | null = null;
  private selectedHex: WorldHex | null = null;
  private listeners: Set<(grid: WorldGrid | null) => void> = new Set();

  // Subscribe to grid changes
  subscribe(listener: (grid: WorldGrid | null) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.grid));
  }

  // Get current grid
  getGrid(): WorldGrid | null {
    return this.grid;
  }

  // Get selected hex
  getSelectedHex(): WorldHex | null {
    return this.selectedHex;
  }

  // Load world grid from API
  async loadWorldGrid(): Promise<boolean> {
    try {
      const response = await apiClient.getWorldGrid();
      if (response.success && response.data) {
        this.grid = response.data;
        this.notifyListeners();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to load world grid:', error);
      return false;
    }
  }

  // Generate new world grid
  async generateWorldGrid(width: number, height: number): Promise<boolean> {
    try {
      const response = await apiClient.generateWorldGrid(width, height);
      if (response.success && response.data) {
        this.grid = response.data;
        this.notifyListeners();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to generate world grid:', error);
      return false;
    }
  }

  // Select a hex
  selectHex(coordinate: HexCoordinate): void {
    if (!this.grid) return;

    const hex = this.grid.hexes.find(h => 
      h.coordinate.q === coordinate.q && 
      h.coordinate.r === coordinate.r && 
      h.coordinate.s === coordinate.s
    );

    if (hex) {
      // Clear previous selection
      this.grid.hexes.forEach(h => h.isSelected = false);
      hex.isSelected = true;
      this.selectedHex = hex;
      this.notifyListeners();
    }
  }

  // Clear selection
  clearSelection(): void {
    if (this.grid) {
      this.grid.hexes.forEach(h => h.isSelected = false);
      this.selectedHex = null;
      this.notifyListeners();
    }
  }

  // Get hex at coordinate
  getHexAt(coordinate: HexCoordinate): WorldHex | null {
    if (!this.grid) return null;

    return this.grid.hexes.find(h => 
      h.coordinate.q === coordinate.q && 
      h.coordinate.r === coordinate.r && 
      h.coordinate.s === coordinate.s
    ) || null;
  }

  // Get neighboring hexes
  getNeighbors(coordinate: HexCoordinate): WorldHex[] {
    if (!this.grid) return [];

    const neighbors: WorldHex[] = [];
    const directions = [
      { q: 1, r: 0, s: -1 },
      { q: 1, r: -1, s: 0 },
      { q: 0, r: -1, s: 1 },
      { q: -1, r: 0, s: 1 },
      { q: -1, r: 1, s: 0 },
      { q: 0, r: 1, s: -1 }
    ];

    directions.forEach(dir => {
      const neighborCoord = {
        q: coordinate.q + dir.q,
        r: coordinate.r + dir.r,
        s: coordinate.s + dir.s
      };
      const neighbor = this.getHexAt(neighborCoord);
      if (neighbor) {
        neighbors.push(neighbor);
      }
    });

    return neighbors;
  }
}

// Export singleton instance
export const worldGridService = new WorldGridService();
export default worldGridService; 