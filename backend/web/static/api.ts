// web/static/api.ts

export async function getHex(hexCode: string): Promise<any> {
  try {
    const response = await fetch(`/api/hex/${hexCode}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching hex:', error);
    throw error;
  }
}

export async function updateHex(hexCode: string, content: string): Promise<any> {
  try {
    const response = await fetch(`/api/hex/${hexCode}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating hex:', error);
    throw error;
  }
}

export async function getCity(hexCode: string): Promise<any> {
  try {
    const response = await fetch(`/api/city/${hexCode}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching city:', error);
    throw error;
  }
}

export async function getSettlement(hexCode: string): Promise<any> {
  try {
    const response = await fetch(`/api/settlement/${hexCode}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching settlement:', error);
    throw error;
  }
}

export async function generateHex(hexCode: string) {
  const res = await fetch('/api/generate-hex', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hex_code: hexCode })
  });
  if (!res.ok) throw new Error(`Failed to generate hex ${hexCode}`);
  return res.json();
}

export async function setLanguage(language: string): Promise<any> {
  try {
    const response = await fetch('/api/set-language', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language })
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error setting language:', error);
    throw error;
  }
}

export async function resetContinent(): Promise<any> {
  try {
    const response = await fetch('/api/reset-continent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
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
    const response = await fetch('/api/lore-overview');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching lore overview:', error);
    throw error;
  }
}

// City Overlay API Functions
export async function getCityOverlays(): Promise<any> {
  try {
    const response = await fetch('/api/city-overlays');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching city overlays:', error);
    throw error;
  }
}

export async function getCityOverlay(overlayName: string): Promise<any> {
  try {
    const response = await fetch(`/api/city-overlay/${overlayName}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching city overlay:', error);
    throw error;
  }
}

export async function getCityOverlayAscii(overlayName: string): Promise<any> {
  try {
    const response = await fetch(`/api/city-overlay/${overlayName}/ascii`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching city overlay ASCII:', error);
    throw error;
  }
}

export async function getCityContext(cityName: string): Promise<any> {
  try {
    const response = await fetch(`/api/city-context/${cityName}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching city context:', error);
    throw error;
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
        const response = await fetch(`/api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching district details:', error);
        throw error;
    }
}

export async function getDistrictRandomTable(overlayName: string, districtName: string): Promise<any> {
    try {
        const response = await fetch(`/api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching district random table:', error);
        throw error;
    }
}

export async function getDistrictSpecificRandomTable(overlayName: string, districtName: string, tableType: string): Promise<any> {
    try {
        const response = await fetch(`/api/city-overlay/${overlayName}/district/${encodeURIComponent(districtName)}/random-table/${tableType}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching district specific random table:', error);
        throw error;
    }
}

export async function regenerateHex(overlayName: string, hexId: string): Promise<any> {
  try {
    const response = await fetch(`/api/regenerate-hex/${overlayName}/${hexId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error regenerating hex:', error);
    throw error;
  }
}

export async function regenerateOverlay(overlayName: string): Promise<any> {
  try {
    const response = await fetch(`/api/regenerate-overlay/${overlayName}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error regenerating overlay:', error);
    throw error;
  }
}
