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
function getApiBase(): string {
  const isCloudFront = typeof window !== 'undefined' && /cloudfront\.net$/i.test(window.location.hostname);
  if (isCloudFront) {
    return 'https://5fbvtc8qx4.execute-api.us-east-1.amazonaws.com/production/';
  }
  // Use document-relative paths (preserves /production/ stage when hosted on API Gateway)
  return '';
}

export async function apiCall<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const base = url.startsWith('api/') ? getApiBase() : '';
    // Attach sandbox id and selected language to API calls
    let finalUrl = base + url;
    let headers: Record<string, string> = {};
    try {
      const { getSandboxId } = await import('./sandboxStore.js');
      const sid = getSandboxId();
      const sep = finalUrl.includes('?') ? '&' : '?';
      finalUrl = `${finalUrl}${sep}sandbox=${encodeURIComponent(sid)}`;
    } catch (_) {}
    try {
      const savedLang = (typeof window !== 'undefined') ? (localStorage.getItem('hexy-language') || localStorage.getItem('language') || 'en') : 'en';
      headers['X-Hexy-Language'] = savedLang;
      const sep2 = finalUrl.includes('?') ? '&' : '?';
      finalUrl = `${finalUrl}${sep2}language=${encodeURIComponent(savedLang)}`;
    } catch (_) {}

    const response = await fetch(finalUrl, withDefaults({
      ...options,
      headers: {
        ...(options?.headers as any),
        ...headers,
      }
    }));
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