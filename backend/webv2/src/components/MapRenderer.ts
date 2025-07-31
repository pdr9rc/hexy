import type { HexData } from '@/models/types';

export class MapRenderer {
  private gridElement: HTMLElement;
  private mapData: { [key: string]: HexData } = {};
  private mapWidth: number = 30;
  private mapHeight: number = 25;
  private hexClickCallback?: (hexCode: string) => void;

  constructor(gridElement: HTMLElement) {
    this.gridElement = gridElement;
  }

  public setMapData(mapData: { [key: string]: HexData }): void {
    this.mapData = mapData;
  }

  public setDimensions(width: number, height: number): void {
    this.mapWidth = width;
    this.mapHeight = height;
  }

  public onHexClick(callback: (hexCode: string) => void): void {
    this.hexClickCallback = callback;
  }

  public renderMap(): void {
    this.gridElement.innerHTML = '';
    
    // Render map rows
    for (let y = 1; y <= this.mapHeight; y++) {
      const rowDiv = document.createElement('div');
      rowDiv.className = 'hex-row';
      
      for (let x = 1; x <= this.mapWidth; x++) {
        const hexCode = x.toString().padStart(2, '0') + y.toString().padStart(2, '0');
        const hex: HexData = this.mapData[hexCode];
        
        // Create hex container for positioning
        const hexContainer = document.createElement('div');
        hexContainer.className = 'hex-container';
        hexContainer.setAttribute('data-hex', hexCode);
        
        const span = document.createElement('span');
        span.className = 'hex-cell';
        span.setAttribute('data-hex', hexCode);
        span.tabIndex = 0;
        
        if (hex) {
          // Apply CSS classes
          hex.css_class.split(' ').forEach((cls: string) => {
            if (cls) span.classList.add(cls);
          });
          
          if (hex.is_city) span.classList.add('major-city');
          if (hex.content_type === 'settlement') span.classList.add('settlement');
          if (hex.has_content) span.classList.add('has-content');
          
          span.textContent = hex.symbol;
          span.title = hex.is_city ? `HEX ${hexCode} - ${hex.city_name}` : `HEX ${hexCode}`;
          
          // Add floating city name if it's a city
          if (hex.is_city && hex.city_name) {
            const cityName = document.createElement('div');
            cityName.className = 'city-name-label';
            cityName.textContent = hex.city_name;
            cityName.title = hex.city_name;
            hexContainer.appendChild(cityName);
          }
        } else {
          span.classList.add('terrain-unknown', 'no-content');
          span.textContent = '?';
          span.title = `HEX ${hexCode}`;
        }
        
        // Add click event listener
        span.addEventListener('click', () => {
          if (this.hexClickCallback) {
            this.hexClickCallback(hexCode);
          }
        });
        
        hexContainer.appendChild(span);
        rowDiv.appendChild(hexContainer);
      }
      
      this.gridElement.appendChild(rowDiv);
    }
  }

  public selectHex(hexCode: string): void {
    // Clear previous selection
    const allHexes = this.gridElement.querySelectorAll('.hex-cell');
    allHexes.forEach(hex => hex.classList.remove('selected'));
    
    // Select the target hex
    const targetHex = this.gridElement.querySelector(`[data-hex="${hexCode}"]`) as HTMLElement;
    if (targetHex) {
      targetHex.classList.add('selected');
    }
  }

  public clearSelection(): void {
    const allHexes = this.gridElement.querySelectorAll('.hex-cell');
    allHexes.forEach(hex => hex.classList.remove('selected'));
  }

  public getHexElement(hexCode: string): HTMLElement | null {
    return this.gridElement.querySelector(`[data-hex="${hexCode}"]`) as HTMLElement;
  }

  public updateHex(hexCode: string, hexData: HexData): void {
    const hexElement = this.getHexElement(hexCode);
    if (!hexElement) return;

    // Clear existing classes
    hexElement.className = 'hex-cell';
    
    // Apply new classes
    hexData.css_class.split(' ').forEach((cls: string) => {
      if (cls) hexElement.classList.add(cls);
    });
    
    if (hexData.is_city) hexElement.classList.add('major-city');
    if (hexData.content_type === 'settlement') hexElement.classList.add('settlement');
    if (hexData.has_content) hexElement.classList.add('has-content');
    
    // Update content
    hexElement.textContent = hexData.symbol;
    hexElement.title = hexData.is_city ? `HEX ${hexCode} - ${hexData.city_name}` : `HEX ${hexCode}`;
  }

  public highlightHexes(hexCodes: string[]): void {
    // Clear previous highlights
    const allHexes = this.gridElement.querySelectorAll('.hex-cell');
    allHexes.forEach(hex => hex.classList.remove('highlighted'));
    
    // Highlight target hexes
    hexCodes.forEach(hexCode => {
      const hexElement = this.getHexElement(hexCode);
      if (hexElement) {
        hexElement.classList.add('highlighted');
      }
    });
  }

  public clearHighlights(): void {
    const allHexes = this.gridElement.querySelectorAll('.hex-cell');
    allHexes.forEach(hex => hex.classList.remove('highlighted'));
  }
} 