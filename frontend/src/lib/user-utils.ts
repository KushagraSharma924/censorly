import { EXTERNAL_URLS } from '@/config/api';

export interface UserProfile {
  id?: string;
  email: string;
  name?: string;
  full_name?: string;
  profile_image?: string;
  profile_image_url?: string;
  avatar_url?: string;
  subscription_status?: string;
  subscription_tier?: string;
  created_at?: string;
  updated_at?: string;
  usage_count?: number;
  monthly_limit?: number;
}

/**
 * Generate a consistent profile image URL for a user
 * This function is used across Header and ProfilePage components
 */
export const getProfileImageUrl = (user: UserProfile | null): string => {
  if (!user) return '';

  // Priority 1: Custom profile image uploaded by user
  if (user.profile_image_url && user.profile_image_url.trim()) {
    return user.profile_image_url;
  }

  // Priority 2: Profile image field
  if (user.profile_image && user.profile_image.trim()) {
    return user.profile_image;
  }

  // Priority 3: Avatar URL field
  if (user.avatar_url && user.avatar_url.trim()) {
    return user.avatar_url;
  }

  // Priority 4: Generate avatar using UI Avatars service
  let displayName = 'User';
  
  if (user.name && user.name.trim()) {
    displayName = user.name.trim();
  } else if (user.full_name && user.full_name.trim()) {
    displayName = user.full_name.trim();
  } else if (user.email && user.email.trim() && user.email.includes('@')) {
    displayName = user.email.split('@')[0];
  }

  return `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&size=200&background=000000&color=ffffff&format=png&rounded=true&bold=true`;
};

/**
 * Get user initials for fallback display
 */
export const getUserInitials = (user: UserProfile | null): string => {
  if (!user) return 'U';

  // Try to get initials from name
  const name = user.name || user.full_name;
  if (name && typeof name === 'string' && name.trim()) {
    const words = name.trim().split(/\s+/);
    const initials = words.map(word => word.charAt(0)).join('').toUpperCase().slice(0, 2);
    return initials || 'U';
  }

  // Fallback to email
  if (user.email && typeof user.email === 'string' && user.email.trim()) {
    return user.email.charAt(0).toUpperCase();
  }

  return 'U';
};

/**
 * Get user display name
 */
export const getUserDisplayName = (user: UserProfile | null): string => {
  if (!user) return 'User';
  
  // Try name first
  const name = user.name || user.full_name;
  if (name && typeof name === 'string' && name.trim()) {
    return name.trim();
  }
  
  // Fallback to email username
  if (user.email && typeof user.email === 'string' && user.email.trim() && user.email.includes('@')) {
    return user.email.split('@')[0];
  }
  
  return 'User';
};

/**
 * Format user data from localStorage or API response
 */
export const formatUserData = (userData: any): UserProfile | null => {
  if (!userData || typeof userData !== 'object') return null;

  // Ensure email exists as it's a required field
  if (!userData.email) return null;

  return {
    id: userData.id || '',
    email: userData.email || '',
    name: userData.name || '',
    full_name: userData.full_name || '',
    profile_image: userData.profile_image || '',
    profile_image_url: userData.profile_image_url || '',
    avatar_url: userData.avatar_url || '',
    subscription_status: userData.subscription_status || 'active',
    subscription_tier: userData.subscription_tier || 'free',
    created_at: userData.created_at || '',
    updated_at: userData.updated_at || '',
    usage_count: Number(userData.usage_count) || 0,
    monthly_limit: Number(userData.monthly_limit) || 100,
  };
};
