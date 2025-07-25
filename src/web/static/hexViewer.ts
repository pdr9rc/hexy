// web/static/hexViewer.ts
import { DyingLandsApp } from './main.js';
import * as api from './api.js';
import * as ui from './uiUtils.js';

export async function renderHexDetails(app: DyingLandsApp, hexCode: string) {
  ui.showLoading('Loading hex details...');
  try {
    const hexData = await api.getHex(hexCode);
    
    if (!hexData || hexData.exists === false) {
      showErrorState('Hex not found');
      return;
    }

    displayHexContent(hexData);
  } catch (error) {
    console.error('Error loading hex details:', error);
    showErrorState('Failed to load hex details');
  }
}

export { showCityDetailsInMap as showCityDetails, showSettlementDetailsInMap as showSettlementDetails, renderHexDetails as showHexDetails };

async function showCityDetailsInMap(app: DyingLandsApp, hexCode: string) {
  try {
      const cityData = await api.getCity(hexCode);
    if (!cityData || !cityData.success) {
      showErrorState('City not found');
      return;
    }
    const city = cityData.city;
    const mapContainer = document.querySelector('.map-container');
    if (!mapContainer) return;
    // Save original content for restoration
    if (!mapContainer.hasAttribute('data-original-content')) {
      mapContainer.setAttribute('data-original-content', mapContainer.innerHTML);
    }
    // Prepare fields
    const name = city.name || '?';
    const location = `HEX ${hexCode} - ${city.region || '?'}`;
    const population = city.population || '?';
    const atmosphere = city.atmosphere || '?';
    const description = city.description?.raw || city.description || 'No description available';
    const features = (city.notable_features && city.notable_features.length > 0) ? city.notable_features.join("\n") : '';
    const keyNpcs = (city.key_npcs && city.key_npcs.length > 0) ? city.key_npcs.join("\n") : '';
    const regionalNpcs = (cityData.regional_npcs && cityData.regional_npcs.length > 0) ? cityData.regional_npcs.join("\n") : '';
    const factions = (cityData.factions && cityData.factions.length > 0) ? cityData.factions.map((f: any) => `${f.name} (${f.influence}) - ${f.description}`).join("\n") : '';
    // Build HTML
    let html = `
      <div class="city-hex-details-box">
        <div class="ascii-box">
          <div class="ascii-inner-box">
            <div class="mb-4" style="text-align:center;">
          <button class="btn btn-mork-borg me-2" onclick="window.app.showCityOverlayInMap('${hexCode}')">MAP GRID</button>
          <button class="btn btn-mork-borg me-2" onclick="window.app.showHexDetails('${hexCode}')">RETURN TO HEX</button>
          <button class="btn btn-mork-borg btn-warning" onclick="window.app.restoreMap()">RETURN TO MAP</button>
        </div>
            <div class="ascii-section ascii-city-name">
              <span>${name}</span>
            </div>
            <div class="ascii-section ascii-city-location">
              <span>LOCATION: ${location}</span>
            </div>
            <div class="ascii-section ascii-city-population">
              <span>POPULATION: ${population}</span>
            </div>
            <div class="ascii-section ascii-city-atmosphere">
              <span>ATMOSPHERE: ${atmosphere}</span>
            </div>
            <div class="ascii-section ascii-city-description">
              <span>DESCRIPTION:</span>
              <pre>${description}</pre>
            </div>
            <div class="ascii-section ascii-city-features">
              <span>NOTABLE FEATURES:</span>
              <pre>${features}</pre>
            </div>
            <div class="ascii-section ascii-city-key-npcs">
              <span>KEY NPCS:</span>
              <pre>${keyNpcs}</pre>
            </div>
            <div class="ascii-section ascii-city-regional-npcs">
              <span>REGIONAL NPCS:</span>
              <pre>${regionalNpcs}</pre>
            </div>
            <div class="ascii-section ascii-city-factions">
              <span>ACTIVE FACTIONS:</span>
              <pre>${factions}</pre>
            </div>
          </div>
        </div>
      </div>
    `;
    mapContainer.innerHTML = html;
  } catch (error) {
    console.error('Error loading city details:', error);
    showErrorState('Failed to load city details');
  }
}

async function showSettlementDetailsInMap(app: DyingLandsApp, hexCode: string) {
  try {
      const settlementData = await api.getSettlement(hexCode);
    if (!settlementData || !settlementData.success) {
      showErrorState('Settlement not found');
      return;
    }
    const settlement = settlementData.settlement;
    const mapContainer = document.querySelector('.map-container');
    if (!mapContainer) return;
    // Save original content for restoration
    if (!mapContainer.hasAttribute('data-original-content')) {
      mapContainer.setAttribute('data-original-content', mapContainer.innerHTML);
    }
    // Prepare fields
    const name = settlement.name || '?';
    const location = `HEX ${hexCode} - ${settlement.region || '?'}`;
    const population = settlement.population || '?';
    const atmosphere = settlement.atmosphere || '?';
    const description = settlement.description || '';
    const features = (settlement.notable_features && settlement.notable_features.length > 0) ? settlement.notable_features.join("\n") : '';
    const tavern = settlement.local_tavern || '';
    const power = settlement.local_power || '';
    // Build HTML
    let html = `
      <div class="city-hex-details-box">
        <div class="ascii-box">
          <div class="ascii-inner-box">
            <div class="mb-4" style="text-align:center;">
          <button class="btn btn-mork-borg btn-warning me-2" onclick="window.app.restoreMap()">RETURN TO MAP</button>
        </div>
            <div class="ascii-section ascii-settlement-name">
              <span>${name}</span>
            </div>
            <div class="ascii-section ascii-settlement-location">
              <span>LOCATION: ${location}</span>
            </div>
            <div class="ascii-section ascii-settlement-population">
              <span>POPULATION: ${population}</span>
            </div>
            <div class="ascii-section ascii-settlement-atmosphere">
              <span>ATMOSPHERE: ${atmosphere}</span>
            </div>
            <div class="ascii-section ascii-settlement-description">
              <span>DESCRIPTION:</span>
              <pre>${description}</pre>
            </div>
            <div class="ascii-section ascii-settlement-features">
              <span>NOTABLE FEATURES:</span>
              <pre>${features}</pre>
            </div>
            <div class="ascii-section ascii-settlement-tavern">
              <span>LOCAL TAVERN:</span>
              <pre>${tavern}</pre>
            </div>
            <div class="ascii-section ascii-settlement-power">
              <span>LOCAL POWER:</span>
              <pre>${power}</pre>
            </div>
          </div>
        </div>
      </div>
    `;
    mapContainer.innerHTML = html;
  } catch (error) {
    console.error('Error loading settlement details:', error);
    showErrorState('Failed to load settlement details');
  }
}

function displayHexContent(hexData: any) {
  const container = document.getElementById('details-panel');
  if (!container) return;

  console.log('🔍 Hex data for display:', hexData);

  // Prepare fields
  const title = hexData.title || `HEX ${hexData.hex_code}`;
  const terrain = hexData.terrain_name || hexData.terrain || 'Unknown';
  const hexType = hexData.hex_type || 'Unknown';
  const encounter = hexData.encounter?.html || hexData.encounter?.raw || hexData.encounter || '';
  const denizen = hexData.denizen?.html || hexData.denizen?.raw || hexData.denizen || '';
  const notableFeature = hexData.notable_feature?.html || hexData.notable_feature?.raw || hexData.notable_feature || '';
  const atmosphere = hexData.atmosphere?.html || hexData.atmosphere?.raw || hexData.atmosphere || '';
  const loot = (hexData.loot && hexData.loot.length > 0) ? hexData.loot.map((item: any) => item.name || JSON.stringify(item)).join("\n") : '';

  let html = `
    <div class="city-hex-details-box">
      <div class="ascii-box">
        <div class="ascii-inner-box">
          <div class="ascii-section ascii-hex-title">
            <span>${title}</span>
          </div>
          <div class="ascii-section ascii-hex-terrain">
            <span>TERRAIN: ${terrain}</span>
          </div>
          <div class="ascii-section ascii-hex-type">
            <span>TYPE: ${hexType}</span>
          </div>
  `;

  if (encounter) {
        html += `
          <div class="ascii-section ascii-hex-encounter">
            <span>ENCOUNTER:</span>
            <pre>${encounter}</pre>
          </div>
    `;
  }

  if (denizen) {
      html += `
          <div class="ascii-section ascii-hex-denizen">
            <span>DENIZEN:</span>
            <pre>${denizen}</pre>
          </div>
    `;
  }

  if (notableFeature) {
      html += `
          <div class="ascii-section ascii-hex-feature">
            <span>NOTABLE FEATURE:</span>
            <pre>${notableFeature}</pre>
          </div>
    `;
  }

  if (atmosphere) {
      html += `
          <div class="ascii-section ascii-hex-atmosphere">
            <span>ATMOSPHERE:</span>
            <pre>${atmosphere}</pre>
          </div>
    `;
  }

  if (loot) {
    html += `
          <div class="ascii-section ascii-hex-loot">
            <span>LOOT:</span>
            <pre>${loot}</pre>
          </div>
    `;
  }

  // If no content was found, show a message
  if (!encounter && !denizen && !notableFeature && !atmosphere && !loot) {
    html += `
          <div class="ascii-section ascii-hex-no-content">
            <span>No additional content available for this hex.</span>
          </div>
    `;
  }

  html += `
        </div>
      </div>
    </div>
  `;

  console.log('Setting details panel:', container, html, hexData); // Add this line before setting innerHTML
  container.innerHTML = html;
}

function showEmptyState(app: DyingLandsApp) {
  const container = document.getElementById('details-panel');
  if (!container) return;

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
}

function showErrorState(message: string) {
  const container = document.getElementById('details-panel');
  if (!container) return;

  container.innerHTML = `
    <div class="city-hex-details-box">
      <div class="ascii-box">
        <div class="ascii-inner-box">
          <div class="ascii-section">
            <span>ERROR</span>
          </div>
          <div class="ascii-section">
            <pre>${message}</pre>
          </div>
        </div>
      </div>
    </div>
  `;
} 