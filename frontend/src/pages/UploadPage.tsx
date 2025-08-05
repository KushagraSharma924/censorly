import React, { useState, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  FileVideo, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Download,
  AlertCircle,
  Trash2
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8080';

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  jobId?: string;
  resultUrl?: string;
  error?: string;
}

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploadSettings, setUploadSettings] = useState({
    auto_censor: true,
    profanity_level: 'medium',
    beep_sound: true,
    custom_wordlist: ''
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList) => {
    const newFiles: UploadedFile[] = Array.from(fileList).map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: 'uploading'
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
      console.log('API URL:', `${API_BASE_URL}/api/process-video`);

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

      xhr.open('POST', `${API_BASE_URL}/api/process-video`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);

    } catch (error) {
      console.error('Upload error:', error);
      updateFileStatus(fileData.id, 'failed', 'Failed to start upload');
    }
  };

  const pollJobStatus = async (fileId: string, jobId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
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
      const response = await fetch(`${API_BASE_URL}/api/download/${jobId}`, {
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

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return <Upload className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'processing':
        return <Clock className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-100 text-blue-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
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
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Videos</h1>
          <p className="text-gray-600">
            Upload your videos to detect and filter profanity with AI
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Area */}
            <Card>
              <CardHeader>
                <CardTitle>Select Videos</CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Drop your videos here
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Or click to browse and select files
                  </p>
                  <Button 
                    onClick={() => fileInputRef.current?.click()}
                    className="mb-4"
                  >
                    Choose Files
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept="video/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <p className="text-xs text-gray-500">
                    Supported formats: MP4, AVI, MOV, WMV, MKV (max 500MB per file)
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Upload Queue */}
            {files.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Upload Queue</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {files.map((file) => (
                      <div key={file.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <FileVideo className="h-5 w-5 text-gray-400" />
                            <div>
                              <p className="font-medium text-gray-900">{file.file.name}</p>
                              <p className="text-sm text-gray-600">
                                {formatFileSize(file.file.size)}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <Badge className={getStatusColor(file.status)}>
                              {getStatusIcon(file.status)}
                              <span className="ml-1 capitalize">{file.status}</span>
                            </Badge>
                            {file.status === 'completed' && file.jobId && (
                              <Button 
                                variant="outline" 
                                size="sm" 
                                onClick={() => downloadFile(file.jobId!, file.file.name)}
                              >
                                <Download className="h-4 w-4 mr-2" />
                                Download
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeFile(file.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        
                        {(file.status === 'uploading' || file.status === 'processing') && (
                          <Progress value={file.progress} className="h-2" />
                        )}
                        
                        {file.error && (
                          <Alert className="mt-2 border-red-200 bg-red-50">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription className="text-red-700">
                              {file.error}
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Settings Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Processing Settings</CardTitle>
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
                    rows={4}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Add custom words or phrases to be detected and censored
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Usage Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Detection method:</span>
                    <span className="font-medium">Regex & Keyword</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Processing method:</span>
                    <span className="font-medium">Regex & Keyword Detection</span>
                  </div>
                  <div className="text-xs text-orange-600 mt-1">
                    Advanced AI detection coming in Pro tier
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Processing time:</span>
                    <span className="font-medium">~2-5 minutes per video</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Supported languages:</span>
                    <span className="font-medium">English only</span>
                  </div>
                  <div className="text-xs text-orange-600 mt-1">
                    Multi-language support coming in Pro tier
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Max file size:</span>
                    <span className="font-medium">500MB</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Concurrent uploads:</span>
                    <span className="font-medium">Up to 3 files</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
