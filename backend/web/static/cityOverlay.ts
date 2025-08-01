// web/static/cityOverlay.ts
import * as ui from './uiUtils.js';

export async function showCityDetailsInMap(app: any, hexCode: string): Promise<void> {
    ui.showLoading('Loading city details...');
    try {
        const response = await fetch(`/api/city/${hexCode}`);
        const data = await response.json();
        if (data.success) {
            const city = data.city;
            const container = document.getElementById('details-panel');
            if (container) {
                container.innerHTML = `
          <div class="ascii-modal">
            <h2>⌂ ${city.name}</h2>
            <p><strong>Population:</strong> ${city.population}</p>
            <p><strong>Region:</strong> ${city.region}</p>
            <p><strong>Atmosphere:</strong> ${city.atmosphere}</p>
            <p><strong>Description:</strong> ${city.description}</p>
            <p><strong>Notable Features:</strong> ${city.notable_features}</p>
            <p><strong>Key NPCs:</strong> ${city.key_npcs}</p>
            <div class="mt-3">
              <button class="btn-mork-borg" onclick="app.showCityOverlayInMap('${hexCode}')">View City Overlay</button>
            </div>
          </div>
        `;
            }
        }
        else {
            showMapErrorState(app, 'City not found');
        }
    }
    catch (error) {
        console.error('Error loading city details:', error);
        showMapErrorState(app, 'Failed to load city details');
    }
    finally {
        ui.hideLoading();
    }
}

export async function showSettlementDetailsInMap(app: any, hexCode: string): Promise<void> {
    ui.showLoading('Loading settlement details...');
    try {
        const response = await fetch(`/api/settlement/${hexCode}`);
        const data = await response.json();
        if (data.success) {
            const settlement = data.settlement;
            const container = document.getElementById('details-panel');
            if (container) {
                container.innerHTML = `
          <div class="ascii-modal">
            <h2>⌂ ${settlement.name}</h2>
            <p><strong>Population:</strong> ${settlement.population}</p>
            <p><strong>Atmosphere:</strong> ${settlement.atmosphere}</p>
            <p><strong>Description:</strong> ${settlement.description}</p>
            <p><strong>Notable Feature:</strong> ${settlement.notable_feature}</p>
            <p><strong>Local Tavern:</strong> ${settlement.local_tavern}</p>
            <p><strong>Local Power:</strong> ${settlement.local_power}</p>
          </div>
        `;
            }
        }
        else {
            showMapErrorState(app, 'Settlement not found');
        }
    }
    catch (error) {
        console.error('Error loading settlement details:', error);
        showMapErrorState(app, 'Failed to load settlement details');
    }
    finally {
        ui.hideLoading();
    }
}

export async function showCityOverlayInMap(app: any, hexCode: string): Promise<void> {
    ui.showLoading('Loading city overlays...');
    try {
        const response = await fetch('/api/city-overlays');
        const data = await response.json();
        if (data.success && data.overlays.length > 0) {
            const overlayName = data.overlays[0].name;
            await showCityOverlayGridInMap(app, overlayName, hexCode);
        }
        else {
            showMapErrorState(app, 'No city overlays available');
        }
    }
    catch (error) {
        console.error('ERROR LOADING CITY OVERLAYS:', error);
        showMapErrorState(app, 'Failed to load city overlays');
    }
    finally {
        ui.hideLoading();
    }
}

export async function showCityOverlayGridInMap(app: any, overlayName: string, hexCode: string): Promise<void> {
    ui.showLoading('Loading city overlay...');
    try {
        const response = await fetch(`/api/city-overlay/${overlayName}`);
        const data = await response.json();
        console.log('DEBUG: Received overlay data:', data);
        if (data.success) {
            const overlay = data.overlay;
            console.log('DEBUG: Overlay object:', overlay);
            console.log('DEBUG: Hex grid keys:', Object.keys(overlay.hex_grid || {}));
            console.log('DEBUG: Sample hex data:', overlay.hex_grid ? Object.values(overlay.hex_grid)[0] : 'No hex grid');
            
            const mapContainer = document.querySelector('.map-container');
            const mapZoomContainer = document.getElementById('map-zoom-container');
            if (mapContainer && mapZoomContainer) {
                if (!mapContainer.getAttribute('data-original-content')) {
                    const hexGrid = mapZoomContainer.querySelector('#hexGrid');
                    if (hexGrid) {
                        mapContainer.setAttribute('data-original-content', hexGrid.innerHTML);
                    }
                }
                let html = `
          <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
            <div class="mb-4">
              <button class="btn-mork-borg btn-warning" onclick="app.restoreMap()">RETURN TO MAP</button>
              <button class="btn-mork-borg" onclick="app.showCityDetailsInMap('${hexCode}')">← RETURN TO CITY</button>
              <button class="btn-mork-borg" onclick="app.showCityOverlayAsciiInMap('${overlayName}', '${hexCode}')">📜 ASCII VIEW</button>
            </div>
            <div style="background: var(--mork-black); border: 2px solid var(--mork-cyan); padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);">
              <h4 style="color: var(--mork-cyan); margin-bottom: 15px;">
                ⌂ ${overlay.display_name.toUpperCase()} - INTERACTIVE GRID
              </h4>
              <div style="margin-bottom: 15px; font-size: 12px; color: var(--mork-gray);">
                <strong>LEGEND:</strong> D=District, B=Building, S=Street, L=Landmark, M=Market, T=Temple, V=Tavern, G=Guild, R=Residence, U=Ruins
              </div>
              <div class="city-overlay-grid">
        `;
                for (let row = 0; row < 5; row++) {
                    html += '<div class="city-overlay-row">';
                    for (let col = 0; col < 5; col++) {
                        const hexId = `${row}_${col}`;
                        const hexData = overlay.hex_grid[hexId];
                        console.log(`DEBUG: Looking for hex ${hexId}:`, hexData);
                        if (hexData) {
                            const content = hexData.content;
                            const symbol = getCityOverlaySymbol(content.type);
                            const cssClass = getCityOverlayCSSClass(content.type);
                            html += `
                <div class="city-hex-cell ${cssClass}" 
                     onclick="app.showCityHexDetailsInMap('${overlayName}', '${hexId}')"
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
            </div>
          </div>
        `;
                if (mapZoomContainer) {
                    mapZoomContainer.innerHTML = html;
                }
            }
        }
        else {
            showMapErrorState(app, 'Failed to load city overlay');
        }
    }
    catch (error) {
        console.error('ERROR LOADING CITY OVERLAY GRID:', error);
        showMapErrorState(app, 'Failed to load city overlay grid');
    }
    finally {
        ui.hideLoading();
    }
}

export async function showCityOverlayAsciiInMap(app: any, overlayName: string, hexCode: string): Promise<void> {
    ui.showLoading('Loading ASCII view...');
    try {
        // Disable zoom when entering ASCII view
        if ((window as any).disableZoom) {
            (window as any).disableZoom();
        }
        
        const response = await fetch(`/api/city-overlay/${overlayName}/ascii`);
        const data = await response.json();
        if (data.success) {
            const mapContainer = document.querySelector('.map-container');
            const mapZoomContainer = document.getElementById('map-zoom-container');
            if (mapContainer && mapZoomContainer) {
                let html = `
          <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
            <div class="mb-4">
              <button class="btn-mork-borg btn-warning" onclick="app.restoreMap()">RETURN TO MAP</button>
              <button class="btn-mork-borg" onclick="app.showCityOverlayGridInMap('${overlayName}', '${hexCode}')">← BACK TO GRID</button>
              <button class="btn-mork-borg" onclick="app.showCityDetailsInMap('${hexCode}')">⌂ RETURN TO CITY</button>
            </div>
            <div style="background: var(--mork-black); border: 2px solid var(--mork-cyan); padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);">
              <h4 style="color: var(--mork-cyan); margin-bottom: 15px;">
                ⌂ CITY OVERLAY - ASCII VIEW
              </h4>
              <pre style="font-family: 'Courier New', monospace; font-size: 10px; line-height: 1.2; color: var(--mork-cyan); margin: 0; white-space: pre-wrap; word-wrap: break-word; text-align: left;">
${data.ascii}
              </div>
            </div>
          </div>
        `;
                if (mapZoomContainer) {
                    mapZoomContainer.innerHTML = html;
                }
            }
        }
        else {
            showMapErrorState(app, 'Failed to load ASCII view');
        }
    }
    catch (error) {
        console.error('ERROR LOADING CITY OVERLAY ASCII:', error);
        showMapErrorState(app, 'Failed to load ASCII view');
    }
    finally {
        ui.hideLoading();
    }
}

export async function showCityHexDetailsInMap(app: any, overlayName: string, hexId: string): Promise<void> {
    ui.showLoading('Loading hex details...');
    try {
        // Disable zoom when entering hex details view
        if ((window as any).disableZoom) {
            (window as any).disableZoom();
        }
        
        const response = await fetch(`/api/city-overlay/${overlayName}/hex/${hexId}`);
        const data = await response.json();
        if (data.success) {
            const hex = data.hex;
            const content = hex.content;
            const mapContainer = document.querySelector('.map-container');
            const mapZoomContainer = document.getElementById('map-zoom-container');
            if (mapContainer && mapZoomContainer) {
                let html = `
          <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
            <div class="mb-4">
              <button class="btn-mork-borg btn-warning" onclick="app.restoreMap()">RETURN TO MAP</button>
              <button class="btn-mork-borg" onclick="app.showCityOverlayGridInMap('${overlayName}', '${hexId}')">← BACK TO GRID</button>
            </div>
            <div style="background: var(--mork-black); border: 2px solid var(--mork-cyan); padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);">
              <h4 style="color: var(--mork-cyan); margin-bottom: 15px;">
                ${getCityOverlaySymbol(content.type)} ${content.name.toUpperCase()}
              </h4>
              <p><strong>Type:</strong> ${content.type}</p>
              <p><strong>Description:</strong> ${content.description}</p>
              <p><strong>Encounter:</strong> ${content.encounter}</p>
              <p><strong>Atmosphere:</strong> ${content.atmosphere}</p>
              <p><strong>Position Type:</strong> ${content.position_type}</p>
            </div>
          </div>
        `;
                if (mapZoomContainer) {
                    mapZoomContainer.innerHTML = html;
                }
            }
        }
        else {
            showMapErrorState(app, 'Failed to load hex details');
        }
    }
    catch (error) {
        console.error('ERROR LOADING CITY HEX DETAILS:', error);
        showMapErrorState(app, 'Failed to load hex details');
    }
    finally {
        ui.hideLoading();
    }
}

function getCityOverlaySymbol(type: string): string {
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

function getCityOverlayCSSClass(type: string): string {
    return `city-${type}`;
}

function showMapErrorState(app: any, message: string): void {
    const mapContainer = document.querySelector('.map-container');
    if (mapContainer) {
        mapContainer.innerHTML = `
      <div style="text-align: center; padding: 50px;">
        <div class="city-hex-details-box">
          <div class="ascii-box">
            <div class="ascii-inner-box">
              <div class="ascii-section ascii-error-title">
                <span>ERROR LOADING CITY OVERLAY</span>
              </div>
              <div class="ascii-section ascii-error-message">
                <span>ERROR DETAILS</span>
                <div class="ascii-content">${message}</div>
              </div>
              <div class="ascii-section ascii-error-description">
                <span>STATUS</span>
                <div class="ascii-content">The darkness has consumed this knowledge...</div>
              </div>
            </div>
          </div>
        </div>
        <button class="btn-mork-borg btn-warning" onclick="app.restoreMap()">RETURN TO MAP</button>
      </div>
    `;
    }
} 