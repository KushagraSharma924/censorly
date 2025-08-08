import React from 'react';
import { Heart, Github, Coffee, Shield, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { EXTERNAL_URLS } from '@/config/api';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-border/50 bg-muted/30">
      <div className="container max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">CleanMyVideo</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI-powered video content filtering for YouTubers, parents, and educational institutions.
              Keep your content family-friendly and professional.
            </p>
          </div>

          {/* Links Section */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Resources
            </h4>
            <div className="space-y-2">
              <a href="#privacy" className="flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors">
                <Shield className="w-4 h-4 mr-2" />
                Privacy Policy
              </a>
              <a href="#terms" className="flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors">
                <FileText className="w-4 h-4 mr-2" />
                Terms of Service
              </a>
              <a href={EXTERNAL_URLS.SOCIAL.GITHUB} className="flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors">
                <Github className="w-4 h-4 mr-2" />
                Open Source
              </a>
            </div>
          </div>

          {/* Support Section */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Support
            </h4>
            <div className="space-y-3">
              <Button variant="outline" size="sm" className="w-full justify-start">
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