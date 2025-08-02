import React, { useState, useCallback } from 'react';
import { Upload, FileVideo, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { videoService } from '@/lib/video-service';
import { useAuth } from '@/contexts/auth-context';
import { toast } from '@/hooks/use-toast';

interface VideoUploadProps {
  onJobCreated?: (jobId: string) => void;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({ onJobCreated }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filterMode, setFilterMode] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  
  const { isAuthenticated } = useAuth();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('video/')) {
        setSelectedFile(file);
      }
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type.startsWith('video/')) {
        setSelectedFile(file);
      }
    }
  }, []);

  const handleSubmit = async () => {
    if (!selectedFile || !filterMode) return;
    
    if (!isAuthenticated) {
      toast({
        title: "Authentication required",
        description: "Please log in to upload and process videos.",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsUploading(true);
      
      const result = await videoService.uploadVideo(selectedFile, {
        censoring_mode: filterMode as 'beep' | 'mute' | 'cut'
      });
      
      toast({
        title: "Upload successful",
        description: `Your video is being processed. Job ID: ${result.job_id}`,
      });
      
      // Reset form
      setSelectedFile(null);
      setFilterMode('');
      
      // Notify parent component
      if (onJobCreated) {
        onJobCreated(result.job_id);
      }
      
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Upload failed';
      toast({
        title: "Upload failed",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-medium bg-gradient-card">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Upload Your Video
        </CardTitle>
        <p className="text-muted-foreground">
          Choose a video file and select how you'd like to clean it
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Upload Area */}
        <div
          className={cn(
            "relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300",
            dragActive
              ? "border-primary bg-accent/50 scale-105"
              : selectedFile
              ? "border-success bg-success/5"
              : "border-muted-foreground/25 hover:border-primary/50 hover:bg-accent/30",
            isUploading && "pointer-events-none opacity-50"
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
          
          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center w-16 h-16 mx-auto bg-success/10 rounded-full">
                <FileVideo className="w-8 h-8 text-success" />
              </div>
              <div>
                <p className="font-medium text-success">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedFile(null)}
                className="text-muted-foreground hover:text-destructive"
              >
                <X className="w-4 h-4 mr-2" />
                Remove
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-center w-16 h-16 mx-auto bg-primary/10 rounded-full">
                <Upload className="w-8 h-8 text-primary" />
              </div>
              <div>
                <p className="text-lg font-medium">
                  Drag & drop your video here
                </p>
                <p className="text-muted-foreground">
                  or click to browse files
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Supports MP4, MOV, AVI (max 500MB)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Filter Mode Selection */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Choose filter mode:</label>
          <Select value={filterMode} onValueChange={setFilterMode} disabled={isUploading}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select how to handle inappropriate content" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="beep">
                🔔 Beep profane words
              </SelectItem>
              <SelectItem value="mute">
                🔇 Mute profane words
              </SelectItem>
              <SelectItem value="cut" disabled>
                ✂️ Cut NSFW scenes (Coming soon)
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Submit Button */}
        <Button
          onClick={handleSubmit}
          disabled={!selectedFile || !filterMode || isUploading}
          variant={isUploading ? "outline" : "default"}
          size="lg"
          className="w-full"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Uploading Video...
            </>
          ) : (
            "Clean My Video"
          )}
        </Button>
      </CardContent>
    </Card>
  );
};