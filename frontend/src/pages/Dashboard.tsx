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
  Trash2
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8080';

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

const Dashboard: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
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
        window.location.href = '/login';
        return;
      }

      const [profileRes, jobsRes, keysRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/auth/profile`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/jobs`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/keys`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      // Check for authentication errors
      if (profileRes.status === 401 || jobsRes.status === 401 || keysRes.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }

      if (profileRes.ok) {
        const profileData = await profileRes.json();
        setProfile(profileData);
      }

      if (jobsRes.ok) {
        const jobsData = await jobsRes.json();
        setJobs(jobsData.jobs || []);
      }

      if (keysRes.ok) {
        const keysData = await keysRes.json();
        setApiKeys(keysData.api_keys || []);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setLoading(false);
    }
  };

  const refreshJobs = async () => {
    setRefreshing(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/jobs`, {
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
      const response = await fetch(`${API_BASE_URL}/api/download/${jobId}`, {
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
      const response = await fetch(`${API_BASE_URL}/api/keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
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
      const response = await fetch(`${API_BASE_URL}/api/keys/${keyId}`, {
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

  const getSubscriptionIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'basic': return <Zap className="h-5 w-5 text-blue-500" />;
      case 'pro': return <Shield className="h-5 w-5 text-purple-500" />;
      case 'enterprise': return <Crown className="h-5 w-5 text-amber-500" />;
      default: return null;
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
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
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

  const usagePercentage = profile.monthly_limit > 0 
    ? (profile.usage_count / profile.monthly_limit) * 100 
    : 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {profile.name}</p>
        </div>

        {/* Overview Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Subscription</p>
                  <div className="flex items-center mt-1">
                    {getSubscriptionIcon(profile.subscription_tier)}
                    <p className="text-2xl font-bold text-gray-900 ml-2">
                      {profile.subscription_tier.charAt(0).toUpperCase() + profile.subscription_tier.slice(1)}
                    </p>
                  </div>
                </div>
                <CreditCard className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Usage This Month</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {profile.usage_count} / {profile.monthly_limit === -1 ? '∞' : profile.monthly_limit}
                  </p>
                  <Progress value={usagePercentage} className="mt-2" />
                </div>
                <BarChart3 className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Jobs</p>
                  <p className="text-2xl font-bold text-gray-900">{jobs.length}</p>
                </div>
                <FileVideo className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">API Keys</p>
                  <p className="text-2xl font-bold text-gray-900">{apiKeys.length}</p>
                </div>
                <Key className="h-8 w-8 text-gray-400" />
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
                    <p className="text-gray-900">{profile.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Name</label>
                    <p className="text-gray-900">{profile.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Member Since</label>
                    <p className="text-gray-900">{new Date(profile.created_at).toLocaleDateString()}</p>
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
                      {getSubscriptionIcon(profile.subscription_tier)}
                      <p className="text-gray-900 ml-2 capitalize">{profile.subscription_tier}</p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Status</label>
                    <p className="text-gray-900 capitalize">{profile.subscription_status}</p>
                  </div>
                  {profile.subscription_expires_at && (
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
