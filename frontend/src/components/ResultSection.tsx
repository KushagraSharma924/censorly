import React from 'react';
import { Download, CheckCircle, RotateCcw, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ResultSectionProps {
  fileName: string;
  onDownload: () => void;
  onStartAgain: () => void;
}

export const ResultSection: React.FC<ResultSectionProps> = ({ 
  fileName, 
  onDownload, 
  onStartAgain 
}) => {
  return (
    <Card className="w-full max-w-2xl mx-auto shadow-medium bg-gradient-card animate-fade-in">
      <CardHeader className="text-center">
        <div className="flex items-center justify-center w-16 h-16 mx-auto bg-success/10 rounded-full mb-4">
          <CheckCircle className="w-8 h-8 text-success" />
        </div>
        <CardTitle className="text-2xl font-bold text-success">
          Video Cleaned Successfully!
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <Alert className="border-success/20 bg-success/5">
          <CheckCircle className="h-4 w-4 text-success" />
          <AlertDescription className="text-success-foreground">
            Your video has been processed and inappropriate content has been filtered.
            The cleaned version is ready for download.
          </AlertDescription>
        </Alert>
        
        <div className="space-y-4">
          <div className="text-center space-y-2">
            <p className="font-medium">Cleaned file:</p>
            <p className="text-sm text-muted-foreground bg-muted rounded-lg px-3 py-2">
              {fileName}
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={onDownload}
              variant="success"
              size="lg"
              className="flex-1"
            >
              <Download className="w-5 h-5 mr-2" />
              Download Cleaned Video
            </Button>
            
            <Button
              variant="outline"
              size="lg"
              className="sm:w-auto"
            >
              <Play className="w-5 h-5 mr-2" />
              Preview
            </Button>
          </div>
          
          <Button
            onClick={onStartAgain}
            variant="ghost"
            size="lg"
            className="w-full"
          >
            <RotateCcw className="w-5 h-5 mr-2" />
            Clean Another Video
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};