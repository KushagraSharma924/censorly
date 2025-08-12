import { API_CONFIG, API_ENDPOINTS, buildApiUrl } from '@/config/api';

// Type definitions
export interface User {
  id: string;
  email: string;
  name?: string;
  full_name?: string;
  profile_image?: string;
  profile_image_url?: string;
  avatar_url?: string;
  subscription_tier?: string;
  subscription_status?: string;
  created_at?: string;
  updated_at?: string;
  usage_count?: number;
  monthly_limit?: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token?: string;
  message?: string;
}

export interface ErrorResponse {
  error: string;
  message?: string;
}

class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';

  // Token management - using HttpOnly cookies instead of localStorage
  // The actual tokens are stored in HttpOnly cookies managed by the server
  // We only keep track of authentication state client-side
  
  getToken(): string | null {
    // We don't actually access the token directly as it's in httpOnly cookie
    // Instead we track if user is logged in
    return localStorage.getItem('is_authenticated') ? 'authenticated' : null;
  }

  setToken(token: string): void {
    // We don't store the actual token, just the authentication state
    localStorage.setItem('is_authenticated', 'true');
  }

  getRefreshToken(): string | null {
    // Refresh token is managed by httpOnly cookies
    return null;
  }

  setRefreshToken(token: string): void {
    // No action needed as refresh token is managed by httpOnly cookies
  }

  removeTokens(): void {
    // Remove authentication state tracking
    localStorage.removeItem('is_authenticated');
    localStorage.removeItem('user');
    
    // Send request to server to clear the httpOnly cookies
    fetch(buildApiUrl('/api/auth/logout'), {
      method: 'POST',
      credentials: 'include' // Important for cookies
    }).catch(err => console.error('Error during logout:', err));
  }

  // API request helper
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = buildApiUrl(endpoint);
    
    // Include credentials for cookie-based auth
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        // CSRF protection - include a custom header that simple requests can't use
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'include', // Include cookies in the request
    };

    const config = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
      credentials: 'include', // Ensure this is set even if options overrides other defaultOptions
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ErrorResponse = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(errorData.error || errorData.message || `Request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.makeRequest<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      {
        method: 'POST',
        body: JSON.stringify(credentials),
      }
    );

    // Store tokens
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    if (response.refresh_token) {
      this.setRefreshToken(response.refresh_token);
    }

    // Store user data including profile information
    if (response.user) {
      localStorage.setItem('user', JSON.stringify(response.user));
    }

    return response;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.makeRequest<AuthResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );

    // Store tokens
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    if (response.refresh_token) {
      this.setRefreshToken(response.refresh_token);
    }

    return response;
  }

  async logout(): Promise<void> {
    try {
      // Attempt to logout on server
      await this.makeRequest(API_ENDPOINTS.AUTH.LOGOUT, {
        method: 'POST',
      });
    } catch (error) {
      // Continue with local logout even if server logout fails
      console.warn('Server logout failed:', error);
    } finally {
      // Always clear local tokens
      this.removeTokens();
    }
  }

  async getProfile(): Promise<User> {
    const profile = await this.makeRequest<User>(API_ENDPOINTS.USER.PROFILE);
    
    // Update stored user data with fresh profile information
    if (profile) {
      localStorage.setItem('user', JSON.stringify(profile));
    }
    
    return profile;
  }

  async verifyToken(): Promise<{ valid: boolean; user?: User }> {
    try {
      const response = await this.makeRequest<{ valid: boolean; user: User }>(
        API_ENDPOINTS.AUTH.VERIFY_TOKEN
      );
      return response;
    } catch (error) {
      return { valid: false };
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.makeRequest<AuthResponse>(
      API_ENDPOINTS.AUTH.REFRESH,
      {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      }
    );

    // Update stored tokens
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    if (response.refresh_token) {
      this.setRefreshToken(response.refresh_token);
    }

    return response;
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getCurrentUser(): User | null {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        return JSON.parse(userData);
      }
    } catch (error) {
      console.error('Error parsing stored user data:', error);
    }
    return null;
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;
