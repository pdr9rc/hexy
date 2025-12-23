// Frontend translations for The Dying Lands
// This file now imports from the unified translation system
import { translationManager } from './utils/translationUtils.js';

export interface Translations {
  [key: string]: {
    en: string;
    pt: string;
  };
}

// Legacy support - this is now powered by the unified translation system
export const translations: Translations = {};

// Get current language from localStorage or default to 'en'
export function getCurrentLanguage(): string {
  return localStorage.getItem('language') || localStorage.getItem('hexy-language') || 'en';
}

// Translate a key to the current language - now uses unified translation system
export function t(key: string, fallback?: string): string {
  return translationManager.t(key, fallback);
}

// Set language and update localStorage
export function setLanguage(language: string): void {
  localStorage.setItem('language', language);
  localStorage.setItem('hexy-language', language);
  
  // Update the translation manager
  translationManager.setLanguage(language).then(() => {
    // Trigger a page reload to update all translations
    window.location.reload();
  }).catch(error => {
    console.warn('Failed to set language:', error);
    window.location.reload();
  });
}
