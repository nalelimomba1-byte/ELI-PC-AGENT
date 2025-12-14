const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Robust Console Patch: Wrap all console methods to catch EPIPE errors
function safeLog(originalMethod, ...args) {
  try {
    originalMethod.apply(console, args);
  } catch (err) {
    // Silently ignore EPIPE/Broken Pipe errors
    if (err.code !== 'EPIPE') {
      // If it's something else, maybe we should know, but for stability we ignore console errors here
    }
  }
}

const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;

console.log = (...args) => safeLog(originalLog, ...args);
console.error = (...args) => safeLog(originalError, ...args);
console.warn = (...args) => safeLog(originalWarn, ...args);

// Keep process handlers as backup
process.stdout.on('error', (err) => { if (err.code === 'EPIPE') return; });
process.stderr.on('error', (err) => { if (err.code === 'EPIPE') return; });

let mainWindow;
let tray;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    frame: true,
    backgroundColor: '#0a0e27',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, 'assets', 'icon.png')
  });

  mainWindow.loadFile('index.html');

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
    return false;
  });
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'assets', 'icon.png'));

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show ELI',
      click: () => {
        mainWindow.show();
      }
    },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('ELI AI Assistant');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    mainWindow.show();
  });
}

function startPythonBackend() {
  // Start Python backend server
  const pythonPath = 'python'; // or 'python3' depending on system
  const scriptPath = path.join(__dirname, '..', 'backend', 'eli_core.py');

  pythonProcess = spawn(pythonPath, [scriptPath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  createWindow();
  createTray();
  startPythonBackend();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;

  // Kill Python backend
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

// IPC Handlers
ipcMain.handle('send-command', async (event, command) => {
  // Send command to Python backend via HTTP
  const axios = require('axios');

  try {
    const response = await axios.post('http://localhost:5000/command', {
      text: command
    });
    return response.data;
  } catch (error) {
    console.error('Failed to send command:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-tasks', async () => {
  const axios = require('axios');

  try {
    const response = await axios.get('http://localhost:5000/tasks');
    return response.data;
  } catch (error) {
    console.error('Failed to get tasks:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-status', async () => {
  return {
    status: 'online',
    voice: true,
    backend: pythonProcess !== null
  };
});
