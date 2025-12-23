#!/usr/bin/env python3
"""
Core utility functions for The Dying Lands
Essential utilities used across the application.
"""

import os
import re
import random
import sys
import shutil
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from backend.config import get_config

def setup_project_paths() -> None:
    """Add project root to Python path for imports."""
    project_root = get_config().paths.project_root
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

def validate_hex_code(hex_code: str) -> bool:
    """Validate hex code format (XXYY)."""
    if not isinstance(hex_code, str):
        return False
    return bool(re.match(r'^\d{4}$', hex_code))

def parse_hex_coordinates(hex_code: str) -> Tuple[int, int]:
    """Parse hex code to x, y coordinates."""
    if not validate_hex_code(hex_code):
        raise ValueError(f"Invalid hex code format: {hex_code}")
    x = int(hex_code[:2])
    y = int(hex_code[2:])
    return x, y

def format_hex_code(x: int, y: int) -> str:
    """Format x, y coordinates to hex code."""
    return f"{x:02d}{y:02d}"

def safe_file_write(file_path: Path, content: str, encoding: str = 'utf-8') -> None:
    """Safely write content to file with proper error handling."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise IOError(f"Failed to write file {file_path}: {e}")

def safe_file_read(file_path: Path, encoding: str = 'utf-8') -> str:
    """Safely read content from file with proper error handling."""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise IOError(f"Failed to read file {file_path}: {e}")

def weighted_choice(weights: Dict[str, float]) -> str:
    """Make a weighted random choice from a dictionary of options and weights."""
    if not weights:
        raise ValueError("Weights dictionary cannot be empty")
    
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")
    
    rand_val = random.uniform(0, total_weight)
    cumulative_weight = 0
    
    for option, weight in weights.items():
        cumulative_weight += weight
        if rand_val <= cumulative_weight:
            return option
    
    # Fallback to last option (shouldn't happen with proper weights)
    return list(weights.keys())[-1]

def extract_title_from_content(content: str) -> str:
    """Extract title from markdown content."""
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        elif line.startswith('**') and line.endswith('**'):
            return line[2:-2].strip()
    return "Untitled"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations."""
    # Remove or replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized

def merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries, with dict2 taking precedence."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dictionaries(result[key], value)
        else:
            result[key] = value
    return result

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_list(nested_list: List[Any]) -> List[Any]:
    """Flatten a nested list structure."""
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened

def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def ensure_directory_exists(directory: Path) -> None:
    """Ensure directory exists, create if necessary."""
    directory.mkdir(parents=True, exist_ok=True)

def list_files_with_extension(directory: Path, extension: str) -> List[Path]:
    """List all files with specified extension in directory."""
    if not directory.exists():
        return []
    return list(directory.glob(f"*.{extension}"))

def backup_file(file_path: Path, backup_suffix: str = ".backup") -> Path:
    """Create a backup of a file."""
    backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
    if file_path.exists():
        shutil.copy2(file_path, backup_path)
    return backup_path

def is_valid_json(content: str) -> bool:
    """Check if string is valid JSON."""
    try:
        json.loads(content)
        return True
    except (json.JSONDecodeError, ValueError):
        return False

def retry_operation(operation, max_attempts: int = 3, delay: float = 1.0):
    """Retry an operation with exponential backoff."""
    
    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            time.sleep(delay * (2 ** attempt))
    
    raise RuntimeError(f"Operation failed after {max_attempts} attempts")

def log_operation(operation_name: str, success: bool, details: str = ""):
    """Log operation results for debugging."""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    timestamp = __import__('datetime').datetime.now().isoformat()
    print(f"[{timestamp}] {status} - {operation_name}: {details}")
