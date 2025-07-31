import { apiClient } from '../api/client';
import { CityOverlayData, CityContext } from '../models/types';

interface CityViewState {
  currentCity: string | null;
  currentOverlay: CityOverlayData | null;
  currentContext: CityContext | null;
  viewMode: 'details' | 'overlay' | 'ascii' | 'hex-details';
  selectedHexId: string | null;
  isLoading: boolean;
  error: string | null;
}

export class CityView {
  private container: HTMLElement;
  private state: CityViewState = {
    currentCity: null,
    currentOverlay: null,
    currentContext: null,
    viewMode: 'details',
    selectedHexId: null,
    isLoading: false,
    error: null
  };

  constructor(container: HTMLElement) {
    this.container = container;
  }

  public async showCityDetails(hexCode: string): Promise<void> {
    try {
      this.setState({ isLoading: true, error: null });
      this.render();

      const response = await apiClient.getCityDetails(hexCode);
      
      if (response.success && response.data) {
        this.setState({
          currentCity: hexCode,
          currentOverlay: null,
          currentContext: null,
          viewMode: 'details',
          isLoading: false
        });
        this.render();
      } else {
        throw new Error('City not found');
      }
    } catch (error) {
      console.error('Error loading city details:', error);
      this.setState({
        error: 'Failed to load city details',
        isLoading: false
      });
      this.render();
    }
  }

  public async showSettlementDetails(hexCode: string): Promise<void> {
    try {
      this.setState({ isLoading: true, error: null });
      this.render();

      const response = await apiClient.getSettlementDetails(hexCode);
      
      if (response.success && response.data) {
        this.setState({
          currentCity: hexCode,
          currentOverlay: null,
          currentContext: null,
          viewMode: 'details',
          isLoading: false
        });
        this.render();
      } else {
        throw new Error('Settlement not found');
      }
    } catch (error) {
      console.error('Error loading settlement details:', error);
      this.setState({
        error: 'Failed to load settlement details',
        isLoading: false
      });
      this.render();
    }
  }

  public async showCityOverlay(hexCode: string): Promise<void> {
    try {
      this.setState({ isLoading: true, error: null });
      this.render();

      // Get available overlays
      const overlaysResponse = await apiClient.getCityOverlays();
      
      if (overlaysResponse.success && overlaysResponse.data.overlays.length > 0) {
        const overlayName = overlaysResponse.data.overlays[0].name;
        await this.loadCityOverlay(overlayName, hexCode);
      } else {
        // If no overlays available, show a default city grid
        this.setState({
          currentCity: hexCode,
          currentOverlay: this.createDefaultCityOverlay(),
          currentContext: null,
          viewMode: 'overlay',
          isLoading: false
        });
        this.render();
      }
    } catch (error) {
      console.error('Error loading city overlays:', error);
      // Show default city grid even if API fails
      this.setState({
        currentCity: hexCode,
        currentOverlay: this.createDefaultCityOverlay(),
        currentContext: null,
        viewMode: 'overlay',
        isLoading: false
      });
      this.render();
    }
  }

  public async loadCityOverlay(overlayName: string, hexCode: string): Promise<void> {
    try {
      this.setState({ isLoading: true, error: null });
      this.render();

      const response = await apiClient.getCityOverlay(overlayName);
      
      if (response.success && response.data) {
        this.setState({
          currentCity: hexCode,
          currentOverlay: response.data.overlay,
          currentContext: null,
          viewMode: 'overlay',
          isLoading: false
        });
        this.render();
      } else {
        throw new Error('Failed to load city overlay');
      }
    } catch (error) {
      console.error('Error loading city overlay:', error);
      this.setState({
        error: 'Failed to load city overlay',
        isLoading: false
      });
      this.render();
    }
  }

  public async showCityOverlayAscii(overlayName: string, hexCode: string): Promise<void> {
    try {
      this.setState({ isLoading: true, error: null });
      this.render();

      const response = await apiClient.getCityOverlayAscii(overlayName);
      
      if (response.success && response.data) {
        this.setState({
          currentCity: hexCode,
          currentOverlay: null,
          currentContext: null,
          viewMode: 'ascii',
          isLoading: false
        });
        this.render();
      } else {
        throw new Error('Failed to load ASCII view');
      }
    } catch (error) {
      console.error('Error loading ASCII view:', error);
      this.setState({
        error: 'Failed to load ASCII view',
        isLoading: false
      });
      this.render();
    }
  }

  public async showCityHexDetails(overlayName: string, hexId: string): Promise<void> {
    try {
      this.setState({ isLoading: true, error: null });
      this.render();

      const response = await apiClient.getCityOverlayHex(overlayName, hexId);
      
      if (response.success && response.data) {
        this.setState({
          selectedHexId: hexId,
          viewMode: 'hex-details',
          isLoading: false
        });
        this.render();
      } else {
        throw new Error('Failed to load hex details');
      }
    } catch (error) {
      console.error('Error loading hex details:', error);
      this.setState({
        error: 'Failed to load hex details',
        isLoading: false
      });
      this.render();
    }
  }

  public setViewMode(mode: CityViewState['viewMode']): void {
    this.setState({ viewMode: mode });
    this.render();
  }

  private setState(updates: Partial<CityViewState>): void {
    this.state = { ...this.state, ...updates };
  }

  private render(): void {
    if (this.state.isLoading) {
      this.renderLoading();
    } else if (this.state.error) {
      this.renderError();
    } else if (this.state.viewMode === 'details') {
      this.renderDetails();
    } else if (this.state.viewMode === 'overlay') {
      this.renderOverlay();
    } else if (this.state.viewMode === 'ascii') {
      this.renderAscii();
    } else if (this.state.viewMode === 'hex-details') {
      this.renderHexDetails();
    } else {
      this.renderEmpty();
    }
  }

  private renderLoading(): void {
    this.container.innerHTML = `
      <div class="city-view-loading">
        <div class="ascii-loading">
          <div class="ascii-loading-text">LOADING CITY DATA...</div>
          <div class="ascii-loading-spinner">⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏</div>
        </div>
      </div>
    `;
  }

  private renderError(): void {
    this.container.innerHTML = `
      <div class="city-view-error">
        <div class="ascii-error">
          <h2 class="ascii-error-title">ERROR</h2>
          <p class="ascii-error-text">${this.state.error}</p>
          <button class="ascii-btn" onclick="this.dispatchEvent(new CustomEvent('city-view-back'))">
            [BACK]
          </button>
        </div>
      </div>
    `;
  }

  private renderEmpty(): void {
    this.container.innerHTML = `
      <div class="city-view-empty">
        <div class="ascii-empty">
          <h2 class="ascii-empty-title">NO CITY SELECTED</h2>
          <p class="ascii-empty-text">Click on a city hex to view its details</p>
        </div>
      </div>
    `;
  }

  private renderDetails(): void {
    if (!this.state.currentCity) return;

    // This would be populated with actual city/settlement data
    const cityData = {
      name: 'Unknown City',
      population: 'Unknown',
      region: 'Unknown',
      atmosphere: 'Unknown',
      description: 'No description available',
      notable_features: 'None',
      key_npcs: 'None'
    };

    this.container.innerHTML = `
      <div class="city-view-details">
        <div class="city-details-header">
          <h2 class="city-details-title">⌂ ${cityData.name}</h2>
          <div class="city-details-controls">
            <button class="ascii-btn ascii-btn-primary" id="city-overlay-btn">
              [VIEW OVERLAY]
            </button>
            <button class="ascii-btn ascii-btn-secondary" id="city-ascii-btn">
              [ASCII VIEW]
            </button>
          </div>
        </div>
        
        <div class="city-details-content">
          <div class="city-info-grid">
            <div class="city-info-item">
              <span class="city-info-label">Population:</span>
              <span class="city-info-value">${cityData.population}</span>
            </div>
            <div class="city-info-item">
              <span class="city-info-label">Region:</span>
              <span class="city-info-value">${cityData.region}</span>
            </div>
            <div class="city-info-item">
              <span class="city-info-label">Atmosphere:</span>
              <span class="city-info-value">${cityData.atmosphere}</span>
            </div>
          </div>
          
          <div class="city-description">
            <h3>Description</h3>
            <p>${cityData.description}</p>
          </div>
          
          <div class="city-features">
            <h3>Notable Features</h3>
            <p>${cityData.notable_features}</p>
          </div>
          
          <div class="city-npcs">
            <h3>Key NPCs</h3>
            <p>${cityData.key_npcs}</p>
          </div>
        </div>
      </div>
    `;

    this.attachDetailsEvents();
  }

  private renderOverlay(): void {
    if (!this.state.currentOverlay) return;

    const overlay = this.state.currentOverlay;
    const hexGrid = overlay.hex_grid || {};

    this.container.innerHTML = `
      <div class="city-view-overlay">
        <div class="city-overlay-header">
          <h2 class="city-overlay-title">⌂ ${overlay.display_name?.toUpperCase() || 'CITY'} - INTERACTIVE GRID</h2>
          <div class="city-overlay-controls">
            <button class="ascii-btn ascii-btn-secondary" id="city-back-btn">
              [← BACK]
            </button>
            <button class="ascii-btn ascii-btn-primary" id="city-ascii-view-btn">
              [📜 ASCII VIEW]
            </button>
          </div>
        </div>
        
        <div class="city-overlay-legend">
          <strong>LEGEND:</strong> D=District, B=Building, S=Street, L=Landmark, M=Market, T=Temple, V=Tavern, G=Guild, R=Residence, U=Ruins
        </div>
        
        <div class="city-overlay-grid">
          ${this.generateOverlayGrid(hexGrid)}
        </div>
      </div>
    `;

    this.attachOverlayEvents();
  }

  private generateOverlayGrid(hexGrid: Record<string, any>): string {
    let html = '';
    
    for (let row = 0; row < 5; row++) {
      html += '<div class="city-overlay-row">';
      for (let col = 0; col < 5; col++) {
        const hexId = `${row}_${col}`;
        const hexData = hexGrid[hexId];
        
        if (hexData && hexData.content) {
          const content = hexData.content;
          const symbol = this.getCityOverlaySymbol(content.type);
          const cssClass = this.getCityOverlayCSSClass(content.type);
          
          html += `
            <div class="city-hex-cell ${cssClass}" 
                 data-hex-id="${hexId}"
                 title="${content.name || 'Unknown'}">
              ${symbol}
            </div>
          `;
        } else {
          html += `
            <div class="city-hex-cell city-empty" style="opacity: 0.3;"></div>
          `;
        }
      }
      html += '</div>';
    }
    
    return html;
  }

  private renderAscii(): void {
    // This would render the ASCII view of the city
    this.container.innerHTML = `
      <div class="city-view-ascii">
        <div class="city-ascii-header">
          <h2 class="city-ascii-title">ASCII CITY VIEW</h2>
          <div class="city-ascii-controls">
            <button class="ascii-btn ascii-btn-secondary" id="city-back-btn">
              [← BACK]
            </button>
          </div>
        </div>
        
        <div class="city-ascii-content">
          <pre class="ascii-art">
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CITY ASCII VIEW                           ║
    ║                                                              ║
    ║  This would display the ASCII art representation              ║
    ║  of the city layout and details.                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
          </pre>
        </div>
      </div>
    `;

    this.attachAsciiEvents();
  }

  private renderHexDetails(): void {
    if (!this.state.selectedHexId) return;

    // This would display detailed information about a specific city hex
    this.container.innerHTML = `
      <div class="city-hex-details">
        <div class="hex-details-header">
          <h2 class="hex-details-title">CITY HEX ${this.state.selectedHexId}</h2>
          <div class="hex-details-controls">
            <button class="ascii-btn ascii-btn-secondary" id="hex-back-btn">
              [← BACK TO GRID]
            </button>
          </div>
        </div>
        
        <div class="hex-details-content">
          <div class="hex-type-badge city-district">
            District
          </div>
          
          <div class="detail-section">
            <h4>Name</h4>
            <p>Unknown District</p>
          </div>
          
          <div class="detail-section">
            <h4>Description</h4>
            <p>This district contains various buildings and landmarks.</p>
          </div>
          
          <div class="detail-section">
            <h4>Notable Features</h4>
            <ul>
              <li>Market Square</li>
              <li>Guard Tower</li>
              <li>Fountain</li>
            </ul>
          </div>
        </div>
      </div>
    `;

    this.attachHexDetailsEvents();
  }

  private getCityOverlaySymbol(type: string): string {
    const symbols: Record<string, string> = {
      'district': 'D',
      'building': 'B',
      'street': 'S',
      'landmark': 'L',
      'market': 'M',
      'temple': 'T',
      'tavern': 'V',
      'guild': 'G',
      'residence': 'R',
      'ruins': 'U'
    };
    return symbols[type] || '?';
  }

  private getCityOverlayCSSClass(type: string): string {
    return `city-${type}`;
  }

  private createDefaultCityOverlay(): CityOverlayData {
    // Create a default 5x5 city grid
    const hexGrid: Record<string, any> = {};
    
    for (let row = 0; row < 5; row++) {
      for (let col = 0; col < 5; col++) {
        const hexId = `${row}_${col}`;
        
        // Create some sample city content
        const cityTypes = ['district', 'building', 'street', 'landmark', 'market', 'temple', 'tavern', 'guild', 'residence', 'ruins'];
        const randomType = cityTypes[Math.floor(Math.random() * cityTypes.length)];
        
        hexGrid[hexId] = {
          content: {
            type: randomType,
            name: `${randomType.charAt(0).toUpperCase() + randomType.slice(1)} ${row}-${col}`,
            description: `A ${randomType} in the city.`
          }
        };
      }
    }
    
    return {
      name: 'default',
      display_name: 'Sample City',
      filename: 'default_city.md',
      grid_type: 'square',
      radius: 2,
      hex_grid: hexGrid,
      total_hexes: 25
    };
  }

  private attachDetailsEvents(): void {
    const overlayBtn = this.container.querySelector('#city-overlay-btn');
    overlayBtn?.addEventListener('click', () => {
      if (this.state.currentCity) {
        this.showCityOverlay(this.state.currentCity);
      }
    });

    const asciiBtn = this.container.querySelector('#city-ascii-btn');
    asciiBtn?.addEventListener('click', () => {
      if (this.state.currentCity) {
        this.showCityOverlayAscii('default', this.state.currentCity);
      }
    });
  }

  private attachOverlayEvents(): void {
    const backBtn = this.container.querySelector('#city-back-btn');
    backBtn?.addEventListener('click', () => {
      this.setState({ viewMode: 'details' });
      this.render();
    });

    const asciiBtn = this.container.querySelector('#city-ascii-view-btn');
    asciiBtn?.addEventListener('click', () => {
      if (this.state.currentCity) {
        this.showCityOverlayAscii('default', this.state.currentCity);
      }
    });

    // Attach click events to hex cells
    const hexCells = this.container.querySelectorAll('.city-hex-cell[data-hex-id]');
    hexCells.forEach(cell => {
      const hexId = cell.getAttribute('data-hex-id');
      if (hexId) {
        cell.addEventListener('click', () => {
          // Emit a custom event that the main app can listen to
          const event = new CustomEvent('city-hex-click', { 
            detail: { hexId, overlayName: this.state.currentOverlay?.name || 'default' }
          });
          this.container.dispatchEvent(event);
        });
      }
    });
  }

  private attachAsciiEvents(): void {
    const backBtn = this.container.querySelector('#city-back-btn');
    backBtn?.addEventListener('click', () => {
      this.setState({ viewMode: 'details' });
      this.render();
    });
  }

  private attachHexDetailsEvents(): void {
    const backBtn = this.container.querySelector('#hex-back-btn');
    backBtn?.addEventListener('click', () => {
      this.setState({ viewMode: 'overlay' });
      this.render();
    });
  }

  public getCurrentOverlay(): CityOverlayData | null {
    return this.state.currentOverlay;
  }

  public async getCityHexDetails(overlayName: string, hexId: string): Promise<any> {
    try {
      const response = await apiClient.getCityOverlayHex(overlayName, hexId);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Error getting city hex details:', error);
      return null;
    }
  }

  public clear(): void {
    this.setState({
      currentCity: null,
      currentOverlay: null,
      currentContext: null,
      viewMode: 'details',
      selectedHexId: null,
      isLoading: false,
      error: null
    });
    this.render();
  }
} 