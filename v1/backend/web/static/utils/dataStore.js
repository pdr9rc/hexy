// web/static/utils/dataStore.ts
// DataStore: persistent client-side IndexedDB for server-backed data
// - meta: version per language (key: `version:<lang>` -> string)
// - hexMarkdown: full markdown per hex (key: `${lang}:${hexCode}`)
// - lore: lore overview per language (key: `<lang>`)
// - cities: structured city details per language+hex (key: `${lang}:${hexCode}`)
// - settlements: structured settlement details per language+hex (key: `${lang}:${hexCode}`)
// - overlays: city overlay grids per language+overlay (key: `${lang}:${overlay}`)
// - overlayHex: overlay hex details per language+overlay+hexId (key: `${lang}:${overlay}:${hexId}`)
const DB_NAME = 'hexy-data-v1';
const DB_VERSION = 3;
const STORE_META = 'meta';
const STORE_HEX = 'hexMarkdown';
const STORE_LORE = 'lore';
const STORE_CITIES = 'cities';
const STORE_SETTLEMENTS = 'settlements';
const STORE_OVERLAYS = 'overlays';
const STORE_OVERLAY_HEX = 'overlayHex';
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
                db.createObjectStore(STORE_HEX);
            }
            if (!db.objectStoreNames.contains(STORE_LORE)) {
                db.createObjectStore(STORE_LORE);
            }
            if (!db.objectStoreNames.contains(STORE_CITIES)) {
                db.createObjectStore(STORE_CITIES);
            }
            if (!db.objectStoreNames.contains(STORE_SETTLEMENTS)) {
                db.createObjectStore(STORE_SETTLEMENTS);
            }
            if (!db.objectStoreNames.contains(STORE_OVERLAYS)) {
                db.createObjectStore(STORE_OVERLAYS);
            }
            if (!db.objectStoreNames.contains(STORE_OVERLAY_HEX)) {
                db.createObjectStore(STORE_OVERLAY_HEX);
            }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
    });
    return dbPromise;
}
async function tx(storeName, mode) {
    const db = await openDb();
    return db.transaction(storeName, mode).objectStore(storeName);
}
async function dumpStore(storeName) {
    const store = await tx(storeName, 'readonly');
    const out = {};
    return await new Promise((resolve, reject) => {
        const req = store.openCursor();
        req.onsuccess = () => {
            const cursor = req.result;
            if (cursor) {
                out[String(cursor.key)] = cursor.value;
                cursor.continue();
            }
            else {
                resolve(out);
            }
        };
        req.onerror = () => reject(req.error);
    });
}
async function restoreStore(storeName, data) {
    const store = await tx(storeName, 'readwrite');
    await new Promise((resolve, reject) => {
        const t = store.transaction;
        Object.entries(data || {}).forEach(([k, v]) => {
            store.put(v, k);
        });
        t.oncomplete = () => resolve();
        t.onerror = () => reject(t.error);
    });
}
export const DataStore = {
    async getVersion(language) {
        try {
            const store = await tx(STORE_META, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(`version:${language}`);
                req.onsuccess = () => resolve(req.result || null);
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async setVersion(language, version) {
        try {
            const store = await tx(STORE_META, 'readwrite');
            await new Promise((resolve, reject) => {
                const req = store.put(version, `version:${language}`);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async getHexMarkdown(language, hexCode) {
        try {
            const store = await tx(STORE_HEX, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(`${language}:${hexCode}`);
                req.onsuccess = () => resolve(req.result || null);
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async setHexMarkdown(language, hexCode, markdown) {
        try {
            const store = await tx(STORE_HEX, 'readwrite');
            await new Promise((resolve, reject) => {
                const req = store.put(markdown, `${language}:${hexCode}`);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async clearHexMarkdown(language) {
        try {
            const store = await tx(STORE_HEX, 'readwrite');
            if (!language) {
                await new Promise((resolve, reject) => {
                    const req = store.clear();
                    req.onsuccess = () => resolve();
                    req.onerror = () => reject(req.error);
                });
                return;
            }
            await new Promise((resolve, reject) => {
                const request = store.openCursor();
                request.onsuccess = () => {
                    const cursor = request.result;
                    if (!cursor) {
                        resolve();
                        return;
                    }
                    if (typeof cursor.key === 'string' && cursor.key.startsWith(`${language}:`)) {
                        store.delete(cursor.key);
                    }
                    cursor.continue();
                };
                request.onerror = () => reject(request.error);
            });
        }
        catch (_) { }
    },
    async getLore(language) {
        try {
            const store = await tx(STORE_LORE, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(language);
                req.onsuccess = () => resolve(req.result || null);
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async setLore(language, data) {
        try {
            const store = await tx(STORE_LORE, 'readwrite');
            await new Promise((resolve, reject) => {
                const req = store.put(data, language);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async getCity(language, hexCode) {
        try {
            const store = await tx(STORE_CITIES, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(`${language}:${hexCode}`);
                req.onsuccess = () => resolve(req.result || null);
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async setCity(language, hexCode, data) {
        try {
            const store = await tx(STORE_CITIES, 'readwrite');
            await new Promise((resolve, reject) => {
                const req = store.put(data, `${language}:${hexCode}`);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async getSettlement(language, hexCode) {
        try {
            const store = await tx(STORE_SETTLEMENTS, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(`${language}:${hexCode}`);
                req.onsuccess = () => resolve(req.result || null);
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async setSettlement(language, hexCode, data) {
        try {
            const store = await tx(STORE_SETTLEMENTS, 'readwrite');
            await new Promise((resolve, reject) => {
                const req = store.put(data, `${language}:${hexCode}`);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async getOverlay(language, overlayName) {
        try {
            const store = await tx(STORE_OVERLAYS, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(`${language}:${overlayName}`);
                req.onsuccess = () => resolve(req.result || null);
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async setOverlay(language, overlayName, data) {
        try {
            const store = await tx(STORE_OVERLAYS, 'readwrite');
            await new Promise((resolve, reject) => {
                const req = store.put(data, `${language}:${overlayName}`);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async getOverlayHex(language, overlayName, hexId) {
        try {
            const store = await tx(STORE_OVERLAY_HEX, 'readonly');
            return await new Promise((resolve, reject) => {
                const req = store.get(`${language}:${overlayName}:${hexId}`);
                req.onsuccess = () => resolve(req.result || null);
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) {
            return null;
        }
    },
    async setOverlayHex(language, overlayName, hexId, data) {
        try {
            const store = await tx(STORE_OVERLAY_HEX, 'readwrite');
            await new Promise((resolve, reject) => {
                const req = store.put(data, `${language}:${overlayName}:${hexId}`);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        }
        catch (_) { }
    },
    async dumpAll() {
        const [meta, hex, lore, cities, settlements, overlays, overlayHex] = await Promise.all([
            dumpStore(STORE_META),
            dumpStore(STORE_HEX),
            dumpStore(STORE_LORE),
            dumpStore(STORE_CITIES),
            dumpStore(STORE_SETTLEMENTS),
            dumpStore(STORE_OVERLAYS),
            dumpStore(STORE_OVERLAY_HEX)
        ]);
        return { meta, hex, lore, cities, settlements, overlays, overlayHex, schema: 1 };
    },
    async restoreAll(data) {
        if (!data || typeof data !== 'object')
            return;
        const { meta = {}, hex = {}, lore = {}, cities = {}, settlements = {}, overlays = {}, overlayHex = {} } = data;
        await restoreStore(STORE_META, meta);
        await restoreStore(STORE_HEX, hex);
        await restoreStore(STORE_LORE, lore);
        await restoreStore(STORE_CITIES, cities);
        await restoreStore(STORE_SETTLEMENTS, settlements);
        await restoreStore(STORE_OVERLAYS, overlays);
        await restoreStore(STORE_OVERLAY_HEX, overlayHex);
    }
};
