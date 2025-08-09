import { app, BrowserWindow, Menu, shell } from 'electron';
import * as path from 'path';

// Keep a global reference of the window object
let mainWindow: BrowserWindow | null = null;

// Ensure desktop integration (icon/WMClass) matches our .desktop entry
app.setName('hexy');

// Flask backend URL
const BACKEND_URL = 'http://127.0.0.1:7777';

// Resolve icon path from installed app dir if available
const INSTALLED_APP_DIR = process.env.HEXY_APP_DIR || path.join(__dirname, '../../');
const ICON_PATH = path.join(INSTALLED_APP_DIR, 'backend/web/static/icons/icon-512.png');

// Check if backend is running
async function checkBackend(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`);
    return response.ok;
  } catch (error) {
    console.log('Backend not ready:', error);
    return false;
  }
}

// Wait for backend to be ready
async function waitForBackend(maxAttempts: number = 30): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    if (await checkBackend()) {
      console.log('Backend is ready!');
      return true;
    }
    console.log(`Waiting for backend... (${i + 1}/${maxAttempts})`);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  return false;
}

function createWindow(): void {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 900,
    minWidth: 1280,
    minHeight: 720,
    useContentSize: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    },
    icon: ICON_PATH,
    title: 'Hexy - The Dying Lands',
    show: false, // Don't show until ready
    titleBarStyle: 'default'
  });

  // Enforce 16:9 aspect ratio
  mainWindow.setAspectRatio(16 / 9);

  // Load the Flask app
  mainWindow.loadURL(BACKEND_URL);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    if (mainWindow) {
      mainWindow.center();
      mainWindow.show();
      mainWindow.focus();
    }
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Emitted when the window is closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create menu
  createMenu();
}

function createMenu(): void {
  const template: Electron.MenuItemConstructorOptions[] = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) {
              mainWindow.reload();
            }
          }
        },
        {
          label: 'Developer Tools',
          accelerator: 'F12',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.toggleDevTools();
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Disable sandbox to avoid sandbox errors
app.commandLine.appendSwitch('--no-sandbox');
app.commandLine.appendSwitch('--disable-setuid-sandbox');

// This method will be called when Electron has finished initialization
app.whenReady().then(async () => {
  console.log('Electron app starting...');
  
  // Wait for backend to be ready
  const backendReady = await waitForBackend();
  
  if (backendReady) {
    createWindow();
  } else {
    console.error('Backend failed to start. Please ensure the Flask backend is running on port 7777');
    app.quit();
  }
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (_event, contents) => {
  contents.on('will-navigate', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});
