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