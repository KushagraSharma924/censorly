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
  if (user.profile_image_url) {
    return user.profile_image_url;
  }

  // Priority 2: Profile image field
  if (user.profile_image) {
    return user.profile_image;
  }

  // Priority 3: Avatar URL field
  if (user.avatar_url) {
    return user.avatar_url;
  }

  // Priority 4: Generate avatar using UI Avatars service
  const displayName = user.name || user.full_name || user.email.split('@')[0];
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&size=200&background=000000&color=ffffff&format=png&rounded=true&bold=true`;
};

/**
 * Get user initials for fallback display
 */
export const getUserInitials = (user: UserProfile | null): string => {
  if (!user) return 'U';

  const name = user.name || user.full_name;
  if (name) {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  }

  if (user.email) {
    return user.email[0].toUpperCase();
  }

  return 'U';
};

/**
 * Get user display name
 */
export const getUserDisplayName = (user: UserProfile | null): string => {
  if (!user) return 'User';
  return user.name || user.full_name || user.email.split('@')[0];
};

/**
 * Format user data from localStorage or API response
 */
export const formatUserData = (userData: any): UserProfile | null => {
  if (!userData) return null;

  return {
    id: userData.id,
    email: userData.email,
    name: userData.name,
    full_name: userData.full_name,
    profile_image: userData.profile_image,
    profile_image_url: userData.profile_image_url,
    avatar_url: userData.avatar_url,
    subscription_status: userData.subscription_status || 'active',
    subscription_tier: userData.subscription_tier || 'free',
    created_at: userData.created_at,
    updated_at: userData.updated_at,
    usage_count: userData.usage_count || 0,
    monthly_limit: userData.monthly_limit || 100,
  };
};
