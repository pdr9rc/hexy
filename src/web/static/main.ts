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
  grid_size: number
  hex_grid: { [key: string]: any }
  total_hexes: number
  hexCode?: string
}

export type { HexData };

class DyingLandsApp {
  public mapData: { [key: string]: HexData } = {}
  public mapWidth = 30
  public mapHeight = 25
  private currentView: "world" | "city" = "world"
  private currentCityOverlay: CityOverlayData | null = null

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
    initializeControls(this)

    console.log("✅ The Dying Lands initialized successfully")
  }

  private initializeEventListeners(): void {
    // Handle hex clicks
    document.addEventListener("click", (event) => {
      const target = event.target as HTMLElement

      if (target.classList.contains("hex-cell")) {
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
            console.log("Calling showWorldMap")
            this.showWorldMap()
            break
        }
      }
    })
  }

  private handleHexClick(hexElement: HTMLElement): void {
    const hexCode = hexElement.getAttribute("data-hex")
    if (!hexCode) return
    selectHexCell(hexCode); // Ensure selected class is applied on click

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
      const response = await getCityOverlayHex(overlayName, hexId)
      if (response.success) {
        this.displayCityHexDetails(response.hex)
      } else {
        showError("Failed to load city hex details")
      }
    } catch (error) {
      console.error("Error loading city hex details:", error)
      showError("Failed to load city hex details")
    }
  }

  private displayCityHexDetails(hexData: any): void {
    const detailsPanel = document.getElementById("details-panel")
    if (!detailsPanel) return

    const content = hexData.content
    const hexId = hexData.hex_id || "?"
    const terrain = content.terrain || "?"
    const type = content.type || "?"
    const name = content.name || "?"
    const description = content.description || ""
    const encounter = content.encounter || ""
    const features = (content.notable_features && content.notable_features.length > 0) ? content.notable_features.join("\n") : ""
    const npcs = (content.npcs && content.npcs.length > 0) ? content.npcs.join("\n") : ""
    const randomEvents = (content.random_table && content.random_table.length > 0) ? content.random_table.join("\n") : ""
    const position = hexData.position || "?"
    const positionType = content.position_type || "?"

    let html = `
      <div class="city-hex-details-box">
        <div class="ascii-box">
          <div class="ascii-inner-box">
            <div class="ascii-section ascii-hex-id">
              <span>HEX ${hexId}</span>
            </div>
            <div class="ascii-section ascii-terrain">
              <span>TERRAIN: ${terrain}</span>
            </div>
            <div class="ascii-section ascii-content">
              <span>TYPE: ${type}</span><br/>
              <span>NAME: ${name}</span>
            </div>
            <div class="ascii-section ascii-description">
              <span>DESCRIPTION:</span>
              <pre>${description}</pre>
            </div>
            <div class="ascii-section ascii-encounter">
              <span>ENCOUNTER:</span>
              <pre>${encounter}</pre>
        </div>
            <div class="ascii-section ascii-features">
              <span>NOTABLE FEATURES:</span>
              <pre>${features}</pre>
        </div>
            <div class="ascii-section ascii-npcs">
              <span>NPCS:</span>
              <pre>${npcs}</pre>
        </div>
            <div class="ascii-section ascii-random-table">
              <span>RANDOM EVENTS:</span>
              <pre>${randomEvents}</pre>
        </div>
            <div class="ascii-section ascii-position">
              <span>POSITION: ${position} (${positionType})</span>
        </div>
        </div>
        </div>
      </div>
    `
    detailsPanel.innerHTML = html
  }

  public async showCityOverlayInMap(hexCode: string): Promise<void> {
    try {
      showNotification("Loading city overlay...")

      // Get city name from hex data
      const hexData = this.mapData[hexCode]
      if (!hexData || !hexData.is_city) {
        showError("Not a major city")
        return
      }

      // Map hex codes to overlay names (you might need to adjust this mapping)
      const overlayName = this.getOverlayNameFromHexCode(hexCode)

      const response = await getCityOverlay(overlayName)
      if (response.success) {
        this.currentCityOverlay = response.overlay
        this.renderCityOverlay(hexCode)
        this.currentView = "city"
        showNotification(`Viewing ${response.overlay.display_name}`)
      } else {
        showError("Failed to load city overlay")
      }
    } catch (error) {
      console.error("Error loading city overlay:", error)
      showError("Failed to load city overlay")
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
    console.log("renderCityOverlay called with hexCode:", hexCode)
    if (!this.currentCityOverlay) return
    
    // Store the hex code for the RETURN TO HEX button
    if (hexCode) {
      this.currentCityOverlay.hexCode = hexCode
    }

    const mapContainer = document.querySelector(".map-container")
    if (!mapContainer) return

    // Save original map content if not already saved
    if (!mapContainer.hasAttribute("data-original-content")) {
      mapContainer.setAttribute("data-original-content", mapContainer.innerHTML);
    }

    // Create city overlay HTML using .city-overlay-grid and .city-overlay-row
    let html = `
      <div class="city-overlay-container">
        <div class="city-overlay-header">
          <h2>🏰 ${this.currentCityOverlay.display_name}</h2>
          <div class="city-overlay-controls">
            <button class="btn btn-mork-borg" onclick="window.app.renderCityOverlay()">MAP GRID</button>
            <button class="btn btn-mork-borg" onclick="window.app.showHexDetails('${this.currentCityOverlay.hexCode || ''}')">RETURN TO HEX</button>
            <button class="btn btn-mork-borg" onclick="window.app.restoreMap()">RETURN TO MAP</button>
          </div>
        </div>
        <div class="city-overlay-grid">
    `

    // Generate 5x5 honeycomb grid
    for (let row = 0; row < this.currentCityOverlay.grid_size; row++) {
      html += '<div class="city-overlay-row">'
      
      // Add offset for even rows to create honeycomb effect
      if (row % 2 === 1) {
        html += '<div class="city-hex-spacer"></div>'
      }
      
      for (let col = 0; col < this.currentCityOverlay.grid_size; col++) {
        const hexId = `${row}_${col}`
        const hexData = this.currentCityOverlay.hex_grid[hexId]
        const content = hexData?.content || {}

        const symbol = this.getCityHexSymbol(content.type)
        const cssClass = `city-hex-cell city-${content.type || "unknown"}`

        html += `
          <div class="${cssClass}" 
               data-hex-id="${hexId}" 
               data-overlay="${this.currentCityOverlay.name}"
               title="${content.name || "Unknown"} (${content.type || "unknown"})"
               onclick="window.app.showCityHexDetails && window.app.showCityHexDetails('${this.currentCityOverlay.name}', '${hexId}')">
            <span class="city-hex-symbol">${symbol}</span>
            <span class="city-hex-coords">${row + 1},${col + 1}</span>
          </div>
        `
      }
      html += "</div>"
    }

    html += `
        </div>
        <div class="city-legend">
          <h4>Legend</h4>
          <div class="legend-items">
            <span class="legend-item"><span class="symbol">D</span> District</span>
            <span class="legend-item"><span class="symbol">B</span> Building</span>
            <span class="legend-item"><span class="symbol">S</span> Street</span>
            <span class="legend-item"><span class="symbol">L</span> Landmark</span>
            <span class="legend-item"><span class="symbol">M</span> Market</span>
            <span class="legend-item"><span class="symbol">T</span> Temple</span>
            <span class="legend-item"><span class="symbol">V</span> Tavern</span>
            <span class="legend-item"><span class="symbol">G</span> Guild</span>
            <span class="legend-item"><span class="symbol">R</span> Residence</span>
            <span class="legend-item"><span class="symbol">U</span> Ruins</span>
          </div>
        </div>
      </div>
    `

    mapContainer.innerHTML = html
  }

  private getCityHexSymbol(contentType: string): string {
    const symbolMap: { [key: string]: string } = {
      district: "D",
      building: "B",
      street: "S",
      landmark: "L",
      market: "M",
      temple: "T",
      tavern: "V",
      guild: "G",
      residence: "R",
      ruins: "U",
    }

    return symbolMap[contentType] || "?"
  }

  public showWorldMap(): void {
    console.log("showWorldMap called")
    this.currentView = "world"
    this.currentCityOverlay = null
    this.renderWorldMap()
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
    const mapContainer = document.querySelector(".map-container");
    if (mapContainer && mapContainer.hasAttribute("data-original-content")) {
      mapContainer.innerHTML = mapContainer.getAttribute("data-original-content")!;
      mapContainer.removeAttribute("data-original-content");
    }
    this.currentView = "world";
    this.currentCityOverlay = null;
    this.initializeEventListeners();
    showNotification("Returned to world map");
  }

  // Public methods for external access
  public getCurrentView(): "world" | "city" {
    return this.currentView
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
}

// Add middle mouse drag scrolling to map and details panels
function enableMiddleMouseDragScroll(panel: HTMLElement) {
  let isDragging = false;
  let lastX = 0;
  let lastY = 0;
  panel.addEventListener('mousedown', (e) => {
    if (e.button === 1) { // Middle mouse
      isDragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      panel.style.cursor = 'grabbing';
      e.preventDefault();
    }
  });
  window.addEventListener('mousemove', (e) => {
    if (isDragging) {
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      panel.scrollLeft -= dx;
      panel.scrollTop -= dy;
      lastX = e.clientX;
      lastY = e.clientY;
    }
  });
  window.addEventListener('mouseup', (e) => {
    if (isDragging && e.button === 1) {
      isDragging = false;
      panel.style.cursor = '';
    }
  });
}

function selectHexCell(hexCode: string) {
  // Remove .selected from any previously selected cell
  document.querySelectorAll('.hex-cell.selected').forEach(cell => {
    cell.classList.remove('selected');
  });
  // Add .selected to the clicked cell
  const cell = document.querySelector(`.hex-cell[data-hex="${hexCode}"]`);
  if (cell) {
    cell.classList.add('selected');
    // Scroll the selected hex into view
    (cell as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
    // Remove .selected after animation so it can be triggered again
    cell.addEventListener('animationend', () => {
      cell.classList.remove('selected');
    }, { once: true });
  }
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
  const detailsPanel = document.getElementById('details-panel') as HTMLElement;
  if (mapPanel) enableMiddleMouseDragScroll(mapPanel);
  if (detailsPanel) enableMiddleMouseDragScroll(detailsPanel);
});

export { DyingLandsApp };
