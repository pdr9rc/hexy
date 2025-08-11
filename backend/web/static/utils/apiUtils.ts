/**
 * API utility functions for centralized error handling and request management.
 */

/**
 * Merge helper to combine default fetch options with caller options
 */
function withDefaults(options?: RequestInit): RequestInit {
  const defaultHeaders: HeadersInit = {
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
  };
  const merged: RequestInit = {
    cache: 'no-store',
    ...options,
    headers: {
      ...defaultHeaders,
      ...(options?.headers as any)
    }
  };
  return merged;
}

/**
 * Generic API call function with centralized error handling.
 * 
 * @param url - API endpoint URL
 * @param options - Fetch options (optional)
 * @returns Promise with response data
 */
export async function apiCall<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(url, withDefaults(options));
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

/**
 * GET request with error handling.
 * 
 * @param url - API endpoint URL
 * @returns Promise with response data
 */
export async function apiGet<T>(url: string): Promise<T> {
  // Append a cache-busting param for APIs to avoid runtime cache hits
  const buster = url.includes('?') ? `&t=${Date.now()}` : `?t=${Date.now()}`;
  return apiCall<T>(`${url}${buster}`);
}

/**
 * POST request with error handling.
 * 
 * @param url - API endpoint URL
 * @param data - Request body data
 * @returns Promise with response data
 */
export async function apiPost<T>(url: string, data?: any): Promise<T> {
  return apiCall<T>(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PUT request with error handling.
 * 
 * @param url - API endpoint URL
 * @param data - Request body data
 * @returns Promise with response data
 */
export async function apiPut<T>(url: string, data?: any): Promise<T> {
  return apiCall<T>(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * DELETE request with error handling.
 * 
 * @param url - API endpoint URL
 * @returns Promise with response data
 */
export async function apiDelete<T>(url: string): Promise<T> {
  return apiCall<T>(url, {
    method: 'DELETE',
  });
}

/**
 * Handle API errors with consistent error messages.
 * 
 * @param error - Error object
 * @param context - Context for error logging
 * @returns Formatted error message
 */
export function handleApiError(error: any, context: string = 'API call'): string {
  console.error(`Error in ${context}:`, error);
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Create a standardized error response.
 * 
 * @param error - Error object
 * @param context - Context for error logging
 * @returns Error response object
 */
export function createErrorResponse(error: any, context: string = 'API call'): { success: false; error: string } {
  return {
    success: false,
    error: handleApiError(error, context)
  };
} 