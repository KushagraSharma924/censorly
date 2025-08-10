import React, { useState } from 'react';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';
import { getProfileImageUrl, getUserInitials, getUserDisplayName, type UserProfile } from '@/lib/user-utils';

interface ProfileAvatarProps {
  user: UserProfile | null;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showSkeleton?: boolean;
  className?: string;
}

export const ProfileAvatar: React.FC<ProfileAvatarProps> = ({ 
  user, 
  size = 'md', 
  showSkeleton = false,
  className = '' 
}) => {
  const [isImageLoading, setIsImageLoading] = useState(true);
  const [hasImageError, setHasImageError] = useState(false);

  const getSizeClasses = () => {
    switch (size) {
      case 'sm': return 'h-6 w-6';
      case 'md': return 'h-8 w-8';
      case 'lg': return 'h-12 w-12';
      case 'xl': return 'h-20 w-20';
      default: return 'h-8 w-8';
    }
  };

  const getSkeletonSize = () => {
    switch (size) {
      case 'sm': return 'h-6 w-6';
      case 'md': return 'h-8 w-8';
      case 'lg': return 'h-12 w-12';
      case 'xl': return 'h-20 w-20';
      default: return 'h-8 w-8';
    }
  };

  const getTextSize = () => {
    switch (size) {
      case 'sm': return 'text-xs';
      case 'md': return 'text-xs';
      case 'lg': return 'text-lg';
      case 'xl': return 'text-2xl';
      default: return 'text-xs';
    }
  };

  // Show skeleton if explicitly requested or if user is null
  if (showSkeleton || !user) {
    return (
      <Skeleton 
        className={`rounded-full ${getSkeletonSize()} ${className}`} 
      />
    );
  }

  const profileImageUrl = getProfileImageUrl(user);
  const userInitials = getUserInitials(user);
  const displayName = getUserDisplayName(user);

  return (
    <Avatar className={`${getSizeClasses()} ${className}`}>
      <AvatarImage 
        src={profileImageUrl}
        alt={displayName || 'User'}
        onLoad={() => setIsImageLoading(false)}
        onError={() => {
          setIsImageLoading(false);
          setHasImageError(true);
        }}
      />
      <AvatarFallback className={`bg-black text-white ${getTextSize()} font-semibold`}>
        {(isImageLoading || hasImageError) ? (
          <Skeleton className={`rounded-full ${getSkeletonSize()}`} />
        ) : (
          userInitials
        )}
      </AvatarFallback>
    </Avatar>
  );
};
