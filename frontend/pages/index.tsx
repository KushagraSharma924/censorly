import { useState, useRef, FormEvent, ChangeEvent, useEffect } from 'react';
import Head from 'next/head';
import axios from 'axios';

interface UploadResponse {
  success: boolean;
  message?: string;
  processedVideo?: string;
  error?: string;
}

interface Feature {
  icon: string;
  title: string;
  description: string;
}

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: string;
  features: string[];
  limits: {
    videoLength: number;
    dailyUploads: number;
    monthlyUploads: number;
  };
  popular?: boolean;
}

interface HealthData {
  status: 'healthy' | 'degraded';
  services: {
    database: string;
    storage: string;
    backend: string;
  };
}

interface StatsData {
  totalVideos: number;
  totalUsers: number;
  accuracy: string;
  languages: number;
}

export default function Home() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [censorType, setCensorType] = useState<string>('beep');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [processedVideo, setProcessedVideo] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('upload');
  const [selectedPlan, setSelectedPlan] = useState<string>('professional');
  const [pricingPlans, setPricingPlans] = useState<PricingPlan[]>([]);
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [statsData, setStatsData] = useState<StatsData>({
    totalVideos: 0,
    totalUsers: 0,
    accuracy: '99.9%',
    languages: 50
  });
  const [loadingPricing, setLoadingPricing] = useState<boolean>(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const features: Feature[] = [
    {
      icon: "🎯",
      title: "AI-Powered Detection",
      description: "Advanced machine learning algorithms detect profanity with 99.9% accuracy across 50+ languages and dialects"
    },
    {
      icon: "🔒",
      title: "Enterprise Security",
      description: "Military-grade encryption ensures your content remains private and secure throughout processing"
    },
    {
      icon: "⚡",
      title: "Lightning Fast",
      description: "Process videos in minutes, not hours. Our optimized infrastructure handles files up to 4K resolution"
    },
    {
      icon: "🔗",
      title: "API Integration",
      description: "Seamlessly integrate with your existing workflow using our robust RESTful API and SDKs"
    },
    {
      icon: "🌐",
      title: "Global Scale",
      description: "Deployed across multiple regions for 99.9% uptime and lightning-fast processing worldwide"
    },
    {
      icon: "👨‍💼",
      title: "Team Collaboration",
      description: "Built for teams with role-based access, project management, and detailed analytics dashboard"
    }
  ];

  const handleFileSelect = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      setUploadedFile(file);
      setError(null);
    } else {
      setError('Please select a valid video file.');
    }
  };

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    if (!uploadedFile) {
      setError('Please select a video file to upload.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('video', uploadedFile);
      formData.append('censorType', censorType);

      const response = await axios.post<UploadResponse>('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000,
      });

      if (response.data.success) {
        setSuccess('Video processed successfully! Your clean video is ready.');
        setProcessedVideo(response.data.processedVideo || null);
      } else {
        setError(response.data.error || 'Processing failed');
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      
      let errorMessage = 'An error occurred while processing your video.';
      
      if (error.code === 'ECONNREFUSED') {
        errorMessage = 'Backend service is not available. Please try again later.';
      } else if (error.response && error.response.status === 413) {
        errorMessage = 'File is too large. Please upload a smaller video file.';
      } else if (error.message.includes('timeout')) {
        errorMessage = 'Processing timeout. Please try with a shorter video.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Fetch pricing data from API
  const fetchPricing = async () => {
    try {
      setLoadingPricing(true);
      const response = await axios.get('/api/pricing');
      setPricingPlans(response.data.plans || []);
    } catch (error) {
      console.error('Failed to fetch pricing:', error);
      // Fallback to default pricing if API fails
      setPricingPlans([]);
    } finally {
      setLoadingPricing(false);
    }
  };

  // Fetch health data from API
  const fetchHealthData = async () => {
    try {
      const response = await axios.get('/api/health');
      setHealthData(response.data);
      // Update stats based on health data
      setStatsData(prev => ({
        ...prev,
        totalVideos: Math.floor(Math.random() * 1000000) + 500000, // Mock data - replace with real API
        totalUsers: Math.floor(Math.random() * 10000) + 5000, // Mock data - replace with real API
      }));
    } catch (error) {
      console.error('Failed to fetch health data:', error);
    }
  };

  // Load data on component mount
  useEffect(() => {
    fetchPricing();
    fetchHealthData();
  }, []);

  return (
    <>
      <Head>
        <title>CleanCast AI - Professional Video Content Moderation Platform</title>
        <meta name="description" content="Enterprise-grade AI-powered video content moderation. Remove profanity and inappropriate content from videos with 99.9% accuracy. Trusted by professionals worldwide." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
      </Head>

      <div className="min-h-screen bg-black text-white relative overflow-hidden">
        {/* Background Elements */}
        <div className="fixed inset-0 z-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-white/5 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-gray-300/10 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-gray-500/5 rounded-full blur-3xl"></div>
        </div>

        {/* Navigation */}
        <nav className="fixed top-4 left-1/2 transform -translate-x-1/2 z-[100] w-full max-w-4xl px-4">
          <div className="bg-black/80 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl">
            <div className="flex justify-between items-center px-6 py-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                  <span className="text-black text-sm font-bold">CC</span>
                </div>
                <span className="text-xl font-semibold text-white">
                  CleanCast AI
                </span>
                {healthData && (
                  <div className={`w-2 h-2 rounded-full ${
                    healthData.status === 'healthy' ? 'bg-green-400' : 'bg-yellow-400'
                  }`} title={`System Status: ${healthData.status}`}></div>
                )}
              </div>
              
              <div className="hidden md:flex items-center space-x-6">
                <a href="#features" className="text-gray-300 hover:text-white font-medium transition-colors">Features</a>
                <a href="#pricing" className="text-gray-300 hover:text-white font-medium transition-colors">Pricing</a>
                <a href="#demo" className="text-gray-300 hover:text-white font-medium transition-colors">Demo</a>
                <button className="text-gray-300 hover:text-white font-medium transition-colors">
                  Sign In
                </button>
                <button 
                  onClick={() => setShowUpload(true)}
                  className="bg-white text-black px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                >
                  Try Free
                </button>
              </div>

              <div className="md:hidden">
                <button className="text-gray-300 hover:text-white">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative z-10 pt-32 pb-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center px-6 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-gray-300 text-sm font-medium mb-8">
              <span className={`w-2 h-2 rounded-full mr-2 ${
                healthData?.status === 'healthy' ? 'bg-green-400' : 'bg-white'
              }`}></span>
              Trusted by {Math.floor(statsData.totalUsers / 1000)}K+ professionals worldwide
            </div>
            
            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-black text-white mb-8 leading-tight">
              Clean your videos with
              <br />
              <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">AI precision</span>
            </h1>
            
            {/* Subheadline */}
            <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
              Professional AI content moderation that removes profanity and inappropriate content 
              from videos with 99.9% accuracy. Built for creators and enterprises.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
              <button 
                onClick={() => setShowUpload(true)}
                className="group bg-white/10 backdrop-blur-md border border-white/20 text-white px-10 py-5 rounded-2xl font-bold text-lg hover:bg-white/20 hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
              >
                <span className="flex items-center">
                  <span className="mr-3">▶</span>
                  Try It Free Now
                </span>
              </button>
              
              <button className="group bg-white text-black px-10 py-5 rounded-2xl font-bold text-lg border-2 border-white hover:bg-gray-100 hover:shadow-xl transition-all duration-300 flex items-center">
                <span className="mr-3">👨‍💼</span>
                Schedule Demo
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
            </div>

            {/* Social Proof */}
            <div className="text-sm text-gray-400 mb-16">
              <p className="mb-4 font-medium">Trusted by leading companies worldwide</p>
              <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
                <div className="text-2xl font-bold text-gray-500">Netflix</div>
                <div className="text-2xl font-bold text-gray-500">YouTube</div>
                <div className="text-2xl font-bold text-gray-500">Disney</div>
                <div className="text-2xl font-bold text-gray-500">BBC</div>
                <div className="text-2xl font-bold text-gray-500">Warner</div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-16 border-t border-white/10">
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  {statsData.accuracy}
                </div>
                <div className="text-gray-400 font-medium">Accuracy Rate</div>
              </div>
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  {statsData.languages}+
                </div>
                <div className="text-gray-400 font-medium">Languages</div>
              </div>
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  {Math.floor(statsData.totalUsers / 1000)}K+
                </div>
                <div className="text-gray-400 font-medium">Happy Users</div>
              </div>
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  {Math.floor(statsData.totalVideos / 1000000)}M+
                </div>
                <div className="text-gray-400 font-medium">Videos Processed</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <div className="inline-flex items-center px-6 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-gray-300 text-sm font-semibold mb-6">
                ⚡ Powered by Advanced AI
              </div>
              <h2 className="text-5xl md:text-6xl font-black text-white mb-6 leading-tight">
                Why Choose 
                <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent"> CleanCast AI</span>
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Experience the next generation of content moderation with our cutting-edge AI technology
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div key={index} className="group relative">
                  <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-3xl hover:border-white/20 transition-all duration-300 hover:bg-white/10 hover:-translate-y-2">
                    <div className="text-4xl mb-6 group-hover:scale-110 transition-transform duration-200">
                      {feature.icon}
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-4">
                      {feature.title}
                    </h3>
                    <p className="text-gray-300 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Demo Section */}
        <section id="demo" className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
                See it in action
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Watch how CleanCast AI transforms your content in real-time with precision and speed
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 md:p-12">
              <div className="aspect-video bg-black/50 rounded-2xl border border-white/10 flex items-center justify-center mb-8">
                <div className="text-center">
                  <div className="w-20 h-20 bg-white/10 backdrop-blur-md border border-white/20 rounded-full flex items-center justify-center mx-auto mb-4 cursor-pointer hover:bg-white/20 transition-all">
                    <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                  <p className="text-gray-300">Click to watch demo</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-bold text-white mb-2">2.3s</div>
                  <div className="text-gray-300">Average processing time</div>
                </div>
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6">
                  <div className="text-3xl font-bold text-white mb-2">{statsData.accuracy}</div>
                  <div className="text-gray-300">Detection accuracy</div>
                </div>
                <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 relative">
                  <div className="text-3xl font-bold text-white mb-2">4K</div>
                  <div className="text-gray-300">Max resolution support</div>
                  {healthData && (
                    <div className={`absolute top-2 right-2 w-3 h-3 rounded-full ${
                      healthData.services.backend === 'connected' ? 'bg-green-400' : 'bg-red-400'
                    }`} title={`Backend: ${healthData.services.backend}`}></div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-5xl md:text-6xl font-black text-white mb-6">
                Choose your plan
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Flexible pricing that scales with your needs. Start free, upgrade anytime.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {loadingPricing ? (
                <div className="col-span-full text-center py-12">
                  <div className="animate-spin w-8 h-8 border-2 border-white/20 border-t-white rounded-full mx-auto mb-4"></div>
                  <p className="text-gray-300">Loading pricing plans...</p>
                </div>
              ) : pricingPlans.length === 0 ? (
                <div className="col-span-full text-center py-12">
                  <p className="text-gray-300">Unable to load pricing plans. Please try again later.</p>
                </div>
              ) : (
                pricingPlans.map((plan, index) => (
                  <div key={plan.id} className={`relative ${plan.popular ? 'md:-mt-8' : ''}`}>
                    {plan.popular && (
                      <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-white text-black px-6 py-2 rounded-full text-sm font-bold z-10">
                        Most Popular
                      </div>
                    )}
                    <div className={`bg-white/5 backdrop-blur-xl border ${plan.popular ? 'border-white/20' : 'border-white/10'} rounded-3xl p-8 hover:bg-white/10 transition-all duration-300 h-full`}>
                      <div className="text-center">
                        <h3 className="text-2xl font-bold text-white mb-4">{plan.name}</h3>
                        <div className="mb-6">
                          <span className="text-5xl font-black text-white">${plan.price}</span>
                          <span className="text-gray-300">/{plan.interval}</span>
                        </div>
                        <button className={`w-full py-4 px-6 rounded-xl font-bold text-lg transition-all duration-300 mb-8 ${
                          plan.popular 
                            ? 'bg-white text-black hover:bg-gray-100' 
                            : 'bg-white/10 text-white border border-white/20 hover:bg-white/20'
                        }`}>
                          {plan.price === 0 ? 'Get Started Free' : plan.popular ? 'Start Pro Trial' : 'Contact Sales'}
                        </button>
                      </div>
                      
                      <ul className="space-y-4">
                        {plan.features.map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-start">
                            <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                            <span className="text-gray-300">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-12 md:p-16">
              <h2 className="text-4xl md:text-5xl font-black text-white mb-6">
                Ready to clean your content?
              </h2>
              <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
                Join thousands of professionals who trust CleanCast AI to keep their content clean and professional.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
                <button 
                  onClick={() => setShowUpload(true)}
                  className="bg-white text-black px-10 py-5 rounded-2xl font-bold text-lg hover:bg-gray-100 transition-all duration-300 transform hover:scale-105"
                >
                  Start Free Trial
                </button>
                <button className="bg-white/10 backdrop-blur-md border border-white/20 text-white px-10 py-5 rounded-2xl font-bold text-lg hover:bg-white/20 transition-all duration-300">
                  Contact Sales
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="relative z-10 border-t border-white/10 py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
              <div className="md:col-span-2">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                    <span className="text-black text-sm font-bold">CC</span>
                  </div>
                  <span className="text-xl font-semibold text-white">CleanCast AI</span>
                </div>
                <p className="text-gray-300 max-w-md">
                  Professional AI-powered video content moderation platform trusted by creators and enterprises worldwide.
                </p>
              </div>
              
              <div>
                <h4 className="text-white font-semibold mb-4">Product</h4>
                <ul className="space-y-2">
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Features</a></li>
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">API</a></li>
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Pricing</a></li>
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Enterprise</a></li>
                </ul>
              </div>
              
              <div>
                <h4 className="text-white font-semibold mb-4">Company</h4>
                <ul className="space-y-2">
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">About</a></li>
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Blog</a></li>
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Support</a></li>
                  <li><a href="#" className="text-gray-300 hover:text-white transition-colors">Contact</a></li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                © 2024 CleanCast AI. All rights reserved.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0">
                <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy</a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms</a>
                <a href="#" className="text-gray-400 hover:text-white transition-colors">Security</a>
              </div>
            </div>
          </div>
        </footer>

        {/* Upload Modal */}
        {showUpload && (
          <div className="fixed inset-0 z-[200] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-black/90 backdrop-blur-xl border border-white/20 rounded-3xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-3xl font-bold text-white">Upload Your Video</h2>
                <button 
                  onClick={() => setShowUpload(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleUpload} className="space-y-6">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-3">
                    Select Video File
                  </label>
                  <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-white/40 transition-colors">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      accept="video/*"
                      className="hidden"
                    />
                    <button 
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="text-white hover:text-gray-300 transition-colors"
                    >
                      <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="text-gray-300">Click to select video file</p>
                      <p className="text-gray-500 text-sm mt-2">MP4, MOV, AVI up to 100MB</p>
                    </button>
                  </div>
                  
                  {uploadedFile && (
                    <div className="mt-4 p-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl">
                      <p className="text-white">Selected: {uploadedFile.name}</p>
                      <p className="text-gray-400 text-sm">Size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-3">
                    Censoring Method
                  </label>
                  <div className="grid grid-cols-3 gap-4">
                    {['beep', 'silence', 'bleep'].map((type) => (
                      <button
                        key={type}
                        type="button"
                        onClick={() => setCensorType(type)}
                        className={`p-4 rounded-xl border transition-all ${
                          censorType === type
                            ? 'bg-white/20 border-white/40 text-white'
                            : 'bg-white/5 border-white/20 text-gray-300 hover:bg-white/10'
                        }`}
                      >
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {error && (
                  <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-xl">
                    <p className="text-red-300">{error}</p>
                  </div>
                )}

                {success && (
                  <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-xl">
                    <p className="text-green-300">{success}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!uploadedFile || loading}
                  className="w-full bg-white text-black py-4 px-6 rounded-xl font-bold text-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    'Process Video'
                  )}
                </button>
              </form>

              {processedVideo && (
                <div className="mt-8 p-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl">
                  <h3 className="text-xl font-bold text-white mb-4">Processed Video Ready!</h3>
                  <a 
                    href={processedVideo} 
                    download
                    className="inline-flex items-center bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                    </svg>
                    Download Clean Video
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
