import type { 
  CityOverlayData, 
  CityContext,
  CityDetails,
  SettlementDetails,
  CityHexContent,
  CityInteraction,
  CityError,
  CityState
} from '@/models/types';
import { apiClient } from '@/api/client';

export class CityOverlayService {
  private currentOverlay: CityOverlayData | null = null;
  private currentContext: CityContext | null = null;
  private overlayListeners: Set<(overlay: CityOverlayData | null) => void> = new Set();
  private contextListeners: Set<(context: CityContext | null) => void> = new Set();
  
  // Enhanced state management
  private state: CityState = {
    overlays: new Map(),
    currentOverlay: null,
    interactions: [],
    errors: [],
    isLoading: false,
    lastAction: null
  };
  
  private stateListeners: Set<(state: CityState) => void> = new Set();

  // Subscribe to overlay changes
  subscribeToOverlay(listener: (overlay: CityOverlayData | null) => void): () => void {
    this.overlayListeners.add(listener);
    return () => this.overlayListeners.delete(listener);
  }

  // Subscribe to context changes
  subscribeToContext(listener: (context: CityContext | null) => void): () => void {
    this.contextListeners.add(listener);
    return () => this.contextListeners.delete(listener);
  }

  private notifyOverlayListeners(): void {
    this.overlayListeners.forEach(listener => listener(this.currentOverlay));
  }

  private notifyContextListeners(): void {
    this.contextListeners.forEach(listener => listener(this.currentContext));
  }

  // Get current overlay
  getCurrentOverlay(): CityOverlayData | null {
    return this.currentOverlay;
  }

  // Get current context
  getCurrentContext(): CityContext | null {
    return this.currentContext;
  }

  // Load city overlay
  async loadCityOverlay(overlayName: string): Promise<boolean> {
    try {
      const response = await apiClient.getCityOverlay(overlayName);
      if (response.success && response.data) {
        this.currentOverlay = response.data.overlay;
        this.notifyOverlayListeners();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to load city overlay:', error);
      return false;
    }
  }

  // Load city context
  async loadCityContext(cityName: string): Promise<boolean> {
    try {
      const response = await apiClient.getCityContext(cityName);
      if (response.success && response.data) {
        this.currentContext = response.data.context;
        this.notifyContextListeners();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to load city context:', error);
      return false;
    }
  }

  // Load city overlay ASCII view
  async loadCityOverlayAscii(overlayName: string): Promise<string | null> {
    try {
      const response = await apiClient.getCityOverlayAscii(overlayName);
      if (response.success && response.data) {
        return response.data.ascii;
      }
      return null;
    } catch (error) {
      console.error('Failed to load city overlay ASCII:', error);
      return null;
    }
  }

  // Get city overlay hex details
  async getCityOverlayHex(overlayName: string, hexId: string): Promise<any | null> {
    try {
      const response = await apiClient.getCityOverlayHex(overlayName, hexId);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Failed to get city overlay hex:', error);
      return null;
    }
  }

  // Get city hex details (alias for getCityOverlayHex for consistency)
  async getCityHexDetails(overlayName: string, hexId: string): Promise<any | null> {
    return this.getCityOverlayHex(overlayName, hexId);
  }

  // Get city districts
  async getCityDistricts(overlayName: string): Promise<any[] | null> {
    try {
      const response = await apiClient.getCityDistricts(overlayName);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Failed to get city districts:', error);
      return null;
    }
  }

  // Get district details
  async getDistrictDetails(overlayName: string, districtName: string): Promise<any | null> {
    try {
      const response = await apiClient.getCityDistrictDetails(overlayName, districtName);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Failed to get district details:', error);
      return null;
    }
  }

  // Clear current overlay
  clearOverlay(): void {
    this.currentOverlay = null;
    this.currentContext = null;
    this.notifyOverlayListeners();
    this.notifyContextListeners();
  }

  // Get overlay name from hex code (helper method)
  getOverlayNameFromHexCode(_hexCode: string): string {
    // This could be enhanced with a mapping or API call
    // For now, return a default overlay name
    return 'galgenbeck';
  }

  // Get city hex symbol
  getCityHexSymbol(contentType: string): string {
    const symbols: Record<string, string> = {
      'tavern': '🍺',
      'shop': '🏪',
      'temple': '⛪',
      'guild': '🏛️',
      'residence': '🏠',
      'warehouse': '🏭',
      'market': '🛒',
      'gate': '🚪',
      'wall': '🧱',
      'tower': '🗼',
      'plaza': '🏛️',
      'garden': '🌳',
      'stable': '🐎',
      'blacksmith': '🔨',
      'inn': '🏨',
      'library': '📚',
      'bank': '💰',
      'jail': '🔒',
      'courthouse': '⚖️',
      'park': '🌲'
    };
    return symbols[contentType] || '⬡';
  }

  // Get city hex CSS class
  getCityHexCSSClass(contentType: string): string {
    const classes: Record<string, string> = {
      'tavern': 'city-tavern',
      'shop': 'city-shop',
      'temple': 'city-temple',
      'guild': 'city-guild',
      'residence': 'city-residence',
      'warehouse': 'city-warehouse',
      'market': 'city-market',
      'gate': 'city-gate',
      'wall': 'city-wall',
      'tower': 'city-tower',
      'plaza': 'city-plaza',
      'garden': 'city-garden',
      'stable': 'city-stable',
      'blacksmith': 'city-blacksmith',
      'inn': 'city-inn',
      'library': 'city-library',
      'bank': 'city-bank',
      'jail': 'city-jail',
      'courthouse': 'city-courthouse',
      'park': 'city-park'
    };
    return classes[contentType] || 'city-default';
  }

  // ===== ENHANCED CITY FEATURES =====

  async showCityDetails(hexCode: string): Promise<CityDetails | null> {
    try {
      this.setStateLoading(true);
      const response = await apiClient.getCityDetails(hexCode);
      
      if (response.success && response.data) {
        const cityDetails: CityDetails = {
          ...response.data,
          hexCode
        };
        
        this.logInteraction({
          type: 'view',
          hexId: hexCode,
          timestamp: new Date(),
          userAction: 'viewed_city_details'
        });
        
        return cityDetails;
      }
      return null;
    } catch (error) {
      this.handleError('loading', `Failed to load city details: ${error}`, hexCode);
      return null;
    } finally {
      this.setStateLoading(false);
    }
  }

  async showSettlementDetails(hexCode: string): Promise<SettlementDetails | null> {
    try {
      this.setStateLoading(true);
      const response = await apiClient.getSettlementDetails(hexCode);
      
      if (response.success && response.data) {
        const settlementDetails: SettlementDetails = {
          ...response.data,
          hexCode
        };
        
        this.logInteraction({
          type: 'view',
          hexId: hexCode,
          timestamp: new Date(),
          userAction: 'viewed_settlement_details'
        });
        
        return settlementDetails;
      }
      return null;
    } catch (error) {
      this.handleError('loading', `Failed to load settlement details: ${error}`, hexCode);
      return null;
    } finally {
      this.setStateLoading(false);
    }
  }

  async regenerateCityHex(hexId: string, overlayName: string): Promise<CityHexContent | null> {
    try {
      this.setStateLoading(true);
      const response = await apiClient.regenerateCityHex(overlayName, hexId);
      
      if (response.success && response.data) {
        this.logInteraction({
          type: 'regenerate',
          hexId,
          timestamp: new Date(),
          userAction: 'regenerated_city_hex'
        });
        
        return response.data.hex;
      }
      return null;
    } catch (error) {
      this.handleError('generation', `Failed to regenerate city hex: ${error}`, hexId);
      return null;
    } finally {
      this.setStateLoading(false);
    }
  }

  // ===== STATE MANAGEMENT =====

  subscribeToState(listener: (state: CityState) => void): () => void {
    this.stateListeners.add(listener);
    listener(this.state);
    
    return () => {
      this.stateListeners.delete(listener);
    };
  }

  private notifyStateListeners(): void {
    this.stateListeners.forEach(listener => listener(this.state));
  }

  private setStateLoading(loading: boolean): void {
    this.state.isLoading = loading;
    this.notifyStateListeners();
  }

  private logInteraction(interaction: CityInteraction): void {
    this.state.interactions.push(interaction);
    this.state.lastAction = interaction.userAction;
    this.notifyStateListeners();
  }

  private handleError(type: CityError['type'], message: string, hexId?: string): void {
    const error: CityError = {
      type,
      message,
      hexId,
      timestamp: new Date(),
      recoverable: true
    };
    
    this.state.errors.push(error);
    this.notifyStateListeners();
  }

  // ===== UTILITY METHODS =====

  getState(): CityState {
    return { ...this.state };
  }

  clearErrors(): void {
    this.state.errors = [];
    this.notifyStateListeners();
  }

  getInteractions(): CityInteraction[] {
    return [...this.state.interactions];
  }

  getErrors(): CityError[] {
    return [...this.state.errors];
  }
}

// Export singleton instance
export const cityOverlayService = new CityOverlayService();
export default cityOverlayService; 