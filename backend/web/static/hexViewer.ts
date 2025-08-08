// web/static/hexViewer.ts
import { DyingLandsApp } from './main.js';
import * as api from './api.js';
import * as ui from './uiUtils.js';
import { generateDistrictColor } from './utils/colorUtils.js';
import { t } from './translations.js';

// Function to load city context in the left panel
function loadCityContext(contextData: any) {
  const detailsPanel = document.getElementById('details-panel');
  if (!detailsPanel) return;
  
  const context = contextData.context;
  
  let html = `
    <div class="city-context-panel">
      <div class="ascii-box">
        <div class="ascii-inner-box">
          <!-- City Information -->
          <div class="ascii-section ascii-city-title">
            <span>${context.name}</span>
          </div>
          <div class="ascii-section ascii-city-description">
            <span>${t('CITY DESCRIPTION')}</span>
            <div class="ascii-content">${context.description}</div>
          </div>
  `;
  
  // City Events
  if (context.city_events && context.city_events.length > 0) {
    html += `
      <div class="ascii-section ascii-city-events">
        <span>${t('CITY EVENTS')}</span>
        <div class="ascii-content">${context.city_events.slice(0, 3).join('\n')}</div>
      </div>
    `;
  }
  
  // Weather Conditions
  if (context.weather_conditions && context.weather_conditions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-weather">
        <span>${t('WEATHER')}</span>
        <div class="ascii-content">${context.weather_conditions.slice(0, 2).join('\n')}</div>
      </div>
    `;
  }
  
  // Regional NPCs
  if (context.regional_npcs && context.regional_npcs.length > 0) {
    html += `
      <div class="ascii-section ascii-city-npcs">
        <span>${t('REGIONAL NPCS')}</span>
        <div class="ascii-content">${context.regional_npcs.slice(0, 3).join('\n')}</div>
      </div>
    `;
  }
  
  // Major Factions
  if (context.major_factions && context.major_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>${t('MAJOR FACTIONS')}</span>
        <div class="ascii-content">
    `;
    
    for (const faction of context.major_factions.slice(0, 3)) {
      html += `• ${faction.name}\n`;
      html += `  Leader: ${faction.leader}\n`;
      html += `  HQ: ${faction.headquarters}\n`;
      html += `  Influence: ${faction.influence}\n`;
      html += `  Attitude: ${faction.attitude}\n`;
      if (faction.activities && faction.activities.length > 0) {
        html += `  Activities: ${faction.activities.slice(0, 2).join(', ')}\n`;
      }
      html += '\n';
    }
    
    html += `
        </div>
      </div>
    `;
  }
  
  // Local Factions
  if (context.local_factions && context.local_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>${t('LOCAL FACTIONS')}</span>
        <div class="ascii-content">
    `;
    
    for (const faction of context.local_factions.slice(0, 3)) {
      html += `• ${faction.name}\n`;
      html += `  Leader: ${faction.leader}\n`;
      html += `  HQ: ${faction.headquarters}\n`;
      html += `  Influence: ${faction.influence}\n`;
      html += `  Attitude: ${faction.attitude}\n`;
      if (faction.activities && faction.activities.length > 0) {
        html += `  Activities: ${faction.activities.slice(0, 2).join(', ')}\n`;
      }
      html += '\n';
    }
    
    html += `
        </div>
      </div>
    `;
  }
  
  // Criminal Factions
  if (context.criminal_factions && context.criminal_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>CRIMINAL FACTIONS:</span>
        <div class="ascii-content">
    `;
    
    for (const faction of context.criminal_factions.slice(0, 2)) {
      html += `• ${faction.name}\n`;
      html += `  Leader: ${faction.leader}\n`;
      html += `  HQ: ${faction.headquarters}\n`;
      html += `  Influence: ${faction.influence}\n`;
      html += `  Attitude: ${faction.attitude}\n`;
      if (faction.activities && faction.activities.length > 0) {
        html += `  Activities: ${faction.activities.slice(0, 2).join(', ')}\n`;
      }
      html += '\n';
    }
    
    html += `
        </div>
      </div>
    `;
  }
  
  // Faction Relationships
  if (context.faction_relationships && context.faction_relationships.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>FACTION RELATIONSHIPS:</span>
        <div class="ascii-content">
    `;
    
    for (const relationship of context.faction_relationships.slice(0, 3)) {
      html += `• ${relationship.faction1} ↔ ${relationship.faction2}\n`;
      html += `  ${relationship.relationship}: ${relationship.description}\n`;
      html += '\n';
    }
    
    html += `
        </div>
      </div>
    `;
  }
  
  // Legacy Factions (fallback)
  if (context.legacy_factions && context.legacy_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>OTHER FACTIONS:</span>
        <div class="ascii-content">
    `;
    
    for (const faction of context.legacy_factions.slice(0, 3)) {
      if (typeof faction === 'string') {
        html += `• ${faction}\n`;
      } else if (faction.name && faction.attitude) {
        html += `• ${faction.name} (${faction.attitude})\n`;
      } else if (faction.name) {
        html += `• ${faction.name}\n`;
      }
    }
    
    html += `
        </div>
      </div>
    `;
  }
  
  // Major Landmarks
  if (context.major_landmarks && context.major_landmarks.length > 0) {
    html += `
      <div class="ascii-section ascii-city-landmarks">
        <span>${t('MAJOR LANDMARKS')}</span>
        <div class="ascii-content">${context.major_landmarks.slice(0, 3).join('\n')}</div>
      </div>
    `;
  }
  
  // District Information
  if (context.districts && Object.keys(context.districts).length > 0) {
    html += `
      <div class="ascii-section ascii-city-districts">
        <span>${t('DISTRICTS')}</span>
        <div class="ascii-content">
    `;
    
    for (const [districtName, districtData] of Object.entries(context.districts)) {
      const district = districtData as any;
      html += `${districtName.toUpperCase()}:\n`;
      html += `  ${district.description}\n`;
      if (district.landmarks && district.landmarks.length > 0) {
        html += `  Landmarks: ${district.landmarks.slice(0, 2).join(', ')}\n`;
      }
      html += '\n';
    }
    
    html += `
        </div>
      </div>
    `;
  }
  
  html += `
        </div>
      </div>
    </div>
  `;
  
  detailsPanel.innerHTML = html;
}

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

// generateDistrictColor function is now imported from utils/colorUtils.js

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
    // Get the city overlay name from the hex code
    const cityOverlayName = app.getOverlayNameFromHexCode(hexCode);
    
    // Load city context data for left panel
    const contextData = await api.getCityContext(cityOverlayName);
    if (contextData && contextData.success) {
      loadCityContext(contextData);
    }
    
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
    let cityOverlayData = null;
    try {
      const overlayResponse = await api.getCityOverlay(cityOverlayName);
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
                 >
              <span class="city-hex-symbol">${symbol}</span>
            </div>
          `;
        }
        cityGridHTML += '</div>';
      }
      cityGridHTML += '</div>';
      
          // Add click handler function to window BEFORE generating HTML
    (window as any).handleCityHexClick = async function(hexId: string, district: string, name: string, description: string, cityHexCode: string) {
      console.log('🔍 handleCityHexClick called with:', { hexId, district, name, description, cityHexCode });
      try {
        // Fetch detailed hex data from API
        console.log('📡 Fetching hex data from API...');
        const response = await fetch(`/api/city-overlay/${cityOverlayName}/hex/${hexId}`);
        const data = await response.json();
        console.log('📦 API response:', data);
        
        if (data.success && data.hex) {
          const hexData = data.hex;
          const content = hexData.content || {};
          console.log('🎯 Processing hex content:', content);
          
          // Get the details panel container
          const detailsPanel = document.getElementById('details-panel');
          if (!detailsPanel) return;
          
          // Build comprehensive HTML with all enriched fields
          let html = `
            <div class="city-hex-details-box">
              <div class="ascii-box">
                <div class="ascii-inner-box">
                  <div class="mb-4" style="text-align:center;">
                    <button class="btn-mork-borg me-2" onclick="window.app.showHexDetails('${cityHexCode}')">RETURN TO HEX</button>
                    <button class="btn-mork-borg btn-warning" onclick="window.app.restoreMap()">RETURN TO MAP</button>
                  </div>
                  
                  <!-- Basic Information Section -->
                  <div class="ascii-section ascii-hex-title">
                    <span>${content.name || name}</span>
                  </div>
                  <div class="ascii-section ascii-hex-type">
                    <span>${t('TYPE')} ${content.type || 'unknown'}</span>
                  </div>
                  <div class="ascii-section ascii-hex-district">
                    <span>${t('DISTRICT')} ${district}</span>
                  </div>
                  <div class="ascii-section ascii-hex-position">
                    <span>${t('POSITION')} ${content.position_type || 'unknown'}</span>
                  </div>
                  
                  <!-- Description Section -->
                  <div class="ascii-section ascii-hex-description">
                    <span>${t('DESCRIPTION')}</span>
                    <div class="ascii-content">${content.description || description || 'No description available.'}</div>
                  </div>
                  
                  <!-- Atmosphere & Encounter Section -->
                  <div class="ascii-section ascii-hex-atmosphere">
                    <span>${t('ATMOSPHERE')}</span>
                    <div class="ascii-content">${content.atmosphere || 'No atmosphere available.'}</div>
                  </div>
                  <div class="ascii-section ascii-hex-encounter">
                    <span>${t('ENCOUNTER')}</span>
                    <div class="ascii-content">${content.encounter || 'No encounter available.'}</div>
                  </div>
          `;
          
          // Enriched Content Section
          if (content.weather || content.city_event || content.notable_features) {
            html += `
              <div class="ascii-section ascii-hex-enriched">
                <span>ENRICHED CONTENT:</span>
                <div class="ascii-content">
            `;
            
            if (content.weather) {
              html += `WEATHER: ${content.weather}\n`;
            }
            if (content.city_event) {
              html += `CITY EVENT: ${content.city_event}\n`;
            }
            if (content.notable_features && content.notable_features.length > 0) {
              html += `NOTABLE FEATURES:\n${content.notable_features.join('\n')}\n`;
            }
            
            html += `
                </div>
              </div>
            `;
          }
          
          // NPC Information Section (for relevant types)
          if (content.npc_trait || content.npc_concern || content.npc_want || content.npc_secret || content.npcs) {
            html += `
              <div class="ascii-section ascii-hex-npcs">
                <span>NPC INFORMATION:</span>
                <div class="ascii-content">
            `;
            
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
            if (content.npcs && content.npcs.length > 0) {
              html += `NPCS: ${content.npcs.join(', ')}\n`;
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
          
          // Cross-References Section
          if (content.related_hexes && content.related_hexes.length > 0) {
            html += `
              <div class="ascii-section ascii-hex-related">
                <span>RELATED HEXES:</span>
                <div class="ascii-content">
            `;
            
            content.related_hexes.forEach((related: any) => {
              html += `<span class="related-hex-link" onclick="navigateToRelatedHex('${related.hex_id}')">${related.hex_id}: ${related.name} (${related.type}) - ${related.relationship}</span>\n`;
            });
            
            html += `
                </div>
              </div>
            `;
          }
          
          // Random Tables Section
          if (content.random_table && content.random_table.length > 0) {
            html += `
              <div class="ascii-section ascii-hex-random">
                <span>RANDOM ENCOUNTERS:</span>
                <div class="ascii-content">
            `;
            
            content.random_table.forEach((entry: string) => {
              html += `${entry}\n`;
            });
            
            html += `
                </div>
              </div>
            `;
          }
          
          // Close the HTML structure
          html += `
                </div>
              </div>
            </div>
          `;
          
          // Update the details panel
          detailsPanel.innerHTML = html;
          
        } else {
          // Fallback to basic display
          const descriptionSection = document.querySelector('.ascii-city-description pre');
          const featuresSection = document.querySelector('.ascii-city-features pre');
          
          if (district && district !== 'unknown' && district !== 'empty') {
            if (descriptionSection) {
              descriptionSection.textContent = `${district.toUpperCase()}\n\n${description || 'No district description available.'}`;
            }
            if (featuresSection) {
              featuresSection.textContent = `District: ${district}\nLocation: ${name}`;
            }
          } else {
            if (descriptionSection) {
              descriptionSection.textContent = description;
            }
            if (featuresSection) {
              featuresSection.textContent = features;
            }
          }
        }
      } catch (error) {
        console.error('Error fetching hex details:', error);
        // Fallback to basic display
        const descriptionSection = document.querySelector('.ascii-city-description pre');
        const featuresSection = document.querySelector('.ascii-city-features pre');
        
        if (district && district !== 'unknown' && district !== 'empty') {
          if (descriptionSection) {
            descriptionSection.textContent = `${district.toUpperCase()}\n\n${description || 'No district description available.'}`;
          }
          if (featuresSection) {
            featuresSection.textContent = `District: ${district}\nLocation: ${name}`;
          }
        } else {
          if (descriptionSection) {
            descriptionSection.textContent = description;
          }
          if (featuresSection) {
            featuresSection.textContent = features;
          }
        }
      }
    };
    
    // Generate enhanced district legend and controls
      districtButtonsHTML = `
        <div class="city-controls-panel">
          <!-- District Legend -->
          <div class="district-legend">
            <h4>DISTRICTS</h4>
            <div class="district-buttons-grid">
            ${districtArray.map(district => `
              <button class="district-button" 
                      style="background: ${generateDistrictColor(district, districtArray)} !important;"
                        title="${district}"
                        onclick="filterByDistrict('${district}')">
                ${district}
              </button>
            `).join('')}
            </div>
          </div>
          
          <!-- Hex Type Legend -->
          <div class="hex-type-legend">
            <h4>HEX TYPES</h4>
            <div class="hex-type-grid">
              <div class="hex-type-item">
                <span class="hex-symbol">☺</span>
                <span>Tavern</span>
              </div>
              <div class="hex-type-item">
                <span class="hex-symbol">◊</span>
                <span>Market</span>
              </div>
              <div class="hex-type-item">
                <span class="hex-symbol">†</span>
                <span>Temple</span>
              </div>
              <div class="hex-type-item">
                <span class="hex-symbol">⚔</span>
                <span>Guild</span>
              </div>
              <div class="hex-type-item">
                <span class="hex-symbol">▲</span>
                <span>Landmark</span>
              </div>
              <div class="hex-type-item">
                <span class="hex-symbol">⌂</span>
                <span>Building</span>
              </div>
              <div class="hex-type-item">
                <span class="hex-symbol">═</span>
                <span>Street</span>
              </div>
            </div>
          </div>
          
          <!-- Quick Navigation -->
          <div class="quick-navigation">
            <h4>QUICK NAV</h4>
            <div class="nav-buttons">
              <button class="btn-mork-borg btn-small" onclick="showAllDistricts()">SHOW ALL</button>
              <button class="btn-mork-borg btn-small" onclick="showTaverns()">TAVERNS</button>
              <button class="btn-mork-borg btn-small" onclick="showMarkets()">MARKETS</button>
              <button class="btn-mork-borg btn-small" onclick="showTemples()">TEMPLES</button>
            </div>
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
              <button class="btn-mork-borg me-2" onclick="window.app.showHexDetails('${hexCode}')">${t('RETURN TO HEX')}</button>
              <button class="btn-mork-borg btn-warning" onclick="window.app.restoreMap()">${t('RETURN TO MAP')}</button>
        </div>
            <div class="ascii-section ascii-city-name">
              <span>${name}</span>
            </div>
            <div class="ascii-section ascii-city-location">
              <span>${t('LOCATION')} ${location}</span>
            </div>
            <div class="ascii-section ascii-city-population">
              <span>${t('POPULATION')} ${population}</span>
            </div>
            <div class="ascii-section ascii-city-atmosphere">
              <span>${t('ATMOSPHERE')} ${atmosphere}</span>
            </div>
            ${cityGridHTML ? `
            <div class="ascii-section ascii-city-grid">
              <span>${t('CITY DISTRICTS')}</span>
              <div class="city-grid-container">
                ${cityGridHTML}
              </div>
            </div>
            ` : ''}
            <div class="ascii-section ascii-city-description">
              <span>${t('DESCRIPTION')}</span>
              <div class="ascii-content">${description}</div>
            </div>
            <div class="ascii-section ascii-city-features">
              <span>${t('NOTABLE FEATURES')}</span>
              <div class="ascii-content">${features}</div>
            </div>
            <div class="ascii-section ascii-city-key-npcs">
              <span>${t('KEY NPCS')}</span>
              <div class="ascii-content">${keyNpcs}</div>
            </div>
            <div class="ascii-section ascii-city-regional-npcs">
              <span>${t('REGIONAL NPCS')}</span>
              <div class="ascii-content">${regionalNpcs}</div>
            </div>
            <div class="ascii-section ascii-city-factions">
              <span>${t('ACTIVE FACTIONS')}</span>
              <div class="ascii-content">${factions}</div>
            </div>
            ${districtButtonsHTML ? `
            <div class="ascii-section ascii-district-buttons">
              <span>${t('DISTRICTS')}</span>
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
    

    
    // Add filtering and navigation functions to window
    (window as any).filterByDistrict = function(districtName: string) {
      const hexCells = document.querySelectorAll('.city-hex-cell');
      hexCells.forEach((cell: any) => {
        const cellDistrict = cell.getAttribute('data-district');
        if (cellDistrict === districtName) {
          cell.style.opacity = '1';
          cell.style.filter = 'none';
        } else {
          cell.style.opacity = '0.3';
          cell.style.filter = 'grayscale(80%)';
        }
      });
    };
    
    (window as any).showAllDistricts = function() {
      const hexCells = document.querySelectorAll('.city-hex-cell');
      hexCells.forEach((cell: any) => {
        cell.style.opacity = '1';
        cell.style.filter = 'none';
      });
    };
    
    (window as any).showTaverns = function() {
      const hexCells = document.querySelectorAll('.city-hex-cell');
      hexCells.forEach((cell: any) => {
        const symbol = cell.querySelector('.city-hex-symbol');
        if (symbol && symbol.textContent === '☺') {
          cell.style.opacity = '1';
          cell.style.filter = 'none';
        } else {
          cell.style.opacity = '0.3';
          cell.style.filter = 'grayscale(80%)';
        }
      });
    };
    
    (window as any).showMarkets = function() {
      const hexCells = document.querySelectorAll('.city-hex-cell');
      hexCells.forEach((cell: any) => {
        const symbol = cell.querySelector('.city-hex-symbol');
        if (symbol && symbol.textContent === '◊') {
          cell.style.opacity = '1';
          cell.style.filter = 'none';
      } else {
          cell.style.opacity = '0.3';
          cell.style.filter = 'grayscale(80%)';
        }
      });
    };
    
    (window as any).showTemples = function() {
      const hexCells = document.querySelectorAll('.city-hex-cell');
      hexCells.forEach((cell: any) => {
        const symbol = cell.querySelector('.city-hex-symbol');
        if (symbol && symbol.textContent === '†') {
          cell.style.opacity = '1';
          cell.style.filter = 'none';
        } else {
          cell.style.opacity = '0.3';
          cell.style.filter = 'grayscale(80%)';
        }
      });
    };
    
    // Navigation function for related hexes
    (window as any).navigateToRelatedHex = function(hexId: string) {
      // Find the hex cell and trigger a click
      const hexCell = document.querySelector(`[data-hex-id="${hexId}"]`) as HTMLElement;
      if (hexCell) {
        hexCell.click();
        // Scroll the hex into view
        hexCell.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
    const features = (() => {
      const arr = Array.isArray(settlement.notable_features)
        ? settlement.notable_features
        : (settlement.notable_feature ? [settlement.notable_feature] : []);
      return arr.length ? arr.join("\n") : '';
    })();
    const tavern = settlement.local_tavern || '';
    const power = settlement.local_power || '';
    // Mörk Borg settlement fields
    const weather = settlement.weather || '';
    const cityEvent = settlement.city_event || '';
    const tavernDetails = settlement.tavern_details || null;
    const formatMenuEntry = (entry: any): string => {
      if (entry == null) return '';
      if (typeof entry === 'string') return entry;
      if (Array.isArray(entry)) return entry.map(formatMenuEntry).join('\n');
      if (typeof entry === 'object') {
        const name = entry.name ?? '';
        const price = entry.price ?? '';
        const currency = entry.currency ?? '';
        const notes = entry.notes ?? entry.quality ?? '';
        const pricePart = [price, currency].filter(Boolean).join(' ');
        const main = [name, pricePart].filter(Boolean).join(' - ');
        return notes ? `${main} (${notes})` : (main || JSON.stringify(entry));
      }
      return String(entry);
    };
    const settlementArt = settlement.settlement_art || '';
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
              <span>${t('LOCATION')}: ${location}</span>
            </div>
            <div class="ascii-section ascii-settlement-population">
              <span>${t('POPULATION')}: ${population}</span>
            </div>
            <div class="ascii-section ascii-settlement-atmosphere">
              <span>${t('ATMOSPHERE')}: ${atmosphere}</span>
            </div>
            <div class="ascii-section ascii-settlement-description">
              <span>${t('DESCRIPTION')}:</span>
              <div class="ascii-content">${description}</div>
            </div>
            <div class="ascii-section ascii-settlement-features">
              <span>${t('NOTABLE FEATURES')}:</span>
              <div class="ascii-content">${features}</div>
            </div>
            <div class="ascii-section ascii-settlement-tavern">
              <span>${t('LOCAL TAVERN')}:</span>
              <div class="ascii-content">${tavern}</div>
            </div>
            <div class="ascii-section ascii-settlement-power">
              <span>${t('LOCAL POWER')}:</span>
              <div class="ascii-content">${power}</div>
            </div>
            ${weather ? `
            <div class="ascii-section ascii-hex-weather">
              <span>${t('WEATHER')}:</span>
              <div class="ascii-content">${weather}</div>
          </div>
            ` : ''}
            ${cityEvent ? `
            <div class="ascii-section ascii-hex-city-event">
              <span>${t('CITY EVENT')}:</span>
              <div class="ascii-content">${cityEvent}</div>
            </div>
            ` : ''}
            ${tavernDetails ? `
            <div class="ascii-section ascii-hex-tavern-details">
              <span>${t('TAVERN DETAILS')}:</span>
              <div class="ascii-content">${[
                tavernDetails.select_menu ? `${t('SELECT MENU')}: ${formatMenuEntry(tavernDetails.select_menu)}` : '',
                tavernDetails.budget_menu ? `${t('BUDGET MENU')}: ${formatMenuEntry(tavernDetails.budget_menu)}` : '',
                tavernDetails.innkeeper ? `${t('INNKEEPER')}: ${tavernDetails.innkeeper}` : '',
                tavernDetails.notable_patron ? `${t('NOTABLE PATRON')}: ${tavernDetails.notable_patron}` : ''
              ].filter(Boolean).join('\n')}</div>
            </div>
            ` : ''}
            ${settlementArt ? `
            <div class="ascii-section ascii-settlement-layout">
              <span>${t('SETTLEMENT LAYOUT')}:</span>
              <div class="ascii-content">${settlementArt}</div>
            </div>
            ` : ''}
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

  // Check if we have raw markdown - if so, show simplified view
  if (hexData.raw_markdown) {
    displaySimplifiedHexView(hexData);
    return;
  }

  // Fallback to original complex view for hexes without raw markdown
  displayComplexHexView(hexData);
}

function displaySimplifiedHexView(hexData: any) {
  const container = document.getElementById('details-panel');
  if (!container) return;

  const title = hexData.title || `HEX ${hexData.hex_code}`;
  const terrain = hexData.terrain_name || hexData.terrain || 'Unknown';
  const hexType = hexData.hex_type || 'Unknown';

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
          <div class="ascii-section ascii-hex-content">
            <span>CONTENT:</span>
            <div class="markdown-content">
              <div class="ascii-content">${hexData.raw_markdown}</div>
            </div>
          </div>
          <div class="ascii-section ascii-hex-actions">
            <button class="btn-mork-borg" onclick="window.app.editHexContent('${hexData.hex_code}')">EDIT</button>
            <button class="btn-mork-borg" onclick="window.app.saveHexContent('${hexData.hex_code}')" id="save-hex-btn" style="display: none;">SAVE</button>
            <button class="btn-mork-borg" onclick="window.app.cancelHexEdit()" id="cancel-hex-btn" style="display: none;">CANCEL</button>
          </div>
        </div>
      </div>
    </div>
  `;

  container.innerHTML = html;
}

function displayComplexHexView(hexData: any) {
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
  
  // Mörk Borg NPC fields
  const npcTrait = hexData.trait || '';
  const npcConcern = hexData.concern || '';
  const npcWant = hexData.want || '';
  const npcApocalypseAttitude = hexData.apocalypse_attitude || '';
  const npcSecret = hexData.secret || '';
  
  // Additional NPC fields
  const npcCarries = hexData.carries || '';
  const npcLocation = hexData.location || '';

  // Beast-specific fields
  const beastType = hexData.beast_type || '';
  const beastFeature = hexData.beast_feature || '';
  const beastBehavior = hexData.beast_behavior || '';
  const threatLevel = hexData.threat_level || '';
  const territory = hexData.territory || '';
  const treasureFound = hexData.treasure_found || '';
  const beastArt = hexData.beast_art || '';

  // Dungeon-specific fields
  const dungeonType = hexData.dungeon_type || '';
  const danger = hexData.danger || '';
  const ancientKnowledge = hexData.ancient_knowledge || '';
  const trapSection = hexData.trap_section || null;
  
  // Settlement-specific fields
  const weather = hexData.weather || '';
  const cityEvent = hexData.city_event || '';
  const tavernDetails = hexData.tavern_details || null;

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
          <div class="ascii-content">${npcName}</div>
        </div>
      `;
    }

    if (npcDenizenType) {
      html += `
        <div class="ascii-section ascii-hex-npc-type">
          <span>DENIZEN TYPE:</span>
          <div class="ascii-content">${npcDenizenType}</div>
        </div>
      `;
    }

    // Mörk Borg NPC fields
    if (npcTrait) {
      html += `
        <div class="ascii-section ascii-hex-npc-trait">
          <span>TRAIT:</span>
          <div class="ascii-content">${npcTrait}</div>
        </div>
      `;
    }

    if (npcConcern) {
      html += `
        <div class="ascii-section ascii-hex-npc-concern">
          <span>CONCERN:</span>
          <div class="ascii-content">${npcConcern}</div>
        </div>
      `;
    }

    if (npcWant) {
      html += `
        <div class="ascii-section ascii-hex-npc-want">
          <span>WANT:</span>
          <div class="ascii-content">${npcWant}</div>
        </div>
      `;
    }

    if (npcApocalypseAttitude) {
      html += `
        <div class="ascii-section ascii-hex-npc-apocalypse">
          <span>APOCALYPSE ATTITUDE:</span>
          <div class="ascii-content">${npcApocalypseAttitude}</div>
        </div>
      `;
    }

    if (npcSecret) {
      html += `
        <div class="ascii-section ascii-hex-npc-secret">
          <span>SECRET:</span>
          <div class="ascii-content">${npcSecret}</div>
        </div>
      `;
    }

    // Fallback to old fields if new ones not available
    if (!npcTrait && npcMotivation) {
      html += `
        <div class="ascii-section ascii-hex-npc-motivation">
          <span>MOTIVATION:</span>
          <div class="ascii-content">${npcMotivation}</div>
        </div>
      `;
    }

    if (!npcConcern && npcFeature) {
      html += `
        <div class="ascii-section ascii-hex-npc-feature">
          <span>FEATURE:</span>
          <div class="ascii-content">${npcFeature}</div>
        </div>
      `;
    }

    if (!npcWant && npcDemeanor) {
      html += `
        <div class="ascii-section ascii-hex-npc-demeanor">
          <span>DEMEANOR:</span>
          <div class="ascii-content">${npcDemeanor}</div>
        </div>
      `;
    }

    // Additional NPC fields
    if (npcCarries) {
      html += `
        <div class="ascii-section ascii-hex-npc-carries">
          <span>CARRIES:</span>
          <div class="ascii-content">${npcCarries}</div>
        </div>
      `;
    }

    if (npcLocation) {
      html += `
        <div class="ascii-section ascii-hex-npc-location">
          <span>LOCATION:</span>
          <div class="ascii-content">${npcLocation}</div>
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
          <div class="ascii-content">${beastType}</div>
        </div>
      `;
    }

    if (beastFeature) {
      html += `
        <div class="ascii-section ascii-hex-beast-feature">
          <span>BEAST FEATURE:</span>
          <div class="ascii-content">${beastFeature}</div>
        </div>
      `;
    }

    if (beastBehavior) {
      html += `
        <div class="ascii-section ascii-hex-beast-behavior">
          <span>BEAST BEHAVIOR:</span>
          <div class="ascii-content">${beastBehavior}</div>
        </div>
      `;
    }

    if (threatLevel) {
      html += `
        <div class="ascii-section ascii-hex-threat-level">
          <span>THREAT LEVEL:</span>
          <div class="ascii-content">${threatLevel}</div>
        </div>
      `;
    }

    if (territory) {
      html += `
        <div class="ascii-section ascii-hex-territory">
          <span>TERRITORY:</span>
          <div class="ascii-content">${territory}</div>
        </div>
      `;
    }

    if (treasureFound) {
      html += `
        <div class="ascii-section ascii-hex-treasure-found">
          <span>TREASURE FOUND:</span>
          <div class="ascii-content">${treasureFound}</div>
        </div>
      `;
    }

    if (beastArt) {
      html += `
        <div class="ascii-section ascii-hex-beast-art">
          <span>BEAST ART:</span>
          <div class="ascii-content">${beastArt}</div>
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
          <div class="ascii-content">${dungeonType}</div>
        </div>
      `;
    }

    if (danger) {
      html += `
        <div class="ascii-section ascii-hex-danger">
          <span>DANGER:</span>
          <div class="ascii-content">${danger}</div>
        </div>
      `;
    }

    if (ancientKnowledge) {
      html += `
        <div class="ascii-section ascii-hex-ancient-knowledge">
          <span>ANCIENT KNOWLEDGE:</span>
          <div class="ascii-content">${formatLoot(ancientKnowledge)}</div>
        </div>
      `;
    }

    // Mörk Borg trap information
    if (trapSection) {
      html += `
        <div class="ascii-section ascii-hex-trap">
          <span>TRAP:</span>
          <div class="ascii-content">Description: ${trapSection.description || 'Unknown'}
Effect: ${trapSection.effect || 'Unknown'}
Builder: ${trapSection.builder || 'Unknown'}</div>
        </div>
      `;
    }
  }

  // Display Settlement-specific information
  if (hexData.is_settlement || hexType === 'settlement') {
    if (weather) {
      html += `
        <div class="ascii-section ascii-hex-weather">
          <span>WEATHER:</span>
          <div class="ascii-content">${weather}</div>
        </div>
      `;
    }

    if (cityEvent) {
      html += `
        <div class="ascii-section ascii-hex-city-event">
          <span>CITY EVENT:</span>
          <div class="ascii-content">${cityEvent}</div>
        </div>
      `;
    }

    // Tavern details
    if (tavernDetails) {
      html += `
        <div class="ascii-section ascii-hex-tavern-details">
          <span>TAVERN DETAILS:</span>
          <div class="ascii-content">${tavernDetails.select_menu ? `Select Menu: ${tavernDetails.select_menu}` : ''}
${tavernDetails.budget_menu ? `Budget Menu: ${tavernDetails.budget_menu}` : ''}
${tavernDetails.innkeeper ? `Innkeeper: ${tavernDetails.innkeeper}` : ''}
${tavernDetails.notable_patron ? `Notable Patron: ${tavernDetails.notable_patron}` : ''}</div>
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
          <div class="ascii-content">${encounterType}</div>
        </div>
      `;
    }

    if (origin) {
      html += `
        <div class="ascii-section ascii-hex-origin">
          <span>ORIGIN:</span>
          <div class="ascii-content">${origin}</div>
        </div>
      `;
    }

    if (behavior) {
      html += `
        <div class="ascii-section ascii-hex-behavior">
          <span>BEHAVIOR:</span>
          <div class="ascii-content">${behavior}</div>
        </div>
      `;
    }


  }

  if (encounter) {
        html += `
          <div class="ascii-section ascii-hex-encounter">
            <span>ENCOUNTER:</span>
            <div class="ascii-content">${encounter}</div>
          </div>
    `;
  }

  if (denizen) {
      html += `
          <div class="ascii-section ascii-hex-denizen">
            <span>DENIZEN:</span>
            <div class="ascii-content">${denizen}</div>
          </div>
    `;
  }

  if (notableFeature) {
      html += `
          <div class="ascii-section ascii-hex-feature">
            <span>NOTABLE FEATURE:</span>
            <div class="ascii-content">${notableFeature}</div>
          </div>
    `;
  }

  if (atmosphere) {
      html += `
          <div class="ascii-section ascii-hex-atmosphere">
            <span>ATMOSPHERE:</span>
            <div class="ascii-content">${atmosphere}</div>
          </div>
    `;
  }

  if (description) {
      html += `
          <div class="ascii-section ascii-hex-description">
            <span>DESCRIPTION:</span>
            <div class="ascii-content">${description}</div>
          </div>
    `;
  }

  // Display treasure/loot information (check all possible field names)
  if (formattedLoot) {
    html += `
          <div class="ascii-section ascii-hex-loot">
            <span>LOOT:</span>
            <div class="ascii-content">${formattedLoot}</div>
          </div>
    `;
  }

  if (formattedTreasure) {
    html += `
          <div class="ascii-section ascii-hex-treasure">
            <span>TREASURE:</span>
            <div class="ascii-content">${formattedTreasure}</div>
          </div>
    `;
  }

  if (formattedSunkenTreasure) {
    html += `
          <div class="ascii-section ascii-hex-sunken-treasure">
            <span>SUNKEN TREASURE:</span>
            <div class="ascii-content">${formattedSunkenTreasure}</div>
          </div>
    `;
  }

  if (magicalEffect) {
    html += `
          <div class="ascii-section ascii-hex-magical-effect">
            <span>MAGICAL EFFECT:</span>
            <div class="ascii-content">${magicalEffect}</div>
          </div>
    `;
  }

  // Check if any content was found
  const hasContent = encounter || denizen || notableFeature || atmosphere || description || 
                    formattedLoot || formattedTreasure || formattedSunkenTreasure || magicalEffect ||
                    npcName || npcDemeanor || npcDenizenType || npcMotivation || npcFeature ||
                    npcTrait || npcConcern || npcWant || npcApocalypseAttitude || npcSecret ||
                    beastType || beastFeature || beastBehavior || threatLevel || territory ||
                    dungeonType || danger || ancientKnowledge || trapSection ||
                    weather || cityEvent || tavernDetails ||
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
            <div class="ascii-content">${message}</div>
          </div>
        </div>
      </div>
    </div>
  `;
} 