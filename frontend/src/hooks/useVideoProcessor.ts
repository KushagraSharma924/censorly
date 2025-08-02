import { useState } from 'react';

const API_BASE_URL = 'http://localhost:8080';

export interface ProcessingResult {
  success: boolean;
  fileName?: string;
  downloadUrl?: string;
  error?: string;
}

export const useVideoProcessor = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);

  const processVideo = async (file: File, mode: string): Promise<ProcessingResult> => {
    setIsProcessing(true);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('video', file);
      formData.append('mode', mode);

      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - let browser set it with boundary for FormData
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error occurred' }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      // Check if response is a file (video) or JSON (error)
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('video/')) {
        // Create a blob URL for the video file
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        
        // Extract filename from Content-Disposition header if available
        const contentDisposition = response.headers.get('content-disposition');
        let fileName = `processed_${file.name}`;
        
        if (contentDisposition) {
          const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
          if (fileNameMatch && fileNameMatch[1]) {
            fileName = fileNameMatch[1].replace(/['"]/g, '');
          }
        }

        return {
          success: true,
          fileName,
          downloadUrl
        };
      } else {
        // Handle JSON response (likely an error)
        const result = await response.json();
        throw new Error(result.error || 'Processing failed');
      }

    } catch (error) {
      console.error('Video processing error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'An unknown error occurred'
      };
    } finally {
      setIsProcessing(false);
      setProgress(0);
    }
  };

  const downloadFile = (downloadUrl: string, fileName: string) => {
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    // Clean up the blob URL after download
    window.URL.revokeObjectURL(downloadUrl);
  };

  return {
    processVideo,
    downloadFile,
    isProcessing,
    progress
  };
};
