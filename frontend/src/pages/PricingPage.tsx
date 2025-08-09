import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Crown, Check, Zap, Shield, Users, Phone, User, ArrowLeft } from 'lucide-react';
import { EXTERNAL_URLS } from '@/config/api';

// Simple auth check
const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

interface Plan {
  id: string;
  name: string;
  price: number;
  currency: string;
  billing_cycle: string;
  features: string[];
  comingSoon?: boolean;
}

const PricingPage: React.FC = () => {
  const loggedIn = isAuthenticated();
  
  // Updated plans - Only showing Free and Basic for now
  const plans = {
    basic: {
      id: 'basic',
      name: 'Basic',
      price: 999,
      currency: '₹',
      billing_cycle: 'monthly',
      popular: true,
      features: [
        '🚀 4x more videos (40 vs 10 per month)',
        '⚡ 4x more API processing calls (40 vs 10)',
        '📊 2x more general API calls (100 vs 50)',
        '🔑 More API keys (10 vs 3 maximum)',
        '💾 Same file size limit (100MB)',
        '🎯 Advanced regex & keyword detection',
        '🌍 English language support',
        '💬 Priority email support',
        '📈 Usage analytics dashboard',
        '🔄 Monthly usage resets'
      ]
    }
  };

  const [loading] = useState(false);
  const [testMode] = useState(false);

  // Payment links for different plans
  const paymentLinks = EXTERNAL_URLS.PAYMENT;

  const handleSubscribe = (planId: string) => {
    const plan = plans[planId as keyof typeof plans];
    
    // Check if plan is coming soon
    if ('comingSoon' in plan && plan.comingSoon) {
      alert('This plan is coming soon! Please check back later or contact support for early access.');
      return;
    }
    
    const paymentLink = paymentLinks[planId.toUpperCase() as keyof typeof paymentLinks];
    if (paymentLink) {
      // Open Razorpay payment link in new tab
      window.open(paymentLink, '_blank');
    } else {
      alert('Payment link not available for this plan');
    }
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'basic': return <Zap className="h-8 w-8 text-blue-500" />;
      case 'pro': return <Shield className="h-8 w-8 text-purple-500" />;
      case 'enterprise': return <Crown className="h-8 w-8 text-amber-500" />;
      default: return <Users className="h-8 w-8 text-gray-500" />;
    }
  };

  const getPlanColor = (planId: string) => {
    switch (planId) {
      case 'basic': return 'border-blue-200 hover:border-blue-300';
      case 'pro': return 'border-purple-200 hover:border-purple-300 ring-2 ring-purple-500';
      case 'enterprise': return 'border-amber-200 hover:border-amber-300';
      default: return 'border-gray-200 hover:border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 backdrop-blur-sm bg-white/95 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => window.location.href = '/'}
                className="mr-4 text-gray-700 hover:text-black hover:bg-gray-50"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
              <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center">
                <Crown className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-black">
                AI Profanity Filter - Pricing
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              {loggedIn ? (
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm" className="border-gray-300 text-black hover:bg-gray-50" onClick={() => window.location.href = '/dashboard'}>
                    <User className="h-4 w-4 mr-2" />
                    Dashboard
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="text-gray-700 hover:text-black hover:bg-gray-50"
                    onClick={() => {
                      localStorage.removeItem('access_token');
                      localStorage.removeItem('refresh_token');
                      localStorage.removeItem('user');
                      window.location.reload();
                    }}
                  >
                    Logout
                  </Button>
                </div>
              ) : (
                <Button onClick={() => window.location.href = '/login'}>
                  Get Started
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Scale your content moderation with our AI-powered profanity filter
          </p>
          {testMode && (
            <Badge variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-300">
              <Zap className="h-4 w-4 mr-1" />
              Test Mode - No Real Charges
            </Badge>
          )}
        </div>

        {/* Pricing Cards - Free and Basic Only */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-12">
          {/* Free Plan */}
          <Card className="border-gray-200 hover:border-gray-300 transition-colors">
            <CardHeader className="text-center">
              <Users className="h-8 w-8 text-gray-500 mx-auto mb-2" />
              <CardTitle className="text-xl text-gray-900">Free</CardTitle>
              <div className="text-3xl font-bold text-gray-900">₹0</div>
              <p className="text-gray-600">Forever free</p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 mb-6">
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">10 videos/month</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">10 API processing calls</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">50 general API calls</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">3 API keys maximum</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">100MB file size</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">Basic detection</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">Community support</span>
                </li>
              </ul>
              {loggedIn ? (
                <Button variant="outline" className="w-full" disabled>
                  Current Plan
                </Button>
              ) : (
                <Button variant="outline" className="w-full" onClick={() => window.location.href = '/login'}>
                  Get Started Free
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Basic Plan - Enhanced */}
          <Card className="border-blue-200 hover:border-blue-300 ring-2 ring-blue-500 relative transform hover:scale-105 transition-all duration-200 shadow-lg">
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <Badge className="bg-blue-500 text-white px-4 py-1 text-sm font-semibold">
                🔥 Most Popular
              </Badge>
            </div>
            <CardHeader className="text-center pt-8">
              <Zap className="h-10 w-10 text-blue-500 mx-auto mb-2" />
              <CardTitle className="text-2xl text-gray-900">Basic</CardTitle>
              <div className="text-4xl font-bold text-blue-600">₹999</div>
              <p className="text-gray-600">per month</p>
              <p className="text-sm text-blue-600 font-medium">⚡ 4x More Powerful Than Free</p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 mb-6">
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">40 videos/month</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">40 API processing calls</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">100 general API calls</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">10 API keys maximum</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">100MB file size</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">Advanced detection</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">Priority email support</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">Usage analytics dashboard</span>
                </li>
              </ul>
              <Button 
                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 text-lg"
                onClick={() => handleSubscribe('basic')}
              >
                🚀 Upgrade to Basic
              </Button>
              <p className="text-xs text-center text-gray-500 mt-2">
                Cancel anytime • 7-day money back guarantee
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Simple Feature Comparison */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-center mb-8">Why Upgrade to Basic?</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="font-semibold text-lg mb-2">4x More Capacity</h3>
              <p className="text-gray-600">Process 40 videos per month instead of just 10. Perfect for growing businesses and content creators.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Enhanced API Access</h3>
              <p className="text-gray-600">Get 4x more API processing calls and 2x general API calls for seamless integration.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Priority Support</h3>
              <p className="text-gray-600">Get priority email support and access to detailed usage analytics dashboard.</p>
            </div>
          </div>
          
          <div className="mt-8 text-center">
            <p className="text-gray-600 mb-4">
              <strong>Only ₹999/month</strong> - Less than ₹33 per day for 4x the capacity!
            </p>
            <Button 
              size="lg" 
              className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3"
              onClick={() => handleSubscribe('basic')}
            >
              🚀 Upgrade Now - Save 70% vs Pay-per-use
            </Button>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold mb-8">Frequently Asked Questions</h2>
          <div className="grid md:grid-cols-2 gap-8 text-left">
            <div>
              <h3 className="font-semibold mb-2">Can I change my plan anytime?</h3>
              <p className="text-gray-600">Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-gray-600">We accept all major credit cards, net banking, UPI, and digital wallets through Razorpay.</p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Is there a free trial?</h3>
              <p className="text-gray-600">Yes, our Free plan lets you process 10 videos per month at no cost.</p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Do you offer refunds?</h3>
              <p className="text-gray-600">We offer a 7-day money-back guarantee for all paid plans. Contact support for assistance.</p>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
};

// Extend window interface for Razorpay
declare global {
  interface Window {
    Razorpay: any;
  }
}

export default PricingPage;
