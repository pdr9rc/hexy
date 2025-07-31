import type { 
  ApiResponse, 
  WorldGrid, 
  City, 
  HexContentResponse,
  HexCoordinate,
  CityOverlayData
} from '@/models/types';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // World Grid API
  async getWorldGrid(): Promise<ApiResponse<WorldGrid>> {
    return this.request<WorldGrid>('/world/grid');
  }

  async generateWorldGrid(width: number, height: number): Promise<ApiResponse<WorldGrid>> {
    return this.request<WorldGrid>('/world/generate', {
      method: 'POST',
      body: JSON.stringify({ width, height }),
    });
  }

  // Hex Content API
  async getHexContent(coordinate: HexCoordinate): Promise<ApiResponse<HexContentResponse>> {
    const { q, r, s } = coordinate;
    return this.request<HexContentResponse>(`/hex/${q}/${r}/${s}`);
  }

  async updateHexContent(coordinate: HexCoordinate, content: Record<string, any>): Promise<ApiResponse<any>> {
    const { q, r, s } = coordinate;
    return this.request<any>(`/hex/${q}/${r}/${s}`, {
      method: 'PUT',
      body: JSON.stringify(content),
    });
  }

  async getWorldHexContent(coordinate: HexCoordinate): Promise<ApiResponse<HexContentResponse>> {
    const { q, r, s } = coordinate;
    return this.request<HexContentResponse>(`/world/hex/${q}/${r}/${s}`);
  }

  async getCityHexContent(coordinate: HexCoordinate): Promise<ApiResponse<HexContentResponse>> {
    const { q, r, s } = coordinate;
    return this.request<HexContentResponse>(`/city/hex/${q}/${r}/${s}`);
  }

  // Cities API
  async getCities(): Promise<ApiResponse<City[]>> {
    return this.request<City[]>('/cities');
  }

  async getCity(cityId: string): Promise<ApiResponse<City>> {
    return this.request<City>(`/cities/${cityId}`);
  }

  async generateCity(coordinate: HexCoordinate): Promise<ApiResponse<City>> {
    return this.request<City>('/cities/generate', {
      method: 'POST',
      body: JSON.stringify({ coordinate }),
    });
  }

  // Hex API (Legacy endpoints)
  async getHex(hexCode: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/hex/${hexCode}`);
  }

  async getSettlement(hexCode: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/settlement/${hexCode}`);
  }

  async generateHex(hexCode: string): Promise<ApiResponse<any>> {
    return this.request<any>('/generate-hex', {
      method: 'POST',
      body: JSON.stringify({ hex_code: hexCode }),
    });
  }

  // Language and Settings
  async setLanguage(language: string): Promise<ApiResponse<any>> {
    return this.request<any>('/set-language', {
      method: 'POST',
      body: JSON.stringify({ language }),
    });
  }

  async resetContinent(): Promise<ApiResponse<any>> {
    return this.request<any>('/reset-continent', {
      method: 'POST',
    });
  }

  async getLoreOverview(): Promise<ApiResponse<any>> {
    return this.request<any>('/lore-overview');
  }

  // City Overlay API
  async getCityOverlays(): Promise<ApiResponse<any>> {
    return this.request<any>('/city-overlays');
  }

  async getCityOverlay(overlayName: string): Promise<ApiResponse<{ overlay: CityOverlayData }>> {
    return this.request<{ overlay: CityOverlayData }>(`/city-overlay/${overlayName}`);
  }

  async getCityOverlayAscii(overlayName: string): Promise<ApiResponse<{ ascii: string }>> {
    return this.request<{ ascii: string }>(`/city-overlay-ascii/${overlayName}`);
  }

  async getCityContext(cityName: string): Promise<ApiResponse<{ context: any }>> {
    return this.request<{ context: any }>(`/city-context/${cityName}`);
  }

  async getCityOverlayHex(overlayName: string, hexId: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/city-overlay-hex/${overlayName}/${hexId}`);
  }

  async getCityDistricts(overlayName: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/city-districts/${overlayName}`);
  }

  async getCityDistrictDetails(overlayName: string, districtName: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/city-district-details/${overlayName}/${districtName}`);
  }

  async getDistrictRandomTable(overlayName: string, districtName: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/district-random-table/${overlayName}/${districtName}`);
  }

  async getDistrictSpecificRandomTable(overlayName: string, districtName: string, tableType: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/district-specific-random-table/${overlayName}/${districtName}/${tableType}`);
  }

  // Enhanced city features
  async getCityDetails(hexCode: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/city/${hexCode}`);
  }

  async getSettlementDetails(hexCode: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/settlement/${hexCode}`);
  }

  async regenerateCityHex(overlayName: string, hexId: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/city-overlay/${overlayName}/hex/${hexId}/regenerate`, {
      method: 'POST'
    });
  }

  async getHexMarkdown(hexCode: string): Promise<ApiResponse<{ hex_code: string; markdown: string; has_content: boolean }>> {
    return this.request<{ hex_code: string; markdown: string; has_content: boolean }>(`/hex/${hexCode}/markdown`);
  }

  async updateHexMarkdown(hexCode: string, markdown: string): Promise<ApiResponse<{ hex_code: string; message: string }>> {
    return this.request<{ hex_code: string; message: string }>(`/hex/${hexCode}/markdown`, {
      method: 'PUT',
      body: JSON.stringify({ markdown })
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient; 