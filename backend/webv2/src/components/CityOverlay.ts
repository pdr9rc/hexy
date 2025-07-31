import type { CityOverlayData, CityContext } from '@/models/types';
import { cityOverlayService } from '@/services/CityOverlayService';

export class CityOverlay {
  private container: HTMLElement;
  private overlayElement: HTMLElement;
  private hexClickCallback?: (hexId: string) => void;
  private currentOverlayName: string = '';

  constructor() {
    this.container = document.getElementById('cities-container') as HTMLElement;
    this.overlayElement = document.createElement('div');
    this.overlayElement.className = 'city-overlay-container';
    this.container.appendChild(this.overlayElement);
    
    this.initialize();
  }

  private initialize(): void {
    this.setupEventListeners();
    this.subscribeToOverlayChanges();
    this.showWelcomeMessage();
  }

  private setupEventListeners(): void {
    // Listen for city hex clicks
    this.overlayElement.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      
      // Handle city hex cell clicks
      if (target.classList.contains('city-hex-cell') && !target.classList.contains('city-empty')) {
        const hexId = target.getAttribute('data-hex-id');
        if (hexId) {
          this.showCityHexDetails(hexId);
        }
      }
      
      // Handle button clicks
      if (target.id === 'ascii-view') {
        this.showAsciiView();
      } else if (target.id === 'back-to-grid') {
        this.renderOverlay(cityOverlayService.getCurrentOverlay());
      } else if (target.id === 'back-to-world') {
        this.clearOverlay();
      }
    });
  }

  private subscribeToOverlayChanges(): void {
    cityOverlayService.subscribeToOverlay((overlay) => {
      this.renderOverlay(overlay);
    });

    cityOverlayService.subscribeToContext((context) => {
      this.renderContext(context);
    });
  }

  private showWelcomeMessage(): void {
    this.overlayElement.innerHTML = `
      <div class="city-welcome-message">
        <h2>City Overlays</h2>
        <p>Select a city hex from the world map to view its detailed overlay.</p>
        <div class="city-instructions">
          <h3>Available Cities:</h3>
          <ul>
            <li>Galgenbeck - The capital city</li>
            <li>Bergen Chrypt - The crypt city</li>
            <li>And more cities to be discovered...</li>
          </ul>
        </div>
      </div>
    `;
  }

  private renderOverlay(overlay: CityOverlayData | null): void {
    if (!overlay) {
      this.showWelcomeMessage();
      return;
    }

    this.currentOverlayName = overlay.name;
    const html = this.generateOverlayHTML(overlay);
    this.overlayElement.innerHTML = html;
  }

  private renderContext(context: CityContext | null): void {
    if (!context) return;

    // Update context information if overlay is currently displayed
    const contextElement = this.overlayElement.querySelector('.city-context');
    if (contextElement) {
      contextElement.innerHTML = this.generateContextHTML(context);
    }
  }

  private generateOverlayHTML(overlay: CityOverlayData): string {
    let html = `
      <div class="city-overlay">
        <div class="city-header">
          <h2>${overlay.display_name}</h2>
          <div class="city-controls">
            <button class="btn btn-secondary" id="back-to-world">← Back to World</button>
            <button class="btn btn-primary" id="ascii-view">ASCII View</button>
          </div>
        </div>
        
        <div class="city-context">
          <!-- Context will be loaded separately -->
        </div>
        
        <div class="city-grid">
          <div class="city-grid-header">
            <h3>City Grid</h3>
            <span class="city-stats">${overlay.total_hexes} hexes</span>
          </div>
          <div class="city-hex-grid">
    `;

    // Generate interactive 5x5 grid like the original
    for (let row = 0; row < 5; row++) {
      html += '<div class="city-overlay-row">';
      for (let col = 0; col < 5; col++) {
        const hexId = `${row}_${col}`;
        const hexData = overlay.hex_grid?.[hexId];
        
        if (hexData) {
          const content = hexData.content;
          const symbol = this.getCityOverlaySymbol(content.type);
          const cssClass = this.getCityOverlayCSSClass(content.type);
          
          html += `
            <div class="city-hex-cell ${cssClass}" 
                 data-hex-id="${hexId}"
                 title="${content.name}">
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

    html += `
          </div>
          <div class="city-legend">
            <strong>LEGEND:</strong> D=District, B=Building, S=Street, L=Landmark, M=Market, T=Temple, V=Tavern, G=Guild, R=Residence, U=Ruins
          </div>
        </div>
        
        ${this.generateDistrictLegend(overlay)}
      </div>
    `;

    return html;
  }

  private generateContextHTML(context: CityContext): string {
    let html = `
      <div class="city-context-panel">
        <div class="context-section">
          <h3>Description</h3>
          <p>${context.description}</p>
        </div>
    `;

    if (context.city_events && context.city_events.length > 0) {
      html += `
        <div class="context-section">
          <h3>City Events</h3>
          <ul>
            ${context.city_events.slice(0, 3).map(event => `<li>${event}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (context.weather_conditions && context.weather_conditions.length > 0) {
      html += `
        <div class="context-section">
          <h3>Weather</h3>
          <ul>
            ${context.weather_conditions.slice(0, 2).map(weather => `<li>${weather}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (context.major_factions && context.major_factions.length > 0) {
      html += `
        <div class="context-section">
          <h3>Major Factions</h3>
          <div class="factions-list">
            ${context.major_factions.slice(0, 3).map(faction => `
              <div class="faction-item">
                <h4>${faction.name}</h4>
                <p><strong>Leader:</strong> ${faction.leader}</p>
                <p><strong>HQ:</strong> ${faction.headquarters}</p>
                <p><strong>Influence:</strong> ${faction.influence}</p>
                <p><strong>Attitude:</strong> ${faction.attitude}</p>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    html += '</div>';
    return html;
  }

  private generateDistrictLegend(overlay: CityOverlayData): string {
    if (!overlay.districts || overlay.districts.length === 0) {
      return '';
    }

    let html = `
      <div class="district-legend">
        <h3>Districts</h3>
        <div class="districts-list">
    `;

    overlay.districts.forEach((district) => {
      const color = this.generateDistrictColor(district.name, overlay.districts?.map(d => d.name) || []);
      html += `
        <div class="district-item" style="border-left: 4px solid ${color}">
          <h4>${district.name}</h4>
          <p>${district.description}</p>
          <p><strong>Theme:</strong> ${district.theme}</p>
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;

    return html;
  }

  private generateDistrictColor(districtName: string, allDistricts: string[]): string {
    const colors = [
      '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
      '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43'
    ];
    
    const index = allDistricts.indexOf(districtName);
    return colors[index % colors.length] || '#666';
  }

  public onHexClick(callback: (hexId: string) => void): void {
    this.hexClickCallback = callback;
  }

  public async loadCityOverlay(hexCode: string): Promise<void> {
    const overlayName = cityOverlayService.getOverlayNameFromHexCode(hexCode);
    
    try {
      const success = await cityOverlayService.loadCityOverlay(overlayName);
      if (success) {
        // Also load city context
        await cityOverlayService.loadCityContext(overlayName);
      }
    } catch (error) {
      console.error('Failed to load city overlay:', error);
    }
  }

  public clearOverlay(): void {
    cityOverlayService.clearOverlay();
  }

  public async showAsciiView(): Promise<void> {
    if (!this.currentOverlayName) return;

    try {
      const asciiContent = await cityOverlayService.loadCityOverlayAscii(this.currentOverlayName);
      if (asciiContent) {
        this.overlayElement.innerHTML = `
          <div class="city-ascii-view">
            <div class="ascii-header">
              <h2>${this.currentOverlayName} - ASCII View</h2>
              <button class="btn btn-secondary" id="back-to-grid">← Back to Grid</button>
            </div>
            <div class="ascii-content">
              <pre>${asciiContent}</pre>
            </div>
          </div>
        `;
      }
    } catch (error) {
      console.error('Failed to load ASCII view:', error);
    }
  }

  public async showCityHexDetails(hexId: string): Promise<void> {
    if (!this.currentOverlayName) return;

    try {
      const hexDetails = await cityOverlayService.getCityHexDetails(this.currentOverlayName, hexId);
      if (hexDetails) {
        const content = hexDetails.content;
        this.overlayElement.innerHTML = `
          <div class="city-hex-details">
            <div class="hex-details-header">
              <h2>${this.getCityOverlaySymbol(content.type)} ${content.name}</h2>
              <button class="btn btn-secondary" id="back-to-grid">← Back to Grid</button>
            </div>
            <div class="hex-details-content">
              <p><strong>Type:</strong> ${content.type}</p>
              <p><strong>Description:</strong> ${content.description}</p>
              <p><strong>Encounter:</strong> ${content.encounter}</p>
              <p><strong>Atmosphere:</strong> ${content.atmosphere}</p>
              <p><strong>Position Type:</strong> ${content.position_type}</p>
            </div>
          </div>
        `;
      }
    } catch (error) {
      console.error('Failed to load hex details:', error);
      this.showErrorState('Failed to load hex details');
    }
  }

  private getCityOverlaySymbol(type: string): string {
    const symbols: { [key: string]: string } = {
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

  private showErrorState(message: string): void {
    this.overlayElement.innerHTML = `
      <div class="city-error-state">
        <div class="error-content">
          <h2>ERROR LOADING CITY OVERLAY</h2>
          <p>${message}</p>
          <button class="btn btn-warning" id="back-to-world">RETURN TO MAP</button>
        </div>
      </div>
    `;
  }
} 