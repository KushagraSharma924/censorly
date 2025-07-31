import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { VideoUpload } from '@/components/VideoUpload';
import { ProcessingState } from '@/components/ProcessingState';
import { ResultSection } from '@/components/ResultSection';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Shield, Zap, Users, CheckCircle, Star, Clock, Award, ArrowRight, PlayCircle } from 'lucide-react';
import heroImage from '@/assets/hero-bg.jpg';
import { useVideoProcessor } from '@/hooks/useVideoProcessor';

type AppState = 'upload' | 'processing' | 'result';

const Index = () => {
  const [appState, setAppState] = useState<AppState>('upload');
  const [processedFileName, setProcessedFileName] = useState<string>('');
  const [downloadUrl, setDownloadUrl] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  
  const { processVideo, downloadFile, isProcessing, progress } = useVideoProcessor();

  const handleVideoUpload = async (file: File, mode: string) => {
    setAppState('processing');
    setErrorMessage('');
    
    try {
      const result = await processVideo(file, mode);
      
      if (result.success && result.downloadUrl && result.fileName) {
        setProcessedFileName(result.fileName);
        setDownloadUrl(result.downloadUrl);
        setAppState('result');
      } else {
        setErrorMessage(result.error || 'Processing failed');
        setAppState('upload');
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'An unexpected error occurred');
      setAppState('upload');
    }
  };

  const handleDownload = () => {
    if (downloadUrl && processedFileName) {
      downloadFile(downloadUrl, processedFileName);
    }
  };

  const handleStartAgain = () => {
    setAppState('upload');
    setProcessedFileName('');
    setDownloadUrl('');
    setErrorMessage('');
    // Clean up the previous blob URL
    if (downloadUrl) {
      window.URL.revokeObjectURL(downloadUrl);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-bg">
      <Header />
      
      {/* Hero Section */}
      <section className="relative py-24 px-4 text-center overflow-hidden">
        <div 
          className="absolute inset-0 opacity-10"
          style={{ 
            backgroundImage: `url(${heroImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="relative z-10 container max-w-5xl mx-auto space-y-10">
          {/* Trust Badge */}
          <div className="flex justify-center">
            <Badge className="bg-primary/10 text-primary border-primary/20 px-4 py-2">
              <Star className="w-4 h-4 mr-2 fill-current" />
              Trusted by 50,000+ Content Creators
            </Badge>
          </div>
          
          <div className="space-y-6">
            <h1 className="text-5xl md:text-7xl font-bold leading-tight">
              <span className="block text-foreground mb-2">Make Your Videos</span>
              <span className="bg-gradient-primary bg-clip-text text-transparent">
                Family-Friendly
              </span>
              <span className="block text-foreground">in Seconds</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Transform inappropriate content into clean, monetizable videos with our AI-powered censoring tool. 
              <span className="text-primary font-semibold"> Perfect for YouTubers, educators, and parents.</span>
            </p>
          </div>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" variant="hero" className="px-8 py-4 text-lg">
              <PlayCircle className="w-5 h-5 mr-2" />
              Start Cleaning Videos Free
            </Button>
            <Button size="lg" variant="outline" className="px-6">
              Watch Demo
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
          
          {/* Social Proof */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-success" />
              <span><strong className="text-foreground">2M+</strong> Videos Processed</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-primary" />
              <span><strong className="text-foreground">30 sec</strong> Average Processing</span>
            </div>
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-warning" />
              <span><strong className="text-foreground">99.8%</strong> Accuracy Rate</span>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-12 px-4">
        <div className="container max-w-7xl mx-auto">
          {appState === 'upload' && (
            <div className="space-y-4">
              {errorMessage && (
                <div className="max-w-2xl mx-auto p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-center">
                  <p className="font-medium">Processing Error</p>
                  <p className="text-sm">{errorMessage}</p>
                </div>
              )}
              <VideoUpload 
                onUpload={handleVideoUpload}
                isProcessing={isProcessing}
              />
            </div>
          )}
          
          {appState === 'processing' && <ProcessingState progress={progress} />}
          
          {appState === 'result' && (
            <ResultSection
              fileName={processedFileName}
              onDownload={handleDownload}
              onStartAgain={handleStartAgain}
            />
          )}
        </div>
      </section>

      {/* Benefits Section */}
      {appState === 'upload' && (
        <>
          <section className="py-20 px-4 bg-muted/30">
            <div className="container max-w-6xl mx-auto">
              <div className="text-center mb-16">
                <Badge className="mb-4 bg-primary/10 text-primary border-primary/20">
                  ⚡ Lightning Fast Processing
                </Badge>
                <h2 className="text-4xl font-bold mb-6">Why 50,000+ Creators Choose Us</h2>
                <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
                  Turn your risky content into platform-compliant videos that get more views, 
                  better engagement, and zero demonetization worries.
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <Card className="shadow-medium bg-gradient-card border-0 hover:shadow-strong transition-all duration-300">
                  <CardContent className="p-8 text-center space-y-6">
                    <div className="w-16 h-16 mx-auto bg-gradient-primary rounded-xl flex items-center justify-center">
                      <Sparkles className="w-8 h-8 text-primary-foreground" />
                    </div>
                    <h3 className="text-xl font-bold">AI-Powered Detection</h3>
                    <p className="text-muted-foreground">
                      Our advanced AI detects profanity, slurs, and inappropriate content with 
                      <span className="text-primary font-semibold"> 99.8% accuracy</span> - better than human reviewers
                    </p>
                    <div className="pt-2">
                      <Badge variant="secondary" className="text-xs">Used by Major Studios</Badge>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="shadow-medium bg-gradient-card border-0 hover:shadow-strong transition-all duration-300">
                  <CardContent className="p-8 text-center space-y-6">
                    <div className="w-16 h-16 mx-auto bg-gradient-primary rounded-xl flex items-center justify-center">
                      <Zap className="w-8 h-8 text-primary-foreground" />
                    </div>
                    <h3 className="text-xl font-bold">Instant Results</h3>
                    <p className="text-muted-foreground">
                      Process 60-minute videos in under 2 minutes. No more waiting hours for manual editing.
                      <span className="text-primary font-semibold"> Save 10+ hours per video</span>
                    </p>
                    <div className="pt-2">
                      <Badge variant="secondary" className="text-xs">Lightning Fast</Badge>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="shadow-medium bg-gradient-card border-0 hover:shadow-strong transition-all duration-300">
                  <CardContent className="p-8 text-center space-y-6">
                    <div className="w-16 h-16 mx-auto bg-gradient-primary rounded-xl flex items-center justify-center">
                      <Shield className="w-8 h-8 text-primary-foreground" />
                    </div>
                    <h3 className="text-xl font-bold">Monetization Safe</h3>
                    <p className="text-muted-foreground">
                      Ensure your content meets YouTube, TikTok, and Instagram guidelines. 
                      <span className="text-success font-semibold"> Zero demonetization risk</span>
                    </p>
                    <div className="pt-2">
                      <Badge variant="secondary" className="text-xs">Platform Approved</Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>

          {/* Pricing Section */}
          <section className="py-20 px-4" id="pricing">
            <div className="container max-w-4xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
                <p className="text-xl text-muted-foreground">Start free, scale as you grow. No hidden fees.</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Free Plan */}
                <Card className="shadow-soft bg-gradient-card">
                  <CardContent className="p-8 space-y-6">
                    <div className="text-center">
                      <h3 className="text-xl font-bold">Starter</h3>
                      <div className="mt-4">
                        <span className="text-4xl font-bold">Free</span>
                      </div>
                      <p className="text-muted-foreground mt-2">Perfect for trying out</p>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>3 videos per month</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Up to 10 minutes each</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Beep & mute options</span>
                      </div>
                    </div>
                    <Button className="w-full" variant="outline">Get Started Free</Button>
                  </CardContent>
                </Card>

                {/* Pro Plan */}
                <Card className="shadow-strong bg-gradient-card border-2 border-primary relative">
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground px-4 py-1">Most Popular</Badge>
                  </div>
                  <CardContent className="p-8 space-y-6">
                    <div className="text-center">
                      <h3 className="text-xl font-bold">Creator Pro</h3>
                      <div className="mt-4">
                        <span className="text-4xl font-bold">$19</span>
                        <span className="text-muted-foreground">/month</span>
                      </div>
                      <p className="text-muted-foreground mt-2">For serious creators</p>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Unlimited videos</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Up to 2 hours each</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>All filter options</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Priority processing</span>
                      </div>
                    </div>
                    <Button className="w-full" variant="hero">Start Pro Trial</Button>
                  </CardContent>
                </Card>

                {/* Business Plan */}
                <Card className="shadow-soft bg-gradient-card">
                  <CardContent className="p-8 space-y-6">
                    <div className="text-center">
                      <h3 className="text-xl font-bold">Business</h3>
                      <div className="mt-4">
                        <span className="text-4xl font-bold">$99</span>
                        <span className="text-muted-foreground">/month</span>
                      </div>
                      <p className="text-muted-foreground mt-2">For teams & agencies</p>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Everything in Pro</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>API access</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Team collaboration</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-success" />
                        <span>Priority support</span>
                      </div>
                    </div>
                    <Button className="w-full" variant="outline">Contact Sales</Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>

          {/* Testimonials */}
          <section className="py-20 px-4 bg-muted/30">
            <div className="container max-w-6xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-4xl font-bold mb-4">Loved by Content Creators</h2>
                <p className="text-xl text-muted-foreground">See what our users say about CleanMyVideo</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <Card className="shadow-medium bg-gradient-card">
                  <CardContent className="p-6 space-y-4">
                    <div className="flex space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-5 h-5 fill-warning text-warning" />
                      ))}
                    </div>
                    <p className="text-muted-foreground italic">
                      "CleanMyVideo saved my channel! I was getting demonetized constantly, 
                      now I can focus on creating content instead of worrying about language."
                    </p>
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
                        <span className="text-primary-foreground font-bold">MK</span>
                      </div>
                      <div>
                        <p className="font-semibold">Mike K.</p>
                        <p className="text-sm text-muted-foreground">Gaming YouTuber, 500K subs</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="shadow-medium bg-gradient-card">
                  <CardContent className="p-6 space-y-4">
                    <div className="flex space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-5 h-5 fill-warning text-warning" />
                      ))}
                    </div>
                    <p className="text-muted-foreground italic">
                      "As a teacher, this tool is perfect for cleaning educational content. 
                      Fast, accurate, and keeps my students focused on learning."
                    </p>
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
                        <span className="text-primary-foreground font-bold">SR</span>
                      </div>
                      <div>
                        <p className="font-semibold">Sarah R.</p>
                        <p className="text-sm text-muted-foreground">High School Teacher</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="shadow-medium bg-gradient-card">
                  <CardContent className="p-6 space-y-4">
                    <div className="flex space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-5 h-5 fill-warning text-warning" />
                      ))}
                    </div>
                    <p className="text-muted-foreground italic">
                      "The AI is incredibly accurate. I've processed over 200 videos and 
                      it catches everything without affecting the flow of conversation."
                    </p>
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
                        <span className="text-primary-foreground font-bold">DJ</span>
                      </div>
                      <div>
                        <p className="font-semibold">David J.</p>
                        <p className="text-sm text-muted-foreground">Podcast Host</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>
        </>
      )}

      <Footer />
    </div>
  );
};

export default Index;
