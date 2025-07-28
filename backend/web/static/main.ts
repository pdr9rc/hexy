// web/static/main.ts
import { getCityOverlay, getCityOverlayHex } from "./api.js"
import { showHexDetails as renderHexDetails, showCityDetails, showSettlementDetails } from "./hexViewer.js"
import { renderMap } from "./mapRenderer.js"
import { initializeControls } from "./controls.js"
import { showNotification, showError } from "./uiUtils.js"
import { showCityOverlayGrid } from './cityOverlays.js';

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
    this.renderWorldMap()
    this.updateWorldMapControlsVisibility()
    initializeControls(this)

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

    this.showCityHexDetails(overlayName, hexId)
  }

  public async showCityHexDetails(overlayName: string, hexId: string): Promise<void> {
    try {
      console.log('🔍 showCityHexDetails called with:', { overlayName, hexId });
      
      // Call the API directly to get enriched hex data
      const response = await fetch(`/api/city-overlay/${overlayName}/hex/${hexId}`);
      const data = await response.json();
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
              <span>TYPE: ${content.type || type}</span>
            </div>
            <div class="ascii-section ascii-hex-district">
              <span>DISTRICT: ${hexData.district || district}</span>
            </div>
            <div class="ascii-section ascii-hex-position">
              <span>POSITION: ${content.position_type || positionType}</span>
            </div>
            
            <!-- Description Section -->
            <div class="ascii-section ascii-hex-description">
              <span>DESCRIPTION:</span>
              <pre>${content.description || description}</pre>
            </div>
            
            <!-- Atmosphere & Encounter Section -->
            <div class="ascii-section ascii-hex-atmosphere">
              <span>ATMOSPHERE:</span>
              <pre>${content.atmosphere || atmosphere || 'No atmosphere available.'}</pre>
            </div>
            <div class="ascii-section ascii-hex-encounter">
              <span>ENCOUNTER:</span>
              <pre>${content.encounter || encounter}</pre>
            </div>
    `

    // Notable Features Section (hex-specific)
    if (content.notable_features && content.notable_features.length > 0) {
      html += `
        <div class="ascii-section ascii-hex-features">
          <span>NOTABLE FEATURES:</span>
          <pre>${content.notable_features.join('\n')}</pre>
        </div>
      `;
    }

                  // NPC Information Section
              if (content.npc_trait || content.npc_concern || content.npc_want || content.npc_secret || content.npc_name || content.npc_trade || content.npc_affiliation || content.npc_attitude) {
                html += `
                  <div class="ascii-section ascii-hex-npcs">
                    <span>NPC INFORMATION:</span>
                    <pre>
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
                    </pre>
                  </div>
                `;
              }

    // Tavern Details Section (for taverns only)
    if (content.type === 'tavern' && (content.tavern_menu || content.tavern_innkeeper || content.tavern_patron)) {
      html += `
        <div class="ascii-section ascii-hex-tavern">
          <span>TAVERN DETAILS:</span>
          <pre>
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
          </pre>
        </div>
      `;
    }

    // Market Items Section (for markets)
    if (content.type === 'market' && (content.items_sold || content.beast_prices || content.services)) {
      html += `
        <div class="ascii-section ascii-hex-market">
          <span>MARKET DETAILS:</span>
          <pre>
      `;
      
      if (content.items_sold) {
        html += `ITEMS SOLD: ${content.items_sold}\n`;
      }
      if (content.beast_prices) {
        html += `BEAST PRICES: ${content.beast_prices}\n`;
      }
      if (content.services) {
        html += `SERVICES: ${content.services}\n`;
      }
      
      html += `
          </pre>
        </div>
      `;
    }

    // Services Section (for service locations)
    if (content.type === 'service' && content.services) {
      html += `
        <div class="ascii-section ascii-hex-services">
          <span>SERVICES:</span>
          <pre>${content.services}</pre>
        </div>
      `;
    }

    // Patrons Section (for businesses with patrons)
    if (content.patrons) {
      html += `
        <div class="ascii-section ascii-hex-patrons">
          <span>PATRONS:</span>
          <pre>${content.patrons}</pre>
        </div>
      `;
    }

    // Random Tables Section
    if (content.random_table && content.random_table.length > 0) {
      html += `
        <div class="ascii-section ascii-hex-random">
          <span>RANDOM ENCOUNTERS:</span>
          <pre>${content.random_table.join('\n')}</pre>
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
      const response = await fetch(`/api/regenerate-hex/${targetOverlayName}/${hexId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const result = await response.json();
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
        console.error("Failed to regenerate hex:", response.statusText);
        showNotification("Failed to regenerate hex: " + response.statusText, "error");
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

  private getOverlayNameFromHexCode(hexCode: string): string {
    // This is a simple mapping - you might want to make this more sophisticated
    // based on your actual city data structure
    const hexData = this.mapData[hexCode]
    if (hexData && hexData.city_name) {
      return hexData.city_name.toLowerCase().replace(/\s+/g, "_")
    }
    return "galgenbeck" // Default fallback
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
              <pre>Click on a hex to view district details and information.</pre>
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
                  <pre>
Click a hex to explore its mysteries...

Each hex contains unique encounters, denizens,
and secrets waiting to be discovered.

The world is dying, but adventure lives on.
                  </pre>
                </div>
                <div class="ascii-section ascii-hex-instructions">
                  <span>INSTRUCTIONS</span>
                  <pre>
• Click any hex on the map to view its details
• Major cities (◆) have additional overlay views
• Settlements (⌂) provide local information
• Bold hexes contain special content
                  </pre>
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
    // Authentic Mörk Borg color palette (12 colors for 12 districts max)
    const morkBorgColors = [
      '#FF00FF', // Magenta - Primary Mörk Borg color
      '#FFFF00', // Yellow - Primary Mörk Borg color
      '#00FFFF', // Cyan - Primary Mörk Borg color
      '#FF0000', // Red - Classic Mörk Borg accent
      '#00FF00', // Green - Classic Mörk Borg accent
      '#0000FF', // Blue - Classic Mörk Borg accent
      '#FF8000', // Orange - Mörk Borg warm tone
      '#8000FF', // Purple - Mörk Borg dark accent
      '#FF0080', // Hot Pink - Mörk Borg vibrant
      '#00FF80', // Spring Green - Mörk Borg bright
      '#FF4000', // Red-Orange - Mörk Borg fiery
      '#800080'  // Purple-Magenta - Mörk Borg deep
    ];
    
    // Use district name to get consistent index (0-11 for 12 districts)
    const districtIndex = this.getDistrictIndex(districtName);
    return morkBorgColors[districtIndex % morkBorgColors.length];
  }

  private getDistrictIndex(districtName: string): number {
    // Create a simple mapping for consistent district colors
    const districtMap: { [key: string]: number } = {};
    let currentIndex = 0;
    
    // Get all unique districts from the current city overlay
    if (this.currentCityOverlay) {
      const uniqueDistricts = new Set<string>();
      for (const hexId of Object.keys(this.currentCityOverlay.hex_grid)) {
        const hexData = this.currentCityOverlay.hex_grid[hexId];
        if (hexData?.district && hexData.district !== 'unknown' && hexData.district !== 'empty') {
          uniqueDistricts.add(hexData.district);
        }
      }
      
      // Create mapping for unique districts only
      const sortedDistricts = Array.from(uniqueDistricts).sort();
      sortedDistricts.forEach(district => {
        if (!districtMap[district]) {
          districtMap[district] = currentIndex++;
        }
      });
    }
    
    // Return mapped index or 0 for unknown districts
    return districtMap[districtName] || 0;
  }

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
    if (e.button === 1 || (e.button === 0 && (e.ctrlKey || e.metaKey))) {
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
