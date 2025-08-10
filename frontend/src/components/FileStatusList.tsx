import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  FileVideo, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Download,
  AlertCircle,
  Trash2,
  Upload,
  Loader2,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FileStatusItem {
  file: File;
  id: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  jobId?: string;
  resultUrl?: string;
  error?: string;
  estimatedTime?: number; // in seconds
}

interface FileStatusCardProps {
  file: FileStatusItem;
  onDownload: (jobId: string, filename: string) => void;
  onRemove: (id: string) => void;
  onRetry?: (file: FileStatusItem) => void;
}

export const FileStatusCard: React.FC<FileStatusCardProps> = ({
  file,
  onDownload,
  onRemove,
  onRetry
}) => {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusConfig = () => {
    switch (file.status) {
      case 'uploading':
        return {
          icon: Upload,
          color: 'blue',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          textColor: 'text-blue-700',
          badgeVariant: 'default' as const,
          title: 'Uploading...',
          description: 'Your file is being uploaded to our servers'
        };
      case 'processing':
        return {
          icon: Loader2,
          color: 'yellow',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-700',
          badgeVariant: 'secondary' as const,
          title: 'Processing...',
          description: 'AI is analyzing and cleaning your video'
        };
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'green',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          textColor: 'text-green-700',
          badgeVariant: 'default' as const,
          title: 'Completed!',
          description: 'Your clean video is ready for download'
        };
      case 'failed':
        return {
          icon: XCircle,
          color: 'red',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-700',
          badgeVariant: 'destructive' as const,
          title: 'Failed',
          description: 'There was an error processing your video'
        };
    }
  };

  const config = getStatusConfig();
  const StatusIcon = config.icon;

  return (
    <Card className={cn("border-2 transition-all duration-200", config.borderColor, config.bgColor)}>
      <CardContent className="p-4">
        <div className="space-y-4">
          {/* File Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <div className={cn(
                "flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center",
                config.bgColor
              )}>
                <FileVideo className={cn("h-5 w-5", config.textColor)} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium text-gray-900 truncate">{file.file.name}</p>
                <p className="text-sm text-gray-600">{formatFileSize(file.file.size)}</p>
                {file.jobId && (
                  <p className="text-xs text-gray-500 font-mono">ID: {file.jobId}</p>
                )}
              </div>
            </div>
            
            {/* Status Badge */}
            <Badge variant={config.badgeVariant} className="ml-2">
              <StatusIcon className={cn(
                "h-3 w-3 mr-1",
                file.status === 'processing' && "animate-spin",
                file.status === 'uploading' && "animate-pulse"
              )} />
              {config.title}
            </Badge>
          </div>

          {/* Progress Section */}
          {(file.status === 'uploading' || file.status === 'processing') && (
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className={config.textColor}>{config.description}</span>
                {file.estimatedTime && (
                  <span className="text-gray-500">
                    ~{formatTime(file.estimatedTime)} remaining
                  </span>
                )}
              </div>
              
              {file.progress > 0 ? (
                <Progress 
                  value={file.progress} 
                  className="h-2"
                />
              ) : (
                <Skeleton className="h-2 w-full" />
              )}
              
              <div className="flex justify-between text-xs text-gray-500">
                <span>{file.progress}% complete</span>
                <span>
                  {file.status === 'uploading' ? 'Uploading...' : 'Processing...'}
                </span>
              </div>
            </div>
          )}

          {/* Error Message */}
          {file.status === 'failed' && file.error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-700 text-sm">
                {file.error}
              </AlertDescription>
            </Alert>
          )}

          {/* Success Message */}
          {file.status === 'completed' && (
            <div className="p-3 bg-green-100 rounded-lg border border-green-200">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm text-green-800 font-medium">
                  Video cleaned successfully! Your content is now family-friendly.
                </span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-2">
            <div className="flex space-x-2">
              {file.status === 'completed' && file.jobId && (
                <Button
                  size="sm"
                  onClick={() => onDownload(file.jobId!, file.file.name)}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Clean Video
                </Button>
              )}
              
              {file.status === 'failed' && onRetry && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onRetry(file)}
                  className="border-blue-200 text-blue-700 hover:bg-blue-50"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
              )}
            </div>

            <Button
              size="sm"
              variant="ghost"
              onClick={() => onRemove(file.id)}
              className="text-gray-500 hover:text-red-600"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface FileStatusListProps {
  files: FileStatusItem[];
  onDownload: (jobId: string, filename: string) => void;
  onRemove: (id: string) => void;
  onRetry?: (file: FileStatusItem) => void;
  isLoading?: boolean;
}

export const FileStatusList: React.FC<FileStatusListProps> = ({
  files,
  onDownload,
  onRemove,
  onRetry,
  isLoading = false
}) => {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 2 }).map((_, i) => (
          <Card key={i} className="border border-gray-200">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-24" />
                </div>
                <Skeleton className="h-6 w-20" />
              </div>
              <div className="mt-4 space-y-2">
                <Skeleton className="h-2 w-full" />
                <div className="flex justify-between">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-3 w-16" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <Card className="border-dashed border-2 border-gray-300">
        <CardContent className="p-8 text-center">
          <FileVideo className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No files uploaded yet</h3>
          <p className="text-gray-600">Upload your first video to get started with AI profanity filtering</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {files.map((file) => (
        <FileStatusCard
          key={file.id}
          file={file}
          onDownload={onDownload}
          onRemove={onRemove}
          onRetry={onRetry}
        />
      ))}
    </div>
  );
};
