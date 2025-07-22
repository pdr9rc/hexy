import * as api from './api.js';
import * as ui from './uiUtils.js';
export async function renderHexDetails(app, hexCode) {
    ui.showLoading('Loading hex details...');
    try {
        const hexData = await api.getHex(hexCode);
        if (!hexData || !hexData.exists) {
            showEmptyState(app);
            return;
        }
        // Check if it's a major city
        if (hexData.is_major_city) {
            await showCityDetailsInMap(app, hexCode);
            return;
        }
        // Check if it's a settlement
        if (hexData.is_settlement) {
            await showSettlementDetailsInMap(app, hexCode);
            return;
        }
        // Regular hex content - show in right panel
        displayHexContent(hexData);
    }
    catch (error) {
        console.error('Error loading hex details:', error);
        showErrorState('Failed to load hex details');
    }
    finally {
        ui.hideLoading();
    }
}
async function showCityDetailsInMap(app, hexCode) {
    try {
        const cityData = await api.getCity(hexCode);
        if (!cityData || !cityData.success) {
            showErrorState('City not found');
            return;
        }
        const city = cityData.city;
        const mapContainer = document.querySelector('.map-container');
        if (!mapContainer)
            return;
        // Save original content for restoration
        if (!mapContainer.hasAttribute('data-original-content')) {
            mapContainer.setAttribute('data-original-content', mapContainer.innerHTML);
        }
        let html = `
      <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
        <div class="mb-4">
          <button class="btn btn-mork-borg me-2" onclick="window.app.showCityOverlayInMap('${hexCode}')">MAP GRID</button>
          <button class="btn btn-mork-borg me-2" onclick="window.app.onHexClick('${hexCode}')">RETURN TO HEX</button>
          <button class="btn btn-mork-borg btn-warning" onclick="window.app.restoreMap()">RETURN TO MAP</button>
        </div>
        <div style="background: var(--mork-black); border: 2px solid var(--mork-cyan); padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);">
          <pre style="font-family: 'Courier New', monospace; font-size: 11px; line-height: 1.2; color: var(--mork-cyan); margin: 0; white-space: pre-wrap; word-wrap: break-word;">
╔══════════════════════════════��═══════════════════════════════╗

║                    ${city.name.toUpperCase().padEnd(50)}║
╠══════════════════════════════════════════════════════════════╣
║ LOCATION: HEX ${hexCode} - ${city.region.toUpperCase().padEnd(40)}║
║ POPULATION: ${city.population.padEnd(50)}║
║ ATMOSPHERE: ${city.atmosphere.substring(0, 50).padEnd(50)}║
╠══════════════════════════════════════════════════════════════╣
║ DESCRIPTION:                                                ║`;
        // Split description into lines
        const cityDescription = city.description?.raw || city.description || 'No description available';
        const descLines = cityDescription.match(/.{1,58}/g) || [cityDescription];
        descLines.forEach((line) => {
            html += `
║ ${line.padEnd(58)}║`;
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║ NOTABLE FEATURES:                                           ║`;
        city.notable_features.forEach((feature) => {
            const featureText = feature?.raw || feature || 'Unknown feature';
            const featureLines = featureText.match(/.{1,56}/g) || [featureText];
            featureLines.forEach((line) => {
                html += `
║ • ${line.padEnd(56)}║`;
            });
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║ KEY NPCS:                                                   ║`;
        city.key_npcs.forEach((npc) => {
            const npcText = npc?.raw || npc || 'Unknown NPC';
            const npcLines = npcText.match(/.{1,56}/g) || [npcText];
            npcLines.forEach((line) => {
                html += `
║ • ${line.padEnd(56)}║`;
            });
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║ REGIONAL NPCS:                                              ║`;
        cityData.regional_npcs.forEach((npc) => {
            const npcLines = npc.match(/.{1,56}/g) || [npc];
            npcLines.forEach((line) => {
                html += `
║ • ${line.padEnd(56)}║`;
            });
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║ ACTIVE FACTIONS:                                            ║`;
        cityData.factions.forEach((faction) => {
            const factionText = `${faction.name} (${faction.influence}) - ${faction.description}`;
            const factionLines = factionText.match(/.{1,56}/g) || [factionText];
            factionLines.forEach((line) => {
                html += `
║ • ${line.padEnd(56)}║`;
            });
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
          </pre>
        </div>
      </div>
    `;
        mapContainer.innerHTML = html;
    }
    catch (error) {
        console.error('Error loading city details:', error);
        showErrorState('Failed to load city details');
    }
}
async function showSettlementDetailsInMap(app, hexCode) {
    try {
        const settlementData = await api.getSettlement(hexCode);
        if (!settlementData || !settlementData.success) {
            showErrorState('Settlement not found');
            return;
        }
        const settlement = settlementData.settlement;
        const mapContainer = document.querySelector('.map-container');
        if (!mapContainer)
            return;
        // Save original content for restoration
        if (!mapContainer.hasAttribute('data-original-content')) {
            mapContainer.setAttribute('data-original-content', mapContainer.innerHTML);
        }
        let html = `
      <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
        <div class="mb-4">
          <button class="btn btn-mork-borg btn-warning me-2" onclick="window.app.restoreMap()">RETURN TO MAP</button>
        </div>
        <div style="background: var(--mork-black); border: 2px solid var(--mork-cyan); padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);">
          <pre style="font-family: 'Courier New', monospace; font-size: 11px; line-height: 1.2; color: var(--mork-cyan); margin: 0; white-space: pre-wrap; word-wrap: break-word;">
╔══════════════════════════════════════════════════════════════╗
║                    ${settlement.name.toUpperCase().padEnd(50)}║
╠══════════════════════════════════════════════════════════════╣
║ LOCATION: HEX ${hexCode} - ${settlement.terrain.toUpperCase().padEnd(40)}║
║ POPULATION: ${settlement.population.padEnd(50)}║
║ ATMOSPHERE: ${settlement.atmosphere.substring(0, 50).padEnd(50)}║
╠══════════════════════════════════════════════════════════════╣
║ DESCRIPTION:                                                ║`;
        // Split description into lines
        const descLines = settlement.description.match(/.{1,58}/g) || [settlement.description];
        descLines.forEach((line) => {
            html += `
║ ${line.padEnd(58)}║`;
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║ NOTABLE FEATURE:                                            ║`;
        // Fix: always treat as string
        let notableFeature = settlement.notable_feature;
        if (typeof notableFeature === 'object' && notableFeature !== null) {
            notableFeature = notableFeature.raw || notableFeature.html || '';
        }
        notableFeature = String(notableFeature);
        const featureLines = notableFeature.match(/.{1,56}/g) || [notableFeature];
        featureLines.forEach((line) => {
            html += `
║ • ${line.padEnd(56)}║`;
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║ LOCAL TAVERN:                                               ║`;
        let localTavern = settlement.local_tavern;
        if (typeof localTavern === 'object' && localTavern !== null) {
            localTavern = localTavern.raw || localTavern.html || '';
        }
        localTavern = String(localTavern);
        const tavernLines = localTavern.match(/.{1,56}/g) || [localTavern];
        tavernLines.forEach((line) => {
            html += `
║ • ${line.padEnd(56)}║`;
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║ LOCAL POWER:                                                ║`;
        let localPower = settlement.local_power;
        if (typeof localPower === 'object' && localPower !== null) {
            localPower = localPower.raw || localPower.html || '';
        }
        localPower = String(localPower);
        const powerLines = localPower.match(/.{1,56}/g) || [localPower];
        powerLines.forEach((line) => {
            html += `
║ • ${line.padEnd(56)}║`;
        });
        html += `
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
          </pre>
        </div>
      </div>
    `;
        mapContainer.innerHTML = html;
    }
    catch (error) {
        console.error('Error loading settlement details:', error);
        showErrorState('Failed to load settlement details');
    }
}
function displayHexContent(hexData) {
    const container = document.getElementById('modalContainer');
    if (!container)
        return;
    console.log('🔍 Hex data for display:', hexData);
    let html = `
    <div style="text-align: center; padding: 20px; height: 100%; overflow-y: auto;">
      <div style="background: var(--mork-black); border: 2px solid var(--mork-cyan); padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);">
        <pre style="font-family: 'Courier New', monospace; font-size: 11px; line-height: 1.2; color: var(--mork-cyan); margin: 0; white-space: pre-wrap; word-wrap: break-word;">
╔══════════════════════════════════════════════════════════════╗
║                    ${(hexData.title || `HEX ${hexData.hex_code}`).toUpperCase().padEnd(50)}║
╠══════════════════════════════════════════════════════════════╣
║ TERRAIN: ${(hexData.terrain_name || hexData.terrain || 'Unknown').toUpperCase().padEnd(50)}║
║ TYPE: ${(hexData.hex_type || 'Unknown').toUpperCase().padEnd(50)}║
╠══════════════════════════════════════════════════════════════╣`;
    // Display encounter content
    if (hexData.encounter) {
        const encounterContent = hexData.encounter.html || hexData.encounter.raw || hexData.encounter;
        if (encounterContent) {
            html += `
║ ENCOUNTER:                                                 ║`;
            // Clean up markdown and split into lines
            const cleanEncounter = encounterContent.replace(/\*\*/g, '').replace(/\*/g, '※');
            const encounterLines = cleanEncounter.match(/.{1,58}/g) || [cleanEncounter];
            encounterLines.forEach((line) => {
                html += `
║ ${line.padEnd(58)}║`;
            });
        }
    }
    // Display denizen content
    if (hexData.denizen) {
        const denizenContent = hexData.denizen.html || hexData.denizen.raw || hexData.denizen;
        if (denizenContent) {
            html += `
╠══════════════════════════════════════════════════════════════╣
║ DENIZEN:                                                   ║`;
            const denizenLines = denizenContent.match(/.{1,58}/g) || [denizenContent];
            denizenLines.forEach((line) => {
                html += `
║ ${line.padEnd(58)}║`;
            });
        }
    }
    // Display notable feature
    if (hexData.notable_feature) {
        const featureContent = hexData.notable_feature.html || hexData.notable_feature.raw || hexData.notable_feature;
        if (featureContent) {
            html += `
╠══════════════════════════════════════════════════════════════╣
║ NOTABLE FEATURE:                                           ║`;
            const featureLines = featureContent.match(/.{1,58}/g) || [featureContent];
            featureLines.forEach((line) => {
                html += `
║ ${line.padEnd(58)}║`;
            });
        }
    }
    // Display atmosphere
    if (hexData.atmosphere) {
        const atmosphereContent = hexData.atmosphere.html || hexData.atmosphere.raw || hexData.atmosphere;
        if (atmosphereContent) {
            html += `
╠══════════════════════════════════════════════════════════════╣
║ ATMOSPHERE:                                                ║`;
            const atmosphereLines = atmosphereContent.match(/.{1,58}/g) || [atmosphereContent];
            atmosphereLines.forEach((line) => {
                html += `
║ ${line.padEnd(58)}║`;
            });
        }
    }
    // Display loot if available
    if (hexData.loot && hexData.loot.length > 0) {
        html += `
╠══════════════════════════════════════════════════════════════╣
║ LOOT:                                                      ║`;
        hexData.loot.forEach((item) => {
            const itemText = item.name || JSON.stringify(item);
            const itemLines = itemText.match(/.{1,56}/g) || [itemText];
            itemLines.forEach((line) => {
                html += `
║ • ${line.padEnd(56)}║`;
            });
        });
    }
    // If no content was found, show a message
    if (!hexData.encounter && !hexData.denizen && !hexData.notable_feature && !hexData.atmosphere && (!hexData.loot || hexData.loot.length === 0)) {
        html += `
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  No additional content available for this hex.              ║
║                                                              ║`;
    }
    html += `
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        </pre>
      </div>
    </div>
  `;
    container.innerHTML = html;
}
function showEmptyState(app) {
    const container = document.getElementById('modalContainer');
    if (!container)
        return;
    container.innerHTML = `
    <div class="empty-state">
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
    </div>
  `;
}
function showErrorState(message) {
    const container = document.getElementById('modalContainer');
    if (!container)
        return;
    container.innerHTML = `
    <div class="error-state">
      <h2>Error</h2>
      <p>${message}</p>
    </div>
  `;
}
