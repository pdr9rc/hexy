// Provides a robust way to obtain a JSZip instance in our non-bundled ES module setup.
// Tries ESM import, then window.JSZip, then injects vendor script.
let cachedJsZip = null;
export async function ensureJsZip() {
    if (cachedJsZip)
        return cachedJsZip;
    try {
        const mod = await import('jszip');
        cachedJsZip = mod.default || mod;
        return cachedJsZip;
    }
    catch (_) { }
    const w = window;
    if (w && w.JSZip) {
        cachedJsZip = w.JSZip;
        return cachedJsZip;
    }
    try {
        cachedJsZip = await new Promise((resolve, reject) => {
            const existing = document.getElementById('jszip-lib');
            if (existing) {
                const win = window;
                return resolve(win.JSZip || null);
            }
            const s = document.createElement('script');
            s.id = 'jszip-lib';
            s.async = true;
            s.src = 'static/vendor/jszip.min.js';
            s.onload = () => {
                const win = window;
                resolve(win.JSZip || null);
            };
            s.onerror = () => reject(new Error('Failed to load jszip vendor'));
            document.head.appendChild(s);
        });
    }
    catch (_) {
        cachedJsZip = null;
    }
    return cachedJsZip;
}
