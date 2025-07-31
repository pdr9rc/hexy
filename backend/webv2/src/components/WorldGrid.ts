import type { WorldHex, HexCoordinate } from '@/models/types';
import { worldGridService } from '@/services/WorldGridService';

export class WorldGrid {
  private container: HTMLElement;
  private gridElement: HTMLElement;
  private hexes: Map<string, HTMLElement> = new Map();
  private hexClickCallback?: (coordinate: HexCoordinate) => void;

  constructor() {
    this.container = document.getElementById('world-grid-container') as HTMLElement;
    this.gridElement = document.createElement('div');
    this.gridElement.className = 'hex-grid';
    this.container.appendChild(this.gridElement);
    
    this.initialize();
  }

  private initialize(): void {
    this.setupEventListeners();
    this.subscribeToGridChanges();
  }

  private setupEventListeners(): void {
    // Listen for hex clicks
    this.gridElement.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      if (target.classList.contains('hex-cell') || target.classList.contains('hex-container')) {
        const coordinate = this.getHexCoordinate(target);
        if (coordinate && this.hexClickCallback) {
          this.hexClickCallback(coordinate);
        }
      }
    });
  }

  private subscribeToGridChanges(): void {
    worldGridService.subscribe((grid) => {
      this.renderGrid(grid);
    });
  }

  private getHexCoordinate(hexElement: HTMLElement): HexCoordinate | null {
    const q = parseInt(hexElement.dataset.q || '0');
    const r = parseInt(hexElement.dataset.r || '0');
    const s = parseInt(hexElement.dataset.s || '0');
    
    if (isNaN(q) || isNaN(r) || isNaN(s)) {
      return null;
    }
    
    return { q, r, s };
  }

  private renderGrid(grid: any): void {
    if (!grid || !grid.hexes) {
      this.gridElement.innerHTML = '<div class="text-center p-3">No world grid available</div>';
      return;
    }

    this.gridElement.innerHTML = '';
    this.hexes.clear();

    // Group hexes by row (r coordinate)
    const hexesByRow = new Map<number, WorldHex[]>();
    grid.hexes.forEach((hex: WorldHex) => {
      const row = hex.coordinate.r;
      if (!hexesByRow.has(row)) {
        hexesByRow.set(row, []);
      }
      hexesByRow.get(row)!.push(hex);
    });

    // Sort rows and hexes within each row
    const sortedRows = Array.from(hexesByRow.keys()).sort((a, b) => a - b);
    
    sortedRows.forEach((rowIndex) => {
      const rowHexes = hexesByRow.get(rowIndex)!.sort((a, b) => a.coordinate.q - b.coordinate.q);
      
      const rowElement = document.createElement('div');
      rowElement.className = 'hex-row';
      
      rowHexes.forEach((hex: WorldHex) => {
        const hexContainer = this.createHexContainer(hex);
        rowElement.appendChild(hexContainer);
      });
      
      this.gridElement.appendChild(rowElement);
    });
  }

  private createHexContainer(hex: WorldHex): HTMLElement {
    const hexContainer = document.createElement('div');
    hexContainer.className = 'hex-container';
    hexContainer.setAttribute('data-hex', `${hex.coordinate.q.toString().padStart(2, '0')}${hex.coordinate.r.toString().padStart(2, '0')}`);
    
    const hexElement = this.createHexElement(hex);
    hexContainer.appendChild(hexElement);
    
    // Store reference for selection updates
    this.hexes.set(`${hex.coordinate.q},${hex.coordinate.r},${hex.coordinate.s}`, hexElement);
    
    return hexContainer;
  }

  private createHexElement(hex: WorldHex): HTMLElement {
    const hexElement = document.createElement('span');
    hexElement.className = `hex-cell ${hex.terrain}`;
    hexElement.dataset.q = hex.coordinate.q.toString();
    hexElement.dataset.r = hex.coordinate.r.toString();
    hexElement.dataset.s = hex.coordinate.s.toString();
    hexElement.setAttribute('data-hex', `${hex.coordinate.q.toString().padStart(2, '0')}${hex.coordinate.r.toString().padStart(2, '0')}`);
    hexElement.tabIndex = 0;

    // Add terrain and content classes
    if (hex.terrain) {
      hexElement.classList.add(`terrain-${hex.terrain}`);
    }
    if (hex.is_city) {
      hexElement.classList.add('major-city');
    }
    if (hex.has_content) {
      hexElement.classList.add('has-content');
    } else {
      hexElement.classList.add('no-content');
    }

    // Add selection class if selected
    if (hex.isSelected) {
      hexElement.classList.add('selected');
    }

    // Set hex content
    const content = this.getHexContent(hex);
    hexElement.textContent = content;
    hexElement.title = hex.is_city ? `HEX ${hex.id} - ${hex.city_name || 'City'}` : `HEX ${hex.id}`;

    // Add floating city name if it's a city
    if (hex.is_city && hex.city_name) {
      const cityName = document.createElement('div');
      cityName.className = 'city-name-label';
      cityName.textContent = hex.city_name;
      cityName.title = hex.city_name;
      hexElement.appendChild(cityName);
    }

    return hexElement;
  }

  private getHexContent(hex: WorldHex): string {
    // Simple content display - can be enhanced later
    if (hex.terrain === 'city') {
      return '🏙️';
    }
    
    const terrainSymbols: Record<string, string> = {
      forest: '🌲',
      mountain: '⛰️',
      plains: '🌾',
      desert: '🏜️',
      water: '🌊',
      swamp: '🌿'
    };

    return terrainSymbols[hex.terrain] || '⬡';
  }

  public onHexClick(callback: (coordinate: HexCoordinate) => void): void {
    this.hexClickCallback = callback;
  }

  public updateHexSelection(coordinate: HexCoordinate): void {
    // Clear all selections
    this.hexes.forEach(hexElement => {
      hexElement.classList.remove('selected');
    });

    // Select the target hex
    const hexKey = `${coordinate.q},${coordinate.r},${coordinate.s}`;
    const hexElement = this.hexes.get(hexKey);
    if (hexElement) {
      hexElement.classList.add('selected');
    }
  }

  public loadGrid(): void {
    worldGridService.loadWorldGrid();
  }

  public generateGrid(width: number, height: number): void {
    worldGridService.generateWorldGrid(width, height);
  }
} 