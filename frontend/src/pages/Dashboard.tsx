import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Header } from '@/components/Header';
import { DashboardSkeleton } from '@/components/DashboardSkeleton';
import { API_CONFIG } from '@/config/api';
import { apiService } from '@/lib/api-service';
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
  Loader2,
  AlertCircle
} from 'lucide-react';

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: string;
  created_at?: string;
}

interface Job {
  id: string;
  filename: string;
  status: string;
  created_at: string;
  completed_at?: string | null;
  error_message?: string | null;
  result_url?: string | null;
  progress?: number;
  censoring_mode?: string;
  languages?: string[];
}

interface APIKey {
  id: string;
  name: string;
  key: string;
  created_at: string;
  last_used?: string | null;
  description?: string;
}

interface UsageStats {
  videos_processed_this_month: number;
  videos_limit: number;
  subscription_tier: string;
  days_remaining: number;
}

export const Dashboard: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // API Key management state
  const [showApiKeyForm, setShowApiKeyForm] = useState(false);
  const [newApiKeyName, setNewApiKeyName] = useState('');
  const [newApiKey, setNewApiKey] = useState('');
  const [showNewApiKey, setShowNewApiKey] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    if (!isInitialLoad) {
      setRefreshing(true);
    }

    try {
      console.log('🔄 Fetching dashboard data...');
      
      // Fetch all data in parallel using API service
      const [profileRes, jobsRes, keysRes, usageRes] = await Promise.allSettled([
        apiService.getProfile(),
        apiService.getJobs(),
        apiService.getApiKeys(),
        apiService.getUsageStats()
      ]);

      console.log('📊 API Results:', { profileRes, jobsRes, keysRes, usageRes });

      // Handle profile data
      if (profileRes.status === 'fulfilled') {
        console.log('✅ Profile data:', profileRes.value);
        const profileData = profileRes.value;
        // Profile data is returned directly, not wrapped in .user
        if (profileData && profileData.id) {
          setProfile(profileData);
          localStorage.setItem('user', JSON.stringify(profileData));
          window.dispatchEvent(new CustomEvent('userDataUpdated'));
        }
      } else {
        console.error('❌ Profile fetch failed:', profileRes.reason);
      }

      // Handle jobs data
      if (jobsRes.status === 'fulfilled') {
        console.log('✅ Jobs data:', jobsRes.value);
        const jobsData = jobsRes.value;
        if (jobsData.jobs) {
          setJobs(jobsData.jobs);
        }
      } else {
        console.error('❌ Jobs fetch failed:', jobsRes.reason);
      }

      // Handle API keys data
      if (keysRes.status === 'fulfilled') {
        console.log('✅ API Keys data:', keysRes.value);
        const keysData = keysRes.value;
        // API keys are returned as 'api_keys' not 'keys'
        if (keysData.api_keys || keysData.keys) {
          setApiKeys(keysData.api_keys || keysData.keys);
        }
      } else {
        console.error('❌ API Keys fetch failed:', keysRes.reason);
      }

      // Handle usage data
      if (usageRes.status === 'fulfilled') {
        console.log('✅ Usage data:', usageRes.value);
        const usageData = usageRes.value;
        setUsageStats(usageData);
      } else {
        console.error('❌ Usage fetch failed:', usageRes.reason);
      }

    } catch (error) {
      console.error('❌ Failed to fetch dashboard data:', error);
    } finally {
      setIsLoading(false);
      setRefreshing(false);
      setIsInitialLoad(false);
    }
  };

  const createApiKey = async () => {
    if (!newApiKeyName.trim()) {
      return;
    }

    // Check free tier limit (3 API keys max)
    if (apiKeys.length >= 3) {
      alert('Free tier limit reached. You can only have 3 API keys. Please delete an existing key to create a new one.');
      return;
    }

    try {
      const data = await apiService.createApiKey(newApiKeyName.trim());
      setNewApiKey(data.key?.key || data.api_key || 'Key created successfully');
      setShowNewApiKey(true);
      setShowApiKeyForm(false);
      setNewApiKeyName('');

      // Refresh API keys list
      const keysData = await apiService.getApiKeys();
      if (keysData.api_keys || keysData.keys) {
        setApiKeys(keysData.api_keys || keysData.keys);
      }
    } catch (error) {
      console.error('Error creating API key:', error);
    }
  };

  const deleteApiKey = async (keyId: string) => {
    try {
      await apiService.deleteApiKey(keyId);
      
      // Refresh API keys list
      const keysData = await apiService.getApiKeys();
      if (keysData.api_keys || keysData.keys) {
        setApiKeys(keysData.api_keys || keysData.keys);
      }
    } catch (error) {
      console.error('Error deleting API key:', error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getSubscriptionIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'premium': return <Crown className="h-5 w-5 text-yellow-500" />;
      case 'pro': return <Shield className="h-5 w-5 text-purple-500" />;
      case 'basic': return <Zap className="h-5 w-5 text-blue-500" />;
      default: return <Key className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'processing': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      case 'queued': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="py-8 px-4">
          <div className="max-w-7xl mx-auto">
            <DashboardSkeleton />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="py-8 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Welcome back, {profile?.full_name || profile?.email || 'User'}
              </p>
            </div>
            <Button 
              onClick={fetchDashboardData} 
              disabled={refreshing}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Videos Processed</p>
                    <p className="text-2xl font-bold text-black">
                      {usageStats?.videos_processed_this_month || 0} / {usageStats?.videos_limit || 0}
                    </p>
                    <Progress value={usageStats ? (usageStats.videos_processed_this_month / usageStats.videos_limit) * 100 : 0} className="mt-2" />
                  </div>
                  <FileVideo className="h-8 w-8 text-black" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Subscription</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {usageStats?.subscription_tier || 'Free'}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">{usageStats?.days_remaining || 0} days remaining</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">API Keys</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {apiKeys?.length || 0}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">Total created</p>
                  </div>
                  <Key className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Jobs</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {jobs?.length || 0}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">All time</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="jobs">Jobs</TabsTrigger>
              <TabsTrigger value="api-keys">API Keys</TabsTrigger>
              <TabsTrigger value="usage">Usage</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Jobs */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileVideo className="h-5 w-5 mr-2" />
                      Recent Jobs
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {jobs.length === 0 ? (
                      <div className="text-center py-8">
                        <FileVideo className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500">No jobs yet. Upload a video to get started!</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {jobs.slice(0, 5).map((job) => (
                          <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                            <div className="flex-1">
                              <p className="font-medium">{job.filename}</p>
                              <p className="text-sm text-gray-500">
                                {new Date(job.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <Badge className={getStatusColor(job.status)}>
                              {job.status}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Account Info */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Settings className="h-5 w-5 mr-2" />
                      Account Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-500">Email</p>
                      <p className="text-gray-900">{profile?.email}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-500">Subscription</p>
                      <div className="flex items-center space-x-2">
                        {getSubscriptionIcon(profile?.subscription_tier || 'free')}
                        <span className="capitalize">{profile?.subscription_tier || 'Free'}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-500">Member Since</p>
                      <p className="text-gray-900">
                        {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Recently'}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Jobs Tab */}
            <TabsContent value="jobs">
              <Card>
                <CardHeader>
                  <CardTitle>All Jobs</CardTitle>
                </CardHeader>
                <CardContent>
                  {jobs.length === 0 ? (
                    <div className="text-center py-12">
                      <FileVideo className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs yet</h3>
                      <p className="text-gray-500 mb-6">Upload your first video to get started with content filtering.</p>
                      <Button onClick={() => window.location.href = '/upload'}>
                        Upload Video
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {jobs.map((job) => (
                        <div key={job.id} className="flex items-center justify-between p-6 border rounded-lg hover:bg-gray-50">
                          <div className="flex-1">
                            <div className="flex items-center space-x-4">
                              <FileVideo className="h-6 w-6 text-gray-400" />
                              <div>
                                <p className="font-medium text-gray-900">{job.filename}</p>
                                <p className="text-sm text-gray-500">
                                  Created: {new Date(job.created_at).toLocaleString()}
                                </p>
                                {job.censoring_mode && (
                                  <p className="text-sm text-gray-500">
                                    Mode: {job.censoring_mode}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4">
                            <Badge className={getStatusColor(job.status)}>
                              {job.status}
                            </Badge>
                            {job.status === 'completed' && (
                              <Button size="sm" variant="outline">
                                <Download className="h-4 w-4 mr-1" />
                                Download
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

            {/* API Keys Tab */}
            <TabsContent value="api-keys">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>API Keys</CardTitle>
                    {/* Free tier: 3 API key limit */}
                    {apiKeys.length >= 3 ? (
                      <div className="text-sm text-gray-500">
                        <p>Free tier limit: 3/3 API keys</p>
                        <p className="text-xs">Delete a key to create a new one</p>
                      </div>
                    ) : (
                      <Button onClick={() => setShowApiKeyForm(true)}>
                        <Key className="h-4 w-4 mr-2" />
                        Create New Key ({apiKeys.length}/3)
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {showApiKeyForm && (
                    <div className="mb-6 p-4 border rounded-lg bg-gray-50">
                      <h3 className="font-medium mb-4">Create New API Key</h3>
                      <div className="flex space-x-4">
                        <input
                          type="text"
                          placeholder="API Key Name"
                          value={newApiKeyName}
                          onChange={(e) => setNewApiKeyName(e.target.value)}
                          className="flex-1 px-3 py-2 border rounded-md"
                        />
                        <Button onClick={createApiKey}>Create</Button>
                        <Button variant="outline" onClick={() => setShowApiKeyForm(false)}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  )}

                  {showNewApiKey && (
                    <div className="mb-6 p-4 border rounded-lg bg-green-50 border-green-200">
                      <h3 className="font-medium text-green-800 mb-2">New API Key Created</h3>
                      <p className="text-sm text-green-600 mb-4">
                        Save this key securely. You won't be able to see it again.
                      </p>
                      <div className="flex items-center space-x-2">
                        <code className="flex-1 p-2 bg-white border rounded text-sm">
                          {newApiKey}
                        </code>
                        <Button size="sm" onClick={() => copyToClipboard(newApiKey)}>
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setShowNewApiKey(false)}>
                          Close
                        </Button>
                      </div>
                    </div>
                  )}

                  {apiKeys.length === 0 ? (
                    <div className="text-center py-12">
                      <Key className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No API keys</h3>
                      <p className="text-gray-500">Create your first API key to access our API programmatically.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {apiKeys.map((key) => (
                        <div key={key.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <p className="font-medium">{key.name}</p>
                            <p className="text-sm text-gray-500">
                              Created: {new Date(key.created_at).toLocaleDateString()}
                            </p>
                            {key.last_used && (
                              <p className="text-sm text-gray-500">
                                Last used: {new Date(key.last_used).toLocaleDateString()}
                              </p>
                            )}
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => deleteApiKey(key.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Usage Tab */}
            <TabsContent value="usage">
              <Card>
                <CardHeader>
                  <CardTitle>Usage Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">Videos Processed</span>
                          <span className="text-sm text-gray-500">
                            {usageStats?.videos_processed_this_month || 0} / {usageStats?.videos_limit || 5}
                          </span>
                        </div>
                        <Progress 
                          value={usageStats ? (usageStats.videos_processed_this_month / usageStats.videos_limit) * 100 : 0} 
                        />
                      </div>
                      
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">API Keys</span>
                          <span className="text-sm text-gray-500">
                            {apiKeys?.length || 0} / 10
                          </span>
                        </div>
                        <Progress value={(apiKeys?.length || 0) * 10} />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <h3 className="font-medium mb-2">Current Plan</h3>
                        <div className="flex items-center space-x-2">
                          {getSubscriptionIcon(usageStats?.subscription_tier || 'free')}
                          <span className="capitalize">{usageStats?.subscription_tier || 'Free'}</span>
                        </div>
                        {usageStats?.days_remaining && (
                          <p className="text-sm text-gray-500 mt-1">
                            {usageStats.days_remaining} days remaining
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
