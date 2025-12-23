"""
City helper utilities for managing fallback content and city data processing.
"""
import random
from typing import Dict, Any, List, Optional


def create_fallback_district_data(
    city_data: Optional[Dict[str, Any]], 
    get_city_content_list_func,
    get_city_encounters_func,
    get_city_atmospheres_func,
    get_city_random_table_func,
    generate_district_random_table_func,
    fallback_content: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Create fallback district data when specific district information is not available.
    
    Args:
        city_data: City data dictionary
        get_city_content_list_func: Function to get city content list
        get_city_encounters_func: Function to get city encounters
        get_city_atmospheres_func: Function to get city atmospheres
        get_city_random_table_func: Function to get city random table
        generate_district_random_table_func: Function to generate district random table
        fallback_content: Optional pre-loaded fallback content from data tables
        
    Returns:
        Dictionary containing fallback district data
    """
    safe_content = fallback_content or {}
    districts = get_city_content_list_func(city_data, 'districts', safe_content.get('districts', []))
    encounters = get_city_encounters_func(city_data, 'district', safe_content.get('encounters', []))
    atmospheres = get_city_atmospheres_func(city_data, safe_content.get('atmospheres', []))
    descriptions = safe_content.get('descriptions', [])
    notable_features = safe_content.get('notable_features', [])
    district_descriptions = safe_content.get('district_descriptions', [])
    markets = safe_content.get('market_specialties', [])
    temples = safe_content.get('temple_deities', [])
    taverns = safe_content.get('tavern_descriptions', [])
    guilds = safe_content.get('guild_purposes', [])
    residences = safe_content.get('residence_inhabitants', [])
    
    random_table = get_city_random_table_func(city_data, 'district', generate_district_random_table_func)
    
    name = random.choice(districts) if districts else "Unknown District"
    encounter = random.choice(encounters) if encounters else "Unclear activity in the district"
    atmosphere = random.choice(atmospheres) if atmospheres else "Foreboding and tense"
    description_choices = district_descriptions or descriptions
    description = random.choice(description_choices) if description_choices else "A forgotten quarter of the city."
    feature_pool = notable_features if notable_features else []
    features = random.sample(feature_pool, k=min(2, len(feature_pool))) if feature_pool else []
    market = random.choice(markets) if markets else None
    temple = random.choice(temples) if temples else None
    tavern_desc = random.choice(taverns) if taverns else None
    guild_purpose = random.choice(guilds) if guilds else None
    residence = random.choice(residences) if residences else None
    
    return {
        'name': name,
        'description': description,
        'encounter': encounter,
        'atmosphere': atmosphere,
        'random_table': random_table,
        'notable_features': features,
        'market_specialty': market,
        'temple_deity': temple,
        'tavern_description': tavern_desc,
        'guild_purpose': guild_purpose,
        'residence_inhabitants': residence
    } 