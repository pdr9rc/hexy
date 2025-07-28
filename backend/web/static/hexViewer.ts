// web/static/hexViewer.ts
import { DyingLandsApp } from './main.js';
import * as api from './api.js';
import * as ui from './uiUtils.js';

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
            <span>CITY DESCRIPTION:</span>
            <pre>${context.description}</pre>
          </div>
  `;
  
  // City Events
  if (context.city_events && context.city_events.length > 0) {
    html += `
      <div class="ascii-section ascii-city-events">
        <span>CITY EVENTS:</span>
        <pre>${context.city_events.slice(0, 3).join('\n')}</pre>
      </div>
    `;
  }
  
  // Weather Conditions
  if (context.weather_conditions && context.weather_conditions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-weather">
        <span>WEATHER:</span>
        <pre>${context.weather_conditions.slice(0, 2).join('\n')}</pre>
      </div>
    `;
  }
  
  // Regional NPCs
  if (context.regional_npcs && context.regional_npcs.length > 0) {
    html += `
      <div class="ascii-section ascii-city-npcs">
        <span>REGIONAL NPCS:</span>
        <pre>${context.regional_npcs.slice(0, 3).join('\n')}</pre>
      </div>
    `;
  }
  
  // Major Factions
  if (context.major_factions && context.major_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>MAJOR FACTIONS:</span>
        <pre>
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
        </pre>
      </div>
    `;
  }
  
  // Local Factions
  if (context.local_factions && context.local_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>LOCAL FACTIONS:</span>
        <pre>
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
        </pre>
      </div>
    `;
  }
  
  // Criminal Factions
  if (context.criminal_factions && context.criminal_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>CRIMINAL FACTIONS:</span>
        <pre>
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
        </pre>
      </div>
    `;
  }
  
  // Faction Relationships
  if (context.faction_relationships && context.faction_relationships.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>FACTION RELATIONSHIPS:</span>
        <pre>
    `;
    
    for (const relationship of context.faction_relationships.slice(0, 3)) {
      html += `• ${relationship.faction1} ↔ ${relationship.faction2}\n`;
      html += `  ${relationship.relationship}: ${relationship.description}\n`;
      html += '\n';
    }
    
    html += `
        </pre>
      </div>
    `;
  }
  
  // Legacy Factions (fallback)
  if (context.legacy_factions && context.legacy_factions.length > 0) {
    html += `
      <div class="ascii-section ascii-city-factions">
        <span>OTHER FACTIONS:</span>
        <pre>
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
        </pre>
      </div>
    `;
  }
  
  // Major Landmarks
  if (context.major_landmarks && context.major_landmarks.length > 0) {
    html += `
      <div class="ascii-section ascii-city-landmarks">
        <span>MAJOR LANDMARKS:</span>
        <pre>${context.major_landmarks.slice(0, 3).join('\n')}</pre>
      </div>
    `;
  }
  
  // District Information
  if (context.districts && Object.keys(context.districts).length > 0) {
    html += `
      <div class="ascii-section ascii-city-districts">
        <span>DISTRICTS:</span>
        <pre>
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
        </pre>
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
    // Load city context data for left panel
    const contextData = await api.getCityContext('galgenbeck');
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
        const response = await fetch(`/api/city-overlay/galgenbeck/hex/${hexId}`);
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
                    <span>TYPE: ${content.type || 'unknown'}</span>
                  </div>
                  <div class="ascii-section ascii-hex-district">
                    <span>DISTRICT: ${district}</span>
                  </div>
                  <div class="ascii-section ascii-hex-position">
                    <span>POSITION: ${content.position_type || 'unknown'}</span>
                  </div>
                  
                  <!-- Description Section -->
                  <div class="ascii-section ascii-hex-description">
                    <span>DESCRIPTION:</span>
                    <pre>${content.description || description || 'No description available.'}</pre>
                  </div>
                  
                  <!-- Atmosphere & Encounter Section -->
                  <div class="ascii-section ascii-hex-atmosphere">
                    <span>ATMOSPHERE:</span>
                    <pre>${content.atmosphere || 'No atmosphere available.'}</pre>
                  </div>
                  <div class="ascii-section ascii-hex-encounter">
                    <span>ENCOUNTER:</span>
                    <pre>${content.encounter || 'No encounter available.'}</pre>
                  </div>
          `;
          
          // Enriched Content Section
          if (content.weather || content.city_event || content.notable_features) {
            html += `
              <div class="ascii-section ascii-hex-enriched">
                <span>ENRICHED CONTENT:</span>
                <pre>
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
                </pre>
              </div>
            `;
          }
          
          // NPC Information Section (for relevant types)
          if (content.npc_trait || content.npc_concern || content.npc_want || content.npc_secret || content.npcs) {
            html += `
              <div class="ascii-section ascii-hex-npcs">
                <span>NPC INFORMATION:</span>
                <pre>
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
          
          // Cross-References Section
          if (content.related_hexes && content.related_hexes.length > 0) {
            html += `
              <div class="ascii-section ascii-hex-related">
                <span>RELATED HEXES:</span>
                <pre>
            `;
            
            content.related_hexes.forEach((related: any) => {
              html += `<span class="related-hex-link" onclick="navigateToRelatedHex('${related.hex_id}')">${related.hex_id}: ${related.name} (${related.type}) - ${related.relationship}</span>\n`;
            });
            
            html += `
                </pre>
              </div>
            `;
          }
          
          // Random Tables Section
          if (content.random_table && content.random_table.length > 0) {
            html += `
              <div class="ascii-section ascii-hex-random">
                <span>RANDOM ENCOUNTERS:</span>
                <pre>
            `;
            
            content.random_table.forEach((entry: string) => {
              html += `${entry}\n`;
            });
            
            html += `
                </pre>
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
    const features = (settlement.notable_features && settlement.notable_features.length > 0) ? settlement.notable_features.join("\n") : '';
    const tavern = settlement.local_tavern || '';
    const power = settlement.local_power || '';
    // Mörk Borg settlement fields
    const weather = settlement.weather || '';
    const cityEvent = settlement.city_event || '';
    const tavernDetails = settlement.tavern_details || null;
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
            ${weather ? `
            <div class="ascii-section ascii-hex-weather">
              <span>WEATHER:</span>
              <pre>${weather}</pre>
          </div>
            ` : ''}
            ${cityEvent ? `
            <div class="ascii-section ascii-hex-city-event">
              <span>CITY EVENT:</span>
              <pre>${cityEvent}</pre>
            </div>
            ` : ''}
            ${tavernDetails ? `
            <div class="ascii-section ascii-hex-tavern-details">
              <span>TAVERN DETAILS:</span>
              <pre>${tavernDetails.select_menu ? `Select Menu: ${tavernDetails.select_menu}` : ''}
${tavernDetails.budget_menu ? `Budget Menu: ${tavernDetails.budget_menu}` : ''}
${tavernDetails.innkeeper ? `Innkeeper: ${tavernDetails.innkeeper}` : ''}
${tavernDetails.notable_patron ? `Notable Patron: ${tavernDetails.notable_patron}` : ''}</pre>
            </div>
            ` : ''}
            ${settlementArt ? `
            <div class="ascii-section ascii-settlement-layout">
              <span>SETTLEMENT LAYOUT:</span>
              <pre>${settlementArt}</pre>
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

    // Mörk Borg NPC fields
    if (npcTrait) {
      html += `
        <div class="ascii-section ascii-hex-npc-trait">
          <span>TRAIT:</span>
          <pre>${npcTrait}</pre>
        </div>
      `;
    }

    if (npcConcern) {
      html += `
        <div class="ascii-section ascii-hex-npc-concern">
          <span>CONCERN:</span>
          <pre>${npcConcern}</pre>
        </div>
      `;
    }

    if (npcWant) {
      html += `
        <div class="ascii-section ascii-hex-npc-want">
          <span>WANT:</span>
          <pre>${npcWant}</pre>
        </div>
      `;
    }

    if (npcApocalypseAttitude) {
      html += `
        <div class="ascii-section ascii-hex-npc-apocalypse">
          <span>APOCALYPSE ATTITUDE:</span>
          <pre>${npcApocalypseAttitude}</pre>
        </div>
      `;
    }

    if (npcSecret) {
      html += `
        <div class="ascii-section ascii-hex-npc-secret">
          <span>SECRET:</span>
          <pre>${npcSecret}</pre>
        </div>
      `;
    }

    // Fallback to old fields if new ones not available
    if (!npcTrait && npcMotivation) {
      html += `
        <div class="ascii-section ascii-hex-npc-motivation">
          <span>MOTIVATION:</span>
          <pre>${npcMotivation}</pre>
        </div>
      `;
    }

    if (!npcConcern && npcFeature) {
      html += `
        <div class="ascii-section ascii-hex-npc-feature">
          <span>FEATURE:</span>
          <pre>${npcFeature}</pre>
        </div>
      `;
    }

    if (!npcWant && npcDemeanor) {
      html += `
        <div class="ascii-section ascii-hex-npc-demeanor">
          <span>DEMEANOR:</span>
          <pre>${npcDemeanor}</pre>
        </div>
      `;
    }

    // Additional NPC fields
    if (npcCarries) {
      html += `
        <div class="ascii-section ascii-hex-npc-carries">
          <span>CARRIES:</span>
          <pre>${npcCarries}</pre>
        </div>
      `;
    }

    if (npcLocation) {
      html += `
        <div class="ascii-section ascii-hex-npc-location">
          <span>LOCATION:</span>
          <pre>${npcLocation}</pre>
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

    if (treasureFound) {
      html += `
        <div class="ascii-section ascii-hex-treasure-found">
          <span>TREASURE FOUND:</span>
          <pre>${treasureFound}</pre>
        </div>
      `;
    }

    if (beastArt) {
      html += `
        <div class="ascii-section ascii-hex-beast-art">
          <span>BEAST ART:</span>
          <pre>${beastArt}</pre>
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

    // Mörk Borg trap information
    if (trapSection) {
      html += `
        <div class="ascii-section ascii-hex-trap">
          <span>TRAP:</span>
          <pre>Description: ${trapSection.description || 'Unknown'}
Effect: ${trapSection.effect || 'Unknown'}
Builder: ${trapSection.builder || 'Unknown'}</pre>
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
          <pre>${weather}</pre>
        </div>
      `;
    }

    if (cityEvent) {
      html += `
        <div class="ascii-section ascii-hex-city-event">
          <span>CITY EVENT:</span>
          <pre>${cityEvent}</pre>
        </div>
      `;
    }

    // Tavern details
    if (tavernDetails) {
      html += `
        <div class="ascii-section ascii-hex-tavern-details">
          <span>TAVERN DETAILS:</span>
          <pre>${tavernDetails.select_menu ? `Select Menu: ${tavernDetails.select_menu}` : ''}
${tavernDetails.budget_menu ? `Budget Menu: ${tavernDetails.budget_menu}` : ''}
${tavernDetails.innkeeper ? `Innkeeper: ${tavernDetails.innkeeper}` : ''}
${tavernDetails.notable_patron ? `Notable Patron: ${tavernDetails.notable_patron}` : ''}</pre>
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