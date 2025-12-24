/**
 * City Logic Module
 * Handles ALL city content generation, encounter selection, and content type selection.
 * Ported from v1 backend CityOverlayAnalyzer.
 * Grid system (grid.js) stays completely untouched.
 */

import * as cache from './cache.js';

// Module-level cache for city data
let cachedCityData = null;

// Cache for all generated hex content (hexId -> content)
let hexContentCache = {};

/**
 * Cache city data from API response
 */
export function cacheCityData(apiResponse) {
  cachedCityData = {
    cityData: apiResponse.city_data,
    encounterTables: apiResponse.encounter_tables,
    language: apiResponse.language,
    cachedAt: Date.now()
  };
  
  // Try to load persisted hex content for this city
  const cityName = apiResponse.city_data?.city_name || apiResponse.city_data?.display_name || 'unknown';
  const lang = apiResponse.language || 'en';
  loadHexContentCache(cityName, lang);
}

/**
 * Get cached city data
 */
export function getCachedCityData() {
  return cachedCityData;
}

/**
 * Get cached hex content
 */
export function getHexContent(hexId) {
  return hexContentCache[hexId] || null;
}

/**
 * Set hex content in cache
 */
export function setHexContent(hexId, content) {
  hexContentCache[hexId] = content;
  // Persist to localStorage using unified cache
  persistHexContentCache();
}

/**
 * Clear hex content cache
 */
export function clearHexContentCache() {
  hexContentCache = {};
  // Clear from localStorage using unified cache
  if (cachedCityData) {
    const cityName = cachedCityData.cityData?.city_name || cachedCityData.cityData?.display_name || 'unknown';
    const lang = cachedCityData.language || 'en';
    cache.clearCache('city', `${cityName}_hexContent`, lang);
  }
}

/**
 * Persist hex content cache to localStorage using unified cache
 */
function persistHexContentCache() {
  if (!cachedCityData || Object.keys(hexContentCache).length === 0) return;
  
  const cityName = cachedCityData.cityData?.city_name || cachedCityData.cityData?.display_name || 'unknown';
  const lang = cachedCityData.language || 'en';
  
  // Use unified cache module
  cache.cacheCityHexContent(cityName, hexContentCache, lang);
}

/**
 * Load hex content cache from localStorage using unified cache
 */
export function loadHexContentCache(cityName, language) {
  const cached = cache.getCachedCityHexContent(cityName, language);
  if (cached) {
    hexContentCache = cached;
    return true;
  }
  return false;
}

/**
 * Get district data from city JSON by name
 */
export function getDistrictData(districtName, cityData) {
  if (!cityData || !cityData.districts) {
    return null;
  }
  
  const districts = cityData.districts;
  for (const district of districts) {
    if (district.name && district.name.toLowerCase() === districtName.toLowerCase()) {
      return district;
    }
  }
  return null;
}

/**
 * Weighted random choice
 */
function weightedChoice(weights) {
  const total = Object.values(weights).reduce((sum, w) => sum + w, 0);
  let random = Math.random() * total;
  
  for (const [item, weight] of Object.entries(weights)) {
    random -= weight;
    if (random <= 0) {
      return item;
    }
  }
  
  // Fallback to first item
  return Object.keys(weights)[0];
}

/**
 * Random choice from array
 */
function randomChoice(array) {
  if (!array || array.length === 0) {
    return null;
  }
  return array[Math.floor(Math.random() * array.length)];
}

/**
 * Select content type based on district data
 * After normalization, only check district data (no city-level arrays)
 */
export function selectContentType(districtData, cityData) {
  const contentWeights = {};
  
  // Check district data only (city-level arrays moved to districts)
  if (districtData.buildings && districtData.buildings.length > 0) {
    contentWeights.building = 0.25;
  }
  if (districtData.streets && districtData.streets.length > 0) {
    contentWeights.street = 0.15;
  }
  if (districtData.landmarks && districtData.landmarks.length > 0) {
    contentWeights.landmark = 0.15;
  }
  if (districtData.markets && districtData.markets.length > 0) {
    contentWeights.market = 0.15;
  }
  if (districtData.temples && districtData.temples.length > 0) {
    contentWeights.temple = 0.15;
  }
  if (districtData.taverns && districtData.taverns.length > 0) {
    contentWeights.tavern = 0.1;
  }
  if (districtData.guilds && districtData.guilds.length > 0) {
    contentWeights.guild = 0.05;
  }
  if (districtData.residences && districtData.residences.length > 0) {
    contentWeights.residence = 0.1;
  }
  if (districtData.ruins && districtData.ruins.length > 0) {
    contentWeights.ruins = 0.1;
  }
  
  // If no specific content types, default to district
  if (Object.keys(contentWeights).length === 0) {
    contentWeights.district = 1.0;
  }
  
  return weightedChoice(contentWeights);
}

/**
 * Get encounter pool for content type
 * Priority: district encounters → generic encounters
 * After normalization, no city-level encounters
 */
export function getEncounterPool(contentType, districtData, cityData, encounterTables) {
  const pool = [];
  
  // 1. District-specific encounters
  if (districtData && districtData.encounters) {
    // Encounters can be object with type keys or array
    if (typeof districtData.encounters === 'object' && !Array.isArray(districtData.encounters)) {
      const districtEncounters = districtData.encounters[contentType];
      if (Array.isArray(districtEncounters) && districtEncounters.length > 0) {
        pool.push(...districtEncounters);
      }
    } else if (Array.isArray(districtData.encounters) && districtData.encounters.length > 0) {
      // If encounters is array, use it for district type
      if (contentType === 'district') {
        pool.push(...districtData.encounters);
      }
    }
  }
  
  // 2. Generic encounters
  const genericKey = contentType === 'district' ? 'district' : contentType;
  const genericEncounters = encounterTables[genericKey];
  if (Array.isArray(genericEncounters) && genericEncounters.length > 0) {
    pool.push(...genericEncounters);
  }
  
  return pool;
}

/**
 * Select random encounter from pool
 */
export function selectEncounter(contentType, districtData, cityData, encounterTables) {
  const pool = getEncounterPool(contentType, districtData, cityData, encounterTables);
  
  if (pool.length > 0) {
    return randomChoice(pool);
  }
  
  // Fallback
  return "Unclear activity in the area";
}

/**
 * Find location type for a location name
 */
export function findLocationType(locationName, districtData) {
  if (!districtData || !locationName) {
    return null;
  }
  
  const locationLower = locationName.toLowerCase();
  const arrays = {
    building: districtData.buildings,
    street: districtData.streets,
    landmark: districtData.landmarks,
    market: districtData.markets,
    temple: districtData.temples,
    tavern: districtData.taverns,
    guild: districtData.guilds,
    residence: districtData.residences,
    ruins: districtData.ruins
  };
  
  for (const [type, arr] of Object.entries(arrays)) {
    if (Array.isArray(arr)) {
      for (const item of arr) {
        const itemName = typeof item === 'string' ? item : (item.name || String(item));
        if (itemName.toLowerCase() === locationLower) {
          return type;
        }
      }
    }
  }
  
  return null;
}

/**
 * Select specific location from district
 */
export function selectLocation(contentType, locationName, districtData) {
  if (!districtData || !locationName) {
    return null;
  }
  
  const locationLower = locationName.toLowerCase();
  const array = districtData[contentType + 's'];
  
  if (Array.isArray(array)) {
    for (const item of array) {
      const itemName = typeof item === 'string' ? item : (item.name || String(item));
      if (itemName.toLowerCase() === locationLower) {
        return item;
      }
    }
  }
  
  return null;
}

/**
 * Generate district content
 */
export function generateDistrictContent(districtData, cityData, encounterTables) {
  if (!districtData) {
    districtData = {};
  }
  
  const name = districtData.name || 'Unknown District';
  const description = districtData.description || 
    `A district where ${randomChoice(['the wealthy once lived', 'merchants once thrived', 'scholars once studied', 'the poor struggle to survive'])}.`;
  
  // Encounters
  const encounter = selectEncounter('district', districtData, cityData, encounterTables);
  
  // Atmosphere
  const atmospheres = districtData.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Dark and foreboding";
  
  // Random table
  const randomTables = districtData.random_tables || {};
  let randomTable = randomTables.district;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Mysterious activities",
      "3-4: Strange occurrences",
      "5-6: Unusual events"
    ];
  }
  
  // Notable features
  const notableFeatures = [];
  for (const contentType of ['buildings', 'streets', 'landmarks']) {
    const entries = districtData[contentType];
    if (Array.isArray(entries) && entries.length > 0) {
      const item = randomChoice(entries);
      if (item) {
        const itemName = typeof item === 'string' ? item : (item.name || String(item));
        notableFeatures.push(itemName);
      }
    }
  }
  
  if (notableFeatures.length === 0) {
    notableFeatures.push(
      randomChoice(["Crumbling mansions", "Narrow alleyways", "Ancient statues", "Broken fountains"]),
      randomChoice(["Abandoned shops", "Boarded windows", "Graffiti-covered walls", "Overgrown gardens"])
    );
  }
  
  return {
    name,
    description,
    encounter,
    atmosphere,
    random_table: randomTable,
    notable_features: notableFeatures,
    type: 'district'
  };
}

/**
 * Generate building content
 */
export function generateBuildingContent(districtData, cityData, encounterTables, specificBuilding = null) {
  // Get buildings from district data (after normalization, no city-level)
  let buildings = [];
  if (districtData && districtData.buildings) {
    buildings = districtData.buildings;
  }
  
  if (buildings.length === 0) {
    buildings = ["Unknown Building", "Abandoned Structure", "Mysterious Edifice"];
  }
  
  // Select building
  let name;
  if (specificBuilding) {
    const found = selectLocation('building', specificBuilding, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(buildings);
  } else {
    name = randomChoice(buildings);
  }
  
  // Purpose/description
  const purpose = randomChoice([
    "abandoned residence of a fallen noble",
    "mysterious workshop of unknown purpose",
    "forgotten library with forbidden knowledge",
    "ancient temple to a forgotten god",
    "guild headquarters for a secret organization",
    "warehouse full of strange artifacts"
  ]);
  
  const description = `An imposing structure that once served as ${purpose}.`;
  
  // Encounter
  const encounter = selectEncounter('building', districtData, cityData, encounterTables);
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Dark and foreboding";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.building;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Mysterious sounds",
      "3-4: Strange lights",
      "5-6: Unusual activity"
    ];
  }
  
  return {
    name,
    type: 'building',
    description,
    encounter,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate street content
 */
export function generateStreetContent(districtData, cityData, encounterTables, specificStreet = null) {
  // Get streets from district data
  let streets = [];
  if (districtData && districtData.streets) {
    streets = districtData.streets;
  }
  
  if (streets.length === 0) {
    streets = ["Unknown Street", "Narrow Alley", "Dark Path"];
  }
  
  // Select street
  let name;
  if (specificStreet) {
    const found = selectLocation('street', specificStreet, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(streets);
  } else {
    name = randomChoice(streets);
  }
  
  const description = `A ${randomChoice(['narrow', 'wide', 'winding', 'straight', 'cobbled', 'dirt'])} street through the district.`;
  
  // Encounter
  const encounter = selectEncounter('street', districtData, cityData, encounterTables);
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Dark and foreboding";
  
  // Threats
  const threats = [
    randomChoice(["Pickpockets", "Street gangs", "Corrupt guards", "Stray dogs"]),
    randomChoice(["Dark alleys", "Broken cobblestones", "Hidden dangers", "Unseen watchers"])
  ];
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.street;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Street activity",
      "3-4: Passing traffic",
      "5-6: Unusual events"
    ];
  }
  
  return {
    name,
    type: 'street',
    description,
    encounter,
    atmosphere,
    threats,
    random_table: randomTable
  };
}

/**
 * Generate landmark content
 */
export function generateLandmarkContent(districtData, cityData, encounterTables, specificLandmark = null) {
  // Get landmarks from district data
  let landmarks = [];
  if (districtData && districtData.landmarks) {
    landmarks = districtData.landmarks;
  }
  
  if (landmarks.length === 0) {
    landmarks = ["Unknown Landmark", "Ancient Monument", "Mysterious Site"];
  }
  
  // Select landmark
  let name;
  if (specificLandmark) {
    const found = selectLocation('landmark', specificLandmark, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(landmarks);
  } else {
    name = randomChoice(landmarks);
  }
  
  const description = `A ${randomChoice(['significant', 'ancient', 'mysterious', 'forgotten', 'sacred', 'cursed'])} landmark in the district.`;
  
  // Encounter
  const encounter = selectEncounter('landmark', districtData, cityData, encounterTables);
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Dark and foreboding";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.landmark;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Landmark significance",
      "3-4: Historical events",
      "5-6: Mysterious properties"
    ];
  }
  
  return {
    name,
    type: 'landmark',
    description,
    encounter,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate market content
 */
export function generateMarketContent(districtData, cityData, encounterTables, specificMarket = null) {
  // Get markets from district data
  let markets = [];
  if (districtData && districtData.markets) {
    markets = districtData.markets;
  }
  
  if (markets.length === 0) {
    markets = ["Unknown Market", "Trading Post", "Merchant Square"];
  }
  
  // Select market
  let name;
  if (specificMarket) {
    const found = selectLocation('market', specificMarket, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(markets);
  } else {
    name = randomChoice(markets);
  }
  
  const description = `A bustling market where ${randomChoice(['merchants', 'traders', 'vendors', 'dealers'])} gather to trade.`;
  
  // Encounter
  const encounter = selectEncounter('market', districtData, cityData, encounterTables);
  
  // Market specialty
  const marketSpecialty = randomChoice([
    "Soul trading",
    "Bone exchange",
    "Corpse parts",
    "Mysterious artifacts",
    "Forbidden knowledge",
    "Strange substances"
  ]);
  
  // Items sold
  const itemsSold = [
    randomChoice(["Weapons", "Armor", "Potions", "Scrolls"]),
    randomChoice(["Food", "Clothing", "Tools", "Supplies"])
  ];
  
  // Services
  const services = [
    randomChoice(["Information", "Repairs", "Appraisals", "Smuggling"])
  ];
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Busy and crowded";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.market;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Market activity",
      "3-4: Trading deals",
      "5-6: Unusual wares"
    ];
  }
  
  return {
    name,
    type: 'market',
    description,
    encounter,
    market_specialty: marketSpecialty,
    items_sold: itemsSold,
    services,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate temple content
 */
export function generateTempleContent(districtData, cityData, encounterTables, specificTemple = null) {
  // Get temples from district data
  let temples = [];
  if (districtData && districtData.temples) {
    temples = districtData.temples;
  }
  
  if (temples.length === 0) {
    temples = ["Unknown Temple", "Sacred Shrine", "Holy Site"];
  }
  
  // Select temple
  let name;
  if (specificTemple) {
    const found = selectLocation('temple', specificTemple, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(temples);
  } else {
    name = randomChoice(temples);
  }
  
  const description = `A ${randomChoice(['sacred', 'ancient', 'forgotten', 'dark', 'cursed'])} temple dedicated to ${randomChoice(['the gods', 'ancient powers', 'forbidden deities', 'dark forces'])}.`;
  
  // Encounter
  const encounter = selectEncounter('temple', districtData, cityData, encounterTables);
  
  // Temple deity
  const templeDeity = randomChoice([
    "The Two-Headed Basilisks",
    "Bone Collection",
    "Final Judgement",
    "Beautiful Endings",
    "The Old One",
    "The Yellow Blob"
  ]);
  
  // Rituals
  const rituals = [
    randomChoice(["Sacrifice ceremonies", "Dark rituals", "Prayer sessions", "Offering rites"])
  ];
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Sacred and foreboding";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.temple;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Religious ceremonies",
      "3-4: Sacred rituals",
      "5-6: Divine intervention"
    ];
  }
  
  return {
    name,
    type: 'temple',
    description,
    encounter,
    temple_deity: templeDeity,
    rituals,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate tavern content
 */
export function generateTavernContent(districtData, cityData, encounterTables, specificTavern = null) {
  // Get taverns from district data
  let taverns = [];
  if (districtData && districtData.taverns) {
    taverns = districtData.taverns;
  }
  
  if (taverns.length === 0) {
    taverns = ["Unknown Tavern", "The Rusty Mug", "The Drunken Sailor"];
  }
  
  // Select tavern
  let name;
  if (specificTavern) {
    const found = selectLocation('tavern', specificTavern, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(taverns);
  } else {
    name = randomChoice(taverns);
  }
  
  const description = `A ${randomChoice(['rowdy', 'quiet', 'dangerous', 'welcoming', 'seedy'])} tavern where ${randomChoice(['travelers', 'locals', 'merchants', 'thieves'])} gather.`;
  
  // Encounter
  const encounter = selectEncounter('tavern', districtData, cityData, encounterTables);
  
  // Tavern menu
  const tavernMenu = randomChoice([
    "Chunky stew and hearty ale",
    "Mysterious meat pies",
    "Questionable food and drink",
    "Simple fare and local brew"
  ]);
  
  // Innkeeper
  const tavernInnkeeper = randomChoice([
    "A wary innkeeper",
    "A friendly host",
    "A suspicious proprietor",
    "A grizzled barkeep"
  ]);
  
  // Patron
  const tavernPatron = randomChoice([
    "Desperate travelers",
    "Local regulars",
    "Suspicious characters",
    "Merchants and traders"
  ]);
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Warm and inviting";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.tavern;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Tavern activity",
      "3-4: Local gossip",
      "5-6: Unusual patrons"
    ];
  }
  
  return {
    name,
    type: 'tavern',
    description,
    encounter,
    tavern_menu: tavernMenu,
    tavern_innkeeper: tavernInnkeeper,
    tavern_patron: tavernPatron,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate guild content
 */
export function generateGuildContent(districtData, cityData, encounterTables, specificGuild = null) {
  // Get guilds from district data
  let guilds = [];
  if (districtData && districtData.guilds) {
    guilds = districtData.guilds;
  }
  
  if (guilds.length === 0) {
    guilds = ["Unknown Guild", "Mysterious Organization", "Secret Society"];
  }
  
  // Select guild
  let name;
  if (specificGuild) {
    const found = selectLocation('guild', specificGuild, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(guilds);
  } else {
    name = randomChoice(guilds);
  }
  
  const description = `A ${randomChoice(['powerful', 'secret', 'ancient', 'corrupt', 'mysterious'])} guild that ${randomChoice(['controls trade', 'enforces laws', 'gathers information', 'performs rituals'])}.`;
  
  // Encounter
  const encounter = selectEncounter('guild', districtData, cityData, encounterTables);
  
  // Guild purpose
  const guildPurpose = randomChoice([
    "Trade and commerce",
    "Law enforcement",
    "Information gathering",
    "Religious activities",
    "Criminal operations"
  ]);
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Organized and structured";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.guild;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Guild activities",
      "3-4: Member meetings",
      "5-6: Secret operations"
    ];
  }
  
  return {
    name,
    type: 'guild',
    description,
    encounter,
    guild_purpose: guildPurpose,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate residence content
 */
export function generateResidenceContent(districtData, cityData, encounterTables, specificResidence = null) {
  // Get residences from district data
  let residences = [];
  if (districtData && districtData.residences) {
    residences = districtData.residences;
  }
  
  if (residences.length === 0) {
    residences = ["Unknown Residence", "Abandoned House", "Mysterious Dwelling"];
  }
  
  // Select residence
  let name;
  if (specificResidence) {
    const found = selectLocation('residence', specificResidence, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(residences);
  } else {
    name = randomChoice(residences);
  }
  
  const description = `A ${randomChoice(['noble', 'common', 'abandoned', 'mysterious', 'cursed'])} residence where ${randomChoice(['a wealthy family', 'common folk', 'nobles', 'strange inhabitants'])} once lived.`;
  
  // Encounter
  const encounter = selectEncounter('residence', districtData, cityData, encounterTables);
  
  // Residence inhabitants
  const residenceInhabitants = randomChoice([
    "A fallen noble family",
    "Common citizens",
    "Mysterious occupants",
    "Abandoned and empty"
  ]);
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Quiet and still";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.residence;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Residence activity",
      "3-4: Inhabitant presence",
      "5-6: Unusual occurrences"
    ];
  }
  
  return {
    name,
    type: 'residence',
    description,
    encounter,
    residence_inhabitants: residenceInhabitants,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate ruins content
 */
export function generateRuinsContent(districtData, cityData, encounterTables, specificRuin = null) {
  // Get ruins from district data
  let ruins = [];
  if (districtData && districtData.ruins) {
    ruins = districtData.ruins;
  }
  
  if (ruins.length === 0) {
    ruins = ["Unknown Ruins", "Collapsed Structure", "Ancient Remains"];
  }
  
  // Select ruin
  let name;
  if (specificRuin) {
    const found = selectLocation('ruins', specificRuin, districtData);
    name = found ? (typeof found === 'string' ? found : (found.name || String(found))) : randomChoice(ruins);
  } else {
    name = randomChoice(ruins);
  }
  
  const description = `The ${randomChoice(['collapsed', 'shattered', 'ancient', 'forgotten', 'cursed'])} remains of what was once ${randomChoice(['a great structure', 'a noble building', 'a sacred site', 'a powerful place'])}.`;
  
  // Encounter
  const encounter = selectEncounter('ruins', districtData, cityData, encounterTables);
  
  // Atmosphere
  const atmospheres = districtData?.atmosphere_modifiers || [];
  const atmosphere = randomChoice(atmospheres) || "Decayed and dangerous";
  
  // Random table
  const randomTables = districtData?.random_tables || {};
  let randomTable = randomTables.ruins;
  if (!randomTable || !Array.isArray(randomTable)) {
    randomTable = [
      "1-2: Ruin hazards",
      "3-4: Ancient dangers",
      "5-6: Collapsed structures"
    ];
  }
  
  return {
    name,
    type: 'ruins',
    description,
    encounter,
    atmosphere,
    random_table: randomTable
  };
}

/**
 * Generate district-based content
 */
export function generateDistrictBasedContent(districtName, cityData, encounterTables) {
  const districtData = getDistrictData(districtName, cityData);
  
  if (!districtData) {
    // Fallback to default district content
    return generateDistrictContent({ name: districtName || 'Unknown District' }, cityData, encounterTables);
  }
  
  // Select content type
  const contentType = selectContentType(districtData, cityData);
  
  // Generate content based on type
  switch (contentType) {
    case 'building':
      return generateBuildingContent(districtData, cityData, encounterTables);
    case 'street':
      return generateStreetContent(districtData, cityData, encounterTables);
    case 'landmark':
      return generateLandmarkContent(districtData, cityData, encounterTables);
    case 'market':
      return generateMarketContent(districtData, cityData, encounterTables);
    case 'temple':
      return generateTempleContent(districtData, cityData, encounterTables);
    case 'tavern':
      return generateTavernContent(districtData, cityData, encounterTables);
    case 'guild':
      return generateGuildContent(districtData, cityData, encounterTables);
    case 'residence':
      return generateResidenceContent(districtData, cityData, encounterTables);
    case 'ruins':
      return generateRuinsContent(districtData, cityData, encounterTables);
    case 'district':
    default:
      return generateDistrictContent(districtData, cityData, encounterTables);
  }
}

/**
 * Main content generation function
 * Generates all hex content based on hexId and options
 */
export function generateHexContent(hexId, cityData, encounterTables, options = {}) {
  // Parse hexId to get row and col
  const parts = hexId.split('_');
  if (parts.length !== 2) {
    throw new Error(`Invalid hexId format: ${hexId}`);
  }
  
  const row = parseInt(parts[0], 10);
  const col = parseInt(parts[1], 10);
  
  if (isNaN(row) || isNaN(col)) {
    throw new Error(`Invalid hexId format: ${hexId}`);
  }
  
  // Get district from district_matrix
  const districtMatrix = cityData.district_matrix || [];
  let districtName = '';
  if (row < districtMatrix.length && col < districtMatrix[row].length) {
    districtName = districtMatrix[row][col] || '';
  }
  
  // Get district data
  const districtData = districtName ? getDistrictData(districtName, cityData) : null;
  
  // Handle regenerateEncounter option
  if (options.regenerateEncounter && options.existingContent) {
    const existingContent = options.existingContent;
    const newEncounter = selectEncounter(existingContent.type, districtData, cityData, encounterTables);
    return {
      ...existingContent,
      encounter: newEncounter
    };
  }
  
  // Handle locationName option
  if (options.locationName && districtData) {
    const locationType = findLocationType(options.locationName, districtData);
    if (locationType) {
      switch (locationType) {
        case 'building':
          return generateBuildingContent(districtData, cityData, encounterTables, options.locationName);
        case 'street':
          return generateStreetContent(districtData, cityData, encounterTables, options.locationName);
        case 'landmark':
          return generateLandmarkContent(districtData, cityData, encounterTables, options.locationName);
        case 'market':
          return generateMarketContent(districtData, cityData, encounterTables, options.locationName);
        case 'temple':
          return generateTempleContent(districtData, cityData, encounterTables, options.locationName);
        case 'tavern':
          return generateTavernContent(districtData, cityData, encounterTables, options.locationName);
        case 'guild':
          return generateGuildContent(districtData, cityData, encounterTables, options.locationName);
        case 'residence':
          return generateResidenceContent(districtData, cityData, encounterTables, options.locationName);
        case 'ruins':
          return generateRuinsContent(districtData, cityData, encounterTables, options.locationName);
      }
    }
  }
  
  // Handle contentType option
  if (options.contentType && districtData) {
    switch (options.contentType) {
      case 'building':
        return generateBuildingContent(districtData, cityData, encounterTables);
      case 'street':
        return generateStreetContent(districtData, cityData, encounterTables);
      case 'landmark':
        return generateLandmarkContent(districtData, cityData, encounterTables);
      case 'market':
        return generateMarketContent(districtData, cityData, encounterTables);
      case 'temple':
        return generateTempleContent(districtData, cityData, encounterTables);
      case 'tavern':
        return generateTavernContent(districtData, cityData, encounterTables);
      case 'guild':
        return generateGuildContent(districtData, cityData, encounterTables);
      case 'residence':
        return generateResidenceContent(districtData, cityData, encounterTables);
      case 'ruins':
        return generateRuinsContent(districtData, cityData, encounterTables);
      case 'district':
        return generateDistrictContent(districtData, cityData, encounterTables);
    }
  }
  
  // Default: generate district-based content
  if (districtName && districtData) {
    return generateDistrictBasedContent(districtName, cityData, encounterTables);
  }
  
  // Fallback: generate default district content
  return generateDistrictContent({ name: 'Unknown District' }, cityData, encounterTables);
}

/**
 * Generate all hex content for a city at once
 * Returns a map of hexId -> content
 */
export function generateAllHexContent(cityData, encounterTables) {
  const districtMatrix = cityData.district_matrix || [];
  const allContent = {};
  
  for (let row = 0; row < districtMatrix.length; row++) {
    for (let col = 0; col < districtMatrix[row].length; col++) {
      const hexId = `${row}_${col}`;
      const districtName = districtMatrix[row][col] || '';
      
      // Skip empty hexes
      if (!districtName) {
        continue;
      }
      
      // Generate content for this hex
      const content = generateHexContent(hexId, cityData, encounterTables);
      allContent[hexId] = content;
    }
  }
  
  return allContent;
}

/**
 * Regenerate only encounter for existing content
 */
export function regenerateEncounter(hexContent, districtData, encounterTables) {
  if (!hexContent || !hexContent.type) {
    throw new Error('Invalid hex content');
  }
  
  const newEncounter = selectEncounter(hexContent.type, districtData, null, encounterTables);
  
  return {
    ...hexContent,
    encounter: newEncounter
  };
}

