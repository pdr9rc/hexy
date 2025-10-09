// web/static/utils/sandboxStore.ts
// Lightweight client-side sandbox store using IndexedDB + localStorage

type HexMarkdownRecord = {
  hexCode: string;
  raw_markdown: string;
  updatedAt: number;
};

type WorldMapRecord = {
  mapData: Record<string, any>;
  savedAt: number;
};

const DB_NAME = 'hexy-sandbox-v1';
const DB_VERSION = 1;
const STORE_META = 'meta';
const STORE_HEX = 'hex';

let dbPromise: Promise<IDBDatabase> | null = null;

function openDb(): Promise<IDBDatabase> {
  if (dbPromise) return dbPromise;
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

function generateId(): string {
  try {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
  } catch (_) {
    // Fallback
    return String(Date.now()) + Math.random().toString(16).slice(2);
  }
}

export function getSandboxId(): string {
  try {
    const key = 'hexy-sandbox-id';
    let id = localStorage.getItem(key);
    if (!id) {
      id = generateId();
      localStorage.setItem(key, id);
    }
    return id;
  } catch (_) {
    return 'anon';
  }
}

async function tx(storeName: string, mode: IDBTransactionMode): Promise<IDBObjectStore> {
  const db = await openDb();
  return db.transaction(storeName, mode).objectStore(storeName);
}

export const SandboxStore = {
  async saveWorldMap(mapData: Record<string, any>): Promise<void> {
    try {
      const store = await tx(STORE_META, 'readwrite');
      const record: WorldMapRecord = { mapData, savedAt: Date.now() };
      await new Promise<void>((resolve, reject) => {
        const req = store.put(record, 'world');
        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
      });
    } catch (_) {}
  },

  async loadWorldMap(): Promise<Record<string, any> | null> {
    try {
      const store = await tx(STORE_META, 'readonly');
      return await new Promise<Record<string, any> | null>((resolve, reject) => {
        const req = store.get('world');
        req.onsuccess = () => {
          const rec = req.result as WorldMapRecord | undefined;
          resolve(rec ? rec.mapData : null);
        };
        req.onerror = () => reject(req.error);
      });
    } catch (_) {
      return null;
    }
  },

  async getHexMarkdown(hexCode: string): Promise<string | null> {
    try {
      const store = await tx(STORE_HEX, 'readonly');
      return await new Promise<string | null>((resolve, reject) => {
        const req = store.get(hexCode);
        req.onsuccess = () => {
          const rec = req.result as HexMarkdownRecord | undefined;
          resolve(rec ? rec.raw_markdown : null);
        };
        req.onerror = () => reject(req.error);
      });
    } catch (_) {
      return null;
    }
  },

  async saveHexMarkdown(hexCode: string, raw_markdown: string): Promise<void> {
    try {
      const store = await tx(STORE_HEX, 'readwrite');
      const rec: HexMarkdownRecord = { hexCode, raw_markdown, updatedAt: Date.now() };
      await new Promise<void>((resolve, reject) => {
        const req = store.put(rec);
        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
      });
    } catch (_) {}
  },

  async dumpAllHex(): Promise<HexMarkdownRecord[]> {
    try {
      const store = await tx(STORE_HEX, 'readonly');
      const out: HexMarkdownRecord[] = [];
      return await new Promise<HexMarkdownRecord[]>((resolve, reject) => {
        const req = (store as any).openCursor();
        req.onsuccess = () => {
          const cursor: IDBCursorWithValue | null = req.result;
          if (cursor) {
            const rec = cursor.value as HexMarkdownRecord;
            if (rec && rec.hexCode && typeof rec.raw_markdown === 'string') {
              out.push(rec);
            }
            cursor.continue();
          } else {
            resolve(out);
          }
        };
        req.onerror = () => reject(req.error);
      });
    } catch (_) {
      return [];
    }
  },

  async restoreAllHex(records: Array<{ hexCode: string; raw_markdown: string; updatedAt?: number }>): Promise<void> {
    try {
      if (!Array.isArray(records) || !records.length) return;
      const store = await tx(STORE_HEX, 'readwrite');
      await new Promise<void>((resolve, reject) => {
        const t = (store as any).transaction;
        for (const rec of records) {
          if (!rec || !rec.hexCode || typeof rec.raw_markdown !== 'string') continue;
          const normalized: HexMarkdownRecord = {
            hexCode: rec.hexCode,
            raw_markdown: rec.raw_markdown,
            updatedAt: rec.updatedAt || Date.now()
          };
          (store as any).put(normalized);
        }
        t.oncomplete = () => resolve();
        t.onerror = () => reject(t.error);
      });
    } catch (_) {}
  },

  async clearAll(): Promise<void> {
    try {
      const db = await openDb();
      await new Promise<void>((resolve, reject) => {
        const t = db.transaction([STORE_META, STORE_HEX], 'readwrite');
        t.objectStore(STORE_META).clear();
        t.objectStore(STORE_HEX).clear();
        t.oncomplete = () => resolve();
        t.onerror = () => reject(t.error);
      });
      // rotate sandbox id
      try {
        localStorage.removeItem('hexy-sandbox-id');
      } catch (_) {}
      getSandboxId();
    } catch (_) {}
  }
};


