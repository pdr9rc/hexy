// Language selector utility
// Import as any to avoid needing declaration files (use dynamic import type)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const translationManager: any = (window as any).translationManager || (await import(/* webpackIgnore: true */ './translationUtils.js')).translationManager;
export const availableLanguages = [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'pt', name: 'Portuguese', nativeName: 'Português' }
];
export class LanguageSelector {
    private static _instance: LanguageSelector | null = null;
    private _currentLanguage: string;
    constructor() {
        this._currentLanguage = 'en';
        this.loadSavedLanguage();
    }
    static getInstance(): LanguageSelector {
        if (!LanguageSelector._instance) {
            LanguageSelector._instance = new LanguageSelector();
        }
        return LanguageSelector._instance;
    }
    loadSavedLanguage() {
        const savedLanguage = localStorage.getItem('hexy-language');
        if (savedLanguage && availableLanguages.some(lang => lang.code === savedLanguage)) {
            this._currentLanguage = savedLanguage;
            translationManager.setLanguage(savedLanguage).catch((error: unknown) => {
                console.warn('Failed to set saved language:', error);
            });
        }
    }
    getCurrentLanguage(): string {
        return this._currentLanguage;
    }
    async setLanguage(languageCode: string) {
        if (!availableLanguages.some(lang => lang.code === languageCode)) {
            console.warn(`Language ${languageCode} not supported`);
            return;
        }
        this._currentLanguage = languageCode;
        localStorage.setItem('hexy-language', languageCode);
        // Update translation manager
        await translationManager.setLanguage(languageCode);
        // Reload the page to apply translations
        window.location.reload();
    }
    createLanguageSelector() {
        const container = document.createElement('div');
        container.className = 'language-selector';
        container.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 1000;
      background: rgba(0, 0, 0, 0.8);
      padding: 10px;
      border-radius: 5px;
      border: 1px solid #666;
    `;
        const label = document.createElement('label');
        label.textContent = 'Language / Idioma:';
        label.style.cssText = `
      color: #fff;
      font-size: 12px;
      margin-right: 10px;
    `;
        const select = document.createElement('select');
        select.style.cssText = `
      background: #333;
      color: #fff;
      border: 1px solid #666;
      padding: 5px;
      border-radius: 3px;
      font-size: 12px;
    `;
        availableLanguages.forEach(language => {
            const option = document.createElement('option');
            option.value = language.code;
            option.textContent = `${language.name} / ${language.nativeName}`;
            if (language.code === this._currentLanguage) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        select.addEventListener('change', async (e: Event) => {
            const target = e.target as HTMLSelectElement | null;
            if (target) {
                await this.setLanguage(target.value);
            }
        });
        container.appendChild(label);
        container.appendChild(select);
        return container;
    }
    injectLanguageSelector() {
        try {
            // Remove existing language selector if present
            const existing = document.querySelector('.language-selector');
            if (existing) {
                existing.remove();
            }
            // Wait a bit for the page to be ready
            setTimeout(() => {
                // Add new language selector
                const selector = this.createLanguageSelector();
                document.body.appendChild(selector);
                console.log('🌐 Language selector injected successfully');
            }, 100);
        }
        catch (error: unknown) {
            console.error('Failed to inject language selector:', error);
        }
    }
}
// Export singleton instance
export const languageSelector = LanguageSelector.getInstance();
