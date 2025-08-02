import React, { useState, useEffect } from 'react';
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

interface PlansResponse {
  plans: Record<string, Plan>;
  currency: string;
  payment_methods: string[];
  test_mode: boolean;
}

const PricingPage: React.FC = () => {
  const [plans, setPlans] = useState<Record<string, Plan>>({});
  const [loading, setLoading] = useState(true);
  const [testMode, setTestMode] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/payment/plans`);
      const data: PlansResponse = await response.json();
      
      setPlans(data.plans);
      setTestMode(data.test_mode);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch plans:', error);
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Please login to subscribe');
        return;
      }

      // Create payment order
      const response = await fetch(`${API_BASE_URL}/api/payment/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ plan_id: planId })
      });

      const orderData = await response.json();
      
      if (!response.ok) {
        throw new Error(orderData.error || 'Failed to create order');
      }

      // Initialize Razorpay payment
      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'AI Profanity Filter',
        description: `Subscribe to ${orderData.plan.name}`,
        order_id: orderData.order_id,
        prefill: {
          name: orderData.user.name,
          email: orderData.user.email
        },
        handler: async (response: any) => {
          // Verify payment
          try {
            const verifyResponse = await fetch(`${API_BASE_URL}/api/payment/verify-payment`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature
              })
            });

            const verifyData = await verifyResponse.json();
            
            if (verifyResponse.ok) {
              alert('Payment successful! Your subscription is now active.');
              window.location.reload();
            } else {
              throw new Error(verifyData.error || 'Payment verification failed');
            }
          } catch (error) {
            console.error('Payment verification error:', error);
            alert('Payment verification failed. Please contact support.');
          }
        },
        modal: {
          ondismiss: () => {
            console.log('Payment modal closed');
          }
        },
        theme: {
          color: '#3B82F6'
        }
      };

      // Load Razorpay script if not already loaded
      if (!window.Razorpay) {
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.onload = () => {
          const rzp = new window.Razorpay(options);
          rzp.open();
        };
        document.body.appendChild(script);
      } else {
        const rzp = new window.Razorpay(options);
        rzp.open();
      }

    } catch (error) {
      console.error('Subscription error:', error);
      alert('Failed to initiate payment. Please try again.');
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
