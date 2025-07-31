// Enhanced world grid models for comprehensive grid functionality

export interface WorldGridState {
  mapData: { [key: string]: EnhancedHexData };
  dimensions: { width: number; height: number };
  selectedHex: string | null;
  highlightedHexes: string[];
  viewMode: 'normal' | 'explored' | 'fog_of_war';
  zoomLevel: number;
  panOffset: { x: number; y: number };
  isLoading: boolean;
  error: string | null;
}

export interface EnhancedHexData {
  // Basic coordinates
  x: number;
  y: number;
  q: number;
  r: number;
  s: number;
  
  // Terrain and appearance
  terrain: string;
  symbol: string;
  css_class: string;
  
  // Content flags
  is_city: boolean;
  has_content: boolean;
  content_type?: string;
  
  // City-specific
  city_name?: string;
  population?: string;
  region?: string;
  
  // Exploration state
  is_explored: boolean;
  is_visible: boolean;
  last_visited?: Date;
  
  // Generation metadata
  generated_at: Date;
  version: string;
  seed?: number;
  
  // Custom properties
  custom_properties: { [key: string]: any };
}

export interface GridGenerationOptions {
  width: number;
  height: number;
  terrainTypes: string[];
  cityDensity: number;
  contentDensity: number;
  seed?: number;
  theme?: string;
  difficulty?: 'easy' | 'medium' | 'hard' | 'deadly';
}

export interface GridDisplayOptions {
  showCoordinates: boolean;
  showTerrain: boolean;
  showContent: boolean;
  showCities: boolean;
  showExploration: boolean;
  compactMode: boolean;
  highlightSelected: boolean;
  showGridLines: boolean;
}

export interface GridInteraction {
  type: 'select' | 'highlight' | 'explore' | 'generate' | 'reset';
  hexId: string;
  timestamp: Date;
  userAction: string;
  metadata?: { [key: string]: any };
}

export interface GridError {
  type: 'generation' | 'display' | 'api' | 'validation';
  message: string;
  hexId?: string;
  timestamp: Date;
  recoverable: boolean;
  context?: { [key: string]: any };
}

export interface TerrainType {
  name: string;
  symbol: string;
  css_class: string;
  color: string;
  description: string;
  movement_cost: number;
  visibility_modifier: number;
  content_probability: number;
  city_probability: number;
}

export interface ContentType {
  name: string;
  symbol: string;
  css_class: string;
  description: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'legendary';
  difficulty: 'easy' | 'medium' | 'hard' | 'deadly';
  terrain_restrictions: string[];
  generation_options: { [key: string]: any };
}

export interface GridStatistics {
  total_hexes: number;
  explored_hexes: number;
  visible_hexes: number;
  cities: number;
  settlements: number;
  content_hexes: number;
  terrain_distribution: { [terrain: string]: number };
  content_distribution: { [content: string]: number };
  exploration_percentage: number;
}

export interface GridExportOptions {
  format: 'json' | 'csv' | 'image' | 'pdf';
  includeMetadata: boolean;
  includeExploration: boolean;
  includeContent: boolean;
  resolution?: { width: number; height: number };
  compression?: boolean;
}

export interface GridImportOptions {
  format: 'json' | 'csv';
  overwriteExisting: boolean;
  preserveExploration: boolean;
  validateData: boolean;
  mergeStrategy: 'replace' | 'merge' | 'append';
}

// Grid navigation models
export interface GridNavigation {
  currentPosition: { q: number; r: number; s: number };
  path: string[];
  destination?: { q: number; r: number; s: number };
  movementCost: number;
  visibility: boolean;
  explored: boolean;
}

// Grid search and filtering
export interface GridSearchCriteria {
  terrain?: string[];
  content?: string[];
  cities?: boolean;
  explored?: boolean;
  visible?: boolean;
  custom_properties?: { [key: string]: any };
}

export interface GridSearchResult {
  hexes: string[];
  count: number;
  criteria: GridSearchCriteria;
  timestamp: Date;
}

// Grid performance models
export interface GridPerformance {
  renderTime: number;
  memoryUsage: number;
  hexCount: number;
  visibleHexes: number;
  updateFrequency: number;
  lastOptimization: Date;
}

// Grid backup and versioning
export interface GridBackup {
  id: string;
  name: string;
  description: string;
  data: WorldGridState;
  created_at: Date;
  version: string;
  size: number;
  checksum: string;
}

export interface GridVersion {
  version: string;
  changes: string[];
  compatibility: string[];
  migration_required: boolean;
  deprecated_features: string[];
} 