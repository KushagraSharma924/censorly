-- Migration: Add profile_image_url column to users table
-- Date: 2025-08-10
-- Description: Add profile image URL column to store user profile pictures

-- Add profile_image_url column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_image_url TEXT;

-- Add comment to document the column
COMMENT ON COLUMN users.profile_image_url IS 'URL to user profile image stored in Supabase Storage';

-- Optional: Add index for faster queries if needed
-- CREATE INDEX IF NOT EXISTS idx_users_profile_image_url ON users(profile_image_url);
