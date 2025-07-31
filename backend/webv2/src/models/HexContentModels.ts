// Enhanced hex content models for rich content display

export interface LootItem {
  type: string;
  item: string;
  description: string;
  full_description?: string;
  value?: number;
  rarity?: 'common' | 'uncommon' | 'rare' | 'legendary';
  magical?: boolean;
  cursed?: boolean;
}

export interface NPCDetails {
  name: string;
  type: string;
  description: string;
  personality: string;
  motivations: string[];
  secrets: string[];
  relationships: string[];
  equipment: string[];
  abilities: string[];
  weaknesses?: string[];
  goals: string[];
}

export interface TavernDetails {
  name: string;
  type: string;
  atmosphere: string;
  description: string;
  innkeeper: NPCDetails;
  menu: string[];
  prices: { [item: string]: number };
  patrons: NPCDetails[];
  rumors: string[];
  events: string[];
  services: string[];
}

export interface MarketDetails {
  name: string;
  type: string;
  description: string;
  merchants: NPCDetails[];
  goods: LootItem[];
  services: string[];
  prices: { [item: string]: number };
  special_items: LootItem[];
  events: string[];
}

// SettlementDetails moved to CityModels.ts to avoid conflicts

export interface DungeonDetails {
  name: string;
  type: string;
  description: string;
  entrance: string;
  layout: string;
  inhabitants: NPCDetails[];
  treasures: LootItem[];
  traps: string[];
  hazards: string[];
  exits: string[];
}

export interface EncounterDetails {
  type: string;
  description: string;
  participants: NPCDetails[];
  environment: string;
  challenges: string[];
  rewards: LootItem[];
  consequences: string[];
  alternatives: string[];
}

export interface BeastDetails {
  name: string;
  type: string;
  description: string;
  behavior: string;
  habitat: string;
  abilities: string[];
  weaknesses: string[];
  loot: LootItem[];
  encounters: string[];
}

export interface MagicalEffect {
  name: string;
  type: string;
  description: string;
  duration: string;
  effects: string[];
  source: string;
  consequences: string[];
  dispel_conditions: string[];
}

export interface RandomTable {
  name: string;
  type: string;
  entries: string[];
  weights?: number[];
  conditions?: string[];
  modifiers?: { [key: string]: string };
}

// Enhanced hex content with all possible details
export interface EnhancedHexContent {
  // Basic info
  id: string;
  coordinate: { q: number; r: number; s: number };
  terrain: string;
  type: 'world' | 'city';
  
  // Content details
  description?: string;
  encounter?: EncounterDetails;
  denizen?: NPCDetails;
  loot?: LootItem[];
  treasure?: LootItem[];
  
  // Settlement-specific
  settlement?: any; // SettlementDetails moved to CityModels.ts
  tavern?: TavernDetails;
  market?: MarketDetails;
  
  // Dungeon-specific
  dungeon?: DungeonDetails;
  
  // Beast-specific
  beast?: BeastDetails;
  
  // Magical effects
  magical_effects?: MagicalEffect[];
  
  // Random tables
  random_tables?: RandomTable[];
  
  // Metadata
  generated_at: Date;
  version: string;
  tags: string[];
}

// Content generation options
export interface ContentGenerationOptions {
  includeNPCs: boolean;
  includeLoot: boolean;
  includeEncounters: boolean;
  includeMagicalEffects: boolean;
  difficulty: 'easy' | 'medium' | 'hard' | 'deadly';
  theme?: string;
  tags?: string[];
}

// Content display options
export interface ContentDisplayOptions {
  showDetails: boolean;
  showLoot: boolean;
  showNPCs: boolean;
  showEncounters: boolean;
  showMagicalEffects: boolean;
  compactMode: boolean;
  showMetadata: boolean;
}

// Content interaction models
export interface ContentInteraction {
  type: 'view' | 'generate' | 'regenerate' | 'expand' | 'collapse';
  contentId: string;
  section?: string;
  timestamp: Date;
  userAction: string;
}

// Content error models
export interface ContentError {
  type: 'generation' | 'display' | 'api' | 'formatting';
  message: string;
  contentId?: string;
  section?: string;
  timestamp: Date;
  recoverable: boolean;
}

// Content state management
export interface ContentState {
  currentContent: EnhancedHexContent | null;
  displayOptions: ContentDisplayOptions;
  interactions: ContentInteraction[];
  errors: ContentError[];
  isLoading: boolean;
  lastAction: string | null;
} 