// Enhanced Data Tables for The Dying Lands

/**
 * Convert hex data to structured HTML table
 */
function generateHexDataTable(data, hexCode) {
    if (!data || !data.exists) {
        return generateEmptyHexTable(hexCode);
    }

    let html = `
        <div class="section-header">HEX ${hexCode} - ${data.terrain_type.toUpperCase()}</div>
        <table class="data-table">
            <tr>
                <td class="label">Location</td>
                <td class="value">Hex ${hexCode}</td>
            </tr>
            <tr>
                <td class="label">Terrain</td>
                <td class="value highlight">${data.terrain_type}</td>
            </tr>
            <tr>
                <td class="label">Weather</td>
                <td class="value">${data.weather || 'Unknown'}</td>
            </tr>
            <tr>
                <td class="label">Difficulty</td>
                <td class="value ${getDifficultyClass(data.difficulty)}">${data.difficulty || 'Normal'}</td>
            </tr>
        </table>`;

    // Add encounters if they exist
    if (data.encounters && data.encounters.length > 0) {
        html += `
            <div class="section-header">ENCOUNTERS</div>
            <table class="data-table">`;
        
        data.encounters.forEach((encounter, index) => {
            html += `
                <tr>
                    <td class="label">Encounter ${index + 1}</td>
                    <td class="value">${encounter}</td>
                </tr>`;
        });
        html += `</table>`;
    }

    // Add NPCs if they exist
    if (data.npcs && data.npcs.length > 0) {
        html += `
            <div class="section-header">NPCS</div>
            <table class="data-table">`;
        
        data.npcs.forEach((npc, index) => {
            html += `
                <tr>
                    <td class="label">NPC ${index + 1}</td>
                    <td class="value">${npc}</td>
                </tr>`;
        });
        html += `</table>`;
    }

    // Add settlements if they exist
    if (data.settlements && data.settlements.length > 0) {
        html += `
            <div class="section-header">SETTLEMENTS</div>
            <table class="data-table">`;
        
        data.settlements.forEach((settlement, index) => {
            html += `
                <tr>
                    <td class="label">Settlement ${index + 1}</td>
                    <td class="value highlight">${settlement}</td>
                </tr>`;
        });
        html += `</table>`;
    }

    // Add loot if it exists
    if (data.loot && data.loot.length > 0) {
        html += `
            <div class="section-header">LOOT</div>
            <table class="data-table">`;
        
        data.loot.forEach((item, index) => {
            html += `
                <tr>
                    <td class="label">Item ${index + 1}</td>
                    <td class="value warning">${item}</td>
                </tr>`;
        });
        html += `</table>`;
    }

    return html;
}

/**
 * Generate city data table
 */
function generateCityDataTable(city, hexCode, regionalData) {
    let html = `
        <div class="section-header">${city.name.toUpperCase()}</div>
        <table class="data-table">
            <tr>
                <td class="label">Location</td>
                <td class="value">Hex ${hexCode}</td>
            </tr>
            <tr>
                <td class="label">Region</td>
                <td class="value">${city.region}</td>
            </tr>
            <tr>
                <td class="label">Population</td>
                <td class="value highlight">${city.population}</td>
            </tr>
            <tr>
                <td class="label">Atmosphere</td>
                <td class="value">${city.atmosphere}</td>
            </tr>
            <tr>
                <td class="label">Description</td>
                <td class="value">${city.description}</td>
            </tr>
        </table>`;

    // Notable features
    if (city.notable_features && city.notable_features.length > 0) {
        html += `
            <div class="section-header">NOTABLE FEATURES</div>
            <div class="table-container">
                <table class="data-table">`;
        
        city.notable_features.forEach((feature, index) => {
            html += `
                <tr>
                    <td class="label">Feature ${index + 1}</td>
                    <td class="value">${feature}</td>
                </tr>`;
        });
        html += `</table></div>`;
    }

    // Key NPCs
    if (city.key_npcs && city.key_npcs.length > 0) {
        html += `
            <div class="section-header">KEY NPCS</div>
            <div class="table-container">
                <table class="data-table">`;
        
        city.key_npcs.forEach((npc, index) => {
            html += `
                <tr>
                    <td class="label">NPC ${index + 1}</td>
                    <td class="value highlight">${npc}</td>
                </tr>`;
        });
        html += `</table></div>`;
    }

    // Regional NPCs
    if (regionalData && regionalData.regional_npcs && regionalData.regional_npcs.length > 0) {
        html += `
            <div class="section-header">REGIONAL NPCS</div>
            <div class="table-container">
                <table class="data-table">`;
        
        regionalData.regional_npcs.forEach((npc, index) => {
            html += `
                <tr>
                    <td class="label">Regional NPC ${index + 1}</td>
                    <td class="value">${npc}</td>
                </tr>`;
        });
        html += `</table></div>`;
    }

    // Factions
    if (regionalData && regionalData.factions && regionalData.factions.length > 0) {
        html += `
            <div class="section-header">ACTIVE FACTIONS</div>
            <div class="table-container">
                <table class="data-table">`;
        
        regionalData.factions.forEach((faction, index) => {
            html += `
                <tr>
                    <td class="label">${faction.name}</td>
                    <td class="value">
                        <span class="warning">${faction.influence}</span><br>
                        ${faction.description}
                    </td>
                </tr>`;
        });
        html += `</table></div>`;
    }

    return html;
}

/**
 * Generate empty hex table
 */
function generateEmptyHexTable(hexCode) {
    return `
        <div class="section-header">HEX ${hexCode} - EMPTY</div>
        <table class="data-table">
            <tr>
                <td class="label">Status</td>
                <td class="value warning">No Content Generated</td>
            </tr>
            <tr>
                <td class="label">Description</td>
                <td class="value">This hex has no content yet. Click "GENERATE CONTENT" to create encounters and details for this location.</td>
            </tr>
        </table>
        <div class="text-center mt-4">
            <button class="btn btn-mork-borg" onclick="generateHexContent('${hexCode}')">GENERATE CONTENT</button>
        </div>`;
}

/**
 * Get CSS class for difficulty level
 */
function getDifficultyClass(difficulty) {
    if (!difficulty) return '';
    
    const lower = difficulty.toLowerCase();
    if (lower.includes('easy') || lower.includes('low')) return 'highlight';
    if (lower.includes('hard') || lower.includes('high') || lower.includes('extreme')) return 'danger';
    if (lower.includes('medium') || lower.includes('moderate')) return 'warning';
    return '';
}

/**
 * Create sortable table functionality
 */
function makeSortable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => sortTable(table, index));
    });
}

/**
 * Sort table by column
 */
function sortTable(table, column) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isAscending = table.dataset.sortOrder !== 'asc';
    
    rows.sort((a, b) => {
        const aValue = a.cells[column].textContent.trim();
        const bValue = b.cells[column].textContent.trim();
        
        if (isAscending) {
            return aValue.localeCompare(bValue);
        } else {
            return bValue.localeCompare(aValue);
        }
    });
    
    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));
    
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
}

/**
 * Filter table by search term
 */
function filterTable(tableId, searchTerm) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Export table data as CSV
 */
function exportTableAsCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = '';
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        const rowData = Array.from(cells).map(cell => `"${cell.textContent.trim()}"`);
        csv += rowData.join(',') + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'table_data.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}