// Enhanced API models for comprehensive API integration
import type { 
  EnhancedHexData, 
  GridStatistics 
} from './WorldGridModels';
import type { 
  EnhancedHexContent, 
  ContentGenerationOptions 
} from './HexContentModels';
import type { 
  CityHexContent, 
  DistrictDetails, 
  CityGenerationOptions,
  EnhancedCityOverlayData 
} from './CityModels';
import type { CityOverlayData, CityContext } from './types';
import type { RandomTable } from './HexContentModels';

// Base API response structure
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: Date;
  version: string;
  requestId: string;
}

// World Grid API Models
export interface WorldGridResponse {
  grid: { [key: string]: EnhancedHexData };
  dimensions: { width: number; height: number };
  statistics: GridStatistics;
  metadata: {
    generated_at: Date;
    version: string;
    seed?: number;
  };
}

export interface GenerateHexResponse {
  hex: EnhancedHexData;
  content?: EnhancedHexContent;
  generated_at: Date;
  seed?: number;
}

export interface ResetContinentResponse {
  success: boolean;
  new_grid: WorldGridResponse;
  reset_at: Date;
}

// City Overlay API Models
export interface CityOverlaysResponse {
  overlays: CityOverlayData[];
  total_count: number;
  available_cities: string[];
}

export interface CityOverlayResponse {
  overlay: EnhancedCityOverlayData;
  context: CityContext;
  ascii_view?: string;
  statistics: {
    total_hexes: number;
    districts: number;
    buildings: number;
    streets: number;
  };
}

export interface CityHexResponse {
  hex: CityHexContent;
  district?: DistrictDetails;
  connections: string[];
  generation_options: CityGenerationOptions;
}

export interface CityDistrictResponse {
  district: DistrictDetails;
  hexes: string[];
  connections: { [hexId: string]: string[] };
  random_tables: RandomTable[];
}

export interface RegenerateCityHexResponse {
  hex: CityHexContent;
  previous_content?: CityHexContent;
  generated_at: Date;
  seed?: number;
}

// Content Generation API Models
export interface GenerateContentResponse {
  content: EnhancedHexContent;
  generation_options: ContentGenerationOptions;
  generated_at: Date;
  seed?: number;
}

export interface RegenerateContentResponse {
  content: EnhancedHexContent;
  previous_content?: EnhancedHexContent;
  generated_at: Date;
  seed?: number;
}

// Lore API Models
export interface LoreOverviewResponse {
  overview: {
    world_name: string;
    description: string;
    major_themes: string[];
    key_locations: string[];
    important_npcs: string[];
    major_events: string[];
  };
  factions: Array<{
    name: string;
    leader: string;
    headquarters: string;
    influence: string;
    attitude: string;
    activities: string[];
  }>;
  regions: Array<{
    name: string;
    description: string;
    characteristics: string[];
    dangers: string[];
  }>;
}

// Language API Models
export interface LanguageResponse {
  language: string;
  available_languages: string[];
  translation_status: {
    [key: string]: 'complete' | 'partial' | 'missing';
  };
}

// Error API Models
export interface ApiError {
  type: 'validation' | 'not_found' | 'server_error' | 'rate_limit' | 'authentication';
  code: string;
  message: string;
  details?: { [key: string]: any };
  timestamp: Date;
  requestId: string;
  recoverable: boolean;
}

// Search and Filter API Models
export interface SearchRequest {
  query: string;
  filters: {
    terrain?: string[];
    content_type?: string[];
    cities?: boolean;
    explored?: boolean;
    region?: string[];
  };
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SearchResponse {
  results: Array<{
    hex_id: string;
    coordinate: { q: number; r: number; s: number };
    terrain: string;
    content_type?: string;
    relevance_score: number;
    preview: string;
  }>;
  total_count: number;
  query: string;
  filters: SearchRequest['filters'];
}

// Export/Import API Models
export interface ExportRequest {
  format: 'json' | 'csv' | 'image' | 'pdf';
  include_metadata: boolean;
  include_exploration: boolean;
  include_content: boolean;
  compression?: boolean;
  resolution?: { width: number; height: number };
}

export interface ExportResponse {
  download_url: string;
  file_size: number;
  format: string;
  expires_at: Date;
  checksum: string;
}

export interface ImportRequest {
  file: File;
  format: 'json' | 'csv';
  overwrite_existing: boolean;
  preserve_exploration: boolean;
  validate_data: boolean;
  merge_strategy: 'replace' | 'merge' | 'append';
}

export interface ImportResponse {
  success: boolean;
  imported_hexes: number;
  skipped_hexes: number;
  errors: Array<{
    hex_id: string;
    error: string;
  }>;
  warnings: string[];
}

// Performance and Analytics API Models
export interface PerformanceMetrics {
  api_response_time: number;
  database_query_time: number;
  memory_usage: number;
  cpu_usage: number;
  active_connections: number;
  requests_per_minute: number;
}

export interface AnalyticsData {
  total_requests: number;
  unique_users: number;
  popular_hexes: string[];
  popular_cities: string[];
  generation_stats: {
    total_generated: number;
    average_generation_time: number;
    most_common_content: string[];
  };
  error_stats: {
    total_errors: number;
    error_types: { [type: string]: number };
    recovery_rate: number;
  };
}

// WebSocket API Models
export interface WebSocketMessage {
  type: 'update' | 'notification' | 'error' | 'status';
  data: any;
  timestamp: Date;
  messageId: string;
}

export interface WebSocketUpdate {
  type: 'hex_update' | 'content_update' | 'city_update' | 'system_update';
  hexId?: string;
  data: any;
  timestamp: Date;
}

// Authentication and Authorization API Models
export interface AuthRequest {
  username: string;
  password: string;
  remember_me?: boolean;
}

export interface AuthResponse {
  token: string;
  refresh_token: string;
  expires_at: Date;
  user: {
    id: string;
    username: string;
    permissions: string[];
    preferences: { [key: string]: any };
  };
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  token: string;
  expires_at: Date;
}

// User Preferences API Models
export interface UserPreferences {
  display_options: {
    theme: 'light' | 'dark' | 'mork_borg';
    language: string;
    compact_mode: boolean;
    show_coordinates: boolean;
    show_grid_lines: boolean;
  };
  content_options: {
    include_npcs: boolean;
    include_loot: boolean;
    include_encounters: boolean;
    difficulty: 'easy' | 'medium' | 'hard' | 'deadly';
  };
  performance_options: {
    enable_animations: boolean;
    enable_sound: boolean;
    auto_save: boolean;
    save_interval: number;
  };
}

export interface UpdatePreferencesRequest {
  preferences: Partial<UserPreferences>;
}

export interface UpdatePreferencesResponse {
  success: boolean;
  updated_preferences: UserPreferences;
  timestamp: Date;
} 