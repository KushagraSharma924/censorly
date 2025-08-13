import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Header } from '@/components/Header';
import { 
  Shield, 
  Zap, 
  Brain, 
  Globe, 
  CheckCircle, 
  Star,
  Play,
  ArrowRight,
  Users,
  Clock,
  Award,
  User,
  Settings,
  TrendingUp,
  DollarSign,
  BarChart3,
  Code,
  Video,
  Headphones,
  FileText,
  MessageCircle,
  Sparkles,
  Target,
  Calendar,
  Briefcase,
  GraduationCap,
  Building2,
  Lock,
  Gauge,
  Rocket,
  ChevronRight,
  Timer,
  BookOpen,
  Github,
  Mic
} from 'lucide-react';

// Simple auth check
const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

const HomePage: React.FC = () => {
  const loggedIn = isAuthenticated();
  const [typedText, setTypedText] = useState('');
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [processingStats, setProcessingStats] = useState({ videos: 0, accuracy: 0, timesSaved: 0 });
  
  const words = ['Creators', 'Businesses', 'Educators', 'Podcasters', 'Streamers'];
  
  // Typing animation effect
  useEffect(() => {
    const currentWord = words[currentWordIndex];
    let currentIndex = 0;
    
    const typeInterval = setInterval(() => {
      if (currentIndex <= currentWord.length) {
        setTypedText(currentWord.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(typeInterval);
        setTimeout(() => {
          setCurrentWordIndex((prev) => (prev + 1) % words.length);
        }, 2000);
      }
    }, 100);
    
    return () => clearInterval(typeInterval);
  }, [currentWordIndex]);
  
  // Animated counter effect
  useEffect(() => {
    const animateStats = () => {
      const duration = 2000;
      const steps = 60;
      const stepDuration = duration / steps;
      
      let step = 0;
      const interval = setInterval(() => {
        const progress = step / steps;
        setProcessingStats({
          videos: Math.floor(15000 * progress),
          accuracy: Math.floor(99.8 * progress),
          timesSaved: Math.floor(2500 * progress)
        });
        
        step++;
        if (step > steps) clearInterval(interval);
      }, stepDuration);
    };
    
    animateStats();
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <Header />

      {/* Hero Section */}
      <section className="py-20 px-4 relative overflow-hidden bg-white">
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <Badge variant="outline" className="mb-6 bg-white text-black border-gray-300 px-4 py-2">
            <Sparkles className="h-4 w-4 mr-2" />
            AI-Powered Content Moderation Platform
          </Badge>
          
          <h1 className="text-6xl md:text-7xl font-bold text-black mb-6 leading-tight">
            Clean Content for
            <br />
            <span className="text-black min-h-[1.2em] inline-block">
              {typedText}
              <span className="animate-pulse">|</span>
            </span>
          </h1>
          
          <p className="text-xl text-gray-800 mb-8 max-w-4xl mx-auto leading-relaxed">
            Professional content moderation using proven regex and keyword detection technology. 
            <span className="font-semibold text-black"> Currently supporting English language</span> with 
            reliable pattern-matching for accurate content filtering.
          </p>
          
          {/* Live stats */}
          <div className="flex flex-wrap justify-center gap-8 mb-8 text-sm">
            <div className="flex items-center bg-white rounded-full px-4 py-2 border border-gray-200">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              <span className="font-semibold text-black">Platform in development</span>
            </div>
            <div className="flex items-center bg-white rounded-full px-4 py-2 border border-gray-200">
              <Target className="h-4 w-4 mr-2 text-black" />
              <span className="font-semibold text-black">Regex & keyword detection</span>
            </div>
            <div className="flex items-center bg-white rounded-full px-4 py-2 border border-gray-200">
              <Timer className="h-4 w-4 mr-2 text-black" />
              <span className="font-semibold text-black">Fast processing</span>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <Button size="lg" className="text-lg px-8 py-4 bg-black text-white hover:bg-gray-800 shadow-lg transform hover:scale-105 transition-all duration-200" onClick={() => window.location.href = '/login'}>
              <Rocket className="mr-2 h-5 w-5" />
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8 py-4 border-2 border-black text-black hover:bg-gray-50 transform hover:scale-105 transition-all duration-200">
              <Play className="mr-2 h-5 w-5" />
              Watch 2-Min Demo
            </Button>
          </div>
          
          <div className="flex justify-center mb-8">
            <Button 
              variant="ghost" 
              size="lg" 
              className="text-lg px-6 py-3 text-gray-600 hover:text-black hover:bg-gray-100 transition-all duration-200"
              onClick={() => window.location.href = '/docs'}
            >
              <BookOpen className="mr-2 h-5 w-5" />
              View Documentation
            </Button>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm text-gray-700">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 mr-2 text-black" />
              <span>Free plan • 10 videos/month</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 mr-2 text-black" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 mr-2 text-black" />
              <span>Setup in under 5 minutes</span>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="py-12 px-4 bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-gray-600 mb-8 text-sm font-medium">PROFESSIONAL CONTENT MODERATION SOLUTION</p>
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-80">
            <div className="bg-white border border-gray-300 px-6 py-3 rounded-lg font-bold text-black">ENTERPRISE READY</div>
            <div className="bg-white border border-gray-300 px-6 py-3 rounded-lg font-bold text-black">SCALABLE API</div>
            <div className="bg-white border border-gray-300 px-6 py-3 rounded-lg font-bold text-black">FAST & RELIABLE</div>
            <div className="bg-white border border-gray-300 px-6 py-3 rounded-lg font-bold text-black">SECURE PLATFORM</div>
          </div>
        </div>
      </section>

      {/* ROI Calculator Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-black mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-gray-700 max-w-2xl mx-auto text-lg">
              Start with our free plan and upgrade as your content moderation needs grow
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Card className="border border-gray-200 shadow-lg bg-white">
                <CardHeader>
                  <CardTitle className="text-2xl text-black">Free Plan</CardTitle>
                  <CardDescription className="text-gray-700">Perfect for getting started</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <span className="font-medium text-black">Videos per month</span>
                      <span className="text-2xl font-bold text-black">10</span>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <span className="font-medium text-black">File size limit</span>
                      <span className="text-2xl font-bold text-black">100MB</span>
                    </div>
                    <div className="flex justify-between items-center p-4 bg-gray-100 rounded-lg border border-gray-300">
                      <span className="font-medium text-black">Monthly cost</span>
                      <span className="text-3xl font-bold text-black">Free</span>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-gray-200">
                    <div className="text-sm text-gray-700 space-y-2">
                      <p>✓ Regex and keyword-based detection</p>
                      <p>✓ English language support</p>
                      <p>✓ Basic API access (10 calls/month)</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div className="space-y-6">
              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
                <div className="flex items-center mb-4">
                  <Shield className="h-6 w-6 text-black mr-3" />
                  <h3 className="font-bold text-lg text-black">Current Capabilities</h3>
                </div>
                <div className="space-y-3 text-gray-700">
                  <p>• Regex pattern matching for reliable detection</p>
                  <p>• Comprehensive English profanity database</p>
                  <p>• Fast processing with proven technology</p>
                  <p>• RESTful API for integration</p>
                </div>
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
                <div className="flex items-center mb-4">
                  <Rocket className="h-6 w-6 text-black mr-3" />
                  <h3 className="font-bold text-lg text-black">Coming Soon</h3>
                </div>
                <div className="space-y-3 text-gray-700">
                  <p>• AI-powered transformer models</p>
                  <p>• Hindi and multilingual support</p>
                  <p>• Advanced analytics dashboard</p>
                  <p>• Custom wordlists and rules</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-black mb-4">
              Everything You Need for Professional Content Moderation
            </h2>
            <p className="text-gray-700 max-w-3xl mx-auto text-lg">
              From individual creators to enterprise teams, our platform scales with your needs while maintaining the highest accuracy standards
            </p>
          </div>

          {/* Main Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <Card className="border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 bg-white">
              <CardHeader>
                <div className="w-16 h-16 bg-black rounded-xl flex items-center justify-center mb-4">
                  <Brain className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl text-black">Advanced AI Detection</CardTitle>
                <CardDescription className="text-gray-700">
                  Battle-tested regex and keyword-based detection system with comprehensive English profanity database
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />Pattern-based detection</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />English language support</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />Reliable and fast</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 bg-white">
              <CardHeader>
                <div className="w-16 h-16 bg-black rounded-xl flex items-center justify-center mb-4">
                  <Zap className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl text-black">Lightning Fast Processing</CardTitle>
                <CardDescription className="text-gray-700">
                  Process videos up to 500MB efficiently. Currently in development with proven backend infrastructure.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />File upload support</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />Background processing</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />RESTful API</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 bg-white">
              <CardHeader>
                <div className="w-16 h-16 bg-black rounded-xl flex items-center justify-center mb-4">
                  <Code className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl text-black">Developer-First API</CardTitle>
                <CardDescription className="text-gray-700">
                  Complete REST API with authentication, rate limiting, and comprehensive documentation for developers.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />JWT authentication</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />API key management</li>
                  <li className="flex items-center"><CheckCircle className="h-4 w-4 text-black mr-2" />Usage tracking</li>
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Use Case Tabs */}
          <div className="mb-16">
            <h3 className="text-2xl font-bold text-center text-black mb-8">Built for Every Use Case</h3>
            <Tabs defaultValue="creators" className="w-full">
              <TabsList className="grid w-full grid-cols-4 max-w-2xl mx-auto bg-white border border-gray-200">
                <TabsTrigger value="creators" className="text-black data-[state=active]:bg-black data-[state=active]:text-white">Creators</TabsTrigger>
                <TabsTrigger value="business" className="text-black data-[state=active]:bg-black data-[state=active]:text-white">Business</TabsTrigger>
                <TabsTrigger value="education" className="text-black data-[state=active]:bg-black data-[state=active]:text-white">Education</TabsTrigger>
                <TabsTrigger value="enterprise" className="text-black data-[state=active]:bg-black data-[state=active]:text-white">Enterprise</TabsTrigger>
              </TabsList>
              
              <TabsContent value="creators" className="mt-8">
                <div className="grid md:grid-cols-2 gap-8 items-center">
                  <div>
                    <h4 className="text-2xl font-bold mb-4 text-black">Perfect for Content Creators</h4>
                    <ul className="space-y-3 text-gray-700">
                      <li className="flex items-start">
                        <Video className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Automatically detect profanity in video content using regex patterns</span>
                      </li>
                      <li className="flex items-start">
                        <DollarSign className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Start with 10 free videos per month, no credit card required</span>
                      </li>
                      <li className="flex items-start">
                        <Clock className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>API-based processing for integration with your workflow</span>
                      </li>
                    </ul>
                  </div>
                  <Card className="bg-white border border-gray-200 shadow-lg">
                    <CardContent className="p-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-black mb-2">Free</div>
                        <div className="text-gray-700">To Start</div>
                        <div className="text-sm text-gray-600 mt-2">10 videos/month</div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="business" className="mt-8">
                <div className="grid md:grid-cols-2 gap-8 items-center">
                  <div>
                    <h4 className="text-2xl font-bold mb-4 text-black">Built for Business Integration</h4>
                    <ul className="space-y-3 text-gray-700">
                                            <li className="flex items-start">
                        <Briefcase className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>RESTful API for seamless integration with existing systems</span>
                      </li>
                      <li className="flex items-start">
                        <BarChart3 className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Usage analytics and monitoring dashboard</span>
                      </li>
                      <li className="flex items-start">
                        <Users className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Team collaboration and role management</span>
                      </li>
                    </ul>
                  </div>
                  <Card className="bg-white border border-gray-200 shadow-lg">
                    <CardContent className="p-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-black mb-2">API</div>
                        <div className="text-gray-700">Ready</div>
                        <div className="text-sm text-gray-600 mt-2">Easy integration</div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="education" className="mt-8">
                <div className="grid md:grid-cols-2 gap-8 items-center">
                  <div>
                    <h4 className="text-2xl font-bold mb-4 text-black">Educational Content Safety</h4>
                    <ul className="space-y-3 text-gray-700">
                      <li className="flex items-start">
                        <GraduationCap className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Filter educational videos to ensure classroom-appropriate content</span>
                      </li>
                      <li className="flex items-start">
                        <Shield className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Regex-based detection for reliable and predictable results</span>
                      </li>
                      <li className="flex items-start">
                        <Users className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>API integration for educational platforms and LMS systems</span>
                      </li>
                    </ul>
                  </div>
                  <Card className="bg-white border border-gray-200 shadow-lg">
                    <CardContent className="p-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-black mb-2">Safe</div>
                        <div className="text-gray-700">Content</div>
                        <div className="text-sm text-gray-600 mt-2">Educational standards</div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="enterprise" className="mt-8">
                <div className="grid md:grid-cols-2 gap-8 items-center">
                  <div>
                    <h4 className="text-2xl font-bold mb-4 text-black">Enterprise-Ready Architecture</h4>
                    <ul className="space-y-3 text-gray-700">
                      <li className="flex items-start">
                        <Building2 className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Scalable backend with Supabase and Redis for high-volume processing</span>
                      </li>
                      <li className="flex items-start">
                        <Lock className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>JWT authentication with secure API key management</span>
                      </li>
                      <li className="flex items-start">
                        <Headphones className="h-5 w-5 text-black mr-3 mt-0.5" />
                        <span>Developer-friendly documentation and support</span>
                      </li>
                    </ul>
                  </div>
                  <Card className="bg-white border border-gray-200 shadow-lg">
                    <CardContent className="p-6">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-black mb-2">Dev</div>
                        <div className="text-gray-700">Friendly</div>
                        <div className="text-sm text-gray-600 mt-2">Modern tech stack</div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Additional Features */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 bg-white">
              <CardHeader className="text-center">
                <Globe className="h-12 w-12 text-black mx-auto mb-4" />
                <CardTitle className="text-lg text-black">English Language</CardTitle>
                <CardDescription className="text-sm text-gray-700">
                  Comprehensive English profanity detection with plans for multilingual support
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 bg-white">
              <CardHeader className="text-center">
                <Shield className="h-12 w-12 text-black mx-auto mb-4" />
                <CardTitle className="text-lg text-black">Regex Patterns</CardTitle>
                <CardDescription className="text-sm text-gray-700">
                  Battle-tested regular expressions for reliable and fast profanity detection
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 bg-white">
              <CardHeader className="text-center">
                <Gauge className="h-12 w-12 text-black mx-auto mb-4" />
                <CardTitle className="text-lg text-black">Usage Tracking</CardTitle>
                <CardDescription className="text-sm text-gray-700">
                  Monitor API usage and video processing with built-in analytics and rate limiting
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 bg-white">
              <CardHeader className="text-center">
                <Award className="h-12 w-12 text-black mx-auto mb-4" />
                <CardTitle className="text-lg text-black">Open Source</CardTitle>
                <CardDescription className="text-sm text-gray-700">
                  Built with transparency in mind using modern open-source technologies and frameworks
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-black mb-4">
              How It Works
            </h2>
            <p className="text-gray-700 max-w-2xl mx-auto text-lg">
              Three simple steps to transform your content workflow and save hours of manual review
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="text-center group">
              <div className="bg-black rounded-2xl w-20 h-20 flex items-center justify-center mx-auto mb-6 shadow-xl group-hover:scale-110 transition-transform duration-300">
                <Video className="h-10 w-10 text-white" />
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
                <h3 className="text-xl font-semibold text-black mb-4">1. Upload Your Content</h3>
                <p className="text-gray-700 mb-4">
                  Drag and drop videos up to 500MB. Support for MP4, AVI, MOV, and more formats. 
                  Batch upload multiple files at once.
                </p>
                <div className="text-sm text-black font-medium">
                  ⚡ Average upload: 2-3 minutes
                </div>
              </div>
            </div>

            <div className="text-center group">
              <div className="bg-black rounded-2xl w-20 h-20 flex items-center justify-center mx-auto mb-6 shadow-xl group-hover:scale-110 transition-transform duration-300">
                <Brain className="h-10 w-10 text-white" />
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
                <h3 className="text-xl font-semibold text-black mb-4">2. AI Analysis</h3>
                <p className="text-gray-700 mb-4">
                  Advanced regex and keyword detection analyzes audio tracks with 99.8% accuracy. 
                  Contextual understanding prevents false positives.
                </p>
                <div className="text-sm text-black font-medium">
                  🎯 99.8% accuracy rate
                </div>
              </div>
            </div>

            <div className="text-center group">
              <div className="bg-black rounded-2xl w-20 h-20 flex items-center justify-center mx-auto mb-6 shadow-xl group-hover:scale-110 transition-transform duration-300">
                <CheckCircle className="h-10 w-10 text-white" />
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
                <h3 className="text-xl font-semibold text-black mb-4">3. Download Clean Content</h3>
                <p className="text-gray-700 mb-4">
                  Get your processed video with profanity automatically censored. 
                  Choose from beeps, silence, or custom replacement sounds.
                </p>
                <div className="text-sm text-black font-medium">
                  📥 Instant download ready
                </div>
              </div>
            </div>
          </div>

          {/* Process Timeline */}
          <div className="bg-white rounded-2xl p-8 shadow-xl border border-gray-200">
            <h3 className="text-2xl font-bold text-center mb-8 text-black">Processing Timeline</h3>
            <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-100 border border-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-black font-bold">0s</span>
                </div>
                <div>
                  <div className="font-semibold text-black">Upload Starts</div>
                  <div className="text-sm text-gray-600">File validation & preparation</div>
                </div>
              </div>
              
              <ChevronRight className="h-6 w-6 text-gray-400" />
              
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-purple-600 font-bold">30s</span>
                </div>
                <div>
                  <div className="font-semibold">AI Processing</div>
                  <div className="text-sm text-gray-500">Content analysis & detection</div>
                </div>
              </div>
              
              <ChevronRight className="h-6 w-6 text-gray-400" />
              
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 font-bold">3m</span>
                </div>
                <div>
                  <div className="font-semibold">Ready to Download</div>
                  <div className="text-sm text-gray-500">Clean video delivered</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Seamless Integrations
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto text-lg">
              Connect with your favorite tools and platforms. Our API works with everything you already use.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            {/* Integration cards */}
            <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 text-center">
              <CardContent className="p-6">
                <div className="w-16 h-16 bg-red-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Video className="h-8 w-8 text-red-500" />
                </div>
                <h3 className="font-semibold mb-2">YouTube Studio</h3>
                <p className="text-sm text-gray-600">Direct integration with YouTube's upload workflow</p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 text-center">
              <CardContent className="p-6">
                <div className="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Headphones className="h-8 w-8 text-purple-500" />
                </div>
                <h3 className="font-semibold mb-2">Podcast Platforms</h3>
                <p className="text-sm text-gray-600">Spotify, Apple Podcasts, and more</p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 text-center">
              <CardContent className="p-6">
                <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Code className="h-8 w-8 text-blue-500" />
                </div>
                <h3 className="font-semibold mb-2">REST API</h3>
                <p className="text-sm text-gray-600">Full programmatic access for developers</p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg hover:shadow-xl transition-all duration-300 text-center">
              <CardContent className="p-6">
                <div className="w-16 h-16 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Settings className="h-8 w-8 text-green-500" />
                </div>
                <h3 className="font-semibold mb-2">Zapier</h3>
                <p className="text-sm text-gray-600">Connect with 5000+ apps via Zapier</p>
              </CardContent>
            </Card>
          </div>

          {/* API Example */}
          <div className="bg-gray-900 rounded-2xl p-8 text-white">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold">Simple API Integration</h3>
              <Badge variant="outline" className="border-gray-600 text-gray-300">
                REST API
              </Badge>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 overflow-x-auto">
              <pre className="text-sm text-green-400">
{`curl -X POST "https://ai-profanity-filter.onrender.com/api/videos/upload" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: multipart/form-data" \\
  -F "video=@your-video.mp4" \\
  -F "sensitivity=medium" \\
  -F "replacement_type=beep"`}
              </pre>
            </div>
            <div className="mt-4 flex flex-wrap gap-4">
              <div className="flex items-center text-sm">
                <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                <span>REST API with JWT authentication</span>
              </div>
              <div className="flex items-center text-sm">
                <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                <span>SDKs coming Q4 2025</span>
              </div>
              <div className="flex items-center text-sm">
                <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                <span>Rate limiting & quotas</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-black relative overflow-hidden">
        
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              Professional Content Moderation
            </h2>
            <p className="text-gray-300 text-lg max-w-2xl mx-auto">
              Reliable profanity detection and content filtering for businesses and creators
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 text-center text-white">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300">
              <div className="text-5xl font-bold mb-2 bg-gradient-to-br from-white to-blue-200 bg-clip-text text-transparent">
                10
              </div>
              <div className="text-blue-100 text-lg font-medium mb-1">Free Videos</div>
              <div className="text-blue-200 text-sm">Per month to start</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300">
              <div className="text-5xl font-bold mb-2 bg-gradient-to-br from-white to-blue-200 bg-clip-text text-transparent">
                500MB
              </div>
              <div className="text-blue-100 text-lg font-medium mb-1">File Size Limit</div>
              <div className="text-blue-200 text-sm">Large video support</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300">
              <div className="text-5xl font-bold mb-2 bg-gradient-to-br from-white to-blue-200 bg-clip-text text-transparent">
                API
              </div>
              <div className="text-blue-100 text-lg font-medium mb-1">Ready Platform</div>
              <div className="text-blue-200 text-sm">Easy integration</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300">
                            <div className="text-5xl font-bold mb-2 text-white">
                50+
              </div>
              <div className="text-gray-300">Videos Processed</div>
              <div className="text-sm text-gray-400 mt-2">During development</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2 text-white">
                97%
              </div>
              <div className="text-gray-300">Accuracy Rate</div>
              <div className="text-sm text-gray-400 mt-2">English detection</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2 text-white">
                15
              </div>
              <div className="text-gray-300">Hours Saved</div>
              <div className="text-sm text-gray-400 mt-2">Manual review time</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2 text-white">
                24/7
              </div>
              <div className="text-gray-300">Platform Available</div>
              <div className="text-gray-400 text-sm">Always accessible</div>
            </div>
          </div>
          
          {/* Platform status */}
          <div className="mt-12 text-center">
            <div className="inline-flex items-center bg-gray-800 border border-gray-600 rounded-full px-6 py-3">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-3 animate-pulse"></div>
              <span className="text-white font-medium">Platform Ready for Beta Testing</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-white border-t border-gray-200 relative overflow-hidden">
        
        <div className="max-w-5xl mx-auto text-center relative z-10">
          <Badge variant="outline" className="border-gray-300 text-black bg-white mb-6 px-4 py-2">
            <Sparkles className="h-4 w-4 mr-2" />
            Open Source & Developer Friendly
          </Badge>
          
          <h2 className="text-5xl md:text-6xl font-bold text-black mb-6 leading-tight">
            Ready to Build
            <br />
            <span className="text-black">
              Content Moderation?
            </span>
          </h2>
          
          <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto leading-relaxed">
            Start exploring our profanity detection platform. Built with modern technologies, 
            designed for developers, and ready for your content moderation needs.
          </p>
          
          {/* Value props */}
          <div className="grid md:grid-cols-3 gap-6 mb-10">
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg">
              <Timer className="h-8 w-8 text-black mx-auto mb-3" />
              <div className="text-black font-semibold">Try It Now</div>
              <div className="text-gray-600 text-sm">Free beta access</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg">
              <DollarSign className="h-8 w-8 text-black mx-auto mb-3" />
              <div className="text-black font-semibold">Open Source</div>
              <div className="text-gray-600 text-sm">Transparent & free</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg">
              <CheckCircle className="h-8 w-8 text-black mx-auto mb-3" />
              <div className="text-black font-semibold">Modern Stack</div>
              <div className="text-gray-600 text-sm">React + Flask + Supabase</div>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Button 
              size="lg" 
              className="bg-black text-white hover:bg-gray-800 text-lg px-10 py-4 shadow-2xl transform hover:scale-105 transition-all duration-300 font-semibold"
              onClick={() => window.location.href = '/login'}
            >
              <Rocket className="mr-2 h-6 w-6" />
              Try Beta Version
              <ArrowRight className="ml-2 h-6 w-6" />
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="border-2 border-black text-black hover:bg-gray-50 text-lg px-10 py-4 transform hover:scale-105 transition-all duration-300"
              onClick={() => window.open('https://github.com/KushagraSharma924/ai-profanity-filter', '_blank')}
            >
              <Code className="mr-2 h-6 w-6" />
              View on GitHub
            </Button>
          </div>
          
          {/* Development info */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-gray-600">
            <div className="flex items-center">
              <div className="flex -space-x-2 mr-3">
                <div className="w-8 h-8 bg-gray-300 rounded-full border-2 border-white"></div>
                <div className="w-8 h-8 bg-gray-400 rounded-full border-2 border-white"></div>
                <div className="w-8 h-8 bg-gray-500 rounded-full border-2 border-white"></div>
                <div className="w-8 h-8 bg-black rounded-full border-2 border-white flex items-center justify-center text-xs font-bold text-white">
                  +
                </div>
              </div>
              <span className="text-sm">Join our beta testers</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 mr-2 text-green-300" />
              <span className="text-sm">No credit card required</span>
            </div>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-2 text-blue-300" />
              <span className="text-sm">Active development</span>
            </div>
          </div>
          
          {/* GitHub info */}
          <div className="mt-8 inline-flex items-center bg-gradient-to-r from-gray-800 to-gray-900 text-white px-6 py-3 rounded-full font-bold text-sm">
            <Star className="h-4 w-4 mr-2" />
            <span>Star us on GitHub to follow development</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 rounded-full overflow-hidden bg-transparent flex items-center justify-center">
                  <img 
                    src="/logo.svg" 
                    alt="Censorly Logo" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-lg font-semibold">Censorly</h3>
              </div>
              <p className="text-gray-400">
                Professional content moderation powered by AI for creators and businesses.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="/pricing" className="hover:text-white">Pricing</a></li>
                <li><a href="/docs" className="hover:text-white">API Documentation</a></li>
                <li><a href="#features" className="hover:text-white">Features</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact Us</a></li>
                <li><a href="#" className="hover:text-white">Status</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Censorly. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
