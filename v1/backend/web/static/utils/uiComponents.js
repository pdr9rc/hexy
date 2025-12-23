// UI Components utility to reduce duplicate HTML generation
import { t } from './translationUtils.js';
export class UIComponents {
    static generateNavigationButtons(overlayName) {
        return `
      <div class="mb-4" style="text-align:center;">
        <button class="btn-mork-borg me-2" onclick="window.app.showHexDetails('${overlayName || ''}')">${t('return_to_hex')}</button>
        <button class="btn-mork-borg btn-warning" onclick="window.app.restoreMap()">${t('return_to_map')}</button>
      </div>
    `;
    }
    static generateBasicInfoSection(content, hexData) {
        const name = content.name || '?';
        const type = content.type || '?';
        const district = hexData.district || '?';
        const position = content.position_type || '?';
        return `
      <div class="ascii-section ascii-hex-title">
        <span>${name}</span>
      </div>
      <div class="ascii-section ascii-hex-type">
        <span>${t('type')}: ${type}</span>
      </div>
      <div class="ascii-section ascii-hex-district">
        <span>${t('district')}: ${district}</span>
      </div>
      <div class="ascii-section ascii-hex-position">
        <span>${t('position')}: ${position}</span>
      </div>
    `;
    }
    static generateDescriptionSection(content) {
        const description = content.description || '';
        const atmosphere = content.atmosphere || t('no_atmosphere');
        const encounter = content.encounter || '';
        return `
      <div class="ascii-section ascii-hex-description">
        <span>${t('description')}:</span>
        <div class="ascii-content">${description}</div>
      </div>
      <div class="ascii-section ascii-hex-atmosphere">
        <span>${t('atmosphere')}:</span>
        <div class="ascii-content">${atmosphere}</div>
      </div>
      <div class="ascii-section ascii-hex-encounter">
        <span>${t('encounter')}:</span>
        <div class="ascii-content">${encounter}</div>
      </div>
    `;
    }
    static generateFeaturesSection(content) {
        if (!content.notable_features || content.notable_features.length === 0) {
            return '';
        }
        return `
      <div class="ascii-section ascii-hex-features">
        <span>${t('notable_features')}:</span>
        <div class="ascii-content">${content.notable_features.join('\n')}</div>
      </div>
    `;
    }
    static generateNPCSection(content) {
        const hasNPCData = content.npc_trait || content.npc_concern || content.npc_want ||
            content.npc_secret || content.npc_name || content.npc_trade ||
            content.npc_affiliation || content.npc_attitude;
        if (!hasNPCData) {
            return '';
        }
        let npcContent = '';
        if (content.npc_name)
            npcContent += `${t('name')}: ${content.npc_name}\n`;
        if (content.npc_trade)
            npcContent += `${t('trade')}: ${content.npc_trade}\n`;
        if (content.npc_trait)
            npcContent += `${t('trait')}: ${content.npc_trait}\n`;
        if (content.npc_concern)
            npcContent += `${t('concern')}: ${content.npc_concern}\n`;
        if (content.npc_want)
            npcContent += `${t('want')}: ${content.npc_want}\n`;
        if (content.npc_secret)
            npcContent += `${t('secret')}: ${content.npc_secret}\n`;
        if (content.npc_affiliation)
            npcContent += `${t('affiliation')}: ${content.npc_affiliation}\n`;
        if (content.npc_attitude)
            npcContent += `${t('attitude')}: ${content.npc_attitude}\n`;
        return `
      <div class="ascii-section ascii-hex-npcs">
        <span>${t('npc_information')}:</span>
        <div class="ascii-content">${npcContent}</div>
      </div>
    `;
    }
    static generateTavernSection(content) {
        if (content.type !== 'tavern' || (!content.tavern_menu && !content.tavern_innkeeper && !content.tavern_patron)) {
            return '';
        }
        let tavernContent = '';
        if (content.tavern_menu)
            tavernContent += `${t('menu')}: ${content.tavern_menu}\n`;
        if (content.tavern_innkeeper)
            tavernContent += `${t('innkeeper')}: ${content.tavern_innkeeper}\n`;
        if (content.tavern_patron)
            tavernContent += `${t('notable_patron')}: ${content.tavern_patron}\n`;
        return `
      <div class="ascii-section ascii-hex-tavern">
        <span>${t('tavern_details')}:</span>
        <div class="ascii-content">${tavernContent}</div>
      </div>
    `;
    }
    static generateMarketSection(content) {
        if (content.type !== 'market' || (!content.items_sold && !content.beast_prices && !content.services)) {
            return '';
        }
        let marketContent = '';
        if (content.items_sold)
            marketContent += `${t('items_sold')}: ${content.items_sold}\n`;
        if (content.beast_prices)
            marketContent += `${t('beast_prices')}: ${content.beast_prices}\n`;
        if (content.services)
            marketContent += `${t('services')}: ${content.services}\n`;
        return `
      <div class="ascii-section ascii-hex-market">
        <span>${t('market_details')}:</span>
        <div class="ascii-content">${marketContent}</div>
      </div>
    `;
    }
    static generateHexDetailsView(hexData, overlayName) {
        const content = hexData.content || {};
        return `
      <div class="city-hex-details-box">
        <div class="ascii-box">
          <div class="ascii-inner-box">
            ${this.generateNavigationButtons(overlayName)}
            ${this.generateBasicInfoSection(content, hexData)}
            ${this.generateDescriptionSection(content)}
            ${this.generateFeaturesSection(content)}
            ${this.generateNPCSection(content)}
            ${this.generateTavernSection(content)}
            ${this.generateMarketSection(content)}
          </div>
        </div>
      </div>
    `;
    }
    static generateCityContextSection(context) {
        let html = `
      <div class="ascii-section ascii-city-title">
        <span>${context.name}</span>
      </div>
      <div class="ascii-section ascii-city-description">
        <span>${t('city_description')}:</span>
        <div class="ascii-content">${context.description}</div>
      </div>
    `;
        const cityEvents = context.city_events ?? [];
        if (cityEvents.length > 0) {
            html += `
        <div class="ascii-section ascii-city-events">
          <span>${t('city_events')}:</span>
          <div class="ascii-content">${cityEvents.slice(0, 3).join('\n')}</div>
        </div>
      `;
        }
        const weatherConditions = context.weather_conditions ?? [];
        if (weatherConditions.length > 0) {
            html += `
        <div class="ascii-section ascii-city-weather">
          <span>${t('weather')}:</span>
          <div class="ascii-content">${weatherConditions.slice(0, 2).join('\n')}</div>
        </div>
      `;
        }
        const regionalNpcs = context.regional_npcs ?? [];
        if (regionalNpcs.length > 0) {
            html += `
        <div class="ascii-section ascii-city-npcs">
          <span>${t('regional_npcs')}:</span>
          <div class="ascii-content">${regionalNpcs.slice(0, 3).join('\n')}</div>
        </div>
      `;
        }
        return html;
    }
    static generateFactionSection(factions, title) {
        if (!factions || factions.length === 0) {
            return '';
        }
        let html = `
      <div class="ascii-section ascii-city-factions">
        <span>${title}:</span>
        <div class="ascii-content">
    `;
        for (const faction of factions.slice(0, 3)) {
            html += `• ${faction.name}\n`;
            html += `  ${t('leader')}: ${faction.leader}\n`;
            html += `  ${t('hq')}: ${faction.headquarters}\n`;
            html += `  ${t('influence')}: ${faction.influence}\n`;
            html += `  ${t('attitude')}: ${faction.attitude}\n`;
            const activities = faction.activities ?? [];
            if (activities.length > 0) {
                html += `  ${t('activities')}: ${activities.slice(0, 2).join(', ')}\n`;
            }
            html += '\n';
        }
        html += `
        </div>
      </div>
    `;
        return html;
    }
}
