import React, { useState, useEffect } from 'react';
import { Video, Menu, User, LogOut, Github, Settings } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { EXTERNAL_URLS } from '@/config/api';
import { authService } from '@/lib/auth-service';
import { getProfileImageUrl, getUserInitials, getUserDisplayName, formatUserData, type UserProfile } from '@/lib/user-utils';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }

      // Try to get user from localStorage first
      const storedUser = authService.getCurrentUser();
      if (storedUser && storedUser.email) {
        const formattedUser = formatUserData(storedUser);
        if (formattedUser) {
          setUser(formattedUser);
          setIsAuthenticated(true);
        }
      }

      // Then fetch fresh data from API
      try {
        const freshProfile = await authService.getProfile();
        if (freshProfile && freshProfile.email) {
          const formattedProfile = formatUserData(freshProfile);
          if (formattedProfile) {
            setUser(formattedProfile);
            setIsAuthenticated(true);
          }
        }
      } catch (error) {
        console.log('Failed to fetch fresh profile, using cached data:', error);
        // If we have cached user data, keep using it
        if (!storedUser || !storedUser.email) {
          setIsAuthenticated(false);
          setUser(null);
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const navItems = [
    { label: 'Pricing', href: '/pricing' },
    { label: 'Documentation', href: '#docs' },
  ];

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state
      setUser(null);
      setIsAuthenticated(false);
      
      // Navigate to home
      navigate('/');
    }
  };

  if (loading) {
    return (
      <header className="bg-white border-b border-gray-200 backdrop-blur-sm bg-white/95 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="animate-pulse h-8 bg-gray-200 rounded w-32"></div>
            <div className="animate-pulse h-8 bg-gray-200 rounded w-24"></div>
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="bg-white border-b border-gray-200 backdrop-blur-sm bg-white/95 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full overflow-hidden bg-transparent flex items-center justify-center">
              <img 
                src="/logo.svg" 
                alt="Censorly Logo" 
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-black">Censorly</h1>
              <div className="flex items-center space-x-2 text-xs text-gray-600">
                <Badge variant="outline" className="text-xs px-2 py-0.5 border-gray-300">
                  Open Source
                </Badge>
                <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                <span>Professional Content Moderation</span>
              </div>
            </div>
          </Link>

          <div className="flex items-center space-x-6">
            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-6">
              {navItems.map((item) => (
                <Button 
                  key={item.label}
                  variant="ghost" 
                  className="text-gray-700 hover:text-black hover:bg-gray-50"
                  onClick={() => navigate(item.href)}
                >
                  {item.label}
                </Button>
              ))}
              <Button 
                variant="ghost" 
                className="text-gray-700 hover:text-black hover:bg-gray-50 flex items-center space-x-2"
                onClick={() => window.open('https://github.com/KushagraSharma924/ai-profanity-filter', '_blank')}
              >
                <Github className="h-4 w-4" />
                <span>GitHub</span>
              </Button>
            </nav>

            {/* Auth Section */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="border-gray-300 text-black hover:bg-gray-50 hidden md:flex"
                  onClick={() => navigate('/dashboard')}
                >
                  <User className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                      <Avatar className="h-8 w-8">
                        <AvatarImage 
                          src={getProfileImageUrl(user)} 
                          alt={getUserDisplayName(user)}
                        />
                        <AvatarFallback className="bg-black text-white text-xs font-semibold">
                          {getUserInitials(user)}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-56" align="end" forceMount>
                    <div className="flex items-center justify-start gap-2 p-2">
                      <div className="flex flex-col space-y-1 leading-none">
                        <p className="font-medium">{getUserDisplayName(user)}</p>
                        <p className="w-[200px] truncate text-sm text-muted-foreground">
                          {user?.email}
                        </p>
                      </div>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => navigate('/dashboard')}>
                      <User className="mr-2 h-4 w-4" />
                      Dashboard
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => navigate('/profile')}>
                      <Settings className="mr-2 h-4 w-4" />
                      Profile
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={handleLogout}>
                      <LogOut className="mr-2 h-4 w-4" />
                      Log out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ) : (
              <Button 
                className="bg-black text-white hover:bg-gray-800 shadow-sm" 
                onClick={() => navigate('/login')}
              >
                Get Started
              </Button>
            )}

            {/* Mobile Navigation */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm" className="md:hidden text-gray-700">
                  <Menu className="w-5 h-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="bg-white">
                <nav className="flex flex-col space-y-4 mt-8">
                  {navItems.map((item) => (
                    <Button
                      key={item.label}
                      variant="ghost"
                      className="justify-start text-gray-700 hover:text-black hover:bg-gray-50"
                      onClick={() => navigate(item.href)}
                    >
                      {item.label}
                    </Button>
                  ))}
                  
                  <Button 
                    variant="ghost" 
                    className="justify-start text-gray-700 hover:text-black hover:bg-gray-50 flex items-center space-x-2"
                    onClick={() => window.open('https://github.com/KushagraSharma924/ai-profanity-filter', '_blank')}
                  >
                    <Github className="h-4 w-4" />
                    <span>GitHub</span>
                  </Button>
                  
                  {isAuthenticated ? (
                    <>
                      <Button
                        variant="ghost"
                        className="justify-start text-gray-700 hover:text-black hover:bg-gray-50"
                        onClick={() => navigate('/dashboard')}
                      >
                        <User className="mr-2 h-4 w-4" />
                        Dashboard
                      </Button>
                      <Button 
                        variant="ghost" 
                        onClick={handleLogout} 
                        className="justify-start text-gray-700 hover:text-black hover:bg-gray-50"
                      >
                        <LogOut className="mr-2 h-4 w-4" />
                        Log out
                      </Button>
                    </>
                  ) : (
                    <Button 
                      className="bg-black text-white hover:bg-gray-800 shadow-sm w-full"
                      onClick={() => navigate('/login')}
                    >
                      Get Started
                    </Button>
                  )}
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;