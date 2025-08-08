// Centralized API Configuration
// This file manages all API endpoints and external URLs used in the frontend

// Environment-based API configuration
const getApiBaseUrl = (): string => {
  // Check if we're running in development mode
  if (import.meta.env.DEV) {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
  }
  
  // Production environment
  return import.meta.env.VITE_API_BASE_URL || 'https://ai-profanity-filter.onrender.com';
};

// Main API configuration
export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 30000, // 30 seconds
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    VERIFY_TOKEN: '/api/auth/verify-token',
    REFRESH: '/api/auth/refresh',
  },
  
  // User Management
  USER: {
    PROFILE: '/api/auth/profile',
    UPDATE_PROFILE: '/api/user/profile',
    DELETE_ACCOUNT: '/api/user/delete',
    USAGE: '/api/auth/usage',
  },
  
  // Profanity Detection
  PROFANITY: {
    CHECK_TEXT: '/api/profanity/check',
    CHECK_BATCH: '/api/profanity/batch',
    CUSTOM_WORDS: '/api/profanity/custom-words',
  },
  
  // Video Processing
  VIDEO: {
    UPLOAD: '/api/video/upload',
    PROCESS: '/api/process-video',
    STATUS: (jobId: string) => `/api/jobs/${jobId}`,
    DOWNLOAD: (jobId: string) => `/api/download/${jobId}`,
    LIST: '/api/video/list',
    JOBS: '/api/jobs',
  },
  
  // Subscription & Billing
  SUBSCRIPTION: {
    PLANS: '/api/subscription/plans',
    CURRENT: '/api/subscription/current',
    UPGRADE: '/api/subscription/upgrade',
    CANCEL: '/api/subscription/cancel',
    USAGE: '/api/subscription/usage',
  },
  
  // API Keys Management
  API_KEYS: {
    LIST: '/api/keys',
    CREATE: '/api/keys',
    DELETE: (keyId: string) => `/api/keys/${keyId}`,
    REGENERATE: (keyId: string) => `/api/keys/${keyId}/regenerate`,
  },

  // Admin (if needed)
  ADMIN: {
    USERS: '/api/admin/users',
    ANALYTICS: '/api/admin/analytics',
  },
  
  // Health & System
  SYSTEM: {
    HEALTH: '/health',
    STATUS: '/api/status',
  },
} as const;

// External URLs (payment, social links, etc.)
export const EXTERNAL_URLS = {
  // Payment Links (Razorpay)
  PAYMENT: {
    BASIC: 'https://rzp.io/rzp/upgradebasic',
    PRO: 'https://rzp.io/rzp/upgradepro',
    ENTERPRISE: 'https://rzp.io/rzp/upgradeenterprise',
  },
  
  // Social Links
  SOCIAL: {
    GITHUB: 'https://github.com/KushagraSharma924/ai-profanity-filter',
    LINKEDIN: 'https://linkedin.com/in/kushagrasharma924',
    TWITTER: 'https://twitter.com/yourusername', // Update with actual
  },
  
  // Documentation & Support
  DOCS: {
    API_DOCS: `${getApiBaseUrl()}/api/docs`,
    USER_GUIDE: '/docs/user-guide',
    FAQ: '/docs/faq',
  },
  
  // Avatar service
  AVATAR: {
    VERCEL: (email: string) => `https://avatar.vercel.sh/${email}`,
  },
} as const;

// Utility function to build full API URL
export const buildApiUrl = (endpoint: string): string => {
  const baseUrl = API_CONFIG.BASE_URL.replace(/\/$/, ''); // Remove trailing slash
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${cleanEndpoint}`;
};

// Utility function for common fetch options
export const getDefaultFetchOptions = (): RequestInit => ({
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'omit', // Changed from 'include' to 'omit' for CORS compatibility
});

// Environment check utilities
export const isDevelopment = (): boolean => import.meta.env.DEV;
export const isProduction = (): boolean => import.meta.env.PROD;

// Debug utility (only logs in development)
export const debugLog = (message: string, data?: any): void => {
  if (isDevelopment()) {
    console.log(`[API Debug] ${message}`, data);
  }
};
