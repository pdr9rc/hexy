// web/static/api.ts
import { apiGet, apiPost, handleApiError } from './utils/apiUtils.js';
import { SandboxStore } from './utils/sandboxStore.js';
import { DataStore } from './utils/dataStore.js';
import { getCurrentLanguage } from './translations.js';
export async function getHex(hexCode) {
    try {
        const lang = getCurrentLanguage();
        const storedMd = await DataStore.getHexMarkdown(lang, hexCode);
        const sandboxMd = await SandboxStore.getHexMarkdown(hexCode);
        if (storedMd) {
            // Offline/base object using locally stored markdown; avoid network
            const raw = sandboxMd || storedMd;
            return {
                hex_code: hexCode,
                exists: true,
                hex_type: 'wilderness',
                is_settlement: false,
                is_major_city: false,
                terrain: 'unknown',
                description: null,
                encounter: null,
                notable_feature: null,
                atmosphere: null,
                raw_markdown: raw
            };
        }
        // Fallback: fetch once from API, then store markdown if present
        const server = await apiGet(`api/hex/${hexCode}`);
        if (server && typeof server.raw_markdown === 'string') {
            await DataStore.setHexMarkdown(lang, hexCode, server.raw_markdown);
        }
        if (sandboxMd)
            return { ...server, raw_markdown: sandboxMd };
        return server;
    }
    catch (error) {
        throw handleApiError(error, 'fetching hex');
    }
}
export async function updateHex(hexCode, content) {
    try {
        // Client-side only: store in sandbox and synthesize response
        await SandboxStore.saveHexMarkdown(hexCode, content);
        return { success: true, sandbox: true };
    }
    catch (error) {
        throw handleApiError(error, 'updating hex');
    }
}
export async function getCity(hexCode) {
    try {
        const lang = getCurrentLanguage();
        const cached = await DataStore.getCity(lang, hexCode);
        if (cached)
            return cached;
        const data = await apiGet(`api/city/${hexCode}`);
        await DataStore.setCity(lang, hexCode, data);
        return data;
    }
    catch (error) {
        throw handleApiError(error, 'fetching city');
    }
}
export async function getSettlement(hexCode) {
    try {
        const lang = getCurrentLanguage();
        const cached = await DataStore.getSettlement(lang, hexCode);
        if (cached)
            return cached;
        const data = await apiGet(`api/settlement/${hexCode}`);
        await DataStore.setSettlement(lang, hexCode, data);
        return data;
    }
    catch (error) {
        throw handleApiError(error, 'fetching settlement');
    }
}
export async function generateHex(hexCode) {
    const res = await fetch('api/generate-hex', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hex_code: hexCode })
    });
    if (!res.ok)
        throw new Error(`Failed to generate hex ${hexCode}`);
    return res.json();
}
export async function setLanguage(language) {
    try {
        return await apiPost('api/set-language', { language });
    }
    catch (error) {
        throw handleApiError(error, 'setting language');
    }
}
export async function resetContinent(language) {
    try {
        const response = await fetch('api/reset-continent', {});
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }
    catch (error) {
        console.error('Error resetting continent:', error);
        throw error;
    }
}
export async function getLoreOverview() {
    try {
        const lang = getCurrentLanguage();
        const cached = await DataStore.getLore(lang);
        if (cached)
            return cached;
        const response = await fetch('api/lore-overview');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        await DataStore.setLore(lang, data);
        return data;
    }
    catch (error) {
        console.error('Error fetching lore overview:', error);
        throw error;
    }
}
export async function importZip(file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch('api/import', {
        method: 'POST',
        body: form
    });
    if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return res.json();
}
// City Overlay API Functions
export async function getCityOverlays() {
    try {
        return await apiGet('api/city-overlays');
    }
    catch (error) {
        console.error('Error fetching city overlays:', error);
        throw error;
    }
}
export async function getCityOverlay(overlayName) {
    try {
        return await apiGet(`api/city-overlay/${overlayName}`);
    }
    catch (error) {
        console.error('Error fetching city overlay:', error);
        throw error;
    }
}
export async function getCityOverlayAscii(overlayName) {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/ascii`);
    }
    catch (error) {
        console.error('Error fetching city overlay ASCII:', error);
        throw error;
    }
}
export async function getCityContext(cityName) {
    try {
        return await apiGet(`api/city-context/${cityName}`);
    }
    catch (error) {
        console.error('Error fetching city context:', error);
        throw error;
    }
}
export async function getCityOverlayHex(overlayName, hexId) {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/hex/${hexId}`);
    }
    catch (error) {
        console.error('Error fetching city overlay hex:', error);
        throw error;
    }
}
// Enhanced District API Functions
export async function getCityDistricts(overlayName) {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/districts`);
    }
    catch (error) {
        console.error('Error fetching city districts:', error);
        throw error;
    }
}
export async function getCityDistrictDetails(overlayName, districtName) {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}`);
    }
    catch (error) {
        console.error('Error fetching district details:', error);
        throw error;
    }
}
export async function getDistrictRandomTable(overlayName, districtName) {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table`);
    }
    catch (error) {
        console.error('Error fetching district random table:', error);
        throw error;
    }
}
export async function getDistrictSpecificRandomTable(overlayName, districtName, tableType) {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table/${tableType}`);
    }
    catch (error) {
        console.error('Error fetching district specific random table:', error);
        throw error;
    }
}
export async function regenerateHex(overlayName, hexId) {
    try {
        return await apiPost(`api/regenerate-hex/${overlayName}/${hexId}`);
    }
    catch (error) {
        console.error('Error regenerating hex:', error);
        throw error;
    }
}
export async function regenerateOverlay(overlayName) {
    try {
        return await apiPost(`api/regenerate-overlay/${overlayName}`);
    }
    catch (error) {
        console.error('Error regenerating overlay:', error);
        throw error;
    }
}
