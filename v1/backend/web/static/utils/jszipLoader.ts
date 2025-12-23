// Provides a robust way to obtain a JSZip instance in our non-bundled ES module setup.
// Tries ESM import, then window.JSZip, then injects vendor script.

let cachedJsZip: any = null;

export async function ensureJsZip(): Promise<any> {
  if (cachedJsZip) return cachedJsZip;
  try {
    const mod = await import('jszip');
    cachedJsZip = (mod as any).default || mod;
    return cachedJsZip;
  } catch (_) {}

  const w: any = window as any;
  if (w && w.JSZip) {
    cachedJsZip = w.JSZip;
    return cachedJsZip;
  }

  try {
    cachedJsZip = await new Promise<any>((resolve, reject) => {
      const existing = document.getElementById('jszip-lib');
      if (existing) {
        const win: any = window as any;
        return resolve(win.JSZip || null);
      }
      const s = document.createElement('script');
      s.id = 'jszip-lib';
      s.async = true;
      s.src = 'static/vendor/jszip.min.js';
      s.onload = () => {
        const win: any = window as any;
        resolve(win.JSZip || null);
      };
      s.onerror = () => reject(new Error('Failed to load jszip vendor'));
      document.head.appendChild(s);
    });
  } catch (_) {
    cachedJsZip = null;
  }
  return cachedJsZip;
}


