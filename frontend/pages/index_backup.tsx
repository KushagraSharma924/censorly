import { useState, useRef, FormEvent, ChangeEvent } from 'react';
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
  name: string;
  price: number;
  period: string;
  features: string[];
  popular?: boolean;
  cta: string;
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
  const fileInputRef = useRef<HTMLInputElement>(null);

  const features: Feature[] = [
    {
      icon: "🧠",
      title: "AI-Powered Detection",
      description: "Advanced machine learning algorithms detect profanity with 99.9% accuracy across 50+ languages and dialects"
    },
    {
      icon: "🛡️",
      title: "Enterprise Security",
      description: "Military-grade encryption ensures your content remains private and secure throughout processing"
    },
    {
      icon: "⚡",
      title: "Lightning Fast",
      description: "Process videos in minutes, not hours. Our optimized infrastructure handles files up to 4K resolution"
    },
    {
      icon: "🔧",
      title: "API Integration",
      description: "Seamlessly integrate with your existing workflow using our robust RESTful API and SDKs"
    },
    {
      icon: "🌍",
      title: "Global Scale",
      description: "Deployed across multiple regions for 99.9% uptime and lightning-fast processing worldwide"
    },
    {
      icon: "👥",
      title: "Team Collaboration",
      description: "Built for teams with role-based access, project management, and detailed analytics dashboard"
    }
  ];

  const pricingPlans: PricingPlan[] = [
    {
      name: "Starter",
      price: 0,
      period: "forever",
      features: [
        "Up to 5 minutes per video",
        "Standard processing speed",
        "Basic censoring options",
        "Community support",
        "720p max resolution",
        "5 videos per month"
      ],
      cta: "Get Started Free"
    },
    {
      name: "Professional",
      price: 49,
      period: "month",
      popular: true,
      features: [
        "Up to 60 minutes per video",
        "Priority processing",
        "Advanced censoring options",
        "Email & chat support",
        "4K resolution support",
        "API access",
        "Custom word filters",
        "Team collaboration",
        "Advanced analytics",
        "100 videos per month"
      ],
      cta: "Start Pro Trial"
    },
    {
      name: "Enterprise",
      price: 199,
      period: "month",
      features: [
        "Unlimited video length",
        "Fastest processing",
        "White-label solution",
        "24/7 phone support",
        "Custom integrations",
        "SLA guarantees",
        "Advanced analytics",
        "Dedicated account manager",
        "Custom AI models",
        "Unlimited videos"
      ],
      cta: "Contact Sales"
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

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
        {/* Navigation */}
        <nav className="fixed top-0 w-full bg-white/90 backdrop-blur-xl border-b border-slate-200/60 z-50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                    <span className="text-white text-lg font-bold">🎬</span>
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></div>
                </div>
                <div>
                  <span className="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                    CleanCast AI
                  </span>
                  <div className="text-xs text-slate-500 font-medium">Professional Platform</div>
                </div>
              </div>
              
              <div className="hidden lg:flex items-center space-x-8">
                <a href="#features" className="text-slate-600 hover:text-slate-900 font-medium transition-all duration-200 hover:scale-105">Features</a>
                <a href="#pricing" className="text-slate-600 hover:text-slate-900 font-medium transition-all duration-200 hover:scale-105">Pricing</a>
                <a href="#demo" className="text-slate-600 hover:text-slate-900 font-medium transition-all duration-200 hover:scale-105">Demo</a>
                <div className="h-6 w-px bg-slate-200"></div>
                <button className="text-slate-700 px-6 py-2.5 rounded-full font-medium hover:bg-slate-100 transition-all duration-200">
                  Sign In
                </button>
                <button 
                  onClick={() => setShowUpload(true)}
                  className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-8 py-2.5 rounded-full font-semibold hover:shadow-lg hover:scale-105 transition-all duration-200"
                >
                  Start Free Trial
                </button>
              </div>

              {/* Mobile Menu Button */}
              <div className="lg:hidden">
                <button className="text-slate-600 hover:text-slate-900">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="pt-32 pb-24 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
          {/* Background Elements */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-violet-400/20 to-purple-400/20 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-indigo-400/20 rounded-full blur-3xl"></div>
          </div>

          <div className="max-w-7xl mx-auto text-center relative">
            {/* Badge */}
            <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-violet-100 to-indigo-100 rounded-full text-violet-800 text-sm font-semibold mb-8 border border-violet-200/50 shadow-sm">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-3 animate-pulse"></span>
              Trusted by 10,000+ professionals • 99.9% uptime
            </div>
            
            {/* Main Headline */}
            <h1 className="text-6xl md:text-8xl font-black text-slate-900 mb-8 leading-[0.9] tracking-tight">
              Clean Your Videos
              <br />
              <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                AI Powered
              </span>
            </h1>
            
            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-4xl mx-auto leading-relaxed font-medium">
              Enterprise-grade AI content moderation that removes profanity and inappropriate content 
              from videos with <span className="text-violet-600 font-semibold">99.9% accuracy</span>. 
              Perfect for content creators, enterprises, and streaming platforms.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
              <button 
                onClick={() => setShowUpload(true)}
                className="group bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-10 py-5 rounded-2xl font-bold text-lg hover:shadow-2xl hover:shadow-violet-500/25 transform hover:scale-105 transition-all duration-300 relative overflow-hidden"
              >
                <span className="relative z-10 flex items-center">
                  <span className="mr-3">🚀</span>
                  Try It Free Now
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-violet-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
              
              <button className="group bg-white text-slate-700 px-10 py-5 rounded-2xl font-bold text-lg border-2 border-slate-200 hover:border-violet-200 hover:shadow-xl transition-all duration-300 flex items-center">
                <span className="mr-3">📅</span>
                Schedule Demo
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
            </div>

            {/* Social Proof */}
            <div className="text-sm text-slate-500 mb-16">
              <p className="mb-4 font-medium">Trusted by leading companies worldwide</p>
              <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
                <div className="text-2xl font-bold text-slate-400">Netflix</div>
                <div className="text-2xl font-bold text-slate-400">YouTube</div>
                <div className="text-2xl font-bold text-slate-400">Disney</div>
                <div className="text-2xl font-bold text-slate-400">BBC</div>
                <div className="text-2xl font-bold text-slate-400">Warner</div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-16 border-t border-slate-200/60">
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  99.9%
                </div>
                <div className="text-slate-600 font-medium">Accuracy Rate</div>
              </div>
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  50+
                </div>
                <div className="text-slate-600 font-medium">Languages</div>
              </div>
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  10K+
                </div>
                <div className="text-slate-600 font-medium">Happy Users</div>
              </div>
              <div className="group text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent mb-3 group-hover:scale-110 transition-transform duration-200">
                  1M+
                </div>
                <div className="text-slate-600 font-medium">Videos Processed</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-white relative">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <div className="inline-flex items-center px-4 py-2 bg-violet-100 rounded-full text-violet-800 text-sm font-semibold mb-6">
                ⚡ Powered by Advanced AI
              </div>
              <h2 className="text-5xl md:text-6xl font-black text-slate-900 mb-6 leading-tight">
                Why Choose 
                <span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent"> CleanCast AI</span>
              </h2>
              <p className="text-xl text-slate-600 max-w-3xl mx-auto">
                Experience the next generation of content moderation with our cutting-edge AI technology
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div key={index} className="group relative">
                  <div className="bg-gradient-to-br from-white to-slate-50 p-8 rounded-3xl border border-slate-200/60 hover:border-violet-200 transition-all duration-300 hover:shadow-xl hover:shadow-violet-500/10 hover:-translate-y-2">
                    <div className="text-4xl mb-6 group-hover:scale-110 transition-transform duration-200">
                      {feature.icon}
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-4">
                      {feature.title}
                    </h3>
                    <p className="text-slate-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Demo Section */}
        <section id="demo" className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-violet-50">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-5xl font-black text-slate-900 mb-6">
                See It In 
                <span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent"> Action</span>
              </h2>
              <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                Experience our AI in action. Upload a video and see the magic happen in real-time.
              </p>
            </div>

            <div className="bg-white rounded-3xl shadow-2xl shadow-violet-500/10 border border-slate-200/60 overflow-hidden">
              {/* Demo Tabs */}
              <div className="flex bg-slate-50 border-b border-slate-200/60">
                {['upload', 'process', 'result'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`flex-1 px-6 py-4 text-sm font-semibold transition-all duration-200 ${
                      activeTab === tab
                        ? 'bg-white text-violet-600 border-b-2 border-violet-600'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <span className="capitalize">{tab}</span>
                  </button>
                ))}
              </div>

              {/* Upload Content */}
              {activeTab === 'upload' && (
                <div className="p-12">
                  <form onSubmit={handleUpload} className="max-w-2xl mx-auto">
                    <div className="mb-8">
                      <label className="block text-lg font-semibold text-slate-900 mb-4">
                        Upload Your Video
                      </label>
                      <div 
                        className="group border-2 border-dashed border-slate-300 rounded-2xl p-12 text-center hover:border-violet-400 transition-all duration-300 cursor-pointer bg-gradient-to-br from-slate-50 to-white"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <div className="text-6xl mb-6 group-hover:scale-110 transition-transform duration-200">
                          {uploadedFile ? '✅' : '📁'}
                        </div>
                        <p className="text-xl text-slate-700 mb-2 font-medium">
                          {uploadedFile ? uploadedFile.name : 'Click to select or drag and drop your video file'}
                        </p>
                        <p className="text-slate-500">
                          Supports MP4, AVI, MOV, MKV, WebM (max 100MB)
                        </p>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="video/*"
                          onChange={handleFileSelect}
                          className="hidden"
                        />
                      </div>
                    </div>

                    {/* Censor Type Selection */}
                    <div className="mb-8">
                      <label className="block text-lg font-semibold text-slate-900 mb-4">
                        Censoring Method
                      </label>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        {[
                          { value: 'beep', label: 'Beep Sound', icon: '🔊' },
                          { value: 'silence', label: 'Silence', icon: '🔇' },
                          { value: 'replace', label: 'Replace Words', icon: '🔄' }
                        ].map((option) => (
                          <button
                            key={option.value}
                            type="button"
                            onClick={() => setCensorType(option.value)}
                            className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                              censorType === option.value
                                ? 'border-violet-500 bg-violet-50 text-violet-700'
                                : 'border-slate-200 bg-white text-slate-700 hover:border-violet-200'
                            }`}
                          >
                            <div className="text-2xl mb-2">{option.icon}</div>
                            <div className="font-medium">{option.label}</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Submit Button */}
                    <button
                      type="submit"
                      disabled={!uploadedFile || loading}
                      className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:shadow-lg hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                    >
                      {loading ? (
                        <span className="flex items-center justify-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Processing Video...
                        </span>
                      ) : (
                        '🚀 Process Video'
                      )}
                    </button>

                    {/* Error/Success Messages */}
                    {error && (
                      <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
                        ❌ {error}
                      </div>
                    )}
                    
                    {success && (
                      <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl text-green-700">
                        ✅ {success}
                        {processedVideo && (
                          <div className="mt-4">
                            <a
                              href={processedVideo}
                              download
                              className="inline-flex items-center text-green-600 hover:text-green-800 font-medium"
                            >
                              📥 Download Processed Video
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </form>
                </div>
              )}

              {/* Process Content */}
              {activeTab === 'process' && (
                <div className="p-12 text-center">
                  <div className="max-w-2xl mx-auto">
                    <div className="text-6xl mb-8">🤖</div>
                    <h3 className="text-2xl font-bold text-slate-900 mb-4">AI Processing Pipeline</h3>
                    <p className="text-slate-600 mb-8">Our advanced AI analyzes your video through multiple stages</p>
                    
                    <div className="space-y-6">
                      {[
                        { step: "Audio Extraction", desc: "Extract and analyze audio tracks", icon: "🎵" },
                        { step: "Speech Recognition", desc: "Convert speech to text with high accuracy", icon: "🗣️" },
                        { step: "Content Analysis", desc: "Identify inappropriate content using AI", icon: "🧠" },
                        { step: "Smart Censoring", desc: "Apply chosen censoring method precisely", icon: "✨" },
                      ].map((item, index) => (
                        <div key={index} className="flex items-center p-4 bg-slate-50 rounded-xl">
                          <div className="text-2xl mr-4">{item.icon}</div>
                          <div className="text-left">
                            <div className="font-semibold text-slate-900">{item.step}</div>
                            <div className="text-slate-600 text-sm">{item.desc}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Result Content */}
              {activeTab === 'result' && (
                <div className="p-12 text-center">
                  <div className="max-w-2xl mx-auto">
                    <div className="text-6xl mb-8">🎉</div>
                    <h3 className="text-2xl font-bold text-slate-900 mb-4">Perfect Results Every Time</h3>
                    <p className="text-slate-600 mb-8">Get professional-quality cleaned videos ready for any platform</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-6 bg-slate-50 rounded-xl">
                        <div className="text-3xl mb-3">📊</div>
                        <h4 className="font-semibold text-slate-900 mb-2">Detailed Analytics</h4>
                        <p className="text-slate-600 text-sm">Complete report of detected and censored content</p>
                      </div>
                      <div className="p-6 bg-slate-50 rounded-xl">
                        <div className="text-3xl mb-3">💾</div>
                        <h4 className="font-semibold text-slate-900 mb-2">Multiple Formats</h4>
                        <p className="text-slate-600 text-sm">Download in various formats and qualities</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-24 px-4 sm:px-6 lg:px-8 bg-white">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <div className="inline-flex items-center px-4 py-2 bg-green-100 rounded-full text-green-800 text-sm font-semibold mb-6">
                💰 Simple, Transparent Pricing
              </div>
              <h2 className="text-5xl md:text-6xl font-black text-slate-900 mb-6 leading-tight">
                Choose Your 
                <span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">Perfect Plan</span>
              </h2>
              <p className="text-xl text-slate-600 max-w-3xl mx-auto">
                Start free, scale as you grow. No hidden fees, no surprises.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {pricingPlans.map((plan, index) => (
                <div
                  key={index}
                  className={`relative rounded-3xl p-8 transition-all duration-300 hover:-translate-y-2 ${
                    plan.popular
                      ? 'bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-2xl shadow-violet-500/25 scale-105'
                      : 'bg-white border-2 border-slate-200 hover:border-violet-200 hover:shadow-xl'
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <div className="bg-gradient-to-r from-yellow-400 to-orange-400 text-slate-900 px-6 py-2 rounded-full text-sm font-bold">
                        ⭐ Most Popular
                      </div>
                    </div>
                  )}

                  <div className="text-center mb-8">
                    <h3 className={`text-2xl font-bold mb-2 ${plan.popular ? 'text-white' : 'text-slate-900'}`}>
                      {plan.name}
                    </h3>
                    <div className="flex items-baseline justify-center">
                      <span className={`text-5xl font-black ${plan.popular ? 'text-white' : 'text-slate-900'}`}>
                        ${plan.price}
                      </span>
                      <span className={`text-lg ml-2 ${plan.popular ? 'text-violet-100' : 'text-slate-500'}`}>
                        /{plan.period}
                      </span>
                    </div>
                  </div>

                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start">
                        <span className={`mr-3 mt-1 ${plan.popular ? 'text-violet-200' : 'text-green-500'}`}>
                          ✓
                        </span>
                        <span className={`${plan.popular ? 'text-violet-100' : 'text-slate-600'}`}>
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>

                  <button
                    className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-200 ${
                      plan.popular
                        ? 'bg-white text-violet-600 hover:bg-violet-50'
                        : 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:shadow-lg hover:scale-105'
                    }`}
                  >
                    {plan.cta}
                  </button>
                </div>
              ))}
            </div>

            {/* Additional pricing info */}
            <div className="text-center mt-16">
              <p className="text-slate-600 mb-6">All plans include 14-day free trial • No setup fees • Cancel anytime</p>
              <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-slate-500">
                <span className="flex items-center">
                  <span className="mr-2">🔒</span>
                  Enterprise Security
                </span>
                <span className="flex items-center">
                  <span className="mr-2">☁️</span>
                  Cloud Processing
                </span>
                <span className="flex items-center">
                  <span className="mr-2">📞</span>
                  24/7 Support
                </span>
                <span className="flex items-center">
                  <span className="mr-2">🔧</span>
                  API Access
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-600 relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Ccircle cx="7" cy="7" r="1"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
          
          <div className="max-w-4xl mx-auto text-center relative">
            <h2 className="text-5xl md:text-6xl font-black text-white mb-8 leading-tight">
              Ready to Clean Your Content?
            </h2>
            <p className="text-xl text-violet-100 mb-12 max-w-2xl mx-auto">
              Join thousands of professionals who trust CleanCast AI for their content moderation needs.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <button 
                onClick={() => setShowUpload(true)}
                className="bg-white text-violet-600 px-10 py-5 rounded-2xl font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all duration-300"
              >
                <span className="mr-3">🚀</span>
                Start Free Trial
              </button>
              <button className="border-2 border-white text-white px-10 py-5 rounded-2xl font-bold text-lg hover:bg-white hover:text-violet-600 transition-all duration-300">
                <span className="mr-3">📞</span>
                Talk to Sales
              </button>
            </div>
            
            <div className="mt-12 text-violet-200 text-sm">
              No credit card required • 14-day free trial • Setup in minutes
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-slate-900 text-white py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
              <div className="md:col-span-1">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-xl flex items-center justify-center">
                    <span className="text-white text-lg font-bold">🎬</span>
                  </div>
                  <span className="text-2xl font-bold">CleanCast AI</span>
                </div>
                <p className="text-slate-400 mb-6">
                  Professional AI-powered video content moderation platform trusted by thousands worldwide.
                </p>
                <div className="flex space-x-4">
                  <a href="#" className="text-slate-400 hover:text-white transition-colors">
                    <span className="sr-only">Twitter</span>
                    🐦
                  </a>
                  <a href="#" className="text-slate-400 hover:text-white transition-colors">
                    <span className="sr-only">LinkedIn</span>
                    💼
                  </a>
                  <a href="#" className="text-slate-400 hover:text-white transition-colors">
                    <span className="sr-only">GitHub</span>
                    🐙
                  </a>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Product</h3>
                <ul className="space-y-2 text-slate-400">
                  <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Integrations</a></li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Company</h3>
                <ul className="space-y-2 text-slate-400">
                  <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Support</h3>
                <ul className="space-y-2 text-slate-400">
                  <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center">
              <p className="text-slate-400 text-sm">
                © 2025 CleanCast AI. All rights reserved.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0 text-sm text-slate-400">
                <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
                <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
                <a href="#" className="hover:text-white transition-colors">Cookie Policy</a>
              </div>
            </div>
          </div>
        </footer>

}
                  </div>
                </div>

                {/* Censor Type */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Censoring Method
                  </label>
                  <select
                    value={censorType}
                    onChange={(e) => setCensorType(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="beep">Audio Beep</option>
                    <option value="silence">Silence</option>
                    <option value="blur">Visual Blur</option>
                  </select>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={!uploadedFile || loading}
                  className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <>
                      <i className="fas fa-spinner fa-spin mr-2"></i>
                      Processing Video...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-magic mr-2"></i>
                      Process Video
                    </>
                  )}
                </button>
              </form>

              {/* Status Messages */}
              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex">
                    <i className="fas fa-exclamation-circle text-red-400 mr-3 mt-0.5"></i>
                    <p className="text-red-700">{error}</p>
                  </div>
                </div>
              )}

              {success && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex">
                    <i className="fas fa-check-circle text-green-400 mr-3 mt-0.5"></i>
                    <p className="text-green-700">{success}</p>
                  </div>
                </div>
              )}

              {/* Processed Video */}
              {processedVideo && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">
                    Your Processed Video
                  </h3>
                  <video 
                    controls 
                    className="w-full rounded-lg"
                    src={processedVideo}
                  >
                    Your browser does not support the video tag.
                  </video>
                  <div className="mt-3 text-center">
                    <a
                      href={processedVideo}
                      download
                      className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      <i className="fas fa-download mr-2"></i>
                      Download Video
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Features Section */}
          <section id="features" className="py-20 bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h2 className="text-4xl font-bold text-gray-900 mb-4">
                  Powerful Features for Professional Results
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                  Built for scale, designed for simplicity. Everything you need to moderate content at enterprise level.
                </p>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                {features.map((feature, index) => (
                  <div key={index} className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-lg transition-shadow border border-gray-200">
                    <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center mb-6">
                      <i className={`${feature.icon} text-white text-xl`}></i>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">{feature.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Demo Section */}
          <section id="demo" className="py-20">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-4xl font-bold text-gray-900 mb-4">
                  See It In Action
                </h2>
                <p className="text-xl text-gray-600">
                  Try our AI-powered content moderation right now. Upload a video and see the magic happen.
                </p>
              </div>

              {/* Upload Interface */}
              {showUpload && (
                <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
                  <form onSubmit={handleUpload}>
                    {/* File Upload */}
                    <div className="mb-6">
                      <label className="block text-sm font-semibold text-gray-900 mb-3">
                        Select Video File
                      </label>
                      <div 
                        className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-indigo-500 transition-colors cursor-pointer bg-gray-50 hover:bg-indigo-50"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <i className="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
                        <p className="text-gray-700 font-medium mb-2">
                          {uploadedFile ? uploadedFile.name : 'Click to select or drag and drop your video file'}
                        </p>
                        <p className="text-sm text-gray-500">
                          Supports MP4, AVI, MOV, MKV, WebM (max 100MB)
                        </p>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="video/*"
                          onChange={handleFileSelect}
                          className="hidden"
                        />
                      </div>
                    </div>

                    {/* Censor Type */}
                    <div className="mb-6">
                      <label className="block text-sm font-semibold text-gray-900 mb-3">
                        Censoring Method
                      </label>
                      <select
                        value={censorType}
                        onChange={(e) => setCensorType(e.target.value)}
                        className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
                      >
                        <option value="beep">Audio Beep</option>
                        <option value="silence">Silence</option>
                        <option value="blur">Visual Blur</option>
                      </select>
                    </div>

                    {/* Submit Button */}
                    <button
                      type="submit"
                      disabled={!uploadedFile || loading}
                      className="w-full bg-indigo-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-lg"
                    >
                      {loading ? (
                        <>
                          <i className="fas fa-spinner fa-spin mr-2"></i>
                          Processing Video...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-magic mr-2"></i>
                          Process Video
                        </>
                      )}
                    </button>
                  </form>

                  {/* Status Messages */}
                  {error && (
                    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
                      <div className="flex">
                        <i className="fas fa-exclamation-circle text-red-400 mr-3 mt-0.5"></i>
                        <p className="text-red-700 font-medium">{error}</p>
                      </div>
                    </div>
                  )}

                  {success && (
                    <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl">
                      <div className="flex">
                        <i className="fas fa-check-circle text-green-400 mr-3 mt-0.5"></i>
                        <p className="text-green-700 font-medium">{success}</p>
                      </div>
                    </div>
                  )}

                  {/* Processed Video */}
                  {processedVideo && (
                    <div className="mt-8">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        Your Processed Video
                      </h3>
                      <video 
                        controls 
                        className="w-full rounded-xl shadow-lg"
                        src={processedVideo}
                      >
                        Your browser does not support the video tag.
                      </video>
                      <div className="mt-4 text-center">
                        <a
                          href={processedVideo}
                          download
                          className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-semibold"
                        >
                          <i className="fas fa-download mr-2"></i>
                          Download Video
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {!showUpload && (
                <div className="text-center">
                  <button 
                    onClick={() => setShowUpload(true)}
                    className="bg-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-indigo-700 transform hover:scale-105 transition-all duration-200 shadow-lg"
                  >
                    <i className="fas fa-play mr-2"></i>
                    Start Free Trial
                  </button>
                </div>
              )}
            </div>
          </section>

          {/* Pricing Section */}
          <section id="pricing" className="py-20 bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h2 className="text-4xl font-bold text-gray-900 mb-4">
                  Simple, Transparent Pricing
                </h2>
                <p className="text-xl text-gray-600">
                  Choose the plan that fits your needs. Start free, scale as you grow.
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-8">
                {pricingPlans.map((plan, index) => (
                  <div key={index} className={`bg-white rounded-2xl shadow-lg p-8 border-2 ${
                    plan.popular ? 'border-indigo-500 relative' : 'border-gray-200'
                  }`}>
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-indigo-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        Most Popular
                      </span>
                    </div>
                  )}
                  
                  <div className="text-center mb-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    <div className="mb-4">
                      <span className="text-5xl font-bold text-gray-900">${plan.price}</span>
                      <span className="text-gray-600 ml-1">/{plan.period}</span>
                    </div>
                  </div>

                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feature, fIndex) => (
                      <li key={fIndex} className="flex items-start">
                        <i className="fas fa-check text-green-500 mr-3 mt-1 flex-shrink-0"></i>
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button className={`w-full py-4 px-6 rounded-xl font-semibold text-lg transition-colors ${
                    plan.popular 
                      ? 'bg-indigo-600 text-white hover:bg-indigo-700' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}>
                    {plan.cta}
                  </button>
                </div>
                ))}
              </div>

              <div className="text-center mt-12">
                <p className="text-gray-600 mb-4">
                  All plans include 99.9% uptime SLA, SSL encryption, and GDPR compliance
                </p>
                <a href="#" className="text-indigo-600 hover:text-indigo-700 font-medium">
                  Compare all features →
                </a>
              </div>
            </div>
          </section>

          {/* Social Proof Section */}
          <section className="py-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h2 className="text-4xl font-bold text-gray-900 mb-4">
                  Trusted by Industry Leaders
                </h2>
                <p className="text-xl text-gray-600">
                  Join thousands of companies using MovieCensorAI to moderate their content
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 items-center opacity-60">
                {/* Company logos placeholder */}
                <div className="h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-500 font-semibold">Company 1</span>
                </div>
                <div className="h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-500 font-semibold">Company 2</span>
                </div>
                <div className="h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-500 font-semibold">Company 3</span>
                </div>
                <div className="h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-500 font-semibold">Company 4</span>
                </div>
                <div className="h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-500 font-semibold">Company 5</span>
                </div>
                <div className="h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-500 font-semibold">Company 6</span>
                </div>
              </div>
            </div>
          </section>

          {/* CTA Section */}
          <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-4xl font-bold text-white mb-6">
                Ready to Clean Your Content?
              </h2>
              <p className="text-xl text-indigo-100 mb-8">
                Join thousands of professionals who trust MovieCensorAI for their content moderation needs.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button 
                  onClick={() => setShowUpload(true)}
                  className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-100 transform hover:scale-105 transition-all duration-200"
                >
                  Start Free Trial
                </button>
                <button className="bg-indigo-700 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-indigo-800 transition-colors border-2 border-indigo-500">
                  Contact Sales
                </button>
              </div>
            </div>
          </section>

          {/* Footer */}
          <footer className="bg-gray-900 text-white py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="grid md:grid-cols-4 gap-8">
                <div>
                  <div className="flex items-center space-x-2 mb-6">
                    <div className="w-8 h-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                      <i className="fas fa-film text-white text-sm"></i>
                    </div>
                    <span className="text-xl font-bold">MovieCensorAI</span>
                  </div>
                  <p className="text-gray-400 mb-6">
                    Professional AI-powered content moderation for the modern world.
                  </p>
                  <div className="flex space-x-4">
                    <a href="#" className="text-gray-400 hover:text-white transition-colors">
                      <i className="fab fa-twitter text-xl"></i>
                    </a>
                    <a href="#" className="text-gray-400 hover:text-white transition-colors">
                      <i className="fab fa-linkedin text-xl"></i>
                    </a>
                    <a href="#" className="text-gray-400 hover:text-white transition-colors">
                      <i className="fab fa-github text-xl"></i>
                    </a>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-6">Product</h3>
                  <ul className="space-y-3">
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Pricing</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">API Docs</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Integrations</a></li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-6">Company</h3>
                  <ul className="space-y-3">
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">About</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Blog</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Careers</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact</a></li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-6">Support</h3>
                  <ul className="space-y-3">
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Help Center</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Status</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Security</a></li>
                    <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy</a></li>
                  </ul>
                </div>
              </div>

              <div className="border-t border-gray-800 mt-12 pt-8 text-center">
                <p className="text-gray-400">
                  © 2024 MovieCensorAI. All rights reserved. Built with ❤️ for content creators.
                </p>
              </div>
            </div>
          </footer>
      </div>
    </>
  );
}
