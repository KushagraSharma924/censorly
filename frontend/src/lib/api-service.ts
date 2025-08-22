/**
 * API Service for making authenticated requests to the backend
 * Uses cookie-based authentication
 */

import { buildApiUrl } from '@/config/api';

interface RequestOptions extends RequestInit {
  timeout?: number;
}

class APIService {
  private async makeRequest<T>(
    endpoint: string,
    options: RequestOptions = {},
    retryCount: number = 0
  ): Promise<T> {
    const { timeout = 30000, ...fetchOptions } = options; // Increased timeout to 30s for production
    const maxRetries = 2;
    
    const url = buildApiUrl(endpoint);
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', // CSRF protection
      },
      credentials: 'include' as RequestCredentials, // Include cookies
    };

    const config = {
      ...defaultOptions,
      ...fetchOptions,
      headers: {
        ...defaultOptions.headers,
        ...fetchOptions.headers,
      },
    };

    // Add timeout support
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.warn(`Request timeout after ${timeout}ms for ${endpoint}`);
      controller.abort();
    }, timeout);

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(errorData.error || errorData.message || `Request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      // Handle specific abort errors and retry
      if (error instanceof Error) {
        if (error.name === 'AbortError' && retryCount < maxRetries) {
          console.warn(`Request aborted, retrying (${retryCount + 1}/${maxRetries}) for ${endpoint}`);
          await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1))); // Exponential backoff
          return this.makeRequest<T>(endpoint, options, retryCount + 1);
        }
        
        // Provide more user-friendly error messages
        if (error.name === 'AbortError') {
          throw new Error('Request timed out. Please check your connection and try again.');
        }
        
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  // User Profile
  async getProfile(): Promise<any> {
    const response = await this.makeRequest<{ user: any }>('/api/auth/profile');
    return response.user;
  }

  async getUsageStats(): Promise<any> {
    return this.makeRequest('/api/auth/usage');
  }

  // Jobs
  async getJobs(page: number = 1, limit: number = 20): Promise<any> {
    return this.makeRequest(`/api/jobs?page=${page}&limit=${limit}`);
  }

  async getJobStatus(jobId: string): Promise<any> {
    return this.makeRequest(`/api/jobs/${jobId}/status`);
  }

  async getJobDetails(jobId: string): Promise<any> {
    return this.makeRequest(`/api/jobs/${jobId}`);
  }

  // API Keys
  async getApiKeys(): Promise<any> {
    return this.makeRequest('/api/keys');
  }

  async createApiKey(name: string): Promise<any> {
    return this.makeRequest('/api/keys', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async deleteApiKey(keyId: string): Promise<any> {
    return this.makeRequest(`/api/keys/${keyId}`, {
      method: 'DELETE',
    });
  }

  // Video Processing
  async uploadVideo(file: File, options: {
    censoring_mode: 'beep' | 'mute' | 'cut';
    profanity_threshold?: number;
    languages?: string[];
  }): Promise<any> {
    const formData = new FormData();
    formData.append('video_file', file);
    formData.append('censoring_mode', options.censoring_mode);
    
    if (options.profanity_threshold) {
      formData.append('profanity_threshold', options.profanity_threshold.toString());
    }
    
    if (options.languages) {
      formData.append('languages', JSON.stringify(options.languages));
    }

    return this.makeRequest('/api/process-video', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        // Don't set Content-Type for FormData, let browser set it with boundary
      },
      body: formData,
    });
  }

  async downloadVideo(jobId: string): Promise<Blob> {
    const response = await fetch(buildApiUrl(`/api/download/${jobId}`), {
      credentials: 'include' as RequestCredentials,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Download failed with status ${response.status}`);
    }

    return await response.blob();
  }

  // Profile Image
  async uploadProfileImage(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('profile_image', file);

    return this.makeRequest('/api/auth/upload-profile-image', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        // Don't set Content-Type for FormData
      },
      body: formData,
    });
  }

  async deleteProfileImage(): Promise<any> {
    return this.makeRequest('/api/auth/delete-profile-image', {
      method: 'DELETE',
    });
  }
}

export const apiService = new APIService();
export default apiService;
