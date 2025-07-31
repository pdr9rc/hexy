import type { HexContent, HexCoordinate, ViewMode } from '@/models/types';
import { apiClient } from '@/api/client';

export class HexContentService {
  private currentContent: HexContent | null = null;
  private currentDetails: any = null;
  private viewMode: ViewMode = 'world';
  private listeners: Set<(content: HexContent | null, details: any) => void> = new Set();

  // Subscribe to content changes
  subscribe(listener: (content: HexContent | null, details: any) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.currentContent, this.currentDetails));
  }

  // Get current content
  getCurrentContent(): { content: HexContent | null; details: any } {
    return {
      content: this.currentContent,
      details: this.currentDetails
    };
  }

  // Get current view mode
  getViewMode(): ViewMode {
    return this.viewMode;
  }

  // Set view mode
  setViewMode(mode: ViewMode): void {
    this.viewMode = mode;
    // Clear content when switching modes
    this.clearContent();
  }

  // Load hex content based on coordinate and view mode
  async loadHexContent(coordinate: HexCoordinate): Promise<boolean> {
    try {
      let response: any;

      if (this.viewMode === 'world') {
        response = await apiClient.getWorldHexContent(coordinate);
      } else {
        response = await apiClient.getCityHexContent(coordinate);
      }

      if (response.success && response.data) {
        this.currentContent = response.data.hex;
        this.currentDetails = response.data.details;
        this.notifyListeners();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to load hex content:', error);
      return false;
    }
  }

  // Load generic hex content (fallback)
  async loadGenericHexContent(coordinate: HexCoordinate): Promise<boolean> {
    try {
      const response = await apiClient.getHexContent(coordinate);
      if (response.success && response.data) {
        this.currentContent = response.data.hex;
        this.currentDetails = response.data.details;
        this.notifyListeners();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to load generic hex content:', error);
      return false;
    }
  }

  // Clear current content
  clearContent(): void {
    this.currentContent = null;
    this.currentDetails = null;
    this.notifyListeners();
  }

  // Update content manually (for testing/debugging)
  updateContent(content: HexContent, details?: any): void {
    this.currentContent = content;
    this.currentDetails = details || null;
    this.notifyListeners();
  }

  // Get formatted content for display
  getFormattedContent(): string {
    if (!this.currentContent) {
      return 'No hex selected';
    }

    const { coordinate, terrain, type } = this.currentContent;
    let formatted = `Hex: (${coordinate.q}, ${coordinate.r}, ${coordinate.s})\n`;
    formatted += `Type: ${type}\n`;
    formatted += `Terrain: ${terrain}\n`;

    if (type === 'world' && this.currentContent.biome) {
      formatted += `Biome: ${this.currentContent.biome}\n`;
    }

    if (type === 'city' && this.currentContent.cityName) {
      formatted += `City: ${this.currentContent.cityName}\n`;
      if (this.currentContent.population) {
        formatted += `Population: ${this.currentContent.population}\n`;
      }
    }

    return formatted;
  }
}

// Export singleton instance
export const hexContentService = new HexContentService();
export default hexContentService; 