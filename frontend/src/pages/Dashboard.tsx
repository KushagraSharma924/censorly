import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Key, 
  CreditCard, 
  FileVideo, 
  Calendar, 
  Download,
  Eye,
  RefreshCw,
  Settings,
  BarChart3,
  Crown,
  Shield,
  Zap,
  Copy,
  Trash2,
  Globe,
  User,
  Github
} from 'lucide-react';
// import { apiService, APICapabilities } from '@/lib/api-service';
import { API_ENDPOINTS, buildApiUrl, getDefaultFetchOptions } from '@/config/api';

interface UserProfile {
  id: string;
  email: string;
  name: string;
  subscription_tier: string;
  subscription_status: string;
  subscription_expires_at: string | null;
  created_at: string;
  usage_count: number;
  monthly_limit: number;
}

interface Job {
  id: string;
  filename: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  result_url: string | null;
}

interface APIKey {
  id: string;
  name: string;
  key_prefix: string;  // Backend returns key_prefix, not key_preview
  created_at: string;
  last_used: string | null;
  is_active: boolean;
  usage_count?: number;
}

interface UsageStats {
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
  limits: {
    general: number;
    processing: number;
    upload: number;
    max_api_keys: number;
  };
  tier: string;
  reset_date: string;
  current_period: {
    start: string;
    end: string;
  };
}

const Dashboard: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [apiCapabilities, setApiCapabilities] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showNewApiKey, setShowNewApiKey] = useState(false);
  const [newApiKey, setNewApiKey] = useState<string>('');
  const [newApiKeyName, setNewApiKeyName] = useState<string>('');
  const [showApiKeyForm, setShowApiKeyForm] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('❌ No token found, redirecting to login');
        window.location.href = '/login';
        return;
      }

      const [profileRes, jobsRes, keysRes, usageRes] = await Promise.all([
        fetch(buildApiUrl(API_ENDPOINTS.USER.PROFILE), {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(buildApiUrl(API_ENDPOINTS.VIDEO.JOBS), {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(buildApiUrl(API_ENDPOINTS.API_KEYS.LIST), {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(buildApiUrl(API_ENDPOINTS.USER.USAGE), {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      console.log('📊 API Response Status:', {
        profile: profileRes.status,
        jobs: jobsRes.status,
        keys: keysRes.status,
        usage: usageRes.status
      });

      // Check for authentication errors
      if (profileRes.status === 401 || jobsRes.status === 401 || keysRes.status === 401 || usageRes.status === 401) {
        console.log('🚫 Authentication failed, clearing tokens');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }

      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setProfile(profileData.user || profileData);
      } else {
        console.log('❌ Profile request failed:', profileRes.status);
      }

      if (jobsRes.ok) {
        const jobsData = await jobsRes.json();
        setJobs(jobsData.jobs || []);
      } else {
        console.log('❌ Jobs request failed:', jobsRes.status);
      }

      if (keysRes.ok) {
        const keysData = await keysRes.json();
        setApiKeys(keysData.api_keys || []);
      } else {
        console.log('❌ Keys request failed:', keysRes.status);
      }

      if (usageRes.ok) {
        const usageData = await usageRes.json();
        setUsageStats(usageData);
      } else {
        console.log('❌ Usage request failed:', usageRes.status);
      }

      // Skip API capabilities for now
      try {
        // API capabilities endpoint has different format
      } catch (error) {
        console.error('Failed to fetch API capabilities:', error);
      }

      setLoading(false);
    } catch (error) {
      console.error('❌ Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  const refreshJobs = async () => {
    setRefreshing(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.VIDEO.JOBS), {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setJobs(data.jobs || []);
      }
    } catch (error) {
      console.error('Failed to refresh jobs:', error);
    }
    setRefreshing(false);
  };

  const downloadFile = async (jobId: string, filename: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.VIDEO.DOWNLOAD(jobId)), {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `processed_${filename}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Download failed:', response.statusText);
        alert('Download failed. Please try again.');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed. Please check your connection and try again.');
    }
  };

  const createAPIKey = async () => {
    if (!newApiKeyName.trim()) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.API_KEYS.CREATE), {
        method: 'POST',
        ...getDefaultFetchOptions(),
        headers: {
          ...getDefaultFetchOptions().headers,
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ name: newApiKeyName.trim() })
      });

      if (response.ok) {
        const data = await response.json();
        setNewApiKey(data.api_key);
        setShowNewApiKey(true);
        setShowApiKeyForm(false);
        setNewApiKeyName('');
        
        // Refresh the API keys list to show the new record
        fetchDashboardData();
        
        // Auto-hide the success panel after 30 seconds for security
        setTimeout(() => {
          setShowNewApiKey(false);
          setNewApiKey('');
        }, 30000);
      } else {
        const error = await response.json();
        console.error('Failed to create API key:', error.error);
      }
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  };

  const deleteAPIKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.API_KEYS.DELETE(keyId)), {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchDashboardData();
      } else {
        const error = await response.json();
        console.error('Failed to delete API key:', error.error);
      }
    } catch (error) {
      console.error('Failed to delete API key:', error);
    }
  };

  const getSubscriptionIcon = (tier: string | undefined) => {
    if (!tier) return null;
    
    switch (tier.toLowerCase()) {
      case 'basic': return <Zap className="h-5 w-5 text-blue-500" />;
      case 'pro': return <Shield className="h-5 w-5 text-purple-500" />;
      case 'enterprise': return <Crown className="h-5 w-5 text-amber-500" />;
      default: return null;
    }
  };

  const getProcessingMethod = (tier: string | undefined) => {
    if (!tier) return 'Loading...';
    
    switch (tier.toLowerCase()) {
      case 'free':
      case 'basic':
        return 'Regex & Keyword Detection';
      case 'pro':
        return 'Advanced AI Detection (Coming Soon)';
      case 'enterprise':
        return 'Custom AI Models (Coming Soon)';
      default:
        return 'Regex & Keyword Detection';
    }
  };

  const getLanguageSupport = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'free':
      case 'basic':
        return {
          current: ['English'],
          comingSoon: ['Hindi', 'Hinglish', 'Urdu']
        };
      case 'pro':
      case 'enterprise':
        return {
          current: ['English'],
          comingSoon: ['Hindi', 'Hinglish', 'Urdu', 'Multiple Languages']
        };
      default:
        return {
          current: ['English'],
          comingSoon: ['Hindi', 'Hinglish', 'Urdu']
        };
    }
  };

  const getTierLanguageSupport = (tier: string | undefined) => {
    if (!tier) {
      return {
        current: ['English'],
        comingSoon: ['Hindi', 'Hinglish', 'Urdu']
      };
    }
    
    switch (tier.toLowerCase()) {
      case 'free':
      case 'basic':
        return {
          current: ['English'],
          comingSoon: ['Hindi', 'Hinglish', 'Urdu']
        };
      case 'pro':
      case 'enterprise':
        return {
          current: ['English'],
          comingSoon: ['Hindi', 'Hinglish', 'Urdu', 'Tamil', 'Telugu', 'Bengali']
        };
      default:
        return {
          current: ['English'],
          comingSoon: ['Hindi', 'Hinglish', 'Urdu']
        };
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          {/* Professional SaaS Loading Animation */}
          <div className="relative">
            {/* Outer rotating ring */}
            <div className="w-20 h-20 border-4 border-blue-200 rounded-full animate-spin border-t-blue-500 mx-auto"></div>
            
            {/* Inner pulsing dot */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
            </div>
            
            {/* Brand icon overlay */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <Shield className="h-6 w-6 text-blue-600 animate-pulse" />
            </div>
          </div>
          
          {/* Loading text with typing animation */}
          <div className="mt-6 space-y-2">
            <h3 className="text-xl font-semibold text-gray-800">Loading Dashboard</h3>
            <div className="flex items-center justify-center space-x-1">
              <span className="text-gray-600">Preparing your analytics</span>
              <div className="flex space-x-1">
                <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
          
          {/* Progress bar simulation */}
          <div className="mt-4 w-64 mx-auto">
            <div className="bg-gray-200 rounded-full h-1.5">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-500 h-1.5 rounded-full animate-pulse" style={{width: '70%'}}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
          <p className="text-gray-600 mb-4">Please log in to access your dashboard.</p>
          <Button onClick={() => window.location.href = '/login'}>
            Go to Login
          </Button>
        </div>
      </div>
    );
  }

  const usagePercentage = profile?.monthly_limit > 0 
    ? (profile.usage_count / profile.monthly_limit) * 100 
    : 0;

  return (
    <div className="min-h-screen bg-white">
      {/* Enhanced Header */}
      <header className="bg-white border-b border-gray-200 backdrop-blur-sm bg-white/95 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center shadow-sm border border-gray-200">
                <img 
                  src="/logo.svg" 
                  alt="Censorly Logo" 
                  className="w-10 h-10 object-cover"
                />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-black tracking-tight">
                  Dashboard
                </h1>
                <div className="flex items-center space-x-3 text-xs text-gray-600">
                  <Badge variant="outline" className="text-xs px-2 py-0.5 border-gray-300 bg-gray-50">
                    <User className="h-3 w-3 mr-1" />
                    {profile?.name || 'User'}
                  </Badge>
                  <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                  <span className="font-medium">
                    {profile?.subscription_tier ? 
                      profile.subscription_tier.charAt(0).toUpperCase() + profile.subscription_tier.slice(1) 
                      : 'Free'
                    } Plan
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <nav className="hidden md:flex items-center space-x-6">
                <Button variant="ghost" className="text-gray-700 hover:text-black hover:bg-gray-50 font-medium" onClick={() => window.location.href = '/'}>
                  Home
                </Button>
                <Button variant="ghost" className="text-gray-700 hover:text-black hover:bg-gray-50 font-medium" onClick={() => window.location.href = '/upload'}>
                  Upload
                </Button>
                <Button 
                  variant="ghost" 
                  className="text-gray-700 hover:text-black hover:bg-gray-50 flex items-center space-x-2 font-medium"
                  onClick={() => window.open('https://github.com/KushagraSharma924/ai-profanity-filter', '_blank')}
                >
                  <Github className="h-4 w-4" />
                  <span>GitHub</span>
                </Button>
              </nav>
              <div className="flex items-center space-x-3">
                <Button variant="outline" size="sm" className="border-gray-300 text-black hover:bg-gray-50 font-medium shadow-sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="text-gray-700 hover:text-black hover:bg-gray-50 font-medium"
                  onClick={() => {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    window.location.href = '/';
                  }}
                >
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">

        {/* Overview Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="border border-gray-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700">Subscription</p>
                  <div className="flex items-center mt-1">
                    {getSubscriptionIcon(profile?.subscription_tier)}
                    <p className="text-2xl font-bold text-black ml-2">
                      {profile?.subscription_tier ? 
                        profile.subscription_tier.charAt(0).toUpperCase() + profile.subscription_tier.slice(1) 
                        : 'Loading...'
                      }
                    </p>
                  </div>
                </div>
                <CreditCard className="h-8 w-8 text-black" />
              </div>
            </CardContent>
          </Card>

          <Card className="border border-gray-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700">Total Uploads</p>
                  <p className="text-2xl font-bold text-black">
                    {usageStats?.usage?.upload?.current || 0} / {usageStats?.usage?.upload?.limit || 0}
                  </p>
                  <Progress value={usageStats?.usage?.upload?.percentage || 0} className="mt-2" />
                </div>
                <FileVideo className="h-8 w-8 text-black" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">API Processing</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {usageStats?.usage?.processing?.current || 0} / {usageStats?.usage?.processing?.limit || 0}
                  </p>
                  <Progress value={usageStats?.usage?.processing?.percentage || 0} className="mt-2" />
                </div>
                <BarChart3 className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">API Keys Used</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {usageStats?.usage?.api_keys?.current || 0} / {usageStats?.usage?.api_keys?.limit || 0}
                  </p>
                  <Progress value={usageStats?.usage?.api_keys?.percentage || 0} className="mt-2" />
                </div>
                <Key className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Usage Statistics */}
        {usageStats && (
          <div className="mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Monthly Usage Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-gray-600">Total Uploads</span>
                      <span className="text-gray-900">
                        {usageStats.usage.upload.current} / {usageStats.usage.upload.limit}
                      </span>
                    </div>
                    <Progress value={usageStats.usage.upload.percentage} className="h-2" />
                    <p className="text-xs text-gray-500">
                      {usageStats.usage.upload.percentage.toFixed(1)}% used
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-gray-600">API Processing</span>
                      <span className="text-gray-900">
                        {usageStats.usage.processing.current} / {usageStats.usage.processing.limit}
                      </span>
                    </div>
                    <Progress value={usageStats.usage.processing.percentage} className="h-2" />
                    <p className="text-xs text-gray-500">
                      {usageStats.usage.processing.percentage.toFixed(1)}% used
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-gray-600">General API Calls</span>
                      <span className="text-gray-900">
                        {usageStats.usage.general.current} / {usageStats.usage.general.limit}
                      </span>
                    </div>
                    <Progress value={usageStats.usage.general.percentage} className="h-2" />
                    <p className="text-xs text-gray-500">
                      {usageStats.usage.general.percentage.toFixed(1)}% used
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-gray-600">API Keys</span>
                      <span className="text-gray-900">
                        {usageStats.usage.api_keys.current} / {usageStats.usage.api_keys.limit}
                      </span>
                    </div>
                    <Progress value={usageStats.usage.api_keys.percentage} className="h-2" />
                    <p className="text-xs text-gray-500">
                      {usageStats.usage.api_keys.percentage.toFixed(1)}% used
                    </p>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200 space-y-1">
                  <div className="flex justify-between items-center text-sm">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                      <span className="text-gray-600">Monthly usage period:</span>
                    </div>
                    <span className="text-gray-900">
                      {new Date(usageStats.current_period.start).toLocaleDateString()} - {new Date(usageStats.current_period.end).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Usage resets monthly on:</span>
                    <span className="text-gray-900 font-medium">
                      {new Date(usageStats.reset_date).toLocaleDateString()} (1st of each month)
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Processing Method & Language Support */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Processing Method
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-lg font-semibold text-gray-900">
                  {getProcessingMethod(profile?.subscription_tier)}
                </p>
                <p className="text-sm text-gray-600">
                  Current method for your {profile?.subscription_tier || 'current'} tier
                </p>
                {(profile?.subscription_tier === 'pro' || profile?.subscription_tier === 'enterprise') && (
                  <Badge variant="outline" className="bg-orange-100 text-orange-800 border-orange-300">
                    Available in Phase 2
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Globe className="h-5 w-5 mr-2" />
                Language Support
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Currently Supported:</p>
                  <div className="flex flex-wrap gap-1">
                    {getTierLanguageSupport(profile?.subscription_tier).current.map((lang) => (
                      <Badge key={lang} variant="default" className="bg-green-100 text-green-800">
                        {lang}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Coming Soon:</p>
                  <div className="flex flex-wrap gap-1">
                    {getTierLanguageSupport(profile?.subscription_tier).comingSoon.map((lang) => (
                      <Badge key={lang} variant="outline" className="bg-orange-50 text-orange-600 border-orange-200">
                        {lang}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="jobs" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="jobs">Recent Jobs</TabsTrigger>
            <TabsTrigger value="api-keys">API Keys</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="jobs">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Recent Processing Jobs</CardTitle>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={refreshJobs}
                  disabled={refreshing}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </CardHeader>
              <CardContent>
                {jobs.length === 0 ? (
                  <div className="text-center py-8">
                    <FileVideo className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No jobs yet. Upload your first video to get started!</p>
                    <Button className="mt-4" onClick={() => window.location.href = '/upload'}>
                      Upload Video
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {jobs.slice(0, 10).map((job) => (
                      <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <FileVideo className="h-5 w-5 text-gray-400" />
                            <div>
                              <p className="font-medium text-gray-900">{job.filename}</p>
                              <p className="text-sm text-gray-600">
                                Created: {new Date(job.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <Badge className={getStatusColor(job.status)}>
                            {job.status}
                          </Badge>
                          {job.status === 'completed' && (
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => downloadFile(job.id, job.filename)}
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </Button>
                          )}
                          {job.status === 'completed' && (
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4 mr-2" />
                              View
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api-keys">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>API Keys</CardTitle>
                <Button onClick={() => setShowApiKeyForm(true)}>
                  <Key className="h-4 w-4 mr-2" />
                  Create New Key
                </Button>
              </CardHeader>
              <CardContent>
                {/* New API Key Creation Form */}
                {showApiKeyForm && (
                  <div className="mb-6 p-4 border rounded-lg bg-gray-50">
                    <h3 className="font-medium text-gray-900 mb-3">Create New API Key</h3>
                    <div className="flex space-x-3">
                      <input
                        type="text"
                        placeholder="Enter API key name..."
                        value={newApiKeyName}
                        onChange={(e) => setNewApiKeyName(e.target.value)}
                        className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onKeyPress={(e) => e.key === 'Enter' && createAPIKey()}
                      />
                      <Button onClick={createAPIKey} disabled={!newApiKeyName.trim()}>
                        Create
                      </Button>
                      <Button variant="outline" onClick={() => setShowApiKeyForm(false)}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}

                {/* New API Key Display */}
                {showNewApiKey && newApiKey && (
                  <div className="mb-6 p-4 border-2 border-green-200 rounded-lg bg-green-50">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-medium text-green-800">🎉 API Key Created Successfully!</h3>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setShowNewApiKey(false);
                          setNewApiKey('');
                        }}
                      >
                        ×
                      </Button>
                    </div>
                    <p className="text-sm text-green-700 mb-3">
                      ⚠️ <strong>Save this key now!</strong> This is the only time you'll see the full key. 
                      It will auto-hide in 30 seconds for security.
                    </p>
                    <div className="flex items-center space-x-2 p-3 bg-white rounded border mb-3">
                      <code className="flex-1 text-sm font-mono break-all">{newApiKey}</code>
                      <Button 
                        size="sm" 
                        onClick={() => copyToClipboard(newApiKey)}
                        className="flex-shrink-0"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="flex space-x-2">
                      <Button 
                        size="sm"
                        onClick={() => copyToClipboard(newApiKey)}
                        className="flex-1"
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Copy Key
                      </Button>
                      <Button 
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setShowNewApiKey(false);
                          setNewApiKey('');
                        }}
                        className="flex-1"
                      >
                        I've Saved It
                      </Button>
                    </div>
                  </div>
                )}

                {apiKeys.length === 0 ? (
                  <div className="text-center py-8">
                    <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No API keys yet. Create one to access our API programmatically.</p>
                    <Button className="mt-4" onClick={() => setShowApiKeyForm(true)}>
                      Create First API Key
                    </Button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b bg-gray-50">
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Key Id</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Created At</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Expiry</th>
                          <th className="text-left py-3 px-4 font-medium text-gray-700">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {apiKeys.map((key) => (
                          <tr key={key.id} className="border-b hover:bg-gray-50">
                            <td className="py-3 px-4 font-mono text-sm text-gray-900">
                              {key.key_prefix}...
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {new Date(key.created_at).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                                hour: 'numeric',
                                minute: '2-digit',
                                hour12: true
                              })}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              Never
                            </td>
                            <td className="py-3 px-4">
                              <Button 
                                variant="destructive" 
                                size="sm"
                                onClick={() => deleteAPIKey(key.id)}
                                className="text-xs"
                              >
                                Delete
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Settings className="h-5 w-5 mr-2" />
                    Account Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Email</label>
                    <p className="text-gray-900">{profile?.email || 'Loading...'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Name</label>
                    <p className="text-gray-900">{profile?.name || 'Loading...'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Member Since</label>
                    <p className="text-gray-900">{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Loading...'}</p>
                  </div>
                  <Button variant="outline" className="w-full">
                    Edit Profile
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CreditCard className="h-5 w-5 mr-2" />
                    Subscription Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Current Plan</label>
                    <div className="flex items-center mt-1">
                      {getSubscriptionIcon(profile?.subscription_tier)}
                      <p className="text-gray-900 ml-2 capitalize">{profile?.subscription_tier || 'Loading...'}</p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Status</label>
                    <p className="text-gray-900 capitalize">{profile?.subscription_status || 'Loading...'}</p>
                  </div>
                  {profile?.subscription_expires_at && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Expires</label>
                      <p className="text-gray-900">{new Date(profile.subscription_expires_at).toLocaleDateString()}</p>
                    </div>
                  )}
                  <div className="space-y-2">
                    <Button className="w-full" onClick={() => window.location.href = '/pricing'}>
                      Upgrade Plan
                    </Button>
                    <Button variant="outline" className="w-full">
                      Billing History
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;
