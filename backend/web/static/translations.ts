// Frontend translations for The Dying Lands
export interface Translations {
  [key: string]: {
    en: string;
    pt: string;
  };
}

export const translations: Translations = {
  // City context labels
  'CITY DESCRIPTION': {
    en: 'CITY DESCRIPTION:',
    pt: 'DESCRIÇÃO DA CIDADE:'
  },
  'CITY EVENTS': {
    en: 'CITY EVENTS:',
    pt: 'EVENTOS DA CIDADE:'
  },
  'WEATHER': {
    en: 'WEATHER:',
    pt: 'CLIMA:'
  },
  'REGIONAL NPCS': {
    en: 'REGIONAL NPCS:',
    pt: 'NPCs REGIONAIS:'
  },
  'MAJOR FACTIONS': {
    en: 'MAJOR FACTIONS:',
    pt: 'FACÇÕES PRINCIPAIS:'
  },
  'LOCAL FACTIONS': {
    en: 'LOCAL FACTIONS:',
    pt: 'FACÇÕES LOCAIS:'
  },
  'CRIMINAL FACTIONS': {
    en: 'CRIMINAL FACTIONS:',
    pt: 'FACÇÕES CRIMINOSAS:'
  },
  'MAJOR LANDMARKS': {
    en: 'MAJOR LANDMARKS:',
    pt: 'MARCO PRINCIPAL:'
  },
  'CITY DISTRICTS': {
    en: 'CITY DISTRICTS:',
    pt: 'DISTRITOS DA CIDADE:'
  },
  'NOTABLE FEATURES': {
    en: 'NOTABLE FEATURES:',
    pt: 'CARACTERÍSTICAS NOTÁVEIS:'
  },
  'KEY NPCS': {
    en: 'KEY NPCS:',
    pt: 'NPCs CHAVE:'
  },
  'ACTIVE FACTIONS': {
    en: 'ACTIVE FACTIONS:',
    pt: 'FACÇÕES ATIVAS:'
  },
  'DISTRICTS': {
    en: 'DISTRICTS:',
    pt: 'DISTRITOS:'
  },
  'LOCATION': {
    en: 'LOCATION:',
    pt: 'LOCALIZAÇÃO:'
  },
  'POPULATION': {
    en: 'POPULATION:',
    pt: 'POPULAÇÃO:'
  },
  'ATMOSPHERE': {
    en: 'ATMOSPHERE:',
    pt: 'ATMOSFERA:'
  },
  'DESCRIPTION': {
    en: 'DESCRIPTION:',
    pt: 'DESCRIÇÃO:'
  },
  'ENCOUNTER': {
    en: 'ENCOUNTER:',
    pt: 'ENCONTRO:'
  },
  'TYPE': {
    en: 'TYPE:',
    pt: 'TIPO:'
  },
  'DISTRICT': {
    en: 'DISTRICT:',
    pt: 'DISTRITO:'
  },
  'POSITION': {
    en: 'POSITION:',
    pt: 'POSIÇÃO:'
  },
  'RANDOM ENCOUNTERS': {
    en: 'RANDOM ENCOUNTERS:',
    pt: 'ENCONTROS ALEATÓRIOS:'
  },
  'MARKET DETAILS': {
    en: 'MARKET DETAILS:',
    pt: 'DETALHES DO MERCADO:'
  },
  'ITEMS SOLD': {
    en: 'ITEMS SOLD:',
    pt: 'ITENS VENDIDOS:'
  },
  'BEAST PRICES': {
    en: 'BEAST PRICES:',
    pt: 'PREÇOS DE BESTAS:'
  },
  'SERVICES': {
    en: 'SERVICES:',
    pt: 'SERVIÇOS:'
  },
  'PATRONS': {
    en: 'PATRONS:',
    pt: 'CLIENTES:'
  },
  'RETURN TO HEX': {
    en: 'RETURN TO HEX',
    pt: 'VOLTAR AO HEX'
  },
  'RETURN TO MAP': {
    en: 'RETURN TO MAP',
    pt: 'VOLTAR AO MAPA'
  },
  'EDIT': {
    en: 'EDIT',
    pt: 'EDITAR'
  },
  'SAVE': {
    en: 'SAVE',
    pt: 'SALVAR'
  },
  'CANCEL': {
    en: 'CANCEL',
    pt: 'CANCELAR'
  },
  'LORE': {
    en: 'LORE',
    pt: 'HISTÓRIA'
  },
  'RESET': {
    en: 'RESET',
    pt: 'REINICIAR'
  },
  'ENRICHED CONTENT': {
    en: 'ENRICHED CONTENT:',
    pt: 'CONTEÚDO ENRIQUECIDO:'
  },
  'CITY EVENT': {
    en: 'CITY EVENT:',
    pt: 'EVENTO DA CIDADE:'
  },
  'NPC INFORMATION': {
    en: 'NPC INFORMATION:',
    pt: 'INFORMAÇÕES DO NPC:'
  },
  'TAVERN DETAILS': {
    en: 'TAVERN DETAILS:',
    pt: 'DETALHES DA TAVERNA:'
  },
  'NAME': {
    en: 'NAME:',
    pt: 'NOME:'
  },
  'TRADE': {
    en: 'TRADE:',
    pt: 'OFÍCIO:'
  },
  'TRAIT': {
    en: 'TRAIT:',
    pt: 'CARACTERÍSTICA:'
  },
  'CONCERN': {
    en: 'CONCERN:',
    pt: 'PREOCUPAÇÃO:'
  },
  'WANT': {
    en: 'WANT:',
    pt: 'DESEJO:'
  },
  'SECRET': {
    en: 'SECRET:',
    pt: 'SEGREDO:'
  },
  'AFFILIATION': {
    en: 'AFFILIATION:',
    pt: 'AFILIAÇÃO:'
  },
  'ATTITUDE': {
    en: 'ATTITUDE:',
    pt: 'ATITUDE:'
  },
  'MENU': {
    en: 'MENU:',
    pt: 'CARDÁPIO:'
  },
  'INNKEEPER': {
    en: 'INNKEEPER:',
    pt: 'ESTALAJADEIRO:'
  },
  'NOTABLE PATRON': {
    en: 'NOTABLE PATRON:',
    pt: 'CLIENTE NOTÁVEL:'
  },
  'LOCAL TAVERN': {
    en: 'LOCAL TAVERN:',
    pt: 'TAVERNA LOCAL:'
  },
  'LOCAL POWER': {
    en: 'LOCAL POWER:',
    pt: 'PODER LOCAL:'
  },
  'SETTLEMENT LAYOUT': {
    en: 'SETTLEMENT LAYOUT:',
    pt: 'LAYOUT DO ASSENTAMENTO:'
  },
  'SELECT MENU': {
    en: 'SELECT MENU:',
    pt: 'CARDÁPIO SELECIONADO:'
  },
  'BUDGET MENU': {
    en: 'BUDGET MENU:',
    pt: 'CARDÁPIO ECONÔMICO:'
  }
};

// Get current language from localStorage or default to 'en'
export function getCurrentLanguage(): string {
  return localStorage.getItem('language') || 'en';
}

// Translate a key to the current language
export function t(key: string): string {
  const language = getCurrentLanguage();
  const translation = translations[key];
  if (!translation) {
    console.warn(`Translation missing for key: ${key}`);
    return key;
  }
  return translation[language as keyof typeof translation] || key;
}

// Set language and update localStorage
export function setLanguage(language: string): void {
  localStorage.setItem('language', language);
  // Trigger a page reload to update all translations
  window.location.reload();
}
