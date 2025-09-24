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
  private readonly TOKEN_KEY = 'access_token';  // Changed to match existing usage
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';

  // Token management - using HttpOnly cookies instead of localStorage
  // The actual tokens are stored in HttpOnly cookies managed by the server
  // We only keep track of authentication state client-side
  
  getToken(): string | null {
    // Return the stored authentication token
    return localStorage.getItem(this.TOKEN_KEY);
  }

  setToken(token: string): void {
    // Store the token for authentication state tracking
    localStorage.setItem(this.TOKEN_KEY, token);
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
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem('user');
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
      credentials: 'include' as RequestCredentials, // Include cookies in the request
    };

    const config = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
      credentials: 'include' as RequestCredentials, // Ensure this is set even if options overrides other defaultOptions
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

    // Store the actual JWT token from response for Bearer auth
    if (response.access_token) {
      this.setToken(response.access_token);
    } else {
      // Fallback - backend uses httpOnly cookies, so we just track authentication state
      this.setToken('authenticated');
    }

    // Store user data
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
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          full_name: data.name, // Backend expects full_name
        }),
      }
    );

    // Backend uses httpOnly cookies, so we just track authentication state
    if (response.user) {
      this.setToken('authenticated');
      localStorage.setItem('user', JSON.stringify(response.user));
    }

    return response;
  }

  async logout(): Promise<void> {
    try {
      // Call server logout to clear httpOnly cookies
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
    const response = await this.makeRequest<{ user: User }>(API_ENDPOINTS.USER.PROFILE);
    
    // Update stored user data with fresh profile information
    if (response.user) {
      localStorage.setItem('user', JSON.stringify(response.user));
      return response.user;
    }
    
    throw new Error('No user data received');
  }

  async verifyToken(): Promise<{ valid: boolean; user?: User }> {
    try {
      const response = await this.makeRequest<{ valid: boolean; user: User }>(
        API_ENDPOINTS.AUTH.VERIFY_TOKEN,
        {
          method: 'POST',
        }
      );
      return response;
    } catch (error) {
      return { valid: false };
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    // Backend handles refresh automatically via httpOnly cookies
    // We can call the refresh endpoint if needed
    const response = await this.makeRequest<AuthResponse>(
      API_ENDPOINTS.AUTH.REFRESH,
      {
        method: 'POST',
      }
    );

    // Update stored user data if provided
    if (response.user) {
      localStorage.setItem('user', JSON.stringify(response.user));
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
