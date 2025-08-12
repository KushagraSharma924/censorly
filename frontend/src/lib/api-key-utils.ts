// API key utility functions for secure frontend handling

import { API_CONFIG } from '../config/api';

/**
 * Utility functions for handling API keys in frontend code
 * These functions provide a standard, secure way of working with API keys
 */

/**
 * Generate request options object with API key authentication header
 * 
 * @param apiKey - The API key to use for authentication
 * @returns RequestInit object with proper headers for fetch API
 */
export const getApiKeyRequestOptions = (apiKey: string): RequestInit => ({
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey,
  },
  // Don't include credentials with API key auth
  credentials: 'omit',
});

/**
 * Validate an API key format before sending to server
 * Helps catch obviously invalid formats client-side
 * 
 * @param apiKey - The API key to validate
 * @returns boolean indicating if the key format appears valid
 */
export const isValidApiKeyFormat = (apiKey: string): boolean => {
  // API keys should follow the format: apf_<32-random-chars>
  // This is a basic check - server does full verification
  if (!apiKey || typeof apiKey !== 'string') return false;
  
  // Check prefix and rough length (should be around 36-40 chars)
  return apiKey.startsWith('apf_') && apiKey.length >= 36;
};

/**
 * Safely format an API key for display by showing only the prefix
 * 
 * @param apiKey - The full API key
 * @returns A display-safe version showing only the prefix
 */
export const formatApiKeyForDisplay = (apiKey: string): string => {
  if (!apiKey || typeof apiKey !== 'string') return '—';
  
  // Show only the first 10 characters (prefix)
  const prefix = apiKey.substring(0, 10);
  return `${prefix}...`;
};

/**
 * Create a secure copy-to-clipboard function for API keys
 * Includes clearing the clipboard after a timeout for security
 * 
 * @param apiKey - The API key to copy
 * @param timeout - Optional timeout in ms to clear clipboard (default: 60000 - 1 minute)
 * @returns Promise resolving to boolean indicating success
 */
export const secureCopyApiKey = async (
  apiKey: string, 
  timeout: number = 60000
): Promise<boolean> => {
  try {
    // Copy the API key to clipboard
    await navigator.clipboard.writeText(apiKey);
    
    // Schedule clearing the clipboard after timeout
    setTimeout(async () => {
      // Check if clipboard still contains our API key
      const clipboardText = await navigator.clipboard.readText();
      if (clipboardText === apiKey) {
        // Only clear if it still contains our API key
        await navigator.clipboard.writeText('');
      }
    }, timeout);
    
    return true;
  } catch (err) {
    console.error('Failed to copy API key:', err);
    return false;
  }
};

/**
 * Log API key usage with security in mind (never log the full key)
 * 
 * @param action - The action being performed with the API key
 * @param keyPrefix - Just the prefix of the API key (never the full key)
 */
export const logApiKeyUsage = (action: string, keyPrefix: string): void => {
  // Only log in development mode
  if (import.meta.env.DEV) {
    console.log(`[API] ${action} using key with prefix ${keyPrefix}...`);
  }
};
