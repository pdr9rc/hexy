// City-related models for enhanced city functionality
import type { CityOverlayData, CityContext } from './types';

export interface CityDetails {
  name: string;
  population: string;
  region: string;
  atmosphere: string;
  description: string;
  notable_features: string;
  key_npcs: string;
  hexCode: string;
}

export interface SettlementDetails {
  name: string;
  population: string;
  atmosphere: string;
  description: string;
  notable_feature: string;
  local_tavern: string;
  local_power: string;
  hexCode: string;
}

export interface CityHexContent {
  name: string;
  type: string;
  description: string;
  encounter: string;
  atmosphere: string;
  position_type: string;
  district?: string;
  buildings?: string[];
  streets?: string[];
  services?: string[];
  patrons?: string[];
  random_encounters?: string[];
}

export interface DistrictDetails {
  name: string;
  description: string;
  theme: string;
  buildings: string[];
  streets: string[];
  color: string;
  hexes: string[];
}

export interface CityOverlayState {
  currentOverlay: CityOverlayData | null;
  currentContext: CityContext | null;
  selectedHex: string | null;
  viewMode: 'grid' | 'ascii' | 'details';
  isLoading: boolean;
  error: string | null;
}

export interface CityGenerationOptions {
  overlayName: string;
  hexId: string;
  preserveExisting: boolean;
  includeRandomEncounters: boolean;
  includeNPCs: boolean;
}

// Enhanced city overlay data with additional properties
export interface EnhancedCityOverlayData extends CityOverlayData {
  districts: DistrictDetails[];
  cityDetails: CityDetails;
  settlements: SettlementDetails[];
  generationOptions: CityGenerationOptions;
  lastUpdated: Date;
  version: string;
}

// City interaction models
export interface CityInteraction {
  type: 'hex_click' | 'district_select' | 'regenerate' | 'view_change' | 'view';
  hexId?: string;
  districtName?: string;
  viewMode?: 'grid' | 'ascii' | 'details';
  timestamp: Date;
  userAction: string;
}

// City error models
export interface CityError {
  type: 'loading' | 'generation' | 'display' | 'api';
  message: string;
  hexId?: string;
  overlayName?: string;
  timestamp: Date;
  recoverable: boolean;
}

// City state management
export interface CityState {
  overlays: Map<string, EnhancedCityOverlayData>;
  currentOverlay: string | null;
  interactions: CityInteraction[];
  errors: CityError[];
  isLoading: boolean;
  lastAction: string | null;
} 