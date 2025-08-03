import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Crown, Check, Zap, Shield, Users, Phone } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8080';

interface Plan {
  id: string;
  name: string;
  price: number;
  currency: string;
  billing_cycle: string;
  features: string[];
}

const PricingPage: React.FC = () => {
  // Static plans with different pricing for each card
  const plans = {
    basic: {
      id: 'basic',
      name: 'Basic',
      price: 799,
      currency: '₹',
      billing_cycle: 'monthly',
      features: [
        '10,000 API calls per month',
        'Basic profanity detection',
        'Text content filtering',
        'Email support',
        'Community access'
      ]
    },
    pro: {
      id: 'pro',
      name: 'Pro',
      price: 2499,
      currency: '₹',
      billing_cycle: 'monthly',
      features: [
        '100,000 API calls per month',
        'Advanced AI detection',
        'Audio & video filtering',
        'Priority support',
        'Custom filters',
        'Analytics dashboard'
      ]
    },
    enterprise: {
      id: 'enterprise',
      name: 'Enterprise',
      price: 7999,
      currency: '₹',
      billing_cycle: 'monthly',
      features: [
        'Unlimited API calls',
        'Custom AI models',
        'Multi-media processing',
        '24/7 phone support',
        'White-label solution',
        'Advanced analytics',
        'SLA guarantee'
      ]
    }
  };

  const [loading] = useState(false);
  const [testMode] = useState(false);

  // Razorpay payment links for different plans
  const razorpayLinks = {
    basic: 'https://rzp.io/rzp/upgradebasic',
    pro: 'https://rzp.io/rzp/upgradepro',
    enterprise: 'https://rzp.io/rzp/upgradeenterprise'
  };

  const handleSubscribe = (planId: string) => {
    const paymentLink = razorpayLinks[planId as keyof typeof razorpayLinks];
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
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

        {/* Free Plan */}
        <div className="grid md:grid-cols-4 gap-8 mb-8">
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
                  <span className="text-sm">100MB file size</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">Basic detection</span>
                </li>
                <li className="flex items-center">
                  <Check className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">Hindi/English</span>
                </li>
              </ul>
              <Button variant="outline" className="w-full" disabled>
                Current Plan
              </Button>
            </CardContent>
          </Card>

          {/* Paid Plans */}
          {Object.entries(plans).map(([planId, plan]) => (
            <Card key={planId} className={`transition-all duration-200 ${getPlanColor(planId)} ${planId === 'pro' ? 'relative' : ''}`}>
              {planId === 'pro' && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-purple-500 text-white px-3 py-1">
                    Most Popular
                  </Badge>
                </div>
              )}
              <CardHeader className="text-center">
                {getPlanIcon(planId)}
                <CardTitle className="text-xl text-gray-900 mt-2">{plan.name}</CardTitle>
                <div className="text-3xl font-bold text-gray-900">₹{plan.price}</div>
                <p className="text-gray-600">per {plan.billing_cycle}</p>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <Check className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  className={`w-full ${planId === 'pro' ? 'bg-purple-500 hover:bg-purple-600' : ''}`}
                  onClick={() => handleSubscribe(planId)}
                >
                  Subscribe Now
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features Comparison */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-center mb-8">Feature Comparison</h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Features</th>
                  <th className="text-center py-3 px-4">Free</th>
                  <th className="text-center py-3 px-4">Basic</th>
                  <th className="text-center py-3 px-4">Pro</th>
                  <th className="text-center py-3 px-4">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3 px-4">Monthly Videos</td>
                  <td className="text-center py-3 px-4">10</td>
                  <td className="text-center py-3 px-4">100</td>
                  <td className="text-center py-3 px-4">500</td>
                  <td className="text-center py-3 px-4">Unlimited</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4">Max File Size</td>
                  <td className="text-center py-3 px-4">100MB</td>
                  <td className="text-center py-3 px-4">500MB</td>
                  <td className="text-center py-3 px-4">1GB</td>
                  <td className="text-center py-3 px-4">5GB</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4">API Access</td>
                  <td className="text-center py-3 px-4">❌</td>
                  <td className="text-center py-3 px-4">✅</td>
                  <td className="text-center py-3 px-4">✅</td>
                  <td className="text-center py-3 px-4">✅</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4">Priority Processing</td>
                  <td className="text-center py-3 px-4">❌</td>
                  <td className="text-center py-3 px-4">❌</td>
                  <td className="text-center py-3 px-4">✅</td>
                  <td className="text-center py-3 px-4">✅</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4">Custom Wordlists</td>
                  <td className="text-center py-3 px-4">❌</td>
                  <td className="text-center py-3 px-4">❌</td>
                  <td className="text-center py-3 px-4">✅</td>
                  <td className="text-center py-3 px-4">✅</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">Support</td>
                  <td className="text-center py-3 px-4">Community</td>
                  <td className="text-center py-3 px-4">Email</td>
                  <td className="text-center py-3 px-4">
                    <Phone className="h-4 w-4 inline mr-1" />
                    Phone
                  </td>
                  <td className="text-center py-3 px-4">Dedicated</td>
                </tr>
              </tbody>
            </table>
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
  );
};

// Extend window interface for Razorpay
declare global {
  interface Window {
    Razorpay: any;
  }
}

export default PricingPage;
