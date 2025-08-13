class TranslationManager {
    private translations: Record<string, string> = {};
    private currentLanguage: string = 'en';
    private fallbackLanguage: string = 'en';
    private isLoading: boolean = false;
    
    constructor() {
        this.loadTranslations();
    }
    
    async loadTranslations(): Promise<void> {
        if (this.isLoading) return;
        this.isLoading = true;
        
        try {
            console.log('🌐 Loading translations for language:', this.currentLanguage);
            
            // Load UI translations from the unified backend API
            const response = await fetch(`/api/translations/ui/${this.currentLanguage}`);
            if (response.ok) {
                const data = await response.json();
                this.translations = this._flattenTranslations(data);
                console.log('✅ Translations loaded successfully:', Object.keys(this.translations).length, 'keys');
            }
            else {
                console.warn('⚠️ Failed to load translations from API, using fallback');
                await this._loadFallbackTranslations();
            }
        }
        catch (error) {
            console.warn('Failed to load translations, using defaults:', error);
            this.loadDefaultTranslations();
        }
        finally {
            this.isLoading = false;
        }
    }
    
    private async _loadFallbackTranslations(): Promise<void> {
        try {
            // Try loading English as fallback
            const fallbackResponse = await fetch(`/api/translations/ui/${this.fallbackLanguage}`);
            if (fallbackResponse.ok) {
                const data = await fallbackResponse.json();
                this.translations = this._flattenTranslations(data);
                console.log('✅ Fallback translations loaded successfully');
            } else {
                this.loadDefaultTranslations();
            }
        } catch (error) {
            console.warn('Failed to load fallback translations:', error);
            this.loadDefaultTranslations();
        }
    }
    
    private _flattenTranslations(data: any): Record<string, string> {
        const flattened: Record<string, string> = {};
        
        for (const [key, value] of Object.entries(data)) {
            if (typeof value === 'string') {
                flattened[key] = value;
            } else if (typeof value === 'object' && value !== null) {
                // Handle nested objects with dot notation
                for (const [subKey, subValue] of Object.entries(value)) {
                    if (typeof subValue === 'string') {
                        flattened[`${key}.${subKey}`] = subValue;
                        // Also add without prefix for backward compatibility
                        flattened[subKey] = subValue;
                    }
                }
            }
        }
        
        return flattened;
    }
    
    loadDefaultTranslations(): void {
        this.translations = {
            // Navigation
            'return_to_hex': 'RETURN TO HEX',
            'return_to_map': 'RETURN TO MAP',
            'return_to_world': 'RETURN TO WORLD MAP',
            'MAP_GRID': 'MAP GRID',
            'RETURN_TO_HEX': 'RETURN TO HEX',
            'RETURN_TO_MAP': 'RETURN TO MAP',
            
            // Hex Details
            'type': 'TYPE',
            'district': 'DISTRICT',
            'position': 'POSITION',
            'description': 'DESCRIPTION',
            'atmosphere': 'ATMOSPHERE',
            'encounter': 'ENCOUNTER',
            'notable_features': 'NOTABLE FEATURES',
            
            // NPC Information
            'npc_information': 'NPC INFORMATION',
            'name': 'NAME',
            'trade': 'TRADE',
            'trait': 'TRAIT',
            'concern': 'CONCERN',
            'want': 'WANT',
            'secret': 'SECRET',
            'affiliation': 'AFFILIATION',
            'attitude': 'ATTITUDE',
            
            // Tavern Details
            'tavern_details': 'TAVERN DETAILS',
            'menu': 'MENU',
            'innkeeper': 'INNKEEPER',
            'notable_patron': 'NOTABLE PATRON',
            
            // Market Details
            'market_details': 'MARKET DETAILS',
            'items_sold': 'ITEMS SOLD',
            'beast_prices': 'BEAST PRICES',
            'services': 'SERVICES',
            
            // City Context
            'city_description': 'CITY DESCRIPTION',
            'city_events': 'CITY EVENTS',
            'weather': 'WEATHER',
            'regional_npcs': 'REGIONAL NPCS',
            'major_factions': 'MAJOR FACTIONS',
            'local_factions': 'LOCAL FACTIONS',
            'criminal_factions': 'CRIMINAL FACTIONS',
            'faction_relationships': 'FACTION RELATIONSHIPS',
            'other_factions': 'OTHER FACTIONS',
            'major_landmarks': 'MAJOR LANDMARKS',
            'districts': 'DISTRICTS',
            
            // Settlement Details
            'location': 'LOCATION',
            'population': 'POPULATION',
            'city_districts': 'CITY DISTRICTS',
            'key_npcs': 'KEY NPCS',
            'active_factions': 'ACTIVE FACTIONS',
            
            // Faction Details
            'leader': 'Leader',
            'hq': 'HQ',
            'influence': 'Influence',
            'activities': 'Activities',
            
            // Error Messages
            'error_loading_map': 'Failed to load map data',
            'error_loading_hex': 'Failed to load hex details',
            'error_loading_city': 'Failed to load city hex details',
            'error_loading_settlement': 'Failed to load settlement details',
            'error_regenerating': 'Error regenerating hex',
            'hex_not_found': 'Hex not found',
            'no_overlay_context': 'Error: No city overlay context found',
            
            // Success Messages
            'hex_regenerated': 'Hex regenerated successfully',
            'returned_to_map': 'Returned to world map',
            'returned_to_hex': 'Returned to hex details view',
            
            // UI Elements
            'SELECTED_DISTRICT': 'SELECTED DISTRICT',
            'CLICK_HEX_FOR_DETAILS': 'Click on a hex to view district details and information.',
            'THE_DYING_LANDS': 'THE DYING LANDS',
            'WELCOME_TO_HEXCRAWL': 'WELCOME TO THE HEXCRAWL',
            'CLICK_HEX_TO_EXPLORE': 'Click a hex to explore its mysteries...',
            'HEX_CONTAINS_UNIQUE_ENCOUNTERS': 'Each hex contains unique encounters, denizens, and secrets waiting to be discovered.',
            'WORLD_IS_DYING': 'The world is dying, but adventure lives on.',
            'ADVENTURE_LIVES_ON': 'Adventure lives on.',
            'INSTRUCTIONS': 'INSTRUCTIONS',
            'CLICK_ANY_HEX_ON_MAP': '• Click any hex on the map to view its details',
            'MAJOR_CITIES_HAVE_ADDITIONAL_OVERLAY_VIEWS': '• Major cities (◆) have additional overlay views',
            'SETTLEMENTS_PROVIDE_LOCAL_INFORMATION': '• Settlements (⌂) provide local information',
            'BOLD_HEXES_CONTAIN_SPECIAL_CONTENT': '• Bold hexes contain special content',
            
            // Default Values
            'unknown': 'Unknown',
            'unknown_type': 'unknown',
            'no_atmosphere': 'No atmosphere available.',
            'empty': 'empty'
        };
    }
    
    t(key: string, fallback?: string): string {
        // Handle key variations and fallbacks
        let translation = this.translations[key];
        
        if (!translation) {
            // Try with uppercase
            translation = this.translations[key.toUpperCase()];
        }
        
        if (!translation) {
            // Try with lowercase
            translation = this.translations[key.toLowerCase()];
        }
        
        return translation || fallback || key;
    }
    
    async setLanguage(language: string): Promise<void> {
        if (this.currentLanguage !== language) {
            this.currentLanguage = language;
            await this.loadTranslations();
        }
    }
    
    getCurrentLanguage(): string {
        return this.currentLanguage;
    }
    
    isTranslationLoaded(): boolean {
        return !this.isLoading && Object.keys(this.translations).length > 0;
    }
}

// Create singleton instance
export const translationManager = new TranslationManager();

// Convenience function
export const t = (key: string, fallback?: string): string => {
    return translationManager.t(key, fallback);
};
