import React, { useState, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Header } from '@/components/Header';
import { UploadGuide } from '@/components/UploadGuide';
import { EnhancedUploadArea } from '@/components/EnhancedUploadArea';
import { FileStatusList, type FileStatusItem } from '@/components/FileStatusList';
import { 
  AlertCircle,
  Settings,
  Zap
} from 'lucide-react';
import { API_ENDPOINTS, buildApiUrl, getDefaultFetchOptions } from '@/config/api';

interface UploadedFile extends FileStatusItem {}

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSettings, setUploadSettings] = useState({
    auto_censor: true,
    profanity_level: 'medium',
    beep_sound: true,
    custom_wordlist: ''
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList) => {
    setIsUploading(true);
    
    const newFiles: UploadedFile[] = Array.from(fileList).map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: 'uploading',
      estimatedTime: Math.floor(file.size / (1024 * 1024)) * 30 // Rough estimate: 30 seconds per MB
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Start uploading each file
    newFiles.forEach(uploadFile);
  };

  const uploadFile = async (fileData: UploadedFile) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        updateFileStatus(fileData.id, 'failed', 'Not authenticated - please login first');
        return;
      }

      console.log('Starting upload for:', fileData.file.name);
      console.log('Token exists:', !!token);
      console.log('API URL:', buildApiUrl(API_ENDPOINTS.VIDEO.PROCESS));

      const formData = new FormData();
      formData.append('video', fileData.file);
      
      // Add processing settings using the correct variable name
      formData.append('censoring_mode', 'beep');  // Default to beep
      formData.append('abuse_threshold', '0.7');  // Default threshold
      formData.append('languages', JSON.stringify(['auto']));
      // Note: whisper_model is now automatically determined by subscription tier

      if (uploadSettings.custom_wordlist && uploadSettings.custom_wordlist.trim()) {
        formData.append('custom_wordlist', uploadSettings.custom_wordlist);
      }

      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          updateFileProgress(fileData.id, progress);
        }
      });

      xhr.onload = async () => {
        if (xhr.status === 200 || xhr.status === 202) {  // Accept both 200 and 202 status codes
          const response = JSON.parse(xhr.responseText);
          updateFileStatus(fileData.id, 'processing', undefined, response.job_id);
          
          // Start polling for job status
          pollJobStatus(fileData.id, response.job_id);
        } else {
          console.error('Upload failed with status:', xhr.status, xhr.responseText);
          try {
            const error = JSON.parse(xhr.responseText);
            updateFileStatus(fileData.id, 'failed', error.error || `Upload failed (${xhr.status})`);
          } catch (e) {
            updateFileStatus(fileData.id, 'failed', `Upload failed (${xhr.status})`);
          }
        }
      };

      xhr.onerror = () => {
        updateFileStatus(fileData.id, 'failed', 'Network error during upload');
      };

      xhr.open('POST', buildApiUrl(API_ENDPOINTS.VIDEO.PROCESS));
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);

    } catch (error) {
      console.error('Upload error:', error);
      updateFileStatus(fileData.id, 'failed', 'Failed to start upload');
    } finally {
      // Check if all files are done uploading
      setTimeout(() => {
        setFiles(currentFiles => {
          const allDone = currentFiles.every(f => 
            f.status === 'completed' || f.status === 'failed'
          );
          if (allDone) {
            setIsUploading(false);
          }
          return currentFiles;
        });
      }, 1000);
    }
  };

  const retryFile = (file: UploadedFile) => {
    // Reset file status and retry upload
    updateFileStatus(file.id, 'uploading');
    updateFileProgress(file.id, 0);
    uploadFile(file);
  };

  const pollJobStatus = async (fileId: string, jobId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.VIDEO.STATUS(jobId)), {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const jobData = await response.json();
        
        if (jobData.status === 'completed') {
          updateFileStatus(fileId, 'completed', undefined, jobId, jobData.download_url);
        } else if (jobData.status === 'failed') {
          updateFileStatus(fileId, 'failed', jobData.error_message || 'Processing failed');
        } else {
          // Continue polling
          setTimeout(() => pollJobStatus(fileId, jobId), 3000);
        }
      } else {
        updateFileStatus(fileId, 'failed', 'Failed to check job status');
      }
    } catch (error) {
      console.error('Polling error:', error);
      updateFileStatus(fileId, 'failed', 'Error checking job status');
    }
  };

  const updateFileProgress = (fileId: string, progress: number) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, progress }
        : file
    ));
  };

  const updateFileStatus = (
    fileId: string, 
    status: UploadedFile['status'], 
    error?: string,
    jobId?: string,
    resultUrl?: string
  ) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, status, error, jobId, resultUrl, progress: status === 'completed' ? 100 : file.progress }
        : file
    ));
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const downloadFile = async (jobId: string, filename: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.VIDEO.DOWNLOAD(jobId)), {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `processed_${filename}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Download failed:', response.statusText);
        alert('Download failed. Please try again.');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed. Please check your connection and try again.');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <div className="py-8 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Page Title */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-black">Upload & Clean Videos</h1>
            <p className="text-gray-700">
              Upload your videos to detect and filter profanity with advanced AI technology
            </p>
          </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Enhanced Upload Area */}
            <EnhancedUploadArea
              onFileSelect={handleFiles}
              isUploading={isUploading}
              dragActive={dragActive}
              onDragStateChange={setDragActive}
              maxSize={500}
              multiple={true}
            />

            {/* Upload Queue */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Upload Queue</span>
                  {files.length > 0 && (
                    <Badge variant="outline">
                      {files.filter(f => f.status === 'completed').length} / {files.length} completed
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FileStatusList
                  files={files}
                  onDownload={downloadFile}
                  onRemove={removeFile}
                  onRetry={retryFile}
                  isLoading={isUploading && files.length === 0}
                />
              </CardContent>
            </Card>
          </div>

          {/* Settings & Guide Panel */}
          <div className="space-y-6">
            <UploadGuide />
            {/* Processing Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="h-5 w-5 mr-2" />
                  Processing Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={uploadSettings.auto_censor}
                      onChange={(e) => setUploadSettings(prev => ({
                        ...prev,
                        auto_censor: e.target.checked
                      }))}
                      className="rounded"
                    />
                    <span>Auto-censor detected profanity</span>
                  </Label>
                  <p className="text-xs text-gray-500 mt-1">
                    Automatically replace profane words with beeps or silence
                  </p>
                </div>

                <div>
                  <Label htmlFor="profanity_level">Detection Sensitivity</Label>
                  <select
                    id="profanity_level"
                    value={uploadSettings.profanity_level}
                    onChange={(e) => setUploadSettings(prev => ({
                      ...prev,
                      profanity_level: e.target.value
                    }))}
                    className="w-full mt-1 p-2 border border-gray-300 rounded-md"
                  >
                    <option value="low">Low - Only severe profanity</option>
                    <option value="medium">Medium - Most profanity</option>
                    <option value="high">High - All inappropriate content</option>
                  </select>
                </div>

                <div>
                  <Label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={uploadSettings.beep_sound}
                      onChange={(e) => setUploadSettings(prev => ({
                        ...prev,
                        beep_sound: e.target.checked
                      }))}
                      className="rounded"
                    />
                    <span>Use beep sound for censoring</span>
                  </Label>
                  <p className="text-xs text-gray-500 mt-1">
                    Replace profanity with beep sound instead of silence
                  </p>
                </div>

                <div>
                  <Label htmlFor="custom_wordlist">Custom Word List</Label>
                  <Textarea
                    id="custom_wordlist"
                    placeholder="Enter additional words to detect (one per line)"
                    value={uploadSettings.custom_wordlist}
                    onChange={(e) => setUploadSettings(prev => ({
                      ...prev,
                      custom_wordlist: e.target.value
                    }))}
                    className="mt-1"
                    rows={3}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Add custom words or phrases to be detected
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="h-5 w-5 mr-2" />
                  Processing Info
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Detection method</p>
                    <p className="font-medium">AI + Regex</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Avg. processing</p>
                    <p className="font-medium">2-5 minutes</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Languages</p>
                    <p className="font-medium">English</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Max file size</p>
                    <p className="font-medium">500MB</p>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                    <div className="text-xs text-blue-700">
                      <p className="font-medium">Pro features coming soon:</p>
                      <p>• Multi-language support</p>
                      <p>• Advanced AI detection</p>
                      <p>• Batch processing</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
