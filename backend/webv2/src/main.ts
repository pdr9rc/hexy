import { Header } from '@/components/Header';
import { WorldGrid } from '@/components/WorldGrid';
import { HexDetailsView } from '@/components/HexDetailsView';
import { CityOverlay } from '@/components/CityOverlay';
import { CityView } from '@/components/CityView';
import { Controls } from '@/components/Controls';
import { worldGridService } from '@/services/WorldGridService';
import { hexContentService } from '@/services/HexContentService';
import { cityOverlayService } from '@/services/CityOverlayService';
import { zoomService } from '@/services/ZoomService';
import { uiUtils } from '@/utils/uiUtils';
import type { ViewMode, HexCoordinate } from '@/models/types';

class HexyApp {
  private header: Header;
  private worldGrid: WorldGrid;
  private hexDetailsView: HexDetailsView;
  private cityOverlay: CityOverlay;
  private cityView: CityView;
  private controls: Controls;
  private currentViewMode: ViewMode = 'world';

  constructor() {
    this.header = new Header();
    this.worldGrid = new WorldGrid();
    this.hexDetailsView = new HexDetailsView(document.getElementById('hex-content-container')!);
    this.cityOverlay = new CityOverlay();
    this.cityView = new CityView(document.getElementById('cities-container')!);
    this.controls = new Controls();
    
    this.initialize();
  }

  private initialize(): void {
    // Initialize UI utilities
    uiUtils.createLoadingIndicator();
    
    // Map renderer initialization removed - using WorldGrid component instead
    
    this.setupEventListeners();
    this.loadInitialData();
  }

  private setupEventListeners(): void {
    // Handle view mode changes
    this.header.onViewModeChange((mode: ViewMode) => {
      this.handleViewModeChange(mode);
    });

    // Handle hex clicks
    this.worldGrid.onHexClick((coordinate: HexCoordinate) => {
      this.handleHexClick(coordinate);
    });

    // Handle city hex clicks
    this.cityOverlay.onHexClick((hexId: string) => {
      this.handleCityHexClick(hexId);
    });

    // Handle header button clicks
    const cityBtn = document.getElementById('city-view-btn');
    cityBtn?.addEventListener('click', () => {
      this.showCityOverlay();
    });

    // Handle city hex clicks
    const citiesContainer = document.getElementById('cities-container');
    citiesContainer?.addEventListener('city-hex-click', (event: Event) => {
      const customEvent = event as CustomEvent;
      const { hexId } = customEvent.detail;
      this.handleCityHexClick(hexId);
    });
  }

  private async loadInitialData(): Promise<void> {
    try {
      // Load world grid
      await this.worldGrid.loadGrid();
      
      // Initialize zoom service after grid is loaded
      this.initializeZoom();
      
      // Set initial view mode
      this.currentViewMode = this.header.getCurrentView();
      hexContentService.setViewMode(this.currentViewMode);
      
      // Enable controls after data is loaded
      this.controls.enableControls();
      
    } catch (error) {
      console.error('Failed to load initial data:', error);
      this.showError('Failed to load initial data. Please refresh the page.');
    }
  }

  private initializeZoom(): void {
    const container = document.getElementById('world-grid-container');
    const gridElement = document.querySelector('.hex-grid');
    
    if (container && gridElement) {
      zoomService.initializeZoom(container, gridElement as HTMLElement);
    }
  }

  private handleViewModeChange(mode: ViewMode): void {
    this.currentViewMode = mode;
    hexContentService.setViewMode(mode);
    zoomService.setViewMode(mode);
    
    // Update UI based on view mode
    this.updateViewModeUI(mode);
    
    // Clear content when switching modes
    this.hexDetailsView.clear();
    
    // Clear city overlay when switching to world view
    if (mode === 'world') {
      this.cityOverlay.clearOverlay();
    }
  }

  private updateViewModeUI(mode: ViewMode): void {
    const worldGridContainer = document.getElementById('world-grid-container');
    const citiesContainer = document.getElementById('cities-container');
    
    if (mode === 'world') {
      worldGridContainer?.classList.remove('hidden');
      citiesContainer?.classList.add('hidden');
      this.cityView.clear(); // Clear city view when switching to world
    } else {
      worldGridContainer?.classList.add('hidden');
      citiesContainer?.classList.remove('hidden');
      // City view will be populated when a city hex is clicked
    }
  }

  private async handleHexClick(coordinate: HexCoordinate): Promise<void> {
    try {
      // Update grid selection
      worldGridService.selectHex(coordinate);
      this.worldGrid.updateHexSelection(coordinate);
      
      // Check if this is a city hex
      const hex = worldGridService.getHexAt(coordinate);
      if (hex && hex.terrain === 'city') {
        // Convert coordinate to hex code
        const hexCode = `${coordinate.q.toString().padStart(2, '0')}${coordinate.r.toString().padStart(2, '0')}`;
        
        // Load city overlay into the left panel
        await this.cityView.showCityOverlay(hexCode);
        
        // Load city details into the right panel
        await this.cityView.showCityDetails(hexCode);
        
        // Switch to cities view
        this.header.setActiveView('cities');
        this.currentViewMode = 'cities';
        this.updateViewModeUI('cities');
      } else {
        // Load regular hex content in the details view
        await this.hexDetailsView.loadHexContent(coordinate);
      }
      
    } catch (error) {
      console.error('Failed to handle hex click:', error);
      this.showError('Failed to load hex content.');
    }
  }

  private async handleCityHexClick(hexId: string): Promise<void> {
    try {
      // Get the current city overlay
      const currentOverlay = this.cityView.getCurrentOverlay();
      if (!currentOverlay) {
        throw new Error('No city overlay loaded');
      }

      // Load city hex details into the right panel
      await this.cityView.showCityHexDetails(currentOverlay.name, hexId);
      
      // Update the right panel with the hex details
      const hexDetails = await this.cityView.getCityHexDetails(currentOverlay.name, hexId);
      if (hexDetails) {
        // Convert city hex data to hex content format for the right panel
        const hexContent = {
          id: hexId,
          coordinate: { q: 0, r: 0, s: 0 }, // City hexes don't use world coordinates
          terrain: 'city',
          type: 'city',
          is_city: true,
          has_content: true,
          content_type: hexDetails.content_type || 'city',
          city_name: hexDetails.name,
          population: hexDetails.population?.toString(),
          content: hexDetails.description || 'No description available'
        };
        
        // Update the hex details view with city hex content
        this.hexDetailsView.updateContent(hexContent);
      }
    } catch (error) {
      console.error('Failed to handle city hex click:', error);
      this.showError('Failed to load city hex details.');
    }
  }

  private async showCityOverlay(): Promise<void> {
    try {
      // Switch to cities view
      this.header.setActiveView('cities');
      this.currentViewMode = 'cities';
      this.updateViewModeUI('cities');
      
      // Load a default city overlay (you can modify this to show available cities)
      await this.cityView.showCityOverlay('0101'); // Default hex code
    } catch (error) {
      console.error('Failed to show city overlay:', error);
      this.showError('Failed to load city overlay.');
    }
  }

  private showError(message: string): void {
    // Simple error display - can be enhanced with a proper error component
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ff4444;
      color: white;
      padding: 1rem;
      border-radius: 4px;
      z-index: 1000;
      max-width: 300px;
    `;
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.parentNode.removeChild(errorDiv);
      }
    }, 5000);
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new HexyApp();
});

// Export for potential external use
export { HexyApp }; 