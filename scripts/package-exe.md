Windows packaging (heads-up)

Option A: Python + Flask bundled as EXE
- Use PyInstaller to package backend into hexy-backend.exe
- Include a small hexy-launcher.ps1 that starts the backend and opens Edge/Chrome in app mode

Option B: Electron shell
- Wrap the existing web UI and spawn the Python backend via child_process
- Build with electron-builder to generate .exe installer

Minimal PyInstaller example:
1) Create backend entry point (backend_win.py) that calls create_app() and runs app.run()
2) pyinstaller --onefile --add-data "backend/web;backend/web" backend_win.py
3) Create a shortcut or installer that runs the EXE and then opens the browser to http://127.0.0.1:7777/

Note: Windows users will need Python or a bundled interpreter; Electron avoids that but adds size.


