// web/static/api.ts
import { apiGet, apiPost, apiPut, handleApiError } from './utils/apiUtils.js';
import { SandboxStore } from './utils/sandboxStore.js';

export async function getHex(hexCode: string): Promise<any> {
  try {
    const server = await apiGet<any>(`api/hex/${hexCode}`);
    // Merge with local sandbox markdown if present
    const localMd = await SandboxStore.getHexMarkdown(hexCode);
    if (localMd) {
      return { ...server, raw_markdown: localMd };
    }
    return server;
  } catch (error) {
    throw handleApiError(error, 'fetching hex');
  }
}

export async function updateHex(hexCode: string, content: string): Promise<any> {
  try {
    // Client-side only: store in sandbox and synthesize response
    await SandboxStore.saveHexMarkdown(hexCode, content);
    return { success: true, sandbox: true };
  } catch (error) {
    throw handleApiError(error, 'updating hex');
  }
}

export async function getCity(hexCode: string): Promise<any> {
  try {
    const cached = await SandboxStore.loadCity(hexCode);
    if (cached) return { success: true, city: cached };
    const server = await apiGet(`api/city/${hexCode}`);
    if (server && server.success && server.city) {
      await SandboxStore.saveCity(hexCode, server.city);
    }
    return server;
  } catch (error) {
    throw handleApiError(error, 'fetching city');
  }
}

export async function getSettlement(hexCode: string): Promise<any> {
  try {
    const cached = await SandboxStore.loadSettlement(hexCode);
    if (cached) return { success: true, settlement: cached };
    const server = await apiGet(`api/settlement/${hexCode}`);
    if (server && server.success && server.settlement) {
      await SandboxStore.saveSettlement(hexCode, server.settlement);
    }
    return server;
  } catch (error) {
    throw handleApiError(error, 'fetching settlement');
  }
}

export async function generateHex(hexCode: string) {
  const res = await fetch('api/generate-hex', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hex_code: hexCode })
  });
  if (!res.ok) throw new Error(`Failed to generate hex ${hexCode}`);
  return res.json();
}

export async function setLanguage(language: string): Promise<any> {
  try {
    return await apiPost('api/set-language', { language });
  } catch (error) {
    throw handleApiError(error, 'setting language');
  }
}

export async function resetContinent(language?: string): Promise<any> {
  try {
    const response = await fetch('api/reset-continent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(language ? { language } : {})
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error resetting continent:', error);
    throw error;
  }
}

export async function getLoreOverview(): Promise<any> {
  try {
    const response = await fetch('api/lore-overview');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching lore overview:', error);
    throw error;
  }
}

export async function importZip(file: File): Promise<any> {
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
export async function getCityOverlays(): Promise<any> {
  try {
    return await apiGet('api/city-overlays');
  } catch (error) {
    console.error('Error fetching city overlays:', error);
    throw error;
  }
}

export async function getCityOverlay(overlayName: string): Promise<any> {
  try {
    return await apiGet(`api/city-overlay/${overlayName}`);
  } catch (error) {
    console.error('Error fetching city overlay:', error);
    throw error;
  }
}

export async function getCityOverlayAscii(overlayName: string): Promise<any> {
  try {
    return await apiGet(`api/city-overlay/${overlayName}/ascii`);
  } catch (error) {
    console.error('Error fetching city overlay ASCII:', error);
    throw error;
  }
}

export async function getCityContext(cityName: string): Promise<any> {
  try {
    return await apiGet(`api/city-context/${cityName}`);
  } catch (error) {
    console.error('Error fetching city context:', error);
    throw error;
  }
}

export async function getCityOverlayHex(overlayName: string, hexId: string): Promise<any> {
  try {
    return await apiGet(`api/city-overlay/${overlayName}/hex/${hexId}`);
  } catch (error) {
    console.error('Error fetching city overlay hex:', error);
    throw error;
  }
}

// Enhanced District API Functions
export async function getCityDistricts(overlayName: string): Promise<any> {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/districts`);
    } catch (error) {
        console.error('Error fetching city districts:', error);
        throw error;
    }
}

export async function getCityDistrictDetails(overlayName: string, districtName: string): Promise<any> {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}`);
    } catch (error) {
        console.error('Error fetching district details:', error);
        throw error;
    }
}

export async function getDistrictRandomTable(overlayName: string, districtName: string): Promise<any> {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table`);
    } catch (error) {
        console.error('Error fetching district random table:', error);
        throw error;
    }
}

export async function getDistrictSpecificRandomTable(overlayName: string, districtName: string, tableType: string): Promise<any> {
    try {
        return await apiGet(`api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table/${tableType}`);
    } catch (error) {
        console.error('Error fetching district specific random table:', error);
        throw error;
    }
}

export async function regenerateHex(overlayName: string, hexId: string): Promise<any> {
  try {
    return await apiPost(`api/regenerate-hex/${overlayName}/${hexId}`);
  } catch (error) {
    console.error('Error regenerating hex:', error);
    throw error;
  }
}

export async function regenerateOverlay(overlayName: string): Promise<any> {
  try {
    return await apiPost(`api/regenerate-overlay/${overlayName}`);
  } catch (error) {
    console.error('Error regenerating overlay:', error);
    throw error;
  }
}
