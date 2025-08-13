/**
 * Video processing utilities
 */

import { apiService } from './api-service';

export interface VideoProcessingOptions {
  censoring_mode: 'beep' | 'mute' | 'cut';
  profanity_threshold?: number;
  languages?: string[];
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  created_at: string;
  updated_at?: string;
  error_message?: string;
  result?: any;
}

export class VideoProcessor {
  
  /**
   * Upload and process a video file
   */
  static async processVideo(file: File, options: VideoProcessingOptions): Promise<{
    job_id: string;
    message: string;
    status: string;
  }> {
    return apiService.uploadVideo(file, options);
  }

  /**
   * Get job status and progress
   */
  static async getJobStatus(jobId: string): Promise<JobStatus> {
    return apiService.getJobStatus(jobId);
  }

  /**
   * Download processed video
   */
  static async downloadVideo(jobId: string, originalFilename?: string): Promise<void> {
    try {
      const blob = await apiService.downloadVideo(jobId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename
      const filename = originalFilename 
        ? `processed_${originalFilename}`
        : `processed_video_${jobId}.mp4`;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      throw error;
    }
  }

  /**
   * Poll job status until completion or failure
   */
  static async pollJobStatus(
    jobId: string, 
    onUpdate?: (status: JobStatus) => void,
    interval: number = 2000,
    maxAttempts: number = 150 // 5 minutes at 2-second intervals
  ): Promise<JobStatus> {
    let attempts = 0;
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          attempts++;
          const status = await this.getJobStatus(jobId);
          
          if (onUpdate) {
            onUpdate(status);
          }
          
          // Job completed successfully
          if (status.status === 'completed') {
            resolve(status);
            return;
          }
          
          // Job failed
          if (status.status === 'failed') {
            reject(new Error(status.error_message || 'Job failed'));
            return;
          }
          
          // Max attempts reached
          if (attempts >= maxAttempts) {
            reject(new Error('Polling timeout - job taking too long'));
            return;
          }
          
          // Continue polling
          setTimeout(poll, interval);
          
        } catch (error) {
          reject(error);
        }
      };
      
      // Start polling
      poll();
    });
  }

  /**
   * Validate video file before upload
   */
  static validateVideoFile(file: File): { valid: boolean; error?: string } {
    // Check file type
    const allowedTypes = [
      'video/mp4',
      'video/avi', 
      'video/mov',
      'video/quicktime',
      'video/x-msvideo',
      'video/webm',
      'video/mkv',
      'video/x-matroska'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'Unsupported file format. Please use MP4, AVI, MOV, MKV, or WEBM.'
      };
    }
    
    // Check file size (500MB limit based on backend)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
      return {
        valid: false,
        error: 'File size exceeds 500MB limit.'
      };
    }
    
    return { valid: true };
  }

  /**
   * Get human-readable file size
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Get processing time estimate based on file size
   */
  static getProcessingTimeEstimate(fileSizeBytes: number): string {
    const fileSizeMB = fileSizeBytes / (1024 * 1024);
    
    if (fileSizeMB < 50) return '1-2 minutes';
    if (fileSizeMB < 200) return '2-5 minutes';
    if (fileSizeMB < 500) return '5-10 minutes';
    return '10-15 minutes';
  }
}

export default VideoProcessor;
