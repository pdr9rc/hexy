#!/usr/bin/env bash
set -euo pipefail

# Start Hexy backend only (no browser). Designed for systemd --user service.

# Detect OS and set appropriate paths
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    STATE_DIR="${HOME}/Library/Application Support/hexy"
    VENVDIR="${STATE_DIR}/venv"
else
    # Linux
    STATE_DIR="${HOME}/.local/share/hexy"
    VENVDIR="${STATE_DIR}/venv"
fi

PIDFILE="${STATE_DIR}/backend.pid"
PORT="${HEXY_PORT:-7777}"

# Get APP_DIR from state file or fallback to script location
if [ -f "${STATE_DIR}/app_dir" ]; then
    APP_DIR="$(cat "${STATE_DIR}/app_dir")"
else
    APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

mkdir -p "${STATE_DIR}"

# Set environment variables
export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"
export HEXY_APP_DIR="${APP_DIR}"

# Migrate/fallback output directory to keep compatibility
OUTPUT_STATE="${STATE_DIR}/dying_lands_output"
OUTPUT_APP="${APP_DIR}/dying_lands_output"
if [ -d "${OUTPUT_APP}/hexes" ] && [ ! -d "${OUTPUT_STATE}/hexes" ]; then
  mkdir -p "${OUTPUT_STATE}" && rsync -a "${OUTPUT_APP}/" "${OUTPUT_STATE}/" || true
fi
if [ -d "${OUTPUT_STATE}/hexes" ]; then
  export HEXY_OUTPUT_DIR="${OUTPUT_STATE}"
else
  export HEXY_OUTPUT_DIR="${OUTPUT_APP}"
fi

export HEXY_PORT="${PORT}"

# Save PID
echo $$ > "${PIDFILE}" 2>/dev/null || true

# Change to app directory
cd "${APP_DIR}"

# Function to install dependencies
install_dependencies() {
    echo "[hexy] Installing dependencies..."
    
    # Try to install Flask and other required packages
    if command -v pip3 >/dev/null 2>&1; then
        echo "[hexy] Installing with pip3..."
        pip3 install flask requests markdown >/dev/null 2>&1 || {
            echo "[hexy] pip3 install failed, trying with --user flag..."
            pip3 install --user flask requests markdown >/dev/null 2>&1 || {
                echo "[hexy] pip3 --user install failed"
                return 1
            }
        }
    elif command -v pip >/dev/null 2>&1; then
        echo "[hexy] Installing with pip..."
        pip install flask requests markdown >/dev/null 2>&1 || {
            echo "[hexy] pip install failed, trying with --user flag..."
            pip install --user flask requests markdown >/dev/null 2>&1 || {
                echo "[hexy] pip --user install failed"
                return 1
            }
        }
    else
        echo "[hexy] No pip found"
        return 1
    fi
    
    echo "[hexy] Dependencies installed successfully"
    return 0
}

# Function to use system Python with dependency installation
use_system_python() {
    command -v python3 >/dev/null 2>&1 || { echo "[hexy] python3 not found" >&2; exit 1; }
    
    # Check if Flask is available
    if ! python3 -c "import flask" 2>/dev/null; then
        echo "[hexy] Flask not found, installing dependencies..."
        install_dependencies
    fi
    
    # Check again after installation
    if ! python3 -c "import flask" 2>/dev/null; then
        echo "[hexy] Failed to install Flask" >&2
        exit 1
    fi
    
    echo "[hexy] Starting backend with system Python..."
    exec python3 -m backend.run
}

# Try virtual environment first
if python3 -m venv --help >/dev/null 2>&1; then
    if [ ! -d "${VENVDIR}" ]; then
        echo "[hexy] Creating virtual environment..."
        python3 -m venv "${VENVDIR}" || {
            echo "[hexy] Failed to create virtual environment, using system Python"
            use_system_python
        }
    fi
    
    if [ -f "${VENVDIR}/bin/activate" ]; then
        echo "[hexy] Activating virtual environment..."
        source "${VENVDIR}/bin/activate"
        
        # Upgrade pip
        pip install --upgrade pip >/dev/null 2>&1 || true
        
        # Install dependencies
        if [ -f "${APP_DIR}/requirements.txt" ]; then
            echo "[hexy] Installing from requirements.txt..."
            pip install -r "${APP_DIR}/requirements.txt" || {
                echo "[hexy] requirements.txt install failed, installing basic dependencies..."
                pip install flask requests markdown || {
                    echo "[hexy] Virtual environment install failed, using system Python"
                    use_system_python
                }
            }
        else
            echo "[hexy] Installing basic dependencies..."
            pip install flask requests markdown || {
                echo "[hexy] Virtual environment install failed, using system Python"
                use_system_python
            }
        fi
        
        echo "[hexy] Starting backend with virtual environment..."
        exec python -m backend.run
    else
        echo "[hexy] Virtual environment activation failed, using system Python"
        use_system_python
    fi
else
    echo "[hexy] venv not available, using system Python"
    use_system_python
fi


