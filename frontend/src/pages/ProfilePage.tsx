import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Header } from '@/components/Header';
import { authService } from '@/lib/auth-service';
import { getProfileImageUrl, getUserInitials, getUserDisplayName, formatUserData, type UserProfile } from '@/lib/user-utils';
import { ProfileAvatar } from '@/components/ProfileAvatar';
import { buildApiUrl, API_ENDPOINTS } from '@/config/api';
import { 
  User, 
  Mail, 
  Calendar, 
  Shield, 
  Key, 
  Bell, 
  Lock, 
  Edit3, 
  Save, 
  X,
  Crown,
  Settings,
  Eye,
  EyeOff,
  Camera,
  RefreshCw,
  AlertCircle,
  Check,
  Trash2
} from 'lucide-react';

interface ProfileFormData {
  name: string;
  email: string;
  current_password?: string;
  new_password?: string;
  confirm_password?: string;
}

const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [formData, setFormData] = useState<ProfileFormData>({
    name: '',
    email: ''
  });
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [passwordChangeMode, setPasswordChangeMode] = useState(false);
  const [imageUploading, setImageUploading] = useState(false);
  const [imageDeleting, setImageDeleting] = useState(false);

  useEffect(() => {
    if (isInitialLoad) {
      loadProfileData();
      setIsInitialLoad(false);
    }
  }, [isInitialLoad]);

  const loadProfileData = async () => {
    setLoading(true);
    try {
      await fetchProfile();
      fetchUsageStats(); // Call after profile is loaded
    } finally {
      setLoading(false);
    }
  };

  const fetchUsageStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      // TODO: Re-enable when backend endpoint is available
      // Temporarily using mock data due to backend deployment pending
      
      // Set some default usage data for now
      setProfile(prev => prev ? {
        ...prev,
        usage_count: 15,
        monthly_limit: 100
      } : null);
      
    } catch (error) {
      // Silently handle error - usage stats are not critical
    }
  };

  const fetchProfile = async () => {
    try {
      // First try to get cached user data
      const cachedUser = authService.getCurrentUser();
      if (cachedUser && cachedUser.email) {
        const formattedUser = formatUserData(cachedUser);
        if (formattedUser) {
          setProfile(formattedUser);
          
          // Update form data with current profile values
          setFormData({
            name: formattedUser.name || formattedUser.full_name || '',
            email: formattedUser.email || ''
          });
        }
      }

      // Then fetch fresh data from API
      const freshProfile = await authService.getProfile();
      
      if (freshProfile && freshProfile.email) {
        const formattedProfile = formatUserData(freshProfile);
        if (formattedProfile) {
          setProfile(formattedProfile);
          
          // Update form data with fresh profile values
          setFormData({
            name: formattedProfile.name || formattedProfile.full_name || '',
            email: formattedProfile.email || ''
          });
        }
      }
      
    } catch (error) {
      console.error('Profile fetch error:', error);
      if (error instanceof Error && error.message.includes('401')) {
        // Redirect to login on authentication error
        window.location.href = '/login';
        return;
      }
      setError('Failed to load profile data');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.USER.PROFILE), {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email
        })
      });

      if (response.ok) {
        const updatedData = await response.json();
        
        // Update profile state directly instead of refetching
        if (updatedData.user || updatedData.profile || updatedData) {
          const newProfileData = updatedData.user || updatedData.profile || updatedData;
          const formattedProfile = formatUserData(newProfileData);
          if (formattedProfile) {
            setProfile(formattedProfile);
            // Update localStorage with fresh data
            localStorage.setItem('user', JSON.stringify(newProfileData));
            // Notify Header component of user data update
            window.dispatchEvent(new CustomEvent('userDataUpdated'));
          }
        }
        
        setMessage('Profile updated successfully');
        setIsEditing(false);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update profile');
      }
    } catch (error) {
      setError('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleProfilePhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image size must be less than 5MB');
      return;
    }

    setImageUploading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required');
        return;
      }

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('profile_image', file);

      const response = await fetch(buildApiUrl(API_ENDPOINTS.USER.UPLOAD_PROFILE_IMAGE), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        
        // Update profile with new image URL
        if (result.profile_image_url || result.image_url) {
          const updatedProfile = {
            ...profile,
            profile_image_url: result.profile_image_url || result.image_url,
            profile_image: result.profile_image_url || result.image_url
          };
          
          setProfile(updatedProfile);
          
          // Update localStorage
          const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
          const updatedUser = {
            ...currentUser,
            profile_image_url: result.profile_image_url || result.image_url,
            profile_image: result.profile_image_url || result.image_url
          };
          localStorage.setItem('user', JSON.stringify(updatedUser));
          
          // Notify Header component
          window.dispatchEvent(new CustomEvent('userDataUpdated'));
          
          setMessage('Profile photo updated successfully');
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to upload profile photo');
      }
    } catch (error) {
      console.error('Profile photo upload error:', error);
      setError('Failed to upload profile photo');
    } finally {
      setImageUploading(false);
      // Reset file input
      event.target.value = '';
    }
  };

  const handleDeleteProfilePhoto = async () => {
    if (!profile?.profile_image_url) {
      setError('No profile photo to delete');
      return;
    }

    setImageDeleting(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Authentication required');
        return;
      }

      const response = await fetch(buildApiUrl(API_ENDPOINTS.USER.DELETE_PROFILE_IMAGE), {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        // Update profile to remove image
        const updatedProfile = {
          ...profile,
          profile_image_url: '',
          profile_image: ''
        };
        
        setProfile(updatedProfile);
        
        // Update localStorage
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        const updatedUser = {
          ...currentUser,
          profile_image_url: '',
          profile_image: ''
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        
        // Notify Header component
        window.dispatchEvent(new CustomEvent('userDataUpdated'));
        
        setMessage('Profile photo deleted successfully');
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to delete profile photo');
      }
    } catch (error) {
      console.error('Profile photo delete error:', error);
      setError('Failed to delete profile photo');
    } finally {
      setImageDeleting(false);
    }
  };

  const handleChangePassword = async () => {
    if (!formData.current_password || !formData.new_password || !formData.confirm_password) {
      setError('All password fields are required');
      return;
    }

    if (formData.new_password !== formData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    if (formData.new_password.length < 6) {
      setError('New password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    setMessage('');
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.USER.CHANGE_PASSWORD), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: formData.current_password,
          new_password: formData.new_password
        })
      });

      if (response.ok) {
        setMessage('Password changed successfully');
        setPasswordChangeMode(false);
        setFormData(prev => ({
          ...prev,
          current_password: '',
          new_password: '',
          confirm_password: ''
        }));
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to change password');
      }
    } catch (error) {
      setError('Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const getSubscriptionIcon = (tier?: string) => {
    switch (tier?.toLowerCase()) {
      case 'premium':
      case 'pro':
        return <Crown className="h-5 w-5 text-yellow-500" />;
      case 'basic':
        return <Shield className="h-5 w-5 text-blue-500" />;
      default:
        return <User className="h-5 w-5 text-gray-500" />;
    }
  };

  const getSubscriptionColor = (tier?: string) => {
    switch (tier?.toLowerCase()) {
      case 'premium':
      case 'pro':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'basic':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (!profile) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="flex justify-center items-center py-20">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-blue-200 rounded-full animate-spin border-t-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="py-8 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Page Title */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-black">Profile Settings</h1>
            <p className="text-gray-700">Manage your account settings and preferences</p>
          </div>

          {/* Messages */}
          {message && (
            <Alert className="mb-6 border-green-200 bg-green-50">
              <AlertDescription className="text-green-700">
                {message}
              </AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert className="mb-6 border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          )}

          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
              <TabsTrigger value="subscription">Subscription</TabsTrigger>
            </TabsList>

            {/* Profile Tab */}
            <TabsContent value="profile">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center space-x-2">
                      <User className="h-5 w-5" />
                      <span>Profile Information</span>
                    </CardTitle>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        if (isEditing) {
                          setIsEditing(false);
                          setFormData({
                            name: profile.name || profile.full_name || '',
                            email: profile.email || ''
                          });
                        } else {
                          setIsEditing(true);
                        }
                      }}
                    >
                      {isEditing ? (
                        <>
                          <X className="h-4 w-4 mr-2" />
                          Cancel
                        </>
                      ) : (
                        <>
                          <Edit3 className="h-4 w-4 mr-2" />
                          Edit
                        </>
                      )}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Profile Picture */}
                  <div className="flex items-center space-x-6">
                    <div className="relative group">
                      <div className="w-20 h-20 rounded-full overflow-hidden border-4 border-white shadow-lg">
                        <ProfileAvatar 
                          user={profile}
                          size="xl"
                          showSkeleton={isInitialLoad}
                          className="w-full h-full"
                        />
                      </div>
                      
                      {/* Hidden file input */}
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleProfilePhotoUpload}
                        className="hidden"
                        id="profile-photo-upload"
                        disabled={imageUploading}
                      />
                      
                      {/* Camera button that triggers file input */}
                      <label
                        htmlFor="profile-photo-upload"
                        className={`absolute bottom-0 right-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white shadow-lg hover:bg-blue-700 transition-colors group-hover:scale-110 transform duration-200 cursor-pointer ${
                          imageUploading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        {imageUploading ? (
                          <RefreshCw className="w-3 h-3 animate-spin" />
                        ) : (
                          <Camera className="w-3 h-3" />
                        )}
                      </label>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold">{getUserDisplayName(profile)}</h3>
                      <p className="text-gray-600">{profile.email}</p>
                      <p className="text-sm text-gray-500">
                        Member since {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        User ID: {profile.id}
                      </p>
                      {imageUploading && (
                        <p className="text-xs text-blue-600 mt-2 flex items-center">
                          <RefreshCw className="w-3 h-3 animate-spin mr-1" />
                          Uploading photo...
                        </p>
                      )}
                      {imageDeleting && (
                        <p className="text-xs text-red-600 mt-2 flex items-center">
                          <RefreshCw className="w-3 h-3 animate-spin mr-1" />
                          Deleting photo...
                        </p>
                      )}
                      <div className="flex items-center space-x-4 mt-2">
                        <p className="text-xs text-gray-400">
                          Click the camera icon to change your profile photo
                        </p>
                        {profile.profile_image_url && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={handleDeleteProfilePhoto}
                            disabled={imageDeleting || imageUploading}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs p-1 h-auto"
                          >
                            <Trash2 className="w-3 h-3 mr-1" />
                            Remove
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Form Fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={!isEditing ? 'bg-gray-50' : ''}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={!isEditing ? 'bg-gray-50' : ''}
                      />
                    </div>
                  </div>

                  {/* Save Button */}
                  {isEditing && (
                    <div className="flex justify-end">
                      <Button onClick={handleSaveProfile} disabled={loading}>
                        <Save className="h-4 w-4 mr-2" />
                        {loading ? 'Saving...' : 'Save Changes'}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Security Tab */}
            <TabsContent value="security">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Lock className="h-5 w-5" />
                    <span>Security Settings</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Password Change Section */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-semibold">Password</h3>
                        <p className="text-sm text-gray-600">Keep your account secure with a strong password</p>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => setPasswordChangeMode(!passwordChangeMode)}
                      >
                        {passwordChangeMode ? 'Cancel' : 'Change Password'}
                      </Button>
                    </div>

                    {passwordChangeMode && (
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="current_password">Current Password</Label>
                          <div className="relative">
                            <Input
                              id="current_password"
                              name="current_password"
                              type={showPassword ? 'text' : 'password'}
                              value={formData.current_password || ''}
                              onChange={handleInputChange}
                              placeholder="Enter current password"
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="new_password">New Password</Label>
                          <Input
                            id="new_password"
                            name="new_password"
                            type={showPassword ? 'text' : 'password'}
                            value={formData.new_password || ''}
                            onChange={handleInputChange}
                            placeholder="Enter new password"
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="confirm_password">Confirm New Password</Label>
                          <Input
                            id="confirm_password"
                            name="confirm_password"
                            type={showPassword ? 'text' : 'password'}
                            value={formData.confirm_password || ''}
                            onChange={handleInputChange}
                            placeholder="Confirm new password"
                          />
                        </div>

                        <Button onClick={handleChangePassword} disabled={loading}>
                          {loading ? 'Changing...' : 'Change Password'}
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Account Security Info */}
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2">Account Security</h3>
                    <div className="space-y-2 text-sm text-gray-600">
                      <p>• Use a strong, unique password for your account</p>
                      <p>• Never share your login credentials</p>
                      <p>• Log out from shared devices</p>
                      <p>• Contact support if you notice suspicious activity</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Subscription Tab */}
            <TabsContent value="subscription">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Crown className="h-5 w-5" />
                    <span>Subscription & Usage</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Current Plan */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        {getSubscriptionIcon(profile.subscription_tier)}
                        <div>
                          <h3 className="font-semibold">Current Plan</h3>
                          <Badge className={getSubscriptionColor(profile.subscription_tier)}>
                            {(profile.subscription_tier || 'Free').charAt(0).toUpperCase() + 
                             (profile.subscription_tier || 'Free').slice(1)}
                          </Badge>
                        </div>
                      </div>
                      <Button 
                        variant="outline"
                        onClick={() => window.location.href = '/pricing'}
                      >
                        Upgrade Plan
                      </Button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900">Monthly Usage</h4>
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-sm">
                            <span>API Calls</span>
                            <span className="font-mono">
                              {profile.usage_count || 0} / {profile.monthly_limit || 100}
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-300 ${
                                (profile.usage_count || 0) / (profile.monthly_limit || 100) > 0.8 
                                  ? 'bg-red-500' 
                                  : (profile.usage_count || 0) / (profile.monthly_limit || 100) > 0.6 
                                  ? 'bg-yellow-500' 
                                  : 'bg-blue-500'
                              }`}
                              style={{
                                width: `${Math.min(
                                  ((profile.usage_count || 0) / (profile.monthly_limit || 100)) * 100, 
                                  100
                                )}%`
                              }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {Math.round(((profile.usage_count || 0) / (profile.monthly_limit || 100)) * 100)}% used
                          </p>
                        </div>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900">Account Status</h4>
                        <div className="mt-2">
                          <Badge 
                            className={
                              profile.subscription_status === 'active' 
                                ? 'bg-green-100 text-green-800 border-green-200'
                                : profile.subscription_status === 'cancelled'
                                ? 'bg-red-100 text-red-800 border-red-200'
                                : 'bg-yellow-100 text-yellow-800 border-yellow-200'
                            }
                          >
                            {(profile.subscription_status || 'Active').charAt(0).toUpperCase() + 
                             (profile.subscription_status || 'Active').slice(1)}
                          </Badge>
                          <p className="text-xs text-gray-500 mt-2">
                            Resets monthly on {new Date().getDate()}th
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Plan Features */}
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-3">Plan Features</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span>API Rate Limit</span>
                        <span className="font-medium">{profile.monthly_limit || 0} calls/month</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Video Processing</span>
                        <span className="font-medium">
                          {profile.subscription_tier === 'free' ? 'Basic' : 'Advanced'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Support</span>
                        <span className="font-medium">
                          {profile.subscription_tier === 'free' ? 'Community' : 'Priority'}
                        </span>
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

export default ProfilePage;
