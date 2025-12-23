// web/static/utils/sandboxStore.ts
// Lightweight client-side sandbox store using IndexedDB + localStorage
const DB_NAME = 'hexy-sandbox-v1';
const DB_VERSION = 1;
const STORE_META = 'meta';
const STORE_HEX = 'hex';
let dbPromise = null;
function openDb() {
    if (dbPromise)
        return dbPromise;
    dbPromise = new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = () => {
            const db = req.result;
            if (!db.objectStoreNames.contains(STORE_META)) {
                db.createObjectStore(STORE_META);
            }
            if (!db.objectStoreNames.contains(STORE_HEX)) {
                db.createObjectStore(STORE_HEX, { keyPath: 'hexCode' });
            }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
    });
    return dbPromise;
}
function generateId() {
    try {
        const bytes = new Uint8Array(16);
        crypto.getRandomValues(bytes);
        return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
    }
    catch (_) {
        // Fallback
        return String(Date.now()) + Math.random().toString(16).slice(2);
    }
}
export function getSandboxId() {
    try {
        const key = 'hexy-sandbox-id';
        let id = localStorage.getItem(key);
        if (!id) {
            id = generateId();
            localStorage.setItem(key, id);
        }
        return id;
    }
    catch (_) {
        return 'anon';
    }
}
async function tx(storeName, mode) {
    const db = await openDb();
    return db.transaction(storeName, mode).objectStore(storeName);
}
export const SandboxStore = {
    async saveWorldMap(mapData) {
        try {
            const store = await tx(STORE_META, 'readwrite');
            const record = { mapData, savedAt: Date.now() };
            await new Promise((resolve, reject) => {
                const req = store.put(record, 'world');
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async loadWorldMap() {
        try {
            const store = await tx(STORE_META, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get('world');
                req.onsuccess = () => {
                    const rec = req.result;
                    resolve(rec ? rec.mapData : null);
                };
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async getHexMarkdown(hexCode) {
        try {
            const store = await tx(STORE_HEX, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(hexCode);
                req.onsuccess = () => {
                    const rec = req.result;
                    resolve(rec ? rec.raw_markdown : null);
                };
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async saveHexMarkdown(hexCode, raw_markdown) {
        try {
            const store = await tx(STORE_HEX, 'readwrite');
            const rec = { hexCode, raw_markdown, updatedAt: Date.now() };
            await new Promise((resolve, reject) => {
                const req = store.put(rec);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async dumpAllHex() {
        try {
            const store = await tx(STORE_HEX, 'readonly');
            const out = [];
            return await new Promise((resolve, reject) => {
                const req = store.openCursor();
                req.onsuccess = () => {
                    const cursor = req.result;
                    if (cursor) {
                        const rec = cursor.value;
                        if (rec && rec.hexCode && typeof rec.raw_markdown === 'string') {
                            out.push(rec);
                        }
                        cursor.continue();
                    }
                    else {
                        resolve(out);
                    }
                };
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return [];
        }
    },
    async restoreAllHex(records) {
        try {
            if (!Array.isArray(records) || !records.length)
                return;
            const store = await tx(STORE_HEX, 'readwrite');
            await new Promise((resolve, reject) => {
                const t = store.transaction;
                for (const rec of records) {
                    if (!rec || !rec.hexCode || typeof rec.raw_markdown !== 'string')
                        continue;
                    const normalized = {
                        hexCode: rec.hexCode,
                        raw_markdown: rec.raw_markdown,
                        updatedAt: rec.updatedAt || Date.now()
                    };
                    store.put(normalized);
                }
                t.oncomplete = () => resolve();
                t.onerror = () => reject(t.error);
            });
        }
        catch (_) { }
    },
    async clearAll() {
        try {
            const db = await openDb();
            await new Promise((resolve, reject) => {
                const t = db.transaction([STORE_META, STORE_HEX], 'readwrite');
                t.objectStore(STORE_META).clear();
                t.objectStore(STORE_HEX).clear();
                t.oncomplete = () => resolve();
                t.onerror = () => reject(t.error);
            });
            // rotate sandbox id
            try {
                localStorage.removeItem('hexy-sandbox-id');
            }
            catch (_) { }
            getSandboxId();
        }
        catch (_) { }
    }
};
