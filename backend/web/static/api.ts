// web/static/api.ts
import { apiGet, apiPost, apiPut, handleApiError } from './utils/apiUtils.js';

export async function getHex(hexCode: string): Promise<any> {
  try {
    return await apiGet(`/api/hex/${hexCode}`);
  } catch (error) {
    throw handleApiError(error, 'fetching hex');
  }
}

export async function updateHex(hexCode: string, content: string): Promise<any> {
  try {
    return await apiPut(`/api/hex/${hexCode}`, { content });
  } catch (error) {
    throw handleApiError(error, 'updating hex');
  }
}

export async function getCity(hexCode: string): Promise<any> {
  try {
    return await apiGet(`/api/city/${hexCode}`);
  } catch (error) {
    throw handleApiError(error, 'fetching city');
  }
}

export async function getSettlement(hexCode: string): Promise<any> {
  try {
    return await apiGet(`/api/settlement/${hexCode}`);
  } catch (error) {
    throw handleApiError(error, 'fetching settlement');
  }
}

export async function generateHex(hexCode: string) {
  try {
    return await apiPost('/api/generate-hex', { hex_code: hexCode });
  } catch (error) {
    throw handleApiError(error, `generating hex ${hexCode}`);
  }
}

export async function setLanguage(language: string): Promise<any> {
  try {
    return await apiPost('/api/set-language', { language });
  } catch (error) {
    throw handleApiError(error, 'setting language');
  }
}

export async function resetContinent(language?: string): Promise<any> {
  try {
    return await apiPost('/api/reset-continent', language ? { language } : {});
  } catch (error) {
    throw handleApiError(error, 'resetting continent');
  }
}

export async function getLoreOverview(): Promise<any> {
  try {
    return await apiGet('/api/lore-overview');
  } catch (error) {
    throw handleApiError(error, 'fetching lore overview');
  }
}

// City Overlay API Functions
export async function getCityOverlays(): Promise<any> {
  try {
    return await apiGet('/api/city-overlays');
  } catch (error) {
    throw handleApiError(error, 'fetching city overlays');
  }
}

export async function getCityOverlay(overlayName: string): Promise<any> {
  try {
    return await apiGet(`/api/city-overlay/${overlayName}`);
  } catch (error) {
    throw handleApiError(error, 'fetching city overlay');
  }
}

export async function getCityOverlayAscii(overlayName: string): Promise<any> {
  try {
    return await apiGet(`/api/city-overlay/${overlayName}/ascii`);
  } catch (error) {
    throw handleApiError(error, 'fetching city overlay ASCII');
  }
}

export async function getCityContext(cityName: string): Promise<any> {
  try {
    return await apiGet(`/api/city-context/${cityName}`);
  } catch (error) {
    throw handleApiError(error, 'fetching city context');
  }
}

export async function getCityOverlayHex(overlayName: string, hexId: string): Promise<any> {
  try {
    const response = await fetch(`/api/city-overlay/${overlayName}/hex/${hexId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching city overlay hex:', error);
    throw error;
  }
}

// Enhanced District API Functions
export async function getCityDistricts(overlayName: string): Promise<any> {
    try {
        const response = await fetch(`/api/city-overlay/${overlayName}/districts`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching city districts:', error);
        throw error;
    }
}

export async function getCityDistrictDetails(overlayName: string, districtName: string): Promise<any> {
    try {
        return await apiGet(`/api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}`);
    } catch (error) {
        throw handleApiError(error, 'fetching district details');
    }
}

export async function getDistrictRandomTable(overlayName: string, districtName: string): Promise<any> {
    try {
        return await apiGet(`/api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table`);
    } catch (error) {
        throw handleApiError(error, 'fetching district random table');
    }
}

export async function getDistrictSpecificRandomTable(overlayName: string, districtName: string, tableType: string): Promise<any> {
    try {
        return await apiGet(`/api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table/${tableType}`);
    } catch (error) {
        throw handleApiError(error, 'fetching district specific random table');
    }
}

export async function regenerateHex(overlayName: string, hexId: string): Promise<any> {
  try {
    return await apiPost(`/api/regenerate-hex/${overlayName}/${hexId}`);
  } catch (error) {
    throw handleApiError(error, 'regenerating hex');
  }
}

export async function regenerateOverlay(overlayName: string): Promise<any> {
  try {
    return await apiPost(`/api/regenerate-overlay/${overlayName}`);
  } catch (error) {
    throw handleApiError(error, 'regenerating overlay');
  }
}
