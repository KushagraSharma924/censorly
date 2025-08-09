import React from 'react';
import { Heart, Github, Coffee, Shield, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { EXTERNAL_URLS } from '@/config/api';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-gray-200 bg-white">
      <div className="container max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full overflow-hidden bg-transparent flex items-center justify-center">
                <img 
                  src="/logo.svg" 
                  alt="Censorly Logo" 
                  className="w-full h-full object-cover"
                />
              </div>
              <h3 className="text-lg font-semibold text-black">Censorly</h3>
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">
              Professional content moderation platform for developers, businesses, and content creators.
              Keep your content clean and compliant.
            </p>
          </div>

          {/* Links Section */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-gray-600">
              Resources
            </h4>
            <div className="space-y-2">
              <a href="#privacy" className="flex items-center text-sm text-gray-700 hover:text-black transition-colors">
                <Shield className="w-4 h-4 mr-2" />
                Privacy Policy
              </a>
              <a href="#terms" className="flex items-center text-sm text-gray-700 hover:text-black transition-colors">
                <FileText className="w-4 h-4 mr-2" />
                Terms of Service
              </a>
              <a href={EXTERNAL_URLS.SOCIAL.GITHUB} className="flex items-center text-sm text-gray-700 hover:text-black transition-colors">
                <Github className="w-4 h-4 mr-2" />
                Open Source
              </a>
            </div>
          </div>

          {/* Support Section */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-gray-600">
              Support
            </h4>
            <div className="space-y-3">
              <Button variant="outline" size="sm" className="w-full justify-start border-gray-300 text-black hover:bg-gray-50">
                <Coffee className="w-4 h-4 mr-2" />
                Buy Me a Coffee
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Heart className="w-4 h-4 mr-2 text-red-500" />
                Donate via Razorpay
              </Button>
            </div>
          </div>
        </div>

        <div className="border-t border-border/50 mt-8 pt-8 text-center">
          <p className="text-sm text-muted-foreground">
            © 2024 CleanMyVideo. Made with ❤️ for content creators everywhere.
          </p>
        </div>
      </div>
    </footer>
  );
};