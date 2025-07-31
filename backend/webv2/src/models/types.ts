// Core types for the Hexy application

export interface HexCoordinate {
  q: number;
  r: number;
  s: number;
}

export interface HexData {
  id: string;
  coordinate: HexCoordinate;
  terrain: string;
  content?: any;
  isSelected?: boolean;
}

export interface WorldHex extends HexData {
  type: 'world';
  biome?: string;
  features?: string[];
}

export interface CityHex extends HexData {
  type: 'city';
  cityName?: string;
  population?: string;
  buildings?: string[];
}

export type HexContent = WorldHex | CityHex;

export interface City {
  id: string;
  name: string;
  coordinates: HexCoordinate;
  population: number;
  type: string;
  description?: string;
}

export interface HexData {
  x: number;
  y: number;
  terrain: string;
  symbol: string;
  is_city: boolean;
  city_name?: string;
  population?: string;
  region?: string;
  has_content: boolean;
  content_type?: string;
  css_class: string;
}

export interface CityOverlayData {
  name: string;
  display_name: string;
  filename: string;
  grid_type: string;
  radius: number;
  hex_grid: { [key: string]: any };
  total_hexes: number;
  hexCode?: string;
  districts?: Array<{
    name: string;
    description: string;
    theme: string;
    buildings: string[];
    streets: string[];
  }>;
}

export interface CityContext {
  name: string;
  description: string;
  city_events?: string[];
  weather_conditions?: string[];
  regional_npcs?: string[];
  major_factions?: Array<{
    name: string;
    leader: string;
    headquarters: string;
    influence: string;
    attitude: string;
    activities?: string[];
  }>;
  local_factions?: Array<{
    name: string;
    leader: string;
    headquarters: string;
    influence: string;
    attitude: string;
    activities?: string[];
  }>;
}

export interface WorldGrid {
  hexes: WorldHex[];
  width: number;
  height: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface HexContentResponse {
  hex: HexContent;
  details: any;
}

export type ViewMode = 'world' | 'cities';

// Re-export enhanced models (with explicit exports to avoid conflicts)
export * from './CityModels';
export * from './HexContentModels';
export * from './WorldGridModels';
export * from './ApiModels'; 