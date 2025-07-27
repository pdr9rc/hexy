// web/static/hexViewer.ts
import { DyingLandsApp } from './main.js';
import * as api from './api.js';
import * as ui from './uiUtils.js';

// Helper functions for city grid generation
function getCityHexSymbol(contentType: string): string {
  switch (contentType?.toLowerCase()) {
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

function generateDistrictColor(districtName: string, allDistricts: string[] = []): string {
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
  
  // Use the old strategy: get district index from sorted array
  const sortedDistricts = allDistricts.sort();
  const districtIndex = sortedDistricts.indexOf(districtName);
  return morkBorgColors[districtIndex % morkBorgColors.length];
}

function getCityHexTerrainClass(contentType: string): string {
  // Map city content types to terrain classes for consistent coloring
  const terrainMap: { [key: string]: string } = {
    'district': 'terrain-plains',      // Residential areas
    'building': 'terrain-mountain',    // Structures
    'street': 'terrain-desert',        // Roads/paths
    'landmark': 'terrain-forest',      // Important locations
    'market': 'terrain-coast',         // Commercial areas
    'temple': 'terrain-snow',          // Religious sites
    'tavern': 'terrain-swamp',         // Entertainment
    'guild': 'terrain-mountain',       // Professional organizations
    'residence': 'terrain-plains',     // Homes
    'ruins': 'terrain-unknown',        // Abandoned areas
    'empty': 'terrain-unknown',        // Empty spaces
    'unknown': 'terrain-unknown'       // Unknown content
  };
  
  return terrainMap[contentType] || 'terrain-unknown';
}

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
    
    // Disable zoom when entering city details view
    if ((window as any).disableZoom) {
      (window as any).disableZoom();
    }
    
    const city = cityData.city;
    const mapContainer = document.querySelector('.map-container');
    const mapZoomContainer = document.getElementById('map-zoom-container');
    if (!mapContainer || !mapZoomContainer) return;
    
    // Save original content for restoration
    if (!mapContainer.hasAttribute('data-original-content')) {
      const hexGrid = mapZoomContainer.querySelector('#hexGrid');
      if (hexGrid) {
        mapContainer.setAttribute('data-original-content', hexGrid.innerHTML);
      }
    }
    
    // Load city overlay data for grid and districts
    const overlayName = 'galgenbeck'; // Default to galgenbeck for now
    let cityOverlayData = null;
    try {
      const overlayResponse = await api.getCityOverlay(overlayName);
      if (overlayResponse.success) {
        cityOverlayData = overlayResponse.overlay;
      }
    } catch (error) {
      console.warn('Could not load city overlay data:', error);
    }
    
    // Prepare city fields
    const name = city.name || '?';
    const location = `HEX ${hexCode} - ${city.region || '?'}`;
    const population = city.population || '?';
    const atmosphere = city.atmosphere || '?';
    const description = city.description?.raw || city.description || 'No description available';
    const features = (city.notable_features && city.notable_features.length > 0) ? city.notable_features.join("\n") : '';
    const keyNpcs = (city.key_npcs && city.key_npcs.length > 0) ? city.key_npcs.join("\n") : '';
    const regionalNpcs = (cityData.regional_npcs && cityData.regional_npcs.length > 0) ? cityData.regional_npcs.join("\n") : '';
    const factions = (cityData.factions && cityData.factions.length > 0) ? cityData.factions.map((f: any) => `${f.name} (${f.influence}) - ${f.description}`).join("\n") : '';
    
    // Generate city grid if overlay data is available
    let cityGridHTML = '';
    let districtButtonsHTML = '';
    let districtArray: string[] = [];
    
    if (cityOverlayData) {
      // Generate district array
      const districts = new Set<string>();
      if (cityOverlayData.hex_grid) {
        for (const hexId of Object.keys(cityOverlayData.hex_grid)) {
          const hexData = cityOverlayData.hex_grid[hexId];
          if (hexData?.district) {
            districts.add(hexData.district);
          }
        }
      }
      districtArray = Array.from(districts)
        .filter(district => district !== 'empty' && district !== 'unknown' && district !== 'Empty')
        .sort();
      
      // Generate grid HTML (simplified version)
      const gridSize = 10;
      cityGridHTML = '<div class="city-overlay-grid">';
      for (let row = 0; row < gridSize; row++) {
        cityGridHTML += '<div class="city-overlay-row">';
        for (let col = 0; col < gridSize; col++) {
          const hexId = `${row}_${col}`;
          const hexData = cityOverlayData.hex_grid[hexId];
          const content = hexData?.content || {};
          const symbol = getCityHexSymbol(content.type);
          const district = hexData?.district || 'unknown';
          const isVisible = hexData && content.name && content.name !== "Unknown" && content.type !== "empty";
          const districtColor = generateDistrictColor(district, districtArray);
          
          cityGridHTML += `
            <div class="city-hex-cell district-${district.toLowerCase().replace(/\s+/g, '-')} ${isVisible ? '' : 'city-hex-invisible'}"
                 data-hex-id="${hexId}" 
                 data-overlay="${cityOverlayData.name}"
                 data-district="${district}"
                 style="background: ${districtColor} !important;"
                 title="${content.name || "Unknown"} (${content.type || "unknown"}) - ${district}"
                 onclick="handleCityHexClick('${hexId}', '${district}', '${content.name || 'Unknown'}', '${content.description || ''}', '${hexCode}')">
              <span class="city-hex-symbol">${symbol}</span>
            </div>
          `;
        }
        cityGridHTML += '</div>';
      }
      cityGridHTML += '</div>';
      
      // Generate district buttons
      districtButtonsHTML = `
        <div class="district-buttons-container">
          <div class="district-buttons-row">
            ${districtArray.map(district => `
              <button class="district-button" 
                      style="background: ${generateDistrictColor(district, districtArray)} !important;"
                      title="${district}">
                ${district}
              </button>
            `).join('')}
          </div>
        </div>
      `;
    }
    
    // Build integrated HTML
    let html = `
      <div class="city-hex-details-box">
        <div class="ascii-box">
          <div class="ascii-inner-box">
            <div class="mb-4" style="text-align:center;">
              <button class="btn-mork-borg me-2" onclick="window.app.showHexDetails('${hexCode}')">RETURN TO HEX</button>
              <button class="btn-mork-borg btn-warning" onclick="window.app.restoreMap()">RETURN TO MAP</button>
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
            ${cityGridHTML ? `
            <div class="ascii-section ascii-city-grid">
              <span>CITY DISTRICTS:</span>
              <div class="city-grid-container">
                ${cityGridHTML}
              </div>
            </div>
            ` : ''}
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
            ${districtButtonsHTML ? `
            <div class="ascii-section ascii-district-buttons">
              <span>DISTRICTS:</span>
              <div class="district-buttons-inline">
                ${districtArray.map(district => `
                  <button class="district-button-inline" 
                          style="background: ${generateDistrictColor(district, districtArray)} !important;"
                          title="${district}">
                    ${district}
                  </button>
                `).join('')}
              </div>
            </div>
            ` : ''}
          </div>
        </div>
      </div>
    `;
    
    if (mapZoomContainer) {
      mapZoomContainer.innerHTML = html;
    }
    
    // Add click handler function to window
    (window as any).handleCityHexClick = function(hexId: string, district: string, name: string, description: string, cityHexCode: string) {
      const descriptionSection = document.querySelector('.ascii-city-description pre');
      const featuresSection = document.querySelector('.ascii-city-features pre');
      
      if (district && district !== 'unknown' && district !== 'empty') {
        // Show district details
        if (descriptionSection) {
          descriptionSection.textContent = `${district.toUpperCase()}\n\n${description || 'No district description available.'}`;
        }
        if (featuresSection) {
          featuresSection.textContent = `District: ${district}\nLocation: ${name}`;
        }
      } else {
        // Show city details
        if (descriptionSection) {
          descriptionSection.textContent = description;
        }
        if (featuresSection) {
          featuresSection.textContent = features;
        }
      }
    };
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
    
    // Disable zoom when entering settlement details view
    if ((window as any).disableZoom) {
      (window as any).disableZoom();
    }
    
    const settlement = settlementData.settlement;
    const mapContainer = document.querySelector('.map-container');
    const mapZoomContainer = document.getElementById('map-zoom-container');
    if (!mapContainer || !mapZoomContainer) return;
    // Save original content for restoration
    if (!mapContainer.hasAttribute('data-original-content')) {
      const hexGrid = mapZoomContainer.querySelector('#hexGrid');
      if (hexGrid) {
        mapContainer.setAttribute('data-original-content', hexGrid.innerHTML);
      }
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
          <button class="btn-mork-borg btn-warning me-2" onclick="window.app.restoreMap()">RETURN TO MAP</button>
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
    if (mapZoomContainer) {
      mapZoomContainer.innerHTML = html;
    }
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
  const description = hexData.description?.html || hexData.description?.raw || hexData.description || '';

  // Treasure/Loot fields - check all possible field names
  const loot = hexData.loot || '';
  const treasure = hexData.treasure || '';
  const sunkenTreasure = hexData.sunken_treasure || '';
  
  // Format loot objects properly
  const formatLoot = (lootData: any) => {
    if (typeof lootData === 'string') return lootData;
    if (typeof lootData === 'object' && lootData !== null) {
      if (lootData.type && lootData.item && lootData.description) {
        return `Type: ${lootData.type}\nItem: ${lootData.item}\nDescription: ${lootData.description}\nFull Description: ${lootData.full_description || lootData.description}`;
      }
      return JSON.stringify(lootData, null, 2);
    }
    return '';
  };

  const formattedLoot = formatLoot(loot);
  const formattedTreasure = formatLoot(treasure);
  const formattedSunkenTreasure = formatLoot(sunkenTreasure);

  // NPC-specific fields
  const npcName = hexData.name || '';
  const npcDemeanor = hexData.demeanor || '';
  const npcDenizenType = hexData.denizen_type || '';
  const npcMotivation = hexData.motivation || '';
  const npcFeature = hexData.feature || '';

  // Beast-specific fields
  const beastType = hexData.beast_type || '';
  const beastFeature = hexData.beast_feature || '';
  const beastBehavior = hexData.beast_behavior || '';
  const threatLevel = hexData.threat_level || '';
  const territory = hexData.territory || '';

  // Dungeon-specific fields
  const dungeonType = hexData.dungeon_type || '';
  const danger = hexData.danger || '';
  const ancientKnowledge = hexData.ancient_knowledge || '';

  // Sea encounter-specific fields
  const encounterType = hexData.encounter_type || '';
  const origin = hexData.origin || '';
  const behavior = hexData.behavior || '';

  // Magical effects
  const magicalEffect = hexData.magical_effect || '';

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

  // Display NPC-specific information if this is an NPC hex
  if (hexData.is_npc || hexType === 'npc') {
    if (npcName) {
      html += `
        <div class="ascii-section ascii-hex-npc-name">
          <span>NAME:</span>
          <pre>${npcName}</pre>
        </div>
      `;
    }

    if (npcDenizenType) {
      html += `
        <div class="ascii-section ascii-hex-npc-type">
          <span>DENIZEN TYPE:</span>
          <pre>${npcDenizenType}</pre>
        </div>
      `;
    }

    if (npcDemeanor) {
      html += `
        <div class="ascii-section ascii-hex-npc-demeanor">
          <span>DEMEANOR:</span>
          <pre>${npcDemeanor}</pre>
        </div>
      `;
    }

    if (npcMotivation) {
      html += `
        <div class="ascii-section ascii-hex-npc-motivation">
          <span>MOTIVATION:</span>
          <pre>${npcMotivation}</pre>
        </div>
      `;
    }

    if (npcFeature) {
      html += `
        <div class="ascii-section ascii-hex-npc-feature">
          <span>FEATURE:</span>
          <pre>${npcFeature}</pre>
        </div>
      `;
    }
  }

  // Display Beast-specific information
  if (hexData.is_beast || hexType === 'beast') {
    if (beastType) {
      html += `
        <div class="ascii-section ascii-hex-beast-type">
          <span>BEAST TYPE:</span>
          <pre>${beastType}</pre>
        </div>
      `;
    }

    if (beastFeature) {
      html += `
        <div class="ascii-section ascii-hex-beast-feature">
          <span>BEAST FEATURE:</span>
          <pre>${beastFeature}</pre>
        </div>
      `;
    }

    if (beastBehavior) {
      html += `
        <div class="ascii-section ascii-hex-beast-behavior">
          <span>BEAST BEHAVIOR:</span>
          <pre>${beastBehavior}</pre>
        </div>
      `;
    }

    if (threatLevel) {
      html += `
        <div class="ascii-section ascii-hex-threat-level">
          <span>THREAT LEVEL:</span>
          <pre>${threatLevel}</pre>
        </div>
      `;
    }

    if (territory) {
      html += `
        <div class="ascii-section ascii-hex-territory">
          <span>TERRITORY:</span>
          <pre>${territory}</pre>
        </div>
      `;
    }
  }

  // Display Dungeon-specific information
  if (hexData.is_dungeon || hexType === 'dungeon') {
    if (dungeonType) {
      html += `
        <div class="ascii-section ascii-hex-dungeon-type">
          <span>DUNGEON TYPE:</span>
          <pre>${dungeonType}</pre>
        </div>
      `;
    }

    if (danger) {
      html += `
        <div class="ascii-section ascii-hex-danger">
          <span>DANGER:</span>
          <pre>${danger}</pre>
        </div>
      `;
    }

    if (ancientKnowledge) {
      html += `
        <div class="ascii-section ascii-hex-ancient-knowledge">
          <span>ANCIENT KNOWLEDGE:</span>
          <pre>${formatLoot(ancientKnowledge)}</pre>
        </div>
      `;
    }
  }

  // Display Sea encounter-specific information
  if (hexData.is_sea_encounter || hexType === 'sea_encounter') {
    if (encounterType) {
      html += `
        <div class="ascii-section ascii-hex-encounter-type">
          <span>ENCOUNTER TYPE:</span>
          <pre>${encounterType}</pre>
        </div>
      `;
    }

    if (origin) {
      html += `
        <div class="ascii-section ascii-hex-origin">
          <span>ORIGIN:</span>
          <pre>${origin}</pre>
        </div>
      `;
    }

    if (behavior) {
      html += `
        <div class="ascii-section ascii-hex-behavior">
          <span>BEHAVIOR:</span>
          <pre>${behavior}</pre>
        </div>
      `;
    }
  }

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

  if (description) {
      html += `
          <div class="ascii-section ascii-hex-description">
            <span>DESCRIPTION:</span>
            <pre>${description}</pre>
          </div>
    `;
  }

  // Display treasure/loot information (check all possible field names)
  if (formattedLoot) {
    html += `
          <div class="ascii-section ascii-hex-loot">
            <span>LOOT:</span>
            <pre>${formattedLoot}</pre>
          </div>
    `;
  }

  if (formattedTreasure) {
    html += `
          <div class="ascii-section ascii-hex-treasure">
            <span>TREASURE:</span>
            <pre>${formattedTreasure}</pre>
          </div>
    `;
  }

  if (formattedSunkenTreasure) {
    html += `
          <div class="ascii-section ascii-hex-sunken-treasure">
            <span>SUNKEN TREASURE:</span>
            <pre>${formattedSunkenTreasure}</pre>
          </div>
    `;
  }

  if (magicalEffect) {
    html += `
          <div class="ascii-section ascii-hex-magical-effect">
            <span>MAGICAL EFFECT:</span>
            <pre>${magicalEffect}</pre>
          </div>
    `;
  }

  // Check if any content was found
  const hasContent = encounter || denizen || notableFeature || atmosphere || description || 
                    formattedLoot || formattedTreasure || formattedSunkenTreasure || magicalEffect ||
                    npcName || npcDemeanor || npcDenizenType || npcMotivation || npcFeature ||
                    beastType || beastFeature || beastBehavior || threatLevel || territory ||
                    dungeonType || danger || ancientKnowledge ||
                    encounterType || origin || behavior;

  if (!hasContent) {
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