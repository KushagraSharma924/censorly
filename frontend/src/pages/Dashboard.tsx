import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Header } from '@/components/Header';
import { API_CONFIG } from '@/config/api';
import { 
  Key, 
  FileVideo, 
  BarChart3,
  RefreshCw,
  Download,
  Eye
} from 'lucide-react';

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: string;
}

interface Job {
  id: string;
  filename: string;
  status: string;
  progress: number;
  created_at: string;
}

interface APIKey {
  id: string;
  name: string;
  key: string;
  created_at: string;
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
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        window.location.href = '/login';
        return;
      }

      // Fetch all data in parallel
      const [profileRes, jobsRes, keysRes, usageRes] = await Promise.allSettled([
        fetch(`${API_CONFIG.BASE_URL}/api/auth/profile`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_CONFIG.BASE_URL}/api/jobs`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_CONFIG.BASE_URL}/api/keys`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_CONFIG.BASE_URL}/api/auth/usage`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      // Handle profile data
      if (profileRes.status === 'fulfilled' && profileRes.value.ok) {
        const profileData = await profileRes.value.json();
        if (profileData.user) {
          setProfile(profileData.user);
          localStorage.setItem('user', JSON.stringify(profileData.user));
        }
      }

      // Handle jobs data
      if (jobsRes.status === 'fulfilled' && jobsRes.value.ok) {
        const jobsData = await jobsRes.value.json();
        if (jobsData.jobs) {
          setJobs(jobsData.jobs);
        }
      }

      // Handle API keys data
      if (keysRes.status === 'fulfilled' && keysRes.value.ok) {
        const keysData = await keysRes.value.json();
        if (keysData.keys) {
          setApiKeys(keysData.keys);
        }
      }

      // Handle usage data
      if (usageRes.status === 'fulfilled' && usageRes.value.ok) {
        const usageData = await usageRes.value.json();
        setUsageStats(usageData);
      }

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="py-8 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-500" />
                <p className="text-gray-500">Loading dashboard...</p>
              </div>
            </div>
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
              onClick={handleRefresh} 
              disabled={refreshing}
              variant="outline"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Videos Processed</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {usageStats?.videos_processed_this_month || 0} / {usageStats?.videos_limit || 5}
                    </p>
                    <Progress 
                      value={usageStats ? (usageStats.videos_processed_this_month / usageStats.videos_limit) * 100 : 0} 
                      className="mt-2" 
                    />
                  </div>
                  <FileVideo className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Subscription</p>
                    <p className="text-2xl font-bold text-gray-900 capitalize">
                      {usageStats?.subscription_tier || 'Free'}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      {usageStats?.days_remaining || 0} days remaining
                    </p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-green-500" />
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
                  <Key className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Jobs */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Jobs</CardTitle>
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
                          Created: {new Date(job.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          job.status === 'completed' ? 'bg-green-100 text-green-800' :
                          job.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                          job.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {job.status}
                        </span>
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
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
