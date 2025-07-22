/**
 * City Overlay Management
 * Clean implementation for city layouts and overlays
 */
import * as api from './api.js';
import * as ui from './uiUtils.js';
/**
 * Show city overlay grid view
 */
export async function showCityOverlayGrid(app, hexCode) {
    try {
        ui.showLoading('Loading city overlays...');
        // Get available overlays
        const overlaysResponse = await api.getCityOverlays();
        if (!overlaysResponse.success || overlaysResponse.overlays.length === 0) {
            throw new Error('No city overlays available');
        }
        const overlayName = overlaysResponse.overlays[0].name;
        const overlayResponse = await api.getCityOverlay(overlayName);
        if (!overlayResponse.success) {
            throw new Error('Failed to load city overlay');
        }
        const overlay = overlayResponse.overlay;
        const mapContainer = document.querySelector('.map-container');
        if (!mapContainer) {
            throw new Error('Map container not found');
        }
        // Save original content if not already saved
        if (!mapContainer.hasAttribute('data-original-content')) {
            mapContainer.setAttribute('data-original-content', mapContainer.innerHTML);
        }
        const html = generateCityOverlayGridHTML(overlay, hexCode);
        mapContainer.innerHTML = html;
        ui.hideLoading();
    }
    catch (error) {
        console.error('Error loading city overlay grid:', error);
        ui.showNotification('Failed to load city overlays', 'error');
        ui.hideLoading();
    }
}
/**
 * Show city overlay ASCII view
 */
export async function showCityOverlayAscii(app, overlayName, hexCode) {
    try {
        ui.showLoading('Loading ASCII view...');
        const response = await api.getCityOverlayAscii(overlayName);
        if (!response.success) {
            throw new Error('Failed to load ASCII view');
        }
        const mapContainer = document.querySelector('.map-container');
        if (!mapContainer) {
            throw new Error('Map container not found');
        }
        const html = generateCityOverlayAsciiHTML(response.ascii, overlayName, hexCode);
        mapContainer.innerHTML = html;
        ui.hideLoading();
    }
    catch (error) {
        console.error('Error loading ASCII view:', error);
        ui.showNotification('Failed to load ASCII view', 'error');
        ui.hideLoading();
    }
}
/**
 * Show city hex details
 */
export async function showCityHexDetails(app, overlayName, hexId) {
    try {
        ui.showLoading('Loading hex details...');
        const response = await api.getCityOverlayHex(overlayName, hexId);
        if (!response.success) {
            throw new Error('Failed to load hex details');
        }
        const hex = response.hex;
        const content = hex.content;
        const modalContainer = document.getElementById('modalContainer');
        if (!modalContainer) {
            throw new Error('Modal container not found');
        }
        const html = generateCityHexDetailsHTML(content);
        modalContainer.innerHTML = html;
        ui.hideLoading();
    }
    catch (error) {
        console.error('Error loading city hex details:', error);
        ui.showNotification('Failed to load hex details', 'error');
        ui.hideLoading();
    }
}
/**
 * Generate city overlay grid HTML
 */
function generateCityOverlayGridHTML(overlay, hexCode) {
    const gridHTML = generateCityGrid(overlay.hex_grid);
    return `
    <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
      <div class="mb-4">
        <button class="btn-mork-borg btn-warning me-2" onclick="window.app.restoreMap()">RETURN TO MAP</button>
        <button class="btn-mork-borg me-2" onclick="window.app.showCityDetailsInMap('${hexCode}')">← RETURN TO CITY</button>
        <button class="btn-mork-borg" onclick="window.app.showCityOverlayAscii('${overlay.name}', '${hexCode}')">📜 ASCII VIEW</button>
      </div>
      <div class="ascii-modal">
        <h4 style="color: var(--mork-cyan); margin-bottom: 15px;">
          🏰 ${overlay.display_name.toUpperCase()} - INTERACTIVE GRID
        </h4>
        <div style="margin-bottom: 15px; font-size: 12px; color: var(--mork-gray);">
          <strong>LEGEND:</strong> D=District, B=Building, S=Street, L=Landmark, M=Market, T=Temple, V=Tavern, G=Guild, R=Residence, U=Ruins
        </div>
        <div class="city-overlay-grid">
          ${gridHTML}
        </div>
      </div>
    </div>
  `;
}
/**
 * Generate city grid HTML
 */
function generateCityGrid(hexGrid) {
    let gridHTML = '';
    for (let row = 0; row < 5; row++) {
        for (let col = 0; col < 5; col++) {
            const hexId = `${row}_${col}`;
            const hexData = hexGrid[hexId];
            if (hexData) {
                const content = hexData.content;
                const symbol = getCityOverlaySymbol(content.type);
                const cssClass = getCityOverlayCSSClass(content.type);
                gridHTML += `
          <div class="city-hex-cell ${cssClass}" 
               onclick="window.app.showCityHexDetails('${hexData.overlay_name}', '${hexId}')"
               title="${content.name}">
            <div class="city-hex-symbol">${symbol}</div>
            <div class="city-hex-type">${content.type.toUpperCase()}</div>
          </div>
        `;
            }
        }
    }
    return gridHTML;
}
/**
 * Generate city overlay ASCII HTML
 */
function generateCityOverlayAsciiHTML(asciiContent, overlayName, hexCode) {
    return `
    <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
      <div class="mb-4">
        <button class="btn-mork-borg btn-warning me-2" onclick="window.app.restoreMap()">RETURN TO MAP</button>
        <button class="btn-mork-borg me-2" onclick="window.app.showCityOverlayGrid('${hexCode}')">← BACK TO GRID</button>
        <button class="btn-mork-borg" onclick="window.app.showCityDetailsInMap('${hexCode}')">🏰 RETURN TO CITY</button>
      </div>
      <div class="ascii-modal">
        <h4 style="color: var(--mork-cyan); margin-bottom: 15px;">
          🏰 CITY OVERLAY - ASCII VIEW
        </h4>
        <pre style="font-family: 'Courier New', monospace; font-size: 10px; line-height: 1.2; color: var(--mork-cyan); margin: 0; white-space: pre-wrap; word-wrap: break-word; text-align: left;">
${asciiContent}
        </pre>
      </div>
    </div>
  `;
}
/**
 * Generate city hex details HTML
 */
function generateCityHexDetailsHTML(content) {
    return `
    <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
      <div class="ascii-modal">
        <h4 style="color: var(--mork-cyan); margin-bottom: 15px;">
          ${content.name.toUpperCase()}
        </h4>
        <div style="margin-bottom: 15px; text-align: left;">
          <strong style="color: var(--mork-yellow);">Type:</strong><br>
          <span style="color: var(--mork-white);">${content.type}</span>
        </div>
        <div style="margin-bottom: 15px; text-align: left;">
          <strong style="color: var(--mork-yellow);">Description:</strong><br>
          <span style="color: var(--mork-white);">${content.description}</span>
        </div>
        <div style="margin-bottom: 15px; text-align: left;">
          <strong style="color: var(--mork-yellow);">Encounter:</strong><br>
          <span style="color: var(--mork-white);">${content.encounter}</span>
        </div>
        <div style="margin-bottom: 15px; text-align: left;">
          <strong style="color: var(--mork-yellow);">Atmosphere:</strong><br>
          <span style="color: var(--mork-white);">${content.atmosphere}</span>
        </div>
        <div style="margin-bottom: 15px; text-align: left;">
          <strong style="color: var(--mork-yellow);">Position:</strong><br>
          <span style="color: var(--mork-white);">${content.position_type}</span>
        </div>
      </div>
    </div>
  `;
}
/**
 * Get city overlay symbol for type
 */
function getCityOverlaySymbol(type) {
    const symbols = {
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
    return symbols[type.toLowerCase()] || '?';
}
/**
 * Get city overlay CSS class for type
 */
function getCityOverlayCSSClass(type) {
    const classes = {
        'district': 'city-district',
        'building': 'city-building',
        'street': 'city-street',
        'landmark': 'city-landmark',
        'market': 'city-market',
        'temple': 'city-temple',
        'tavern': 'city-tavern',
        'guild': 'city-guild',
        'residence': 'city-residence',
        'ruins': 'city-ruins'
    };
    return classes[type.toLowerCase()] || 'city-unknown';
}
