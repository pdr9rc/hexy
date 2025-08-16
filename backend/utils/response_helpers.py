"""
Response helper utilities for creating standardized Flask responses with proper headers.
"""
from flask import jsonify
from typing import Dict, Any, Optional


def _set_no_cache_headers(response):
    """Set headers to prevent caching issues."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'


def create_json_response(data: Any, success: bool = True, status_code: int = 200) -> tuple:
    """
    Create a standardized JSON response with cache control headers.
    
    Args:
        data: Response data
        success: Whether the response indicates success
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    response = jsonify(data)
    _set_no_cache_headers(response)
    return response, status_code


def create_success_response(data: Any, status_code: int = 200) -> tuple:
    """
    Create a success response with standardized format.
    
    Args:
        data: Response data
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    return create_json_response({'success': True, 'data': data}, True, status_code)


def create_error_response(error_message: str, status_code: int = 500) -> tuple:
    """
    Create an error response with standardized format.
    
    Args:
        error_message: Error message
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    return create_json_response({'success': False, 'error': error_message}, False, status_code)


def create_overlay_response(overlay_data: Dict[str, Any]) -> tuple:
    """
    Create a response for overlay data with proper headers.
    
    Args:
        overlay_data: Overlay data dictionary
        
    Returns:
        Tuple of (response, status_code)
    """
    response = jsonify({'success': True, 'overlay': overlay_data})
    _set_no_cache_headers(response)
    return response, 200


def create_hex_response(hex_data: Dict[str, Any]) -> tuple:
    """
    Create a response for hex data with proper headers.
    
    Args:
        hex_data: Hex data dictionary
        
    Returns:
        Tuple of (response, status_code)
    """
    response = jsonify(hex_data)
    _set_no_cache_headers(response)
    return response, 200


def handle_exception_response(exception: Exception, context: str = "operation") -> tuple:
    """
    Create a standardized error response for exceptions.
    
    Args:
        exception: The exception that occurred
        context: Context for the error (e.g., "fetching hex", "updating content")
        
    Returns:
        Tuple of (response, status_code)
    """
    import traceback
    traceback.print_exc()
    
    error_message = f"Error during {context}: {str(exception)}"
    return create_error_response(error_message, 500) 