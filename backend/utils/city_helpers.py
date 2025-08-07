"""
City helper utilities for managing fallback content and city data processing.
"""
import random
from typing import Dict, Any, List, Optional


def get_fallback_district_content() -> Dict[str, List[str]]:
    """
    Get fallback district content for city overlays when specific data is not available.
    
    Returns:
        Dictionary containing fallback lists for districts, encounters, and atmospheres
    """
    return {
        'districts': [
            "O Bairro dos Cadáveres", "Decadência dos Mercadores", "Os Mercados de Ossos", "Ala da Peste",
            "Os Jardins dos Enforcados", "Ruína dos Eruditos", "Paraíso dos Ladrões", "As Ruas Sangrentas",
            "Decadência dos Nobres", "Os Comuns Amaldiçoados"
        ],
        'encounters': [
            "Mendigos com peste pedindo esmolas", "Guardas corruptos exigindo subornos",
            "Figuras misteriosas em vestes negras", "Profeta louco gritando profecias",
            "Matilha de cães famintos", "Alma perdida vagando sem rumo"
        ],
        'atmospheres': [
            "Espesso com o fedor da decadência", "Crepúsculo perpétuo envolve as ruas",
            "Sussurros ecoam de prédios vazios", "Sombras se movem onde ninguém anda",
            "O ar tem gosto de cobre e medo", "Luzes estranhas piscam nas janelas"
        ]
    }


def create_fallback_district_data(
    city_data: Optional[Dict[str, Any]], 
    get_city_content_list_func,
    get_city_encounters_func,
    get_city_atmospheres_func,
    get_city_random_table_func,
    generate_district_random_table_func
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
        
    Returns:
        Dictionary containing fallback district data
    """
    fallback_content = get_fallback_district_content()
    
    districts = get_city_content_list_func(city_data, 'districts', fallback_content['districts'])
    encounters = get_city_encounters_func(city_data, 'district', fallback_content['encounters'])
    atmospheres = get_city_atmospheres_func(city_data, fallback_content['atmospheres'])
    random_table = get_city_random_table_func(city_data, 'district', generate_district_random_table_func)
    
    name = random.choice(districts)
    encounter = random.choice(encounters) if encounters else "Atividades misteriosas no bairro"
    atmosphere = random.choice(atmospheres) if atmospheres else "Sombrio e ameaçador"
    
    return {
        'name': name,
        'description': f"Um bairro onde {random.choice(['os ricos uma vez viveram', 'os mercadores uma vez prosperaram', 'os eruditos uma vez estudaram', 'os pobres lutam para sobreviver'])}.",
        'encounter': encounter,
        'atmosphere': atmosphere,
        'random_table': random_table,
        'notable_features': [
            random.choice(["Mansões em ruínas", "Becos estreitos", "Estatuas antigas", "Fontes quebradas"]),
            random.choice(["Lojas abandonadas", "Janelas tapadas", "Paredes com grafites", "Jardins abandonados"])
        ]
    } 