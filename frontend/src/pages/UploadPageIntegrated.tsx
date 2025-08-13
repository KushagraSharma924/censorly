import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Header } from '@/components/Header';
import { VideoUpload } from '@/components/VideoUpload';
import { useAuth } from '@/contexts/auth-context';
import { VideoProcessor } from '@/lib/video-processor';
import { dashboardService } from '@/lib/dashboard-service';
import { 
  FileVideo,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle
} from 'lucide-react';

interface ProcessingJob {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  error_message?: string;
  created_at: string;
}

const UploadPageIntegrated: React.FC = () => {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const { isAuthenticated } = useAuth();

  const handleJobCreated = async (jobId: string) => {
    try {
      // Fetch the job details
      const jobDetails = await dashboardService.getJobDetails(jobId);
      setJobs(prev => [jobDetails, ...prev]);
      
      // Start polling for updates
      pollJobStatus(jobId);
    } catch (error) {
      console.error('Failed to fetch job details:', error);
    }
  };

  const pollJobStatus = async (jobId: string) => {
    try {
      await VideoProcessor.pollJobStatus(
        jobId,
        (status) => {
          // Update job in the list
          setJobs(prev => prev.map(job => 
            job.id === jobId ? { ...job, ...status } : job
          ));
        },
        2000, // Poll every 2 seconds
        150   // Max 5 minutes
      );
    } catch (error) {
      console.error('Job polling failed:', error);
      // Update job as failed
      setJobs(prev => prev.map(job => 
        job.id === jobId 
          ? { ...job, status: 'failed' as const, error_message: 'Polling timeout' }
          : job
      ));
    }
  };

  const handleDownload = async (job: ProcessingJob) => {
    try {
      await VideoProcessor.downloadVideo(job.id, job.filename);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const classes = {
      completed: 'bg-green-100 text-green-800',
      processing: 'bg-blue-100 text-blue-800',
      pending: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800'
    };
    
    return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="flex items-center justify-center py-20">
          <Card className="w-full max-w-md">
            <CardContent className="pt-6">
              <div className="text-center">
                <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Authentication Required</h3>
                <p className="text-gray-600 mb-4">
                  Please log in to upload and process videos.
                </p>
                <Button 
                  onClick={() => window.location.href = '/login'}
                  className="w-full"
                >
                  Go to Login
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="py-8 px-4">
        <div className="max-w-4xl mx-auto">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Upload & Process Videos
            </h1>
            <p className="text-gray-600">
              Upload your videos to automatically detect and censor profanity
            </p>
          </div>

          {/* Upload Area */}
          <div className="mb-8">
            <VideoUpload onJobCreated={handleJobCreated} />
          </div>

          {/* Processing Jobs */}
          {jobs.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileVideo className="h-5 w-5" />
                  Processing Queue
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {jobs.map((job) => (
                  <div
                    key={job.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      {getStatusIcon(job.status)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-gray-900">
                            {job.filename}
                          </span>
                          <Badge className={getStatusBadge(job.status)}>
                            {job.status}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                          Started {formatDate(job.created_at)}
                        </div>
                        {job.status === 'processing' && job.progress && (
                          <Progress value={job.progress} className="w-full mt-2" />
                        )}
                        {job.error_message && (
                          <div className="text-sm text-red-600 mt-1">
                            {job.error_message}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {job.status === 'completed' && (
                        <Button
                          size="sm"
                          onClick={() => handleDownload(job)}
                          className="flex items-center gap-1"
                        >
                          <Download className="h-4 w-4" />
                          Download
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Empty State */}
          {jobs.length === 0 && (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <FileVideo className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No videos uploaded yet
                  </h3>
                  <p className="text-gray-600">
                    Upload your first video to get started with profanity detection
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadPageIntegrated;
