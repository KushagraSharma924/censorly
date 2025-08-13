/**
 * Dashboard Service - handles all dashboard-related data operations
 */

import { apiService } from './api-service';

export interface DashboardData {
  profile?: UserProfile;
  jobs?: Job[];
  apiKeys?: APIKey[];
  usage?: UsageStats;
  errors: string[];
}

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  full_name?: string;
  profile_image_url?: string;
  subscription_tier: string;
  subscription_status?: string;
  created_at: string;
  videos_processed?: number;
  total_processing_time?: number;
  is_verified?: boolean;
}

export interface Job {
  id: string;
  original_filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  error_message?: string;
  result_url?: string;
  progress?: number;
  censoring_mode?: string;
  languages?: string[];
  file_size?: number;
}

export interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  usage_count: number;
  last_used?: string;
  created_at: string;
}

export interface UsageStats {
  usage: {
    processing: {
      current: number;
      limit: number;
      percentage: number;
    };
    upload: {
      current: number;
      limit: number;
      percentage: number;
    };
    general: {
      current: number;
      limit: number;
      percentage: number;
    };
    api_keys: {
      current: number;
      limit: number;
      percentage: number;
    };
  };
  limits: any;
  tier: string;
  reset_date: string;
  current_period: {
    start: string;
    end: string;
  };
}

class DashboardService {
  
  /**
   * Fetch all dashboard data in parallel
   */
  async fetchAllData(): Promise<DashboardData> {
    const errors: string[] = [];
    const results: Partial<DashboardData> = {};

    // Use Promise.allSettled to fetch all data in parallel
    const [profileResult, jobsResult, apiKeysResult, usageResult] = await Promise.allSettled([
      apiService.getProfile(),
      apiService.getJobs(),
      apiService.getApiKeys(),
      apiService.getUsageStats()
    ]);

    // Process profile data
    if (profileResult.status === 'fulfilled') {
      results.profile = profileResult.value;
    } else {
      errors.push(`Profile: ${profileResult.reason?.message || 'Unknown error'}`);
    }

    // Process jobs data
    if (jobsResult.status === 'fulfilled') {
      results.jobs = jobsResult.value.jobs || jobsResult.value;
    } else {
      errors.push(`Jobs: ${jobsResult.reason?.message || 'Unknown error'}`);
    }

    // Process API keys data
    if (apiKeysResult.status === 'fulfilled') {
      results.apiKeys = apiKeysResult.value.api_keys || apiKeysResult.value;
    } else {
      errors.push(`API Keys: ${apiKeysResult.reason?.message || 'Unknown error'}`);
    }

    // Process usage data
    if (usageResult.status === 'fulfilled') {
      results.usage = usageResult.value;
    } else {
      errors.push(`Usage: ${usageResult.reason?.message || 'Unknown error'}`);
    }

    return {
      ...results,
      errors
    } as DashboardData;
  }

  /**
   * Refresh specific data section
   */
  async refreshProfile(): Promise<UserProfile> {
    return apiService.getProfile();
  }

  async refreshJobs(): Promise<Job[]> {
    const result = await apiService.getJobs();
    return result.jobs || result;
  }

  async refreshApiKeys(): Promise<APIKey[]> {
    const result = await apiService.getApiKeys();
    return result.api_keys || result;
  }

  async refreshUsage(): Promise<UsageStats> {
    return apiService.getUsageStats();
  }

  /**
   * API Key operations
   */
  async createApiKey(name: string): Promise<{ key: string; keyInfo: any }> {
    const result = await apiService.createApiKey(name);
    return {
      key: result.api_key || result.key,
      keyInfo: result.key_info || result
    };
  }

  async deleteApiKey(keyId: string): Promise<void> {
    await apiService.deleteApiKey(keyId);
  }

  /**
   * Profile operations
   */
  async uploadProfileImage(file: File): Promise<any> {
    return apiService.uploadProfileImage(file);
  }

  async deleteProfileImage(): Promise<any> {
    return apiService.deleteProfileImage();
  }

  /**
   * Job operations
   */
  async getJobDetails(jobId: string): Promise<Job> {
    return apiService.getJobDetails(jobId);
  }

  async getJobStatus(jobId: string): Promise<any> {
    return apiService.getJobStatus(jobId);
  }

  /**
   * Utility methods
   */
  getSubscriptionTierInfo(tier: string) {
    const tiers = {
      free: {
        name: 'Free',
        color: 'text-gray-500',
        bgColor: 'bg-gray-100',
        features: ['5 videos/month', '100MB file limit', '5min duration']
      },
      basic: {
        name: 'Basic',
        color: 'text-blue-500',
        bgColor: 'bg-blue-100',
        features: ['50 videos/month', '500MB file limit', '30min duration']
      },
      pro: {
        name: 'Pro',
        color: 'text-purple-500',
        bgColor: 'bg-purple-100',
        features: ['200 videos/month', '1GB file limit', '60min duration']
      },
      premium: {
        name: 'Premium',
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-100',
        features: ['Unlimited videos', '2GB file limit', '120min duration']
      }
    };

    return tiers[tier.toLowerCase() as keyof typeof tiers] || tiers.free;
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  getStatusBadgeClass(status: string): string {
    const classes = {
      completed: 'bg-green-100 text-green-800 border-green-200',
      processing: 'bg-blue-100 text-blue-800 border-blue-200',
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      failed: 'bg-red-100 text-red-800 border-red-200'
    };

    return classes[status.toLowerCase() as keyof typeof classes] || 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;
