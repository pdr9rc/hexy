import type { HexContent } from '@/models/types';
import { hexContentService } from '@/services/HexContentService';

export class HexContentDisplay {
  private container: HTMLElement;
  private contentElement: HTMLElement;

  constructor() {
    this.container = document.getElementById('hex-content') as HTMLElement;
    this.contentElement = document.createElement('div');
    this.contentElement.className = 'hex-content-display';
    this.container.appendChild(this.contentElement);
    
    this.initialize();
  }

  private initialize(): void {
    this.subscribeToContentChanges();
    this.showWelcomeMessage();
  }

  private subscribeToContentChanges(): void {
    hexContentService.subscribe((content, details) => {
      this.renderContent(content, details);
    });
  }

  private showWelcomeMessage(): void {
    this.contentElement.innerHTML = `
      <div class="welcome-message">
        <h2>Welcome to Hexy</h2>
        <p>Select a hex on the world grid to view its details.</p>
        <div class="instructions">
          <h3>Instructions:</h3>
          <ul>
            <li>Click on any hex to view its content</li>
            <li>Switch between World and Cities view using the header buttons</li>
            <li>Explore the generated world and discover its secrets</li>
          </ul>
        </div>
      </div>
    `;
  }

  private renderContent(content: HexContent | null, details: any): void {
    if (!content) {
      this.showWelcomeMessage();
      return;
    }

    const contentHtml = this.generateContentHtml(content, details);
    this.contentElement.innerHTML = contentHtml;
  }

  private generateContentHtml(content: HexContent, details: any): string {
    const { coordinate, terrain, type } = content;
    
    // Prepare fields with fallbacks
    const title = content.id || `HEX ${coordinate.q},${coordinate.r},${coordinate.s}`;
    const terrainName = terrain || 'Unknown';
    const hexType = type || 'Unknown';
    
    let html = `
      <div class="city-hex-details-box">
        <div class="ascii-box">
          <div class="ascii-inner-box">
            <div class="ascii-section ascii-hex-title">
              <span>${title}</span>
            </div>
            <div class="ascii-section ascii-hex-terrain">
              <span>TERRAIN: ${terrainName}</span>
            </div>
            <div class="ascii-section ascii-hex-type">
              <span>TYPE: ${hexType}</span>
            </div>
    `;

    // Add type-specific content
    if (type === 'city') {
      html += this.generateCityHexHtml(content as any);
    } else if (type === 'world') {
      html += this.generateWorldHexHtml(content as any);
    }

    // Add details if available
    if (details) {
      html += this.generateDetailsSection(details);
    }

    html += `
          </div>
        </div>
      </div>
    `;
    
    return html;
  }

  private generateWorldHexHtml(hex: any): string {
    let html = '<div class="world-hex-info">';
    
    if (hex.biome) {
      html += `<p><strong>Biome:</strong> ${hex.biome}</p>`;
    }
    
    if (hex.features && hex.features.length > 0) {
      html += `
        <div class="hex-features">
          <h3>Features:</h3>
          <ul>
            ${hex.features.map((feature: string) => `<li>${feature}</li>`).join('')}
          </ul>
        </div>
      `;
    }
    
    html += '</div>';
    return html;
  }

  private generateCityHexHtml(hex: any): string {
    let html = '';
    
    if (hex.cityName) {
      html += `
        <div class="ascii-section ascii-hex-city-name">
          <span>CITY NAME:</span>
          <pre>${hex.cityName}</pre>
        </div>
      `;
    }
    
    if (hex.population) {
      html += `
        <div class="ascii-section ascii-hex-population">
          <span>POPULATION:</span>
          <pre>${hex.population}</pre>
        </div>
      `;
    }
    
    if (hex.buildings && hex.buildings.length > 0) {
      html += `
        <div class="ascii-section ascii-hex-buildings">
          <span>BUILDINGS:</span>
          <pre>${hex.buildings.join('\n')}</pre>
        </div>
      `;
    }
    
    return html;
  }

  private generateDetailsSection(details: any): string {
    let html = '';
    
    // Handle different types of details
    if (details.encounter) {
      html += `
        <div class="ascii-section ascii-hex-encounter">
          <span>ENCOUNTER:</span>
          <pre>${this.formatContent(details.encounter)}</pre>
        </div>
      `;
    }
    
    if (details.denizen) {
      html += `
        <div class="ascii-section ascii-hex-denizen">
          <span>DENIZEN:</span>
          <pre>${this.formatContent(details.denizen)}</pre>
        </div>
      `;
    }
    
    if (details.description) {
      html += `
        <div class="ascii-section ascii-hex-description">
          <span>DESCRIPTION:</span>
          <pre>${this.formatContent(details.description)}</pre>
        </div>
      `;
    }
    
    if (details.loot) {
      html += `
        <div class="ascii-section ascii-hex-loot">
          <span>LOOT:</span>
          <pre>${this.formatLoot(details.loot)}</pre>
        </div>
      `;
    }
    
    if (details.treasure) {
      html += `
        <div class="ascii-section ascii-hex-treasure">
          <span>TREASURE:</span>
          <pre>${this.formatLoot(details.treasure)}</pre>
        </div>
      `;
    }
    
    return html;
  }

  private formatContent(content: any): string {
    if (typeof content === 'string') return content;
    if (typeof content === 'object' && content !== null) {
      return content.html || content.raw || JSON.stringify(content, null, 2);
    }
    return '';
  }

  private formatLoot(lootData: any): string {
    if (typeof lootData === 'string') return lootData;
    if (typeof lootData === 'object' && lootData !== null) {
      if (lootData.type && lootData.item && lootData.description) {
        return `Type: ${lootData.type}\nItem: ${lootData.item}\nDescription: ${lootData.description}\nFull Description: ${lootData.full_description || lootData.description}`;
      }
      return JSON.stringify(lootData, null, 2);
    }
    return '';
  }

  public clearContent(): void {
    this.showWelcomeMessage();
  }
} 