// web/static/main.ts
import { getCityOverlay, getCityOverlayHex, updateHex } from "./api.js"
import { apiGet, apiPost } from './utils/apiUtils.js'
import { showHexDetails as renderHexDetails, showCityDetails, showSettlementDetails } from "./hexViewer.js"
import { renderMap } from "./mapRenderer.js"
import { initializeControls } from "./controls.js"
import { showNotification, showError } from "./uiUtils.js"
import { showCityOverlayGrid } from './cityOverlays.js';
import { generateDistrictColor } from './utils/colorUtils.js';
import { t, getCurrentLanguage } from './translations.js';
import { SandboxStore, getSandboxId } from './utils/sandboxStore.js';
import { prefetchAllHexMarkdown } from './utils/prefetch.js';

// Global state for hex editing
let currentEditingHex: string | null = null;
let originalHexContent: string | null = null;

interface HexData {
  x: number
  y: number
  terrain: string
  symbol: string
  is_city: boolean
  city_name?: string
  population?: string
  region?: string
  has_content: boolean
  content_type?: string
  css_class: string
}

interface CityOverlayData {
  name: string
  display_name: string
  filename: string
  grid_type: string
  radius: number
  hex_grid: { [key: string]: any }
  total_hexes: number
  hexCode?: string
  districts?: Array<{
    name: string
    description: string
    theme: string
    buildings: string[]
    streets: string[]
  }>
}

export type { HexData };

class DyingLandsApp {
  public mapData: { [key: string]: HexData } = {}
  public mapWidth = 30
  public mapHeight = 25
  private currentView: "world" | "city" = "world"
  private currentCityOverlay: CityOverlayData | null = null
  private selectedCityHex: string | null = null

  constructor() {
    this.initializeApp()
  }

  private initializeApp(): void {
    console.log("🗺️ Initializing The Dying Lands...")

    // Get map data from template
    const mapDataElement = document.getElementById("map-data")
    if (mapDataElement) {
      try {
        this.mapData = JSON.parse(mapDataElement.textContent || "{}")
        console.log(`📊 Loaded ${Object.keys(this.mapData).length} hexes`)
      } catch (error) {
        console.error("❌ Failed to parse map data:", error)
        showError("Failed to load map data")
      }
    }

    // Get map dimensions
    const dimensionsElement = document.getElementById("map-dimensions")
    if (dimensionsElement) {
      try {
        const dimensions = JSON.parse(dimensionsElement.textContent || "[30, 25]")
        this.mapWidth = dimensions[0]
        this.mapHeight = dimensions[1]
      } catch (error) {
        console.error("❌ Failed to parse map dimensions:", error)
      }
    }

    // Initialize components
    this.initializeEventListeners()
    // Try to hydrate map from sandbox; fallback to server-rendered mapData
    void (async () => {
      const cached = await SandboxStore.loadWorldMap();
      if (cached && Object.keys(cached).length) {
        this.mapData = cached as any;
      }
      this.renderWorldMap()
    })();
    this.updateWorldMapControlsVisibility()
    initializeControls(this)

    // Begin background prefetch of all hex markdown for offline/local-first usage
    void (async () => {
      try {
        await prefetchAllHexMarkdown((p) => {
          if (p.total > 0 && p.processed % 200 === 0) {
            console.log(`Prefetch progress: ${p.processed}/${p.total}`);
          }
        });
      } catch (e: any) {
        console.warn('Prefetch error:', e?.message || e);
      }
    })();

    console.log("✅ The Dying Lands initialized successfully")
  }

  private initializeEventListeners(): void {
    // Handle hex clicks
    document.addEventListener("click", (event) => {
      const target = event.target as HTMLElement

      if (target.classList.contains("hex-cell") || target.classList.contains("hex-container")) {
        this.handleHexClick(target)
      } else if (target.classList.contains("city-hex-cell")) {
        this.handleCityHexClick(target)
      }
    })

    // Handle navigation buttons
    document.addEventListener("click", (event) => {
      const target = event.target as HTMLElement

      if (target.id === "back-to-world" || target.closest("#back-to-world")) {
        this.showWorldMap()
      } else if (target.id === "city-overlay-btn" || target.closest("#city-overlay-btn")) {
        const hexCode = target.getAttribute("data-hex-code") || target.closest("#city-overlay-btn")?.getAttribute("data-hex-code")
        if (hexCode) {
          this.showCityOverlayInMap(hexCode)
        }
      } else if (target.hasAttribute("data-action")) {
        const action = target.getAttribute("data-action")
        console.log("Button clicked with action:", action)
        switch (action) {
          case "map-grid":
            console.log("Calling renderCityOverlay")
            const hexCode = this.currentCityOverlay?.hexCode
            this.renderCityOverlay(hexCode)
            break
          case "return-to-hex":
            console.log("Calling showHexDetails")
            this.showHexDetails()
            break
          case "return-to-map":
            console.log("Calling restoreMap")
            this.restoreMap()
            break
        }
      }
    })
  }

  private handleHexClick(hexElement: HTMLElement): void {
    // Handle both hex-cell and hex-container clicks
    const hexCode = hexElement.getAttribute("data-hex") || hexElement.querySelector('.hex-cell')?.getAttribute("data-hex")
    if (!hexCode) return
    
    // Call selectHexCell with fallback options
    const selectHexCellFn = (window as any).selectHexCell || (window as any).app?.selectHexCell;
    if (selectHexCellFn) {
      selectHexCellFn(hexCode); // Ensure selected class is applied on click
    }

    const hexData = this.mapData[hexCode]
    if (!hexData) return

    if (hexData.is_city) {
      showCityDetails(this, hexCode)
    } else if (hexData.content_type === "settlement") {
      showSettlementDetails(this, hexCode)
            } else {
          renderHexDetails(this, hexCode)
        }
  }

  private handleCityHexClick(hexElement: HTMLElement): void {
    const hexId = hexElement.getAttribute("data-hex-id")
    const overlayName = hexElement.getAttribute("data-overlay")

    if (!hexId || !overlayName) return

    // Immediate visual feedback: toggle selected class
    document.querySelectorAll('.city-hex-cell.city-hex-selected').forEach(el => el.classList.remove('city-hex-selected'))
    hexElement.classList.add('city-hex-selected')

    this.showCityHexDetails(overlayName, hexId)
  }

  public async showCityHexDetails(overlayName: string, hexId: string): Promise<void> {
    try {
      console.log('🔍 showCityHexDetails called with:', { overlayName, hexId });
      
      // Call the API directly to get enriched hex data
      const data: any = await apiGet(`api/city-overlay/${overlayName}/hex/${hexId}`);
      console.log('📦 API response:', data);
      
      if (data.success && data.hex) {
        // Update selected hex
        this.selectedCityHex = hexId;
        
        // Refresh the city grid to show selection
        if (this.currentCityOverlay) {
          this.renderCityOverlay(this.currentCityOverlay.hexCode);
        }
        
        // Build the view directly from the API data
        this.buildHexDetailsView(data.hex, overlayName);
      } else {
        showError("Failed to load city hex details")
      }
    } catch (error) {
      console.error("Error loading city hex details:", error)
      showError("Failed to load city hex details")
    }
  }

  private buildHexDetailsView(hexData: any, overlayName?: string): void {
    console.log('🎯 buildHexDetailsView called with:', { hexData, overlayName });
    const detailsPanel = document.getElementById("details-panel")
    if (!detailsPanel) return

    const content = hexData.content || {}
    console.log('📦 Content data:', content);
    const hexId = hexData.id || hexData.hex_id || "?"
    const terrain = content.terrain || "?"
    const type = content.type || "?"
    const name = content.name || "?"
    const description = content.description || ""
    const encounter = content.encounter || ""
    const atmosphere = content.atmosphere || ""
    const features = (content.notable_features && content.notable_features.length > 0) ? content.notable_features.join("\n") : ""
    const npcs = (content.npcs && content.npcs.length > 0) ? content.npcs.join("\n") : ""
    const randomEvents = (content.random_table && content.random_table.length > 0) ? content.random_table.join("\n") : ""
    const position = hexData.position || "?"
    const positionType = content.position_type || "?"
    const district = hexData.district || "?"

    // Update district details in city overlay if we're in city view
    if (this.currentView === "city") {
      this.updateDistrictDetails(hexData)
    }

    let html = `
      <div class="city-hex-details-box">
        <div class="ascii-box">
          <div class="ascii-inner-box">
            <div class="mb-4" style="text-align:center;">
              <button class="btn-mork-borg me-2" onclick="window.app.showHexDetails('${overlayName || ''}')">RETURN TO HEX</button>
              <button class="btn-mork-borg btn-warning" onclick="window.app.restoreMap()">RETURN TO MAP</button>
            </div>
            
            <!-- Basic Information Section -->
            <div class="ascii-section ascii-hex-title">
              <span>${content.name || name}</span>
            </div>
            <div class="ascii-section ascii-hex-type">
              <span>${t('TYPE')} ${content.type || type}</span>
            </div>
            <div class="ascii-section ascii-hex-district">
              <span>${t('DISTRICT')} ${hexData.district || district}</span>
            </div>
            <div class="ascii-section ascii-hex-position">
              <span>${t('POSITION')} ${content.position_type || positionType}</span>
            </div>
            
            <!-- Description Section -->
            <div class="ascii-section ascii-hex-description">
              <span>${t('DESCRIPTION')}</span>
              <div class="ascii-content">${content.description || description}</div>
            </div>
            
            <!-- Atmosphere & Encounter Section -->
            <div class="ascii-section ascii-hex-atmosphere">
              <span>${t('ATMOSPHERE')}</span>
              <div class="ascii-content">${content.atmosphere || atmosphere || 'No atmosphere available.'}</div>
            </div>
            <div class="ascii-section ascii-hex-encounter">
              <span>${t('ENCOUNTER')}</span>
              <div class="ascii-content">${content.encounter || encounter}</div>
            </div>
    `

    // Notable Features Section (hex-specific)
    if (content.notable_features && content.notable_features.length > 0) {
      html += `
        <div class="ascii-section ascii-hex-features">
          <span>NOTABLE FEATURES:</span>
          <div class="ascii-content">${content.notable_features.join('\n')}</div>
        </div>
      `;
    }

                  // NPC Information Section
              if (content.npc_trait || content.npc_concern || content.npc_want || content.npc_secret || content.npc_name || content.npc_trade || content.npc_affiliation || content.npc_attitude) {
                html += `
                  <div class="ascii-section ascii-hex-npcs">
                    <span>NPC INFORMATION:</span>
                    <div class="ascii-content">
                `;
                
                if (content.npc_name) {
                  html += `NAME: ${content.npc_name}\n`;
                }
                if (content.npc_trade) {
                  html += `TRADE: ${content.npc_trade}\n`;
                }
                if (content.npc_trait) {
                  html += `TRAIT: ${content.npc_trait}\n`;
                }
                if (content.npc_concern) {
                  html += `CONCERN: ${content.npc_concern}\n`;
                }
                if (content.npc_want) {
                  html += `WANT: ${content.npc_want}\n`;
                }
                if (content.npc_secret) {
                  html += `SECRET: ${content.npc_secret}\n`;
                }
                if (content.npc_affiliation) {
                  html += `AFFILIATION: ${content.npc_affiliation}\n`;
                }
                if (content.npc_attitude) {
                  html += `ATTITUDE: ${content.npc_attitude}\n`;
                }
                
                html += `
                    </div>
                  </div>
                `;
              }

    // Tavern Details Section (for taverns only)
    if (content.type === 'tavern' && (content.tavern_menu || content.tavern_innkeeper || content.tavern_patron)) {
      html += `
        <div class="ascii-section ascii-hex-tavern">
          <span>TAVERN DETAILS:</span>
          <div class="ascii-content">
      `;
      
      if (content.tavern_menu) {
        html += `MENU: ${content.tavern_menu}\n`;
      }
      if (content.tavern_innkeeper) {
        html += `INNKEEPER: ${content.tavern_innkeeper}\n`;
      }
      if (content.tavern_patron) {
        html += `NOTABLE PATRON: ${content.tavern_patron}\n`;
      }
      
      html += `
          </div>
        </div>
      `;
    }

    // Market Items Section (for markets)
    if (content.type === 'market' && (content.items_sold || content.beast_prices || content.services)) {
      html += `
        <div class="ascii-section ascii-hex-market">
          <span>${t('MARKET DETAILS')}</span>
          <div class="ascii-content">
      `;
      
      // Helper to format arrays of strings or objects
      const formatEntries = (arr: any[]): string => {
        const lang = getCurrentLanguage();
        const currencyLabel = (c: string): string => {
          if (lang === 'pt') {
            if (!c) return c;
            const m = c.toLowerCase();
            if (m === 'silver') return 'prata';
            if (m === 'gold') return 'ouro';
            if (m === 'copper') return 'cobre';
          }
          return c;
        };
        if (!Array.isArray(arr)) return '';
        return arr.map((item: any) => {
          if (typeof item === 'string') return item;
          if (item && typeof item === 'object') {
            const name = item.name ?? '';
            const price = item.price ?? '';
            const currency = currencyLabel(item.currency ?? '');
            const notes = item.notes ?? '';
            const pricePart = [price, currency].filter(Boolean).join(' ');
            const main = [name, pricePart].filter(Boolean).join(' - ');
            return notes ? `${main} (${notes})` : main || JSON.stringify(item);
          }
          return String(item);
        }).join('\n');
      };

      if (content.items_sold && Array.isArray(content.items_sold) && content.items_sold.length) {
        html += `${t('ITEMS SOLD')}\n${formatEntries(content.items_sold)}\n`;
      }
      if (content.beast_prices && Array.isArray(content.beast_prices) && content.beast_prices.length) {
        html += `${t('BEAST PRICES')}\n${formatEntries(content.beast_prices)}\n`;
      }
      if (content.services && Array.isArray(content.services) && content.services.length) {
        html += `${t('SERVICES')}\n${formatEntries(content.services)}\n`;
      }
      
      html += `
          </div>
        </div>
      `;
    }

    // Services Section (for service locations)
    if (content.type === 'service' && content.services) {
      html += `
        <div class="ascii-section ascii-hex-services">
          <span>${t('SERVICES')}</span>
          <div class="ascii-content">${(() => {
            const arr = Array.isArray(content.services) ? content.services : [];
            const format = (a: any[]) => a.map((item: any) => {
              if (typeof item === 'string') return item;
              if (item && typeof item === 'object') {
                const name = item.name ?? '';
                const price = item.price ?? '';
                const currency = item.currency ?? '';
                const notes = item.notes ?? '';
                const pricePart = [price, currency].filter(Boolean).join(' ');
                const main = [name, pricePart].filter(Boolean).join(' - ');
                return notes ? `${main} (${notes})` : main || JSON.stringify(item);
              }
              return String(item);
            }).join('\n');
            return format(arr);
          })()}</div>
        </div>
      `;
    }

    // Patrons Section (for businesses with patrons)
    if (content.patrons) {
      html += `
        <div class="ascii-section ascii-hex-patrons">
          <span>${t('PATRONS')}</span>
          <div class="ascii-content">${content.patrons}</div>
        </div>
      `;
    }

    // Random Tables Section
    if (content.random_table && content.random_table.length > 0) {
      html += `
        <div class="ascii-section ascii-hex-random">
          <span>RANDOM ENCOUNTERS:</span>
          <div class="ascii-content">${content.random_table.join('\n')}</div>
        </div>
      `;
    }

    // Close the HTML structure
    html += `
          </div>
        </div>
      </div>
    `;
    
    detailsPanel.innerHTML = html

    // Ensure ascii-content blocks are touch-scrollable and show grab cursor on touchstart
    detailsPanel.querySelectorAll('.ascii-content').forEach((el) => {
      const block = el as HTMLElement
      block.style.maxHeight = block.style.maxHeight || '50vh'
      block.style.overflow = 'auto'
      ;(block.style as any).webkitOverflowScrolling = 'touch'
      block.style.touchAction = 'pan-y'
      block.addEventListener('touchstart', () => { block.style.cursor = 'grabbing' }, { passive: true })
      block.addEventListener('touchend', () => { block.style.cursor = '' }, { passive: true })
    })
  }

  private updateDistrictDetails(hexData: any): void {
    const districtDetailsSection = document.querySelector('.city-overlay-ascii-section pre')
    if (!districtDetailsSection || !hexData) return

    const content = hexData.content || {}
    const district = hexData.district || "Unknown"
    const description = content.description || "No description available."
    
    // Get district description from the city overlay data
    let districtDescription = description
    if (this.currentCityOverlay && this.currentCityOverlay.districts) {
      const districtData = this.currentCityOverlay.districts.find((d: any) => 
        d.name.toLowerCase() === district.toLowerCase()
      )
      if (districtData && districtData.description) {
        districtDescription = districtData.description
      }
    }

    districtDetailsSection.textContent = `${district.toUpperCase()}\n\n${districtDescription}`
  }

  public async regenerateHex(hexId: string, overlayName?: string): Promise<void> {
    console.log("regenerateHex called with", hexId, "overlayName:", overlayName);
    
    // Use provided overlay name or fall back to currentCityOverlay
    const targetOverlayName = overlayName || (this.currentCityOverlay ? this.currentCityOverlay.name : null);
    
    if (!targetOverlayName) {
      console.error("No overlay name provided and no current city overlay to regenerate hex");
      showNotification("Error: No city overlay context found", "error");
      return;
    }
    
    try {
      // Call the backend to regenerate the hex
      const result: any = await apiPost(`api/regenerate-hex/${targetOverlayName}/${hexId}`);
      if (result) {
        if (result.success) {
          // Update the current overlay with new hex data if it exists
          if (this.currentCityOverlay) {
            this.currentCityOverlay.hex_grid[hexId] = result.hex_data;
            
            // Refresh the display by re-rendering the city overlay
            this.renderCityOverlay();
          }
          
          // Show success notification
          console.log("Hex regenerated successfully");
          showNotification("Hex regenerated successfully", "info");
        } else {
          console.error("Failed to regenerate hex:", result.error);
          showNotification("Failed to regenerate hex: " + result.error, "error");
        }
      } else {
        console.error("Failed to regenerate hex:", result.error || 'unknown');
        showNotification("Failed to regenerate hex: " + (result.error || 'unknown'), "error");
      }
    } catch (error) {
      console.error("Error regenerating hex:", error);
      showNotification("Error regenerating hex: " + error, "error");
    }
  }

  private async loadCityOverlay(overlayName: string): Promise<CityOverlayData | null> {
    try {
      const response = await getCityOverlay(overlayName);
      if (response.success) {
        return response.overlay;
      } else {
        console.error("Failed to load city overlay:", response.error);
        return null;
      }
    } catch (error) {
      console.error("Error loading city overlay:", error);
      return null;
    }
  }

  public async showCityOverlayInMap(hexCode: string): Promise<void> {
    console.log("showCityOverlayInMap called with", hexCode)
    
    // Immediately disable zoom when entering city view
    if ((window as any).disableZoom) {
      (window as any).disableZoom();
    }
    
    this.currentView = "city"
    this.selectedCityHex = null // Clear selected hex when entering new city overlay
    this.updateWorldMapControlsVisibility()
    const overlayName = this.getOverlayNameFromHexCode(hexCode)
    
    if (overlayName) {
      this.currentCityOverlay = await this.loadCityOverlay(overlayName)
      if (this.currentCityOverlay) {
        this.currentCityOverlay.hexCode = hexCode
        this.renderCityOverlay(hexCode)
      }
    }
  }

  public getOverlayNameFromHexCode(hexCode: string): string {
    console.log('🔍 getOverlayNameFromHexCode called with hexCode:', hexCode);
    
    // Map hex codes to actual overlay names (based on existing overlay files)
    const cityMap: { [key: string]: string } = {
      '1427': 'galgenbeck',                    // Galgenbeck (14,27)
      '0507': 'allians',                       // Allians (5,7)
      '1017': 'schleswig',                     // Schleswig (10,17)
      '1507': 'bergen_chrypt',                 // Bergen Chrypt (15,7)
      '0814': 'valley_of_unfortunate_undead',  // Valley of Unfortunate Undead (8,14)
      '1513': 'graven_tosk',                   // Graven-Tosk (15,13)
      '2313': 'grift'                          // Grift (23,13)
    }
    
    // Check if we have a direct mapping for this hex code
    if (cityMap[hexCode]) {
      console.log('✅ Found direct mapping for hex', hexCode, '->', cityMap[hexCode]);
      return cityMap[hexCode]
    }
    
    // Fallback: check if hex data has city information
    const hexData = this.mapData[hexCode]
    console.log('📊 Hex data for', hexCode, ':', hexData);
    
    if (hexData && hexData.city_name) {
      const cityName = hexData.city_name.toLowerCase().replace(/\s+/g, "_")
      console.log('🏙️ City name from hex data:', cityName);
      
      // Map common city names to actual overlay names
      const nameMap: { [key: string]: string } = {
        'galgenbeck': 'galgenbeck',
        'allians': 'allians',
        'alliáns': 'allians',
        'schleswig': 'schleswig',
        'bergen_chrypt': 'bergen_chrypt',
        'bergen chrypt': 'bergen_chrypt',
        'valley_of_unfortunate_undead': 'valley_of_unfortunate_undead',
        'valley of unfortunate undead': 'valley_of_unfortunate_undead',
        'graven_tosk': 'graven_tosk',
        'graven-tosk': 'graven_tosk',
        'graven tosk': 'graven_tosk',
        'grift': 'grift'
      }
      
      if (nameMap[cityName]) {
        console.log('✅ Found name mapping for', cityName, '->', nameMap[cityName]);
        return nameMap[cityName]
      } else {
        console.log('❌ No name mapping found for', cityName);
        return cityName // Return the city name as-is instead of defaulting to galgenbeck
      }
    }
    
    console.log('❌ No hex data or city name found for', hexCode);
    return hexCode // Return the hex code as the overlay name instead of defaulting to galgenbeck
  }

  public renderCityOverlay(hexCode?: string): void {
    console.log("renderCityOverlay called")
    
    // Ensure zoom is disabled when rendering city overlay
    if ((window as any).disableZoom) {
      (window as any).disableZoom();
    }
    
    if (!this.currentCityOverlay) {
      console.error("No current city overlay to render")
      return
    }
    
    // Store the hex code for the RETURN TO HEX button
    if (hexCode) {
      this.currentCityOverlay.hexCode = hexCode
    }

    const mapContainer = document.querySelector(".map-container")
    const mapZoomContainer = document.getElementById("map-zoom-container")
    if (!mapContainer || !mapZoomContainer) return

    // Save original map content if not already saved
    if (!mapContainer.hasAttribute("data-original-content")) {
      const hexGrid = mapZoomContainer.querySelector('#hexGrid');
      if (hexGrid) {
        const contentToSave = hexGrid.innerHTML;
        console.log("Saving original content, length:", contentToSave.length);
        console.log("Content preview:", contentToSave.substring(0, 100));
        mapContainer.setAttribute("data-original-content", contentToSave);
      } else {
        console.warn("No hex grid found when trying to save original content");
      }
    }

    // Determine grid size from hex data and collect districts
    let gridSize = 10; // Changed from 5 to 10 for 10 vertical hexes
    const districts = new Set<string>();
    if (this.currentCityOverlay.hex_grid) {
      const rows = new Set<number>();
      const cols = new Set<number>();
      for (const hexId of Object.keys(this.currentCityOverlay.hex_grid)) {
        if (hexId.includes('_')) {
          const [row, col] = hexId.split('_').map(Number);
          const hexData = this.currentCityOverlay.hex_grid[hexId];
          const content = hexData?.content || {};
          // Only include hexes that have actual content
          if (hexData && content.name && content.name !== "Unknown") {
            rows.add(row);
            cols.add(col);
            // Collect district information
            if (hexData.district) {
              districts.add(hexData.district);
            }
          }
        }
      }
      // Ensure we have at least 10 rows for vertical hexes, but allow more if data requires it
      if (rows.size > 0 && cols.size > 0) {
        const maxRow = Math.max(...rows);
        const maxCol = Math.max(...cols);
        gridSize = Math.max(10, Math.max(maxRow, maxCol) + 1);
      }
    }

    // Convert districts set to array, filter out empty/unknown, and sort for consistent display
    const districtArray = Array.from(districts)
      .filter(district => district !== 'empty' && district !== 'unknown' && district !== 'Empty')
      .sort();

    // Create city overlay HTML using .city-overlay-grid and .city-overlay-row
    let html = `
      <div class="city-overlay-wrapper">
        <div class="city-overlay-content">
          <div class="city-overlay-container">
            <div class="city-overlay-header">
              <h2>⌂ ${this.currentCityOverlay.display_name}</h2>
              <div class="city-overlay-controls">
                <button class="btn-mork-borg" onclick="window.app.renderCityOverlay()">MAP GRID</button>
                <button class="btn-mork-borg" onclick="window.app.showHexDetails('${this.currentCityOverlay.hexCode || ''}')">RETURN TO HEX</button>
                <button class="btn-mork-borg btn-warning" onclick="window.app.restoreMap()">RETURN TO MAP</button>
              </div>
            </div>
            <div class="city-overlay-grid">
    `

    // Generate grid based on determined size - always generate 10 rows
    for (let row = 0; row < gridSize; row++) {
      html += '<div class="city-overlay-row">'
      
      for (let col = 0; col < gridSize; col++) {
        const hexId = `${row}_${col}`
        const hexData = this.currentCityOverlay.hex_grid[hexId]
        const content = hexData?.content || {}

        // Show all hexes but make empty ones invisible
        const symbol = this.getCityHexSymbol(content.type)
        const district = hexData.district || 'unknown'
        const isVisible = hexData && content.name && content.name !== "Unknown" && content.type !== "empty"
        const isSelected = this.selectedCityHex === hexId
        const cssClass = `city-hex-cell city-${content.type || "unknown"} district-${district.toLowerCase().replace(/\s+/g, '-')} ${isVisible ? '' : 'city-hex-invisible'} ${isSelected ? 'city-hex-selected' : ''}`
        const districtColor = this.generateDistrictColor(district)

        html += `
          <div class="${cssClass}" 
               data-hex-id="${hexId}" 
               data-overlay="${this.currentCityOverlay.name}"
               data-district="${district}"
               style="background: ${districtColor} !important;"
               title="${content.name || "Unknown"} (${content.type || "unknown"}) - ${district}"
               onclick="window.app.showCityHexDetails && window.app.showCityHexDetails('${this.currentCityOverlay.name}', '${hexId}')">
            <span class="city-hex-symbol">${symbol}</span>
          </div>
        `
      }
      html += '</div>'
    }

    html += `
        </div>
        <div class="city-overlay-ascii-box">
          <div class="city-overlay-ascii-inner-box">
            <div class="city-overlay-ascii-section">
              <span>SELECTED DISTRICT</span>
              <div class="ascii-content">Click on a hex to view district details and information.</div>
            </div>
          </div>
        </div>
      </div>
    `

    if (mapZoomContainer) {
      mapZoomContainer.innerHTML = html
    }

    this.currentView = "city"
    this.updateWorldMapControlsVisibility()
    this.updateDistrictButtonsVisibility()
    this.initializeEventListeners()
    if (this.currentCityOverlay.hexCode && this.currentCityOverlay.hex_grid[this.currentCityOverlay.hexCode]) {
      this.updateDistrictDetails(this.currentCityOverlay.hex_grid[this.currentCityOverlay.hexCode])
    }
    if ((window as any).disableZoom) { (window as any).disableZoom(); }

    // Add district buttons inside the city overlay wrapper
    console.log("DEBUG: districtArray:", districtArray);
    console.log("DEBUG: districtArray length:", districtArray.length);
    
    const districtButtonsHTML = `
      <div class="district-buttons-container">
        <div class="district-buttons-row">
          ${districtArray.map(district => `
            <button class="district-button" 
                    style="background: ${this.generateDistrictColor(district)} !important;"
                    title="${district}">
              ${district}
            </button>
          `).join('')}
        </div>
      </div>
    `

    console.log("DEBUG: districtButtonsHTML:", districtButtonsHTML);

    // Remove existing buttons before adding new ones
    const existingDistrictButtons = document.querySelector('.district-buttons-container');
    if (existingDistrictButtons) {
      existingDistrictButtons.remove();
    }
    
    // Add district buttons inside the city overlay wrapper
    const cityOverlayWrapper = document.querySelector('.city-overlay-wrapper');
    if (cityOverlayWrapper) {
      cityOverlayWrapper.insertAdjacentHTML('beforeend', districtButtonsHTML);
    }
    
    console.log("DEBUG: District buttons added to DOM");
    console.log("DEBUG: Current view:", this.currentView);
    console.log("DEBUG: District buttons container in DOM:", document.querySelector('.district-buttons-container'));
  }

  private getCityHexSymbol(contentType: string): string {
    switch (contentType.toLowerCase()) {
      case 'district':
        return '◆' // Diamond for districts
      case 'building':
        return '⌂' // House symbol for buildings
      case 'street':
        return '═' // Double line for streets
      case 'landmark':
        return '▲' // Triangle for landmarks
      case 'market':
        return '◊' // Lozenge for markets
      case 'temple':
        return '†' // Cross for temples
      case 'tavern':
        return '☺' // Smiley for taverns
      case 'guild':
        return '⚔' // Crossed swords for guilds
      case 'residence':
        return '⌂' // House symbol for residences
      case 'ruins':
        return '☒' // X mark for ruins
      default:
        return '?' // Question mark for unknown
    }
  }

  public showWorldMap(): void {
    console.log("showWorldMap called")
    this.currentView = "world"
    this.currentCityOverlay = null
    this.selectedCityHex = null // Clear selected hex when returning to world map
    this.renderWorldMap()
    
    // Re-enable zoom functionality for world view
    if ((window as any).enableZoom) {
      (window as any).enableZoom();
    }
    
    // Reset zoom when returning to world map
    if ((window as any).resetZoom) {
      (window as any).resetZoom();
    }
    
    showNotification("Returned to world map")
  }

  public showHexDetails(hexCode?: string): void {
    console.log("showHexDetails called with hexCode:", hexCode)
    
    if (hexCode && hexCode.trim() !== '') {
      // If a hex code is provided, show the hex details for that specific hex
      const hexData = this.mapData[hexCode]
      if (hexData) {
        if (hexData.is_city) {
          showCityDetails(this, hexCode)
        } else if (hexData.content_type === "settlement") {
          showSettlementDetails(this, hexCode)
        } else {
          // Use the imported showHexDetails function from hexViewer
          renderHexDetails(this, hexCode)
        }
      } else {
        showNotification("Hex not found")
      }
    } else {
      // Show the default empty state in the right panel
      const container = document.getElementById('details-panel');
      console.log("details-panel found:", container)
      if (container) {
        console.log("Setting innerHTML for details-panel")
        container.innerHTML = `
          <div class="city-hex-details-box">
            <div class="ascii-box">
              <div class="ascii-inner-box">
                <div class="ascii-section ascii-hex-title">
                  <span>THE DYING LANDS</span>
                </div>
                <div class="ascii-section ascii-hex-description">
                  <span>WELCOME TO THE HEXCRAWL</span>
                  <div class="ascii-content">
Click a hex to explore its mysteries...

Each hex contains unique encounters, denizens,
and secrets waiting to be discovered.

The world is dying, but adventure lives on.
                  </div>
                </div>
                <div class="ascii-section ascii-hex-instructions">
                  <span>INSTRUCTIONS</span>
                  <div class="ascii-content">
• Click any hex on the map to view its details
• Major cities (◆) have additional overlay views
• Settlements (⌂) provide local information
• Bold hexes contain special content
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
        console.log("innerHTML set successfully")
      } else {
        console.error("details-panel not found!")
      }
      showNotification("Returned to hex details view")
    }
  }

  private renderWorldMap(): void {
    renderMap(this)
    // Persist the current map locally for sandboxing
    void SandboxStore.saveWorldMap(this.mapData)
  }

  public showCityDetailsInMap(hexCode: string): void {
    console.log("showCityDetailsInMap called with", hexCode);
    showCityDetails(this, hexCode);
  }

  public restoreMap(): void {
    console.log("restoreMap called");
    
    // Get the map container and zoom container
    const mapContainer = document.querySelector(".map-container");
    const mapZoomContainer = document.getElementById("map-zoom-container");
    
    console.log("Map container found:", !!mapContainer);
    console.log("Map zoom container found:", !!mapZoomContainer);
    console.log("Has original content:", mapContainer?.hasAttribute("data-original-content"));
    
    if (mapContainer && mapContainer.hasAttribute("data-original-content")) {
      // Restore the original content to the zoom container
      if (mapZoomContainer) {
        const savedContent = mapContainer.getAttribute("data-original-content")!;
        console.log("Saved content length:", savedContent.length);
        console.log("Saved content preview:", savedContent.substring(0, 100));
        
        // Check if the saved content is just hex grid content or full zoom container content
        if (savedContent.includes('<div class="hex-row">')) {
          console.log("Detected hex grid content");
          // It's hex grid content, so we need to wrap it properly
          const hexGrid = mapZoomContainer.querySelector('#hexGrid');
          if (hexGrid) {
            console.log("Found existing hex grid, restoring content");
            hexGrid.innerHTML = savedContent;
          } else {
            console.log("No hex grid found, recreating structure");
            // If hex grid doesn't exist, recreate the proper structure
            mapZoomContainer.innerHTML = `<div class="hex-grid" id="hexGrid" aria-label="Hex Map Grid">${savedContent}</div>`;
          }
        } else {
          console.log("Detected full zoom container content");
          // It's full zoom container content
          mapZoomContainer.innerHTML = savedContent;
        }
      }
      mapContainer.removeAttribute("data-original-content");
    } else {
      console.log("No original content saved, re-rendering world map");
      // If no original content was saved, re-render the world map
      this.renderWorldMap();
    }
    
    this.currentView = "world";
    this.currentCityOverlay = null;
    this.updateWorldMapControlsVisibility();
    this.updateDistrictButtonsVisibility(); // Set initial visibility for district buttons
    this.initializeEventListeners();

    // Clean up district buttons when returning to world map
    const existingDistrictButtons = document.querySelector('.district-buttons-container');
    if (existingDistrictButtons) {
      existingDistrictButtons.remove();
    }
    
    // Re-enable zoom functionality for world view
    if ((window as any).enableZoom) {
      (window as any).enableZoom();
    }
    
    // Reset zoom when returning to world map
    if ((window as any).resetZoom) {
      (window as any).resetZoom();
    }
    
    showNotification("Returned to world map");
  }

  // Public methods for external access
  public getCurrentView(): "world" | "city" {
    return this.currentView
  }

  // Hex editing methods
  public editHexContent(hexCode: string): void {
    console.log('🔧 Starting edit for hex:', hexCode);
    
    const container = document.getElementById('details-panel');
    if (!container) return;

    // Find the markdown content; if missing, try to fetch raw markdown and inject
    let markdownContent = container.querySelector('.markdown-content pre, .markdown-content .ascii-content') as HTMLElement | null;
    const ensureMarkdownBlock = async (): Promise<HTMLElement | null> => {
      if (markdownContent) return markdownContent;
      try {
        const data: any = await apiGet(`api/hex/${hexCode}`);
        if (data && data.raw_markdown) {
          const block = document.createElement('div');
          block.className = 'markdown-content';
          const pre = document.createElement('pre');
          pre.className = 'ascii-content';
          pre.textContent = data.raw_markdown;
          block.appendChild(pre);
          container.appendChild(block);
          return pre as HTMLElement;
        }
      } catch (_) {}
      // Fallback: create an empty editable block so user can start a new file
      const block = document.createElement('div');
      block.className = 'markdown-content';
      const pre = document.createElement('pre');
      pre.className = 'ascii-content';
      pre.textContent = `# HEX ${hexCode}\n\nDESCRIPTION: \n\nENCOUNTER: \n\nNOTABLE FEATURES: \n`;
      block.appendChild(pre);
      container.appendChild(block);
      return pre as HTMLElement;
    };

    const proceed = async () => {
      markdownContent = await ensureMarkdownBlock();
      if (!markdownContent) {
        showError('No editable content found');
        return;
      }

      // Prefer locally cached edits if available
      let content = markdownContent.textContent || '';
      try {
        SandboxStore.getHexMarkdown(hexCode).then(localMd => {
          if (localMd) {
            content = localMd;
          }
        }).finally(() => {
          finalize(content);
        });
        return;
      } catch (_) {}
      finalize(content);

      function finalize(current: string) {
        originalHexContent = current;
        currentEditingHex = hexCode;

        // Replace the content with a textarea
        const textarea = document.createElement('textarea');
        textarea.value = current;
        textarea.style.width = '100%';
        textarea.style.minHeight = '300px';
        textarea.style.fontFamily = 'monospace';
        textarea.style.backgroundColor = '#1a1a1a';
        textarea.style.color = '#ffffff';
        textarea.style.border = '1px solid #333';
        textarea.style.padding = '10px';
        textarea.style.resize = 'vertical';

        markdownContent!.parentNode?.replaceChild(textarea, markdownContent!);

        // Show save/cancel buttons
        const saveBtn = document.getElementById('save-hex-btn') as HTMLElement | null;
        const cancelBtn = document.getElementById('cancel-hex-btn') as HTMLElement | null;
        const editBtn = container ? (container.querySelector('button[onclick*="editHexContent"]') as HTMLElement | null) : null;
        if (saveBtn) saveBtn.style.display = 'inline-block';
        if (cancelBtn) cancelBtn.style.display = 'inline-block';
        if (editBtn) editBtn.style.display = 'none';
      }
    };

    void proceed();
  }

  public async saveHexContent(hexCode: string): Promise<void> {
    console.log('💾 Saving hex content:', hexCode);
    
    const container = document.getElementById('details-panel');
    if (!container) { showError('No details panel'); return; }

    const textarea = container.querySelector('textarea');
    if (!textarea) {
      showError('No textarea found for editing');
      return;
    }

    const newContent = (textarea as HTMLTextAreaElement).value;

    try {
      await SandboxStore.saveHexMarkdown(hexCode, newContent);
      showNotification('Saved to your sandbox');
      
      // Refresh the hex details
      this.showHexDetails(hexCode);
      
      // Reset editing state
      currentEditingHex = null;
      originalHexContent = null;
    } catch (error) {
      console.error('Error saving hex content:', error);
      showError('Failed to save hex content');
    }
  }

  public cancelHexEdit(): void {
    console.log('❌ Canceling hex edit');
    
    const container = document.getElementById('details-panel');
    if (!container) return;

    const textarea = container.querySelector('textarea');
    if (!textarea) return;

    // Restore original content
    const pre = document.createElement('pre');
    pre.textContent = originalHexContent || '';
    textarea.parentNode?.replaceChild(pre, textarea);

    // Hide save/cancel buttons, show edit button
    const saveBtn = document.getElementById('save-hex-btn') as HTMLElement;
    const cancelBtn = document.getElementById('cancel-hex-btn') as HTMLElement;
    const editBtn = container.querySelector('button[onclick*="editHexContent"]') as HTMLElement;
    
    if (saveBtn) saveBtn.style.display = 'none';
    if (cancelBtn) cancelBtn.style.display = 'none';
    if (editBtn) editBtn.style.display = 'inline-block';

    // Reset editing state
    currentEditingHex = null;
    originalHexContent = null;
  }

  private updateWorldMapControlsVisibility(): void {
    const worldMapControls = document.querySelector('.world-map-controls');
    if (worldMapControls) {
      if (this.currentView === "city") {
        worldMapControls.classList.add('city-view');
      } else {
        worldMapControls.classList.remove('city-view');
      }
    }
  }

  private updateDistrictButtonsVisibility(): void {
    const districtButtons = document.querySelector('.district-buttons-container');
    console.log("DEBUG: updateDistrictButtonsVisibility called");
    console.log("DEBUG: currentView:", this.currentView);
    console.log("DEBUG: districtButtons found:", !!districtButtons);
    if (districtButtons) {
      if (this.currentView === "city") {
        districtButtons.classList.remove('world-view');
        console.log("DEBUG: Removed world-view class");
      } else {
        districtButtons.classList.add('world-view');
        console.log("DEBUG: Added world-view class");
      }
    }
  }

  public getMapData(): { [key: string]: HexData } {
    return this.mapData
  }

  public onHexClick(hexCode: string): void {
    console.log("onHexClick called with", hexCode);
    this.restoreMap();
    setTimeout(() => {
      const hexElement = document.querySelector(`[data-hex='${hexCode}']`) as HTMLElement;
      if (hexElement) {
        this.handleHexClick(hexElement);
      } else {
        console.warn(`Hex element with code ${hexCode} not found in DOM.`);
      }
    }, 50);
  }

  public showCityOverlayGrid(hexCode: string): void {
    console.log("showCityOverlayGrid called with", hexCode);
    (window as any).showCityOverlayGrid(this, hexCode);
  }

  private generateDistrictColor(districtName: string): string {
    // Use centralized color utility
    const allDistricts = this.getCurrentDistricts();
    return generateDistrictColor(districtName, allDistricts);
  }

  private getCurrentDistricts(): string[] {
    const districts: string[] = [];
    if (this.currentCityOverlay) {
      for (const hexId of Object.keys(this.currentCityOverlay.hex_grid)) {
        const hexData = this.currentCityOverlay.hex_grid[hexId];
        if (hexData?.district && hexData.district !== 'unknown' && hexData.district !== 'empty') {
          districts.push(hexData.district);
        }
      }
    }
    return [...new Set(districts)]; // Remove duplicates
  }

  // getDistrictIndex method removed - now using centralized color utility

  private generateDistrictLegendRows(districts: string[]): string {
    const itemsPerRow = 3; // Show 3 districts per row for better readability
    const rows: string[] = [];
    
    for (let i = 0; i < districts.length; i += itemsPerRow) {
      const rowDistricts = districts.slice(i, i + itemsPerRow);
      const rowHtml = rowDistricts.map(district => {
        const color = this.generateDistrictColor(district);
        return `<span class="district-legend-item" style="background: ${color} !important;">${district}</span>`;
      }).join('');
      rows.push(`<div class="legend-row">${rowHtml}</div>`);
    }
    
    return rows.join('');
  }

}

// Add middle mouse drag scrolling to map and details panels
function enableMiddleMouseDragScroll(panel: HTMLElement) {
  let isDragging = false;
  let isTouchDragging = false;
  let lastX = 0;
  let lastY = 0;
  let animationFrameId: number | null = null;
  
  // Optimized mouse move handler with throttling
  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;
    
    // Cancel any pending animation frame
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
    
    // Use requestAnimationFrame for smooth scrolling
    animationFrameId = requestAnimationFrame(() => {
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      
      // Apply scroll changes directly with hardware acceleration
      panel.scrollLeft -= dx;
      panel.scrollTop -= dy;
      
      lastX = e.clientX;
      lastY = e.clientY;
    });
  };
  
  // Optimized touch move handler
  const handleTouchMove = (e: TouchEvent) => {
    if (!isTouchDragging || e.touches.length !== 1) return;
    
    e.preventDefault(); // Prevent default touch behavior
    
    // Cancel any pending animation frame
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
    
    // Use requestAnimationFrame for smooth scrolling
    animationFrameId = requestAnimationFrame(() => {
      const touch = e.touches[0];
      const dx = touch.clientX - lastX;
      const dy = touch.clientY - lastY;
      
      // Apply scroll changes directly with hardware acceleration
      panel.scrollLeft -= dx;
      panel.scrollTop -= dy;
      
      lastX = touch.clientX;
      lastY = touch.clientY;
    });
  };
  
  panel.addEventListener('mousedown', (e) => {
    // Support both middle mouse (button 1) and left mouse with spacebar/ctrl (button 0)
    if (e.button === 1 || e.button === 0) {
      isDragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      panel.style.cursor = 'grabbing';
      panel.style.userSelect = 'none'; // Prevent text selection during drag
      e.preventDefault();
    }
  });
  
  // Touch event handlers
  panel.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      isTouchDragging = true;
      const touch = e.touches[0];
      lastX = touch.clientX;
      lastY = touch.clientY;
      panel.style.userSelect = 'none';
    }
  }, { passive: false });
  
  // Use passive: false for better performance on mousemove
  window.addEventListener('mousemove', handleMouseMove, { passive: false });
  
  // Touch move with passive: false for better performance
  window.addEventListener('touchmove', handleTouchMove, { passive: false });
  
  window.addEventListener('mouseup', (e) => {
    if (isDragging && (e.button === 1 || e.button === 0)) {
      isDragging = false;
      panel.style.cursor = '';
      panel.style.userSelect = '';
      
      // Cancel any pending animation frame
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
    }
  });
  
  window.addEventListener('touchend', (e) => {
    if (isTouchDragging) {
      isTouchDragging = false;
      panel.style.userSelect = '';
      
      // Cancel any pending animation frame
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
    }
  });
  
  // Clean up on mouse leave
  window.addEventListener('mouseleave', () => {
    if (isDragging) {
      isDragging = false;
      panel.style.cursor = '';
      panel.style.userSelect = '';
      
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
    }
  });
  
  // Clean up on touch cancel
  window.addEventListener('touchcancel', () => {
    if (isTouchDragging) {
      isTouchDragging = false;
      panel.style.userSelect = '';
      
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
    }
  });
}



document.addEventListener('DOMContentLoaded', () => {
  const appInstance = new DyingLandsApp();
  (window as any).dyingLandsApp = appInstance;
  (window as any).app = appInstance;
  (window as any).showCityOverlayGrid = appInstance.showCityOverlayGrid;
  (window as any).showCityHexDetails = appInstance.showCityHexDetails.bind(appInstance);
  (window as any).app.showCityHexDetails = appInstance.showCityHexDetails.bind(appInstance);
  (window as any).app.restoreMap = appInstance.restoreMap.bind(appInstance);
  (window as any).restoreMap = appInstance.restoreMap.bind(appInstance);
  (window as any).app.showWorldMap = appInstance.showWorldMap.bind(appInstance);
  (window as any).showWorldMap = appInstance.showWorldMap.bind(appInstance);
  (window as any).app.renderCityOverlay = appInstance.renderCityOverlay.bind(appInstance);
  (window as any).renderCityOverlay = appInstance.renderCityOverlay.bind(appInstance);
  (window as any).app.showHexDetails = appInstance.showHexDetails.bind(appInstance);
  (window as any).showHexDetails = appInstance.showHexDetails.bind(appInstance);
  (window as any).app.editHexContent = appInstance.editHexContent.bind(appInstance);
  (window as any).app.saveHexContent = appInstance.saveHexContent.bind(appInstance);
  (window as any).app.cancelHexEdit = appInstance.cancelHexEdit.bind(appInstance);
  const mapPanel = document.querySelector('.map-container') as HTMLElement;
  const mapZoomContainer = document.getElementById('map-zoom-container') as HTMLElement;
  const detailsPanel = document.querySelector('.modal-content-container') as HTMLElement;
  
  // Enable middle mouse drag scrolling for both panels
  if (mapZoomContainer) {
    enableMiddleMouseDragScroll(mapZoomContainer);
  }
  if (detailsPanel) {
    enableMiddleMouseDragScroll(detailsPanel);
  }

  // Improved zoom functionality with touch support
  let currentZoom = 1;
  const ZOOM_MIN = 1.0; // Prevent zooming out beyond initial size
const ZOOM_MAX = 2.0;
const ZOOM_STEP = 0.1;
  
  // Make zoom state globally accessible
  (window as any).currentZoom = currentZoom;
  
  // Store event listener references for proper cleanup
  let zoomEventListeners: {
    wheel: (e: WheelEvent) => void;
    touchstart: (e: TouchEvent) => void;
    touchmove: (e: TouchEvent) => void;
    touchend: (e: TouchEvent) => void;
    touchcancel: (e: TouchEvent) => void;
  } | null = null;

  function handleMapZoom(e: WheelEvent) {
    // Disable zooming in city view
    if ((window as any).app && (window as any).app.getCurrentView() === "city") {
      return;
    }
    
    if (e.ctrlKey) return; // Allow browser zoom when Ctrl is pressed
    
    e.preventDefault();
    
    const delta = e.deltaY > 0 ? -1 : 1;
    const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, currentZoom + (delta * ZOOM_STEP)));
    
    if (newZoom !== currentZoom) {
      currentZoom = newZoom;
      applyZoom();
    }
  }

  function applyZoom() {
    // Don't apply zoom in city view
    if ((window as any).app && (window as any).app.getCurrentView() === "city") {
      return;
    }
    
    if (mapZoomContainer) {
      // Use transform3d for hardware acceleration
      mapZoomContainer.style.transform = `scale3d(${currentZoom}, ${currentZoom}, 1)`;
      mapZoomContainer.style.transformOrigin = 'top left';
    }
    // Update global zoom state
    (window as any).currentZoom = currentZoom;
  }

  function resetZoom() {
    // Don't reset zoom in city view
    if ((window as any).app && (window as any).app.getCurrentView() === "city") {
      return;
    }
    
    currentZoom = 1;
    applyZoom();
  }

  // Touch/pinch-to-zoom functionality
  let pinchState = {
    initialDistance: 0,
    initialZoom: 1,
    active: false
  };

  function handleTouchStart(e: TouchEvent) {
    // Disable touch zooming in city view
    if ((window as any).app && (window as any).app.getCurrentView() === "city") {
      return;
    }
    
    if (e.touches.length === 2) {
      pinchState.active = true;
      pinchState.initialDistance = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      pinchState.initialZoom = currentZoom;
      e.preventDefault();
    }
  }

  function handleTouchMove(e: TouchEvent) {
    // Disable touch zooming in city view
    if ((window as any).app && (window as any).app.getCurrentView() === "city") {
      return;
    }
    
    if (pinchState.active && e.touches.length === 2) {
      e.preventDefault();
      
      const newDistance = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      
      const scaleDelta = newDistance / pinchState.initialDistance;
      const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, pinchState.initialZoom * scaleDelta));
      
      if (newZoom !== currentZoom) {
        currentZoom = newZoom;
        applyZoom();
      }
    }
  }

  function handleTouchEnd(e: TouchEvent) {
    if (e.touches.length < 2 && pinchState.active) {
      pinchState.active = false;
    }
  }

  function handleTouchCancel() {
    pinchState.active = false;
  }

  // Function to enable zoom functionality
  function enableZoom() {
    if (!mapZoomContainer || zoomEventListeners) return; // Already enabled or no zoom container
    
    zoomEventListeners = {
      wheel: handleMapZoom,
      touchstart: handleTouchStart,
      touchmove: handleTouchMove,
      touchend: handleTouchEnd,
      touchcancel: handleTouchCancel
    };
    
    mapZoomContainer.addEventListener('wheel', zoomEventListeners.wheel, { passive: false });
    mapZoomContainer.addEventListener('touchstart', zoomEventListeners.touchstart, { passive: false });
    mapZoomContainer.addEventListener('touchmove', zoomEventListeners.touchmove, { passive: false });
    mapZoomContainer.addEventListener('touchend', zoomEventListeners.touchend, { passive: false });
    mapZoomContainer.addEventListener('touchcancel', zoomEventListeners.touchcancel, { passive: false });
    
    // Enable hardware acceleration
    mapZoomContainer.style.willChange = 'transform';
    mapZoomContainer.style.backfaceVisibility = 'hidden';
  }

  // Function to disable zoom functionality
  function disableZoom() {
    if (!mapZoomContainer || !zoomEventListeners) return; // Not enabled or no zoom container
    
    mapZoomContainer.removeEventListener('wheel', zoomEventListeners.wheel);
    mapZoomContainer.removeEventListener('touchstart', zoomEventListeners.touchstart);
    mapZoomContainer.removeEventListener('touchmove', zoomEventListeners.touchmove);
    mapZoomContainer.removeEventListener('touchend', zoomEventListeners.touchend);
    mapZoomContainer.removeEventListener('touchcancel', zoomEventListeners.touchcancel);
    
    // Reset zoom to 1 when disabling
    currentZoom = 1;
    if (mapZoomContainer) {
      mapZoomContainer.style.transform = 'scale3d(1, 1, 1)';
      mapZoomContainer.style.willChange = 'auto';
      mapZoomContainer.style.backfaceVisibility = 'visible';
    }
    
    zoomEventListeners = null;
  }

  // Initialize zoom functionality for world view
  enableZoom();

  // Add keyboard shortcut for resetting zoom (R key)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
      resetZoom();
    }
  });

  // Make zoom functions globally accessible
  (window as any).resetZoom = resetZoom;
  (window as any).applyZoom = applyZoom;
  (window as any).enableZoom = enableZoom;
  (window as any).disableZoom = disableZoom;

  // Function to select and center a hex cell
  function selectHexCell(hexCode: string) {
    // Remove .selected from any previously selected cell
    document.querySelectorAll('.hex-cell.selected').forEach(cell => {
      cell.classList.remove('selected');
    });
    
    // Add .selected to the clicked cell (handle both hex-cell and hex-container)
    let cell = document.querySelector(`.hex-cell[data-hex="${hexCode}"]`) as HTMLElement;
    if (!cell) {
      // Try to find it within a hex container
      const container = document.querySelector(`.hex-container[data-hex="${hexCode}"]`) as HTMLElement;
      if (container) {
        cell = container.querySelector('.hex-cell') as HTMLElement;
      }
    }
    
    if (cell) {
      cell.classList.add('selected');
      
      // Get the map zoom container
      const mapZoomContainer = document.getElementById('map-zoom-container') as HTMLElement;
      
      if (mapZoomContainer) {
        // Calculate the position of the cell relative to the zoom container, accounting for zoom
        const cellRect = cell.getBoundingClientRect();
        const containerRect = mapZoomContainer.getBoundingClientRect();
        
        // Calculate the center position of the cell within the container
        const cellCenterX = cellRect.left + cellRect.width / 2;
        const cellCenterY = cellRect.top + cellRect.height / 2;
        const containerCenterX = containerRect.left + containerRect.width / 2;
        const containerCenterY = containerRect.top + containerRect.height / 2;
        
        // Calculate the scroll position needed to center the cell, accounting for zoom
        const scrollLeft = mapZoomContainer.scrollLeft + (cellCenterX - containerCenterX) / currentZoom;
        const scrollTop = mapZoomContainer.scrollTop + (cellCenterY - containerCenterY) / currentZoom;
        
        // Smooth scroll to center the cell
        mapZoomContainer.scrollTo({
          left: scrollLeft,
          top: scrollTop,
          behavior: 'smooth'
        });
      }
      
      // Remove .selected after animation so it can be triggered again
      cell.addEventListener('animationend', () => {
        cell.classList.remove('selected');
      }, { once: true });
    }
  }

  // Make selectHexCell available globally
  (window as any).selectHexCell = selectHexCell;
  
  // Also make it available as a method on the app instance
  (window as any).app.selectHexCell = selectHexCell;
});

export { DyingLandsApp };
