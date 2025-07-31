import React from 'react';
import { Loader2, Video, Sparkles } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface ProcessingStateProps {
  progress?: number;
}

export const ProcessingState: React.FC<ProcessingStateProps> = ({ progress = 0 }) => {
  const getProcessingStage = (progress: number) => {
    if (progress < 20) return 'Uploading video...';
    if (progress < 40) return 'Extracting audio...';
    if (progress < 60) return 'Transcribing with AI...';
    if (progress < 80) return 'Detecting content...';
    if (progress < 95) return 'Processing censorship...';
    return 'Finalizing video...';
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-medium bg-gradient-card">
      <CardContent className="py-12 text-center space-y-6">
        <div className="relative">
          <div className="flex items-center justify-center w-24 h-24 mx-auto bg-warning/10 rounded-full animate-pulse-glow">
            <Video className="w-12 h-12 text-warning" />
          </div>
          <div className="absolute -top-2 -right-2">
            <Sparkles className="w-8 h-8 text-primary animate-pulse" />
          </div>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-2xl font-bold">Processing your video</h3>
          <p className="text-muted-foreground">
            Our AI is cleaning your content. This may take a minute...
          </p>
        </div>
        
        <div className="w-full max-w-xs mx-auto">
          <div className="flex items-center justify-center space-x-1">
            <Loader2 className="w-5 h-5 animate-spin text-primary" />
            <span className="text-sm text-muted-foreground">{getProcessingStage(progress)}</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2 mt-4">
            <div 
              className="bg-gradient-primary h-2 rounded-full transition-all duration-500 ease-out" 
              style={{ width: `${Math.max(progress, 10)}%` }}
            ></div>
          </div>
          <div className="text-xs text-muted-foreground mt-2">
            {progress > 0 ? `${Math.round(progress)}% complete` : 'Starting...'}
          </div>
        </div>
        
        <p className="text-xs text-muted-foreground">
          Processing time depends on video length and complexity
        </p>
      </CardContent>
    </Card>
  );
};