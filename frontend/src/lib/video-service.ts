import { apiService } from './api-service';

interface UploadOptions {
  censoring_mode: 'beep' | 'mute' | 'cut';
  profanity_threshold?: number;
  languages?: string[];
}

interface UploadResult {
  success: boolean;
  job_id: string;
  message?: string;
}

export const videoService = {
  uploadVideo: async (file: File, options: UploadOptions): Promise<UploadResult> => {
    const data = await apiService.uploadVideo(file, options);
    return {
      success: true,
      job_id: data.job_id,
      message: data.message
    };
  },

  getJobStatus: async (jobId: string): Promise<any> => {
    return apiService.getJobStatus(jobId);
  },

  downloadProcessedVideo: async (jobId: string, originalFilename: string): Promise<{ url: string, filename: string }> => {
    const blob = await apiService.downloadVideo(jobId);
    const url = window.URL.createObjectURL(blob);
    const filename = `processed_${originalFilename}`;

    return { url, filename };
  }
};
