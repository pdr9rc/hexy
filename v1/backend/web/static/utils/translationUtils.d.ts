declare module 'translationUtils_js' {
  export const translationManager: {
    setLanguage: (lang: string) => void;
    getCurrentLanguage: () => string;
    t: (key: string, fallback?: string) => string;
  };
  export const t: (key: string, fallback?: string) => string;
}


