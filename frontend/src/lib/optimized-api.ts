/**
 * Optimized API Service for Dashboard Data Fetching
 * Handles timeouts, retries, caching, and error handling
 */

import { API_ENDPOINTS, API_CONFIG, buildApiUrl } from '@/config/api';

interface RequestOptions {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  cache?: boolean;
}

class OptimizedAPIService {
  private requestCache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  private ongoingRequests = new Map<string, Promise<any>>();

  /**
   * Enhanced fetch with timeout, retries, and caching
   */
  async fetchWithRetry(
    url: string, 
    options: RequestInit & RequestOptions = {}
  ): Promise<Response> {
    const {
      timeout = API_CONFIG.TIMEOUT,
      retries = API_CONFIG.RETRY_ATTEMPTS,
      retryDelay = API_CONFIG.RETRY_DELAY,
      cache = true,
      ...fetchOptions
    } = options;

    const cacheKey = `${url}-${JSON.stringify(fetchOptions)}`;
    
    // Check cache first
    if (cache && this.requestCache.has(cacheKey)) {
      const cached = this.requestCache.get(cacheKey)!;
      if (Date.now() - cached.timestamp < cached.ttl) {
        console.log(`📦 Cache hit for ${url}`);
        return new Response(JSON.stringify(cached.data), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        });
      } else {
        this.requestCache.delete(cacheKey);
      }
    }

    // Check for ongoing request (deduplication)
    if (this.ongoingRequests.has(cacheKey)) {
      console.log(`🔄 Deduplicating request for ${url}`);
      return this.ongoingRequests.get(cacheKey);
    }

    const makeRequest = async (): Promise<Response> => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(url, {
          ...fetchOptions,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        
        // Cache successful responses
        if (cache && response.ok) {
          const clonedResponse = response.clone();
          const data = await clonedResponse.json();
          this.requestCache.set(cacheKey, {
            data,
            timestamp: Date.now(),
            ttl: 30000 // 30 seconds cache
          });
        }

        return response;
      } catch (error) {
        clearTimeout(timeoutId);
        throw error;
      }
    };

    const requestPromise = this.retryRequest(makeRequest, retries, retryDelay);
    this.ongoingRequests.set(cacheKey, requestPromise);

    try {
      const response = await requestPromise;
      return response;
    } finally {
      this.ongoingRequests.delete(cacheKey);
    }
  }

  /**
   * Retry logic for failed requests
   */
  private async retryRequest(
    requestFn: () => Promise<Response>,
    retries: number,
    delay: number
  ): Promise<Response> {
    let lastError: any;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await requestFn();
        
        // Don't retry on 4xx errors (client errors)
        if (response.status >= 400 && response.status < 500) {
          return response;
        }
        
        // Retry on 5xx errors or network issues
        if (response.status >= 500 && attempt < retries) {
          console.log(`🔄 Retrying request (attempt ${attempt + 1}/${retries + 1})`);
          await this.sleep(delay * (attempt + 1)); // Exponential backoff
          continue;
        }

        return response;
      } catch (error) {
        lastError = error;
        
        if (attempt < retries) {
          console.log(`🔄 Retrying request after error (attempt ${attempt + 1}/${retries + 1}):`, error);
          await this.sleep(delay * (attempt + 1)); // Exponential backoff
        }
      }
    }

    throw lastError;
  }

  /**
   * Sleep utility for delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Fetch dashboard data with optimization
   */
  async fetchDashboardData(token: string): Promise<{
    profile?: any;
    jobs?: any;
    apiKeys?: any;
    usage?: any;
    errors: string[];
  }> {
    const errors: string[] = [];
    const results: any = {};

    const authHeaders = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Use Promise.allSettled for parallel requests that don't fail if one fails
    const requests = [
      { 
        key: 'profile', 
        promise: this.fetchWithRetry(buildApiUrl(API_ENDPOINTS.USER.PROFILE), {
          headers: authHeaders,
          timeout: 8000, // Shorter timeout for profile
        })
      },
      { 
        key: 'jobs', 
        promise: this.fetchWithRetry(buildApiUrl(API_ENDPOINTS.VIDEO.JOBS), {
          headers: authHeaders,
          timeout: 12000, // Longer timeout for jobs (might be more data)
        })
      },
      { 
        key: 'apiKeys', 
        promise: this.fetchWithRetry(buildApiUrl(API_ENDPOINTS.API_KEYS.LIST), {
          headers: authHeaders,
          timeout: 8000,
        })
      },
      { 
        key: 'usage', 
        promise: this.fetchWithRetry(buildApiUrl(API_ENDPOINTS.USER.USAGE), {
          headers: authHeaders,
          timeout: 8000,
        })
      },
    ];

    const requestResults = await Promise.allSettled(
      requests.map(req => req.promise)
    );

    // Process results
    for (let i = 0; i < requestResults.length; i++) {
      const result = requestResults[i];
      const { key } = requests[i];

      if (result.status === 'fulfilled') {
        try {
          if (result.value.ok) {
            const data = await result.value.json();
            
            // Handle different response formats
            switch (key) {
              case 'profile':
                results[key] = data.user || data;
                break;
              case 'jobs':
                results[key] = data.jobs || data;
                break;
              case 'apiKeys':
                results[key] = data.keys || data.api_keys || data;
                break;
              case 'usage':
                results[key] = data;
                break;
            }
          } else {
            errors.push(`${key}: HTTP ${result.value.status}`);
          }
        } catch (parseError) {
          errors.push(`${key}: Parse error`);
        }
      } else {
        errors.push(`${key}: ${result.reason?.message || 'Network error'}`);
      }
    }

    return { ...results, errors };
  }

  /**
   * Clear all caches
   */
  clearCache(): void {
    this.requestCache.clear();
    this.ongoingRequests.clear();
  }

  /**
   * Get cache stats for debugging
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.requestCache.size,
      keys: Array.from(this.requestCache.keys())
    };
  }
}

export const optimizedAPI = new OptimizedAPIService();
