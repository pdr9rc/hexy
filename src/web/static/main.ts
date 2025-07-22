// web/static/main.ts
import { renderMapGrid } from './mapRenderer.js';
import { renderHexDetails } from './hexViewer.js';
import { setupControls } from './controls.js';
import * as ui from './uiUtils.js';

export interface HexData {
  x: number;
  y: number;
  terrain: string;
  symbol: string;
  is_city: boolean;
  has_content: boolean;
  content_type?: string;
  css_class: string;
  city_name?: string;
}

export class DyingLandsApp {
  mapData: { [hexCode: string]: HexData } = {};
  mapWidth: number = 0;
  mapHeight: number = 0;
  currentHex: string = '';

  constructor() {
    console.log('🔧 DyingLandsApp constructor starting...');
    this.loadMapData();
    console.log('🗺️ Map data loaded, width:', this.mapWidth, 'height:', this.mapHeight);
    console.log('🗺️ Map data keys:', Object.keys(this.mapData).length);
    renderMapGrid(this);
    console.log('🎮 Setting up controls...');
    setupControls(this);
    this.showEmptyState();
    ui.hideLoading();
    console.log('🗺️ Dying Lands App initialized');
  }

  loadMapData() {
    console.log('📊 Loading map data...');
    const mapDataElement = document.getElementById('mapData');
    if (mapDataElement) {
      console.log('📊 Found mapData element');
      const mapJson = mapDataElement.getAttribute('data-map');
      console.log('📊 Map JSON length:', mapJson?.length || 0);
      if (mapJson && mapJson.trim().length > 0) {
        try {
          this.mapData = JSON.parse(mapJson);
          console.log('📊 Successfully parsed map data');
        } catch (e) {
          console.error('❌ Invalid map JSON:', mapJson, e);
          this.mapData = {};
        }
      } else {
        console.warn('⚠️ No map data found in #mapData element.');
        this.mapData = {};
      }
      this.mapWidth = parseInt(mapDataElement.getAttribute('data-width') || '0');
      this.mapHeight = parseInt(mapDataElement.getAttribute('data-height') || '0');
      console.log('📊 Map dimensions:', this.mapWidth, 'x', this.mapHeight);
    } else {
      console.error('❌ mapData element not found!');
    }
  }

  onHexClick(hexCode: string) {
    console.log('🖱️ Hex clicked:', hexCode);
    this.currentHex = hexCode;
    renderHexDetails(this, hexCode);
    this.highlightSelectedHex(hexCode);
  }

  highlightSelectedHex(hexCode: string) {
    document.querySelectorAll('.hex-cell.selected').forEach(el => el.classList.remove('selected'));
    const el = document.querySelector(`.hex-cell[data-hex="${hexCode}"]`);
    if (el) el.classList.add('selected');
  }

  restoreMap() {
    const mapContainer = document.querySelector('.map-container');
    if (!mapContainer) return;
    
    const originalContent = mapContainer.getAttribute('data-original-content');
    
    if (originalContent) {
      mapContainer.innerHTML = originalContent;
      mapContainer.removeAttribute('data-original-content');
      // Re-render the map grid after restoration
      import('./mapRenderer.js').then(({ renderMapGrid }) => {
        renderMapGrid(this);
      });
    } else {
      // Fallback: reload the page
      window.location.reload();
    }
  }

  showCityOverlayInMap(hexCode: string) {
    // TODO: Implement city overlay functionality
    console.log('City overlay for hex:', hexCode);
    alert('City overlay functionality coming soon!');
  }

  showEmptyState() {
    const container = document.getElementById('modalContainer');
    if (container) {
      container.innerHTML = `<div class="empty-state">
        <h2>Select a Hex</h2>
        <p>Click on any hex on the map to view its details, encounters, and lore.</p>
        <div class="ascii-modal">
╔══════════════════════════════════════════════════════════════╗
║                    THE DYING LANDS                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Click a hex to explore its mysteries...                    ║
║                                                              ║
║  Each hex contains unique encounters, denizens,             ║
║  and secrets waiting to be discovered.                      ║
║                                                              ║
║  The world is dying, but adventure lives on.                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        </div>
      </div>`;
    }
  }
}

// --- Bootstrap ---
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 DOM loaded, checking for mapData element...');
  if (document.getElementById('mapData')) {
    console.log('✅ mapData element found, creating app...');
    (window as any).app = new DyingLandsApp();
    console.log('✅ App created and assigned to window.app');
  } else {
    console.error('❌ mapData element not found on DOM load!');
  }
}); 