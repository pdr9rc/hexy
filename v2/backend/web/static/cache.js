/**
 * Unified Cache Module
 * Handles all frontend data caching with language awareness, versioning, and import/export support.
 * Follows consistent patterns aligned with the translation system.
 */

const CACHE_VERSION = 1;

/**
 * Generate storage key for cache entry
 * Format: hexy_{cacheType}_{identifier}_{lang}_v{version}
 */
function getStorageKey(cacheType, identifier, language) {
  return `hexy_${cacheType}_${identifier}_${language}_v${CACHE_VERSION}`;
}

/**
 * Cache world map data (terrain_map, road_hexes, ascii, parsed grid)
 */
export function cacheWorldMapData(mapData, language) {
  const storageKey = getStorageKey('map', 'world', language);
  try {
    const dataToStore = {
      version: CACHE_VERSION,
      language: language,
      cachedAt: Date.now(),
      data: mapData
    };
    localStorage.setItem(storageKey, JSON.stringify(dataToStore));
  } catch (e) {
    console.warn('Failed to cache world map data:', e);
  }
}

/**
 * Get cached world map data
 */
export function getCachedWorldMapData(language) {
  const storageKey = getStorageKey('map', 'world', language);
  try {
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      const data = JSON.parse(stored);
      if (data.data && data.version === CACHE_VERSION && data.language === language) {
        return data.data;
      }
    }
  } catch (e) {
    console.warn('Failed to get cached world map data:', e);
  }
  return null;
}

/**
 * Cache individual world hex content
 */
export function cacheWorldHex(hexCode, hexData, language) {
  const storageKey = getStorageKey('hex', hexCode, language);
  try {
    const dataToStore = {
      version: CACHE_VERSION,
      language: language,
      cachedAt: Date.now(),
      data: hexData
    };
    localStorage.setItem(storageKey, JSON.stringify(dataToStore));
  } catch (e) {
    console.warn(`Failed to cache world hex ${hexCode}:`, e);
  }
}

/**
 * Get cached world hex content
 */
export function getCachedWorldHex(hexCode, language) {
  const storageKey = getStorageKey('hex', hexCode, language);
  try {
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      const data = JSON.parse(stored);
      if (data.data && data.version === CACHE_VERSION && data.language === language) {
        return data.data;
      }
    }
  } catch (e) {
    console.warn(`Failed to get cached world hex ${hexCode}:`, e);
  }
  return null;
}

/**
 * Batch cache all world hexes
 */
export function cacheAllWorldHexes(hexesMap, language) {
  let cached = 0;
  let failed = 0;
  for (const [hexCode, hexData] of Object.entries(hexesMap)) {
    try {
      cacheWorldHex(hexCode, hexData, language);
      cached++;
    } catch (e) {
      failed++;
      console.warn(`Failed to cache hex ${hexCode}:`, e);
    }
  }
  return { cached, failed };
}

/**
 * Get all cached world hexes for a language
 */
export function getAllCachedWorldHexes(language) {
  const hexes = {};
  try {
    // Pattern: hexy_hex_{hexCode}_{lang}_v1
    const prefix = `hexy_hex_`;
    const suffix = `_${language}_v${CACHE_VERSION}`;
    
    // Iterate through all localStorage keys
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix) && key.endsWith(suffix)) {
        try {
          const stored = localStorage.getItem(key);
          if (stored) {
            const data = JSON.parse(stored);
            if (data.data && data.version === CACHE_VERSION && data.language === language) {
              // Extract hexCode from key: hexy_hex_{hexCode}_{lang}_v1
              // Remove prefix and suffix to get hexCode
              const hexCode = key.slice(prefix.length, -suffix.length);
              hexes[hexCode] = data.data;
            }
          }
        } catch (e) {
          console.warn(`Failed to parse cached hex from key ${key}:`, e);
        }
      }
    }
  } catch (e) {
    console.warn('Failed to get all cached world hexes:', e);
  }
  return hexes;
}

/**
 * Cache city hex content (unified interface for city.js)
 */
export function cacheCityHexContent(cityName, hexContent, language) {
  const storageKey = getStorageKey('city', `${cityName}_hexContent`, language);
  try {
    const dataToStore = {
      version: CACHE_VERSION,
      language: language,
      cachedAt: Date.now(),
      data: {
        hexContent: hexContent,
        cityName: cityName
      }
    };
    localStorage.setItem(storageKey, JSON.stringify(dataToStore));
  } catch (e) {
    console.warn(`Failed to cache city hex content for ${cityName}:`, e);
  }
}

/**
 * Get cached city hex content
 */
export function getCachedCityHexContent(cityName, language) {
  const storageKey = getStorageKey('city', `${cityName}_hexContent`, language);
  try {
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      const data = JSON.parse(stored);
      if (data.data && data.version === CACHE_VERSION && data.language === language) {
        return data.data.hexContent || null;
      }
    }
  } catch (e) {
    console.warn(`Failed to get cached city hex content for ${cityName}:`, e);
  }
  return null;
}

/**
 * Cache district colors (unified interface)
 */
export function cacheDistrictColors(cityName, districtColors, language) {
  const storageKey = getStorageKey('city', `${cityName}_districtColors`, language);
  try {
    const dataToStore = {
      version: CACHE_VERSION,
      language: language,
      cachedAt: Date.now(),
      data: {
        districtColors: districtColors,
        cityName: cityName
      }
    };
    localStorage.setItem(storageKey, JSON.stringify(dataToStore));
  } catch (e) {
    console.warn(`Failed to cache district colors for ${cityName}:`, e);
  }
}

/**
 * Get cached district colors
 */
export function getCachedDistrictColors(cityName, language) {
  const storageKey = getStorageKey('city', `${cityName}_districtColors`, language);
  try {
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      const data = JSON.parse(stored);
      if (data.data && data.version === CACHE_VERSION && data.language === language) {
        return data.data.districtColors || null;
      }
    }
  } catch (e) {
    console.warn(`Failed to get cached district colors for ${cityName}:`, e);
  }
  return null;
}

/**
 * Export all cache data for a language
 */
export function exportCacheData(language) {
  const exportData = {
    version: CACHE_VERSION,
    language: language,
    exportedAt: Date.now(),
    map: {},
    hexes: {},
    cities: {}
  };

  try {
    // Export world map
    const mapData = getCachedWorldMapData(language);
    if (mapData) {
      exportData.map = mapData;
    }

    // Export all world hexes
    exportData.hexes = getAllCachedWorldHexes(language);

    // Export city data (iterate through localStorage to find all city caches)
    // Pattern: hexy_city_{cityName}_{type}_{lang}_v1
    const cityPrefix = `hexy_city_`;
    const citySuffix = `_${language}_v${CACHE_VERSION}`;
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(cityPrefix) && key.endsWith(citySuffix)) {
        try {
          const stored = localStorage.getItem(key);
          if (stored) {
            const data = JSON.parse(stored);
            if (data.data && data.version === CACHE_VERSION && data.language === language) {
              // Extract city name and type from key
              // Format: hexy_city_{cityName}_{type}_{lang}_v1
              // Remove prefix and suffix, then split by _ to get cityName and type
              const middle = key.slice(cityPrefix.length, -citySuffix.length);
              const lastUnderscore = middle.lastIndexOf('_');
              if (lastUnderscore > 0) {
                const cityName = middle.slice(0, lastUnderscore);
                const type = middle.slice(lastUnderscore + 1); // hexContent or districtColors
                if (!exportData.cities[cityName]) {
                  exportData.cities[cityName] = {};
                }
                exportData.cities[cityName][type] = data.data;
              }
            }
          }
        } catch (e) {
          console.warn(`Failed to export city data from key ${key}:`, e);
        }
      }
    }
  } catch (e) {
    console.warn('Failed to export cache data:', e);
  }

  return exportData;
}

/**
 * Import cache data
 */
export function importCacheData(cacheData, language) {
  if (!cacheData || cacheData.language !== language) {
    console.warn('Cache data language mismatch or invalid data');
    return false;
  }

  try {
    // Import world map
    if (cacheData.map) {
      cacheWorldMapData(cacheData.map, language);
    }

    // Import world hexes
    if (cacheData.hexes && typeof cacheData.hexes === 'object') {
      cacheAllWorldHexes(cacheData.hexes, language);
    }

    // Import city data
    if (cacheData.cities && typeof cacheData.cities === 'object') {
      for (const [cityName, cityData] of Object.entries(cacheData.cities)) {
        if (cityData.hexContent) {
          cacheCityHexContent(cityName, cityData.hexContent.hexContent, language);
        }
        if (cityData.districtColors) {
          cacheDistrictColors(cityName, cityData.districtColors.districtColors, language);
        }
      }
    }

    return true;
  } catch (e) {
    console.warn('Failed to import cache data:', e);
    return false;
  }
}

/**
 * Clear specific cache
 */
export function clearCache(cacheType, identifier, language) {
  const storageKey = getStorageKey(cacheType, identifier, language);
  try {
    localStorage.removeItem(storageKey);
    return true;
  } catch (e) {
    console.warn(`Failed to clear cache ${cacheType}/${identifier}:`, e);
    return false;
  }
}

/**
 * Clear all cache for a language
 */
export function clearAllCache(language) {
  let cleared = 0;
  try {
    const prefix = `hexy_`;
    const suffix = `_${language}_v${CACHE_VERSION}`;
    const keysToRemove = [];
    
    // Collect all keys to remove
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix) && key.endsWith(suffix)) {
        keysToRemove.push(key);
      }
    }
    
    // Remove all collected keys
    keysToRemove.forEach(key => {
      try {
        localStorage.removeItem(key);
        cleared++;
      } catch (e) {
        console.warn(`Failed to remove cache key ${key}:`, e);
      }
    });
  } catch (e) {
    console.warn('Failed to clear all cache:', e);
  }
  
  return cleared;
}

/**
 * Get cache statistics
 */
export function getCacheStats(language) {
  const stats = {
    language: language,
    map: false,
    hexCount: 0,
    cityCount: 0,
    totalSize: 0
  };

  try {
    // Check for world map
    const mapData = getCachedWorldMapData(language);
    stats.map = mapData !== null;

    // Count hexes
    const hexes = getAllCachedWorldHexes(language);
    stats.hexCount = Object.keys(hexes).length;

    // Count cities and calculate total size
    const prefix = `hexy_`;
    const suffix = `_${language}_v${CACHE_VERSION}`;
    const cities = new Set();
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix) && key.endsWith(suffix)) {
        try {
          const stored = localStorage.getItem(key);
          if (stored) {
            stats.totalSize += stored.length;
            // Extract city name if it's a city cache
            if (key.includes('_city_')) {
              const parts = key.split('_');
              if (parts.length >= 3) {
                cities.add(parts[2]);
              }
            }
          }
        } catch (e) {
          // Ignore errors
        }
      }
    }
    
    stats.cityCount = cities.size;
  } catch (e) {
    console.warn('Failed to get cache stats:', e);
  }

  return stats;
}

/**
 * Migrate old cache format to new format
 * Handles migration from keys without version suffix
 */
export function migrateOldCache(language) {
  let migrated = 0;
  try {
    const oldPatterns = [
      { type: 'city', pattern: /^hexy_city_(.+?)_(hexContent|districtColors)$/ },
      { type: 'hex', pattern: /^hexy_hex_(.+?)$/ },
      { type: 'map', pattern: /^hexy_map_world$/ }
    ];

    const keysToMigrate = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key) continue;

      // Skip already migrated keys
      if (key.includes(`_v${CACHE_VERSION}`)) continue;

      // Check if it matches old patterns and contains language
      if (key.includes(`_${language}_`) || key.endsWith(`_${language}`)) {
        for (const { type, pattern } of oldPatterns) {
          const match = key.match(pattern);
          if (match) {
            keysToMigrate.push({ oldKey: key, type, match });
            break;
          }
        }
      }
    }

    // Migrate each key
    for (const { oldKey, type, match } of keysToMigrate) {
      try {
        const stored = localStorage.getItem(oldKey);
        if (stored) {
          const data = JSON.parse(stored);
          
          // Determine new key format
          let newKey;
          if (type === 'city') {
            const cityName = match[1];
            const subType = match[2];
            newKey = getStorageKey('city', `${cityName}_${subType}`, language);
          } else if (type === 'hex') {
            const hexCode = match[1];
            newKey = getStorageKey('hex', hexCode, language);
          } else if (type === 'map') {
            newKey = getStorageKey('map', 'world', language);
          }

          if (newKey) {
            // Store with new format
            const newData = {
              version: CACHE_VERSION,
              language: language,
              cachedAt: data.cachedAt || Date.now(),
              data: data.data || data.hexContent || data.districtColors || data
            };
            localStorage.setItem(newKey, JSON.stringify(newData));
            // Remove old key
            localStorage.removeItem(oldKey);
            migrated++;
          }
        }
      } catch (e) {
        console.warn(`Failed to migrate cache key ${oldKey}:`, e);
      }
    }
  } catch (e) {
    console.warn('Failed to migrate old cache:', e);
  }

  return migrated;
}

