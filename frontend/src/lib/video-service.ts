import { API_ENDPOINTS, buildApiUrl } from '@/config/api';

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
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const formData = new FormData();
    formData.append('video_file', file);  // Changed from 'video' to 'video_file'
    formData.append('mode', options.censoring_mode); // Changed from 'censoring_mode' to 'mode'
    
    if (options.profanity_threshold) {
      formData.append('profanity_threshold', options.profanity_threshold.toString());
    }
    
    if (options.languages) {
      formData.append('languages', JSON.stringify(options.languages));
    }

    const response = await fetch(buildApiUrl(API_ENDPOINTS.VIDEO.PROCESS), {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      job_id: data.job_id,
      message: data.message
    };
  },

  getJobStatus: async (jobId: string): Promise<any> => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(buildApiUrl(API_ENDPOINTS.VIDEO.STATUS(jobId)), {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }

    return await response.json();
  },

  downloadProcessedVideo: async (jobId: string, originalFilename: string): Promise<{ url: string, filename: string }> => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(buildApiUrl(API_ENDPOINTS.VIDEO.DOWNLOAD(jobId)), {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error ${response.status}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const filename = `processed_${originalFilename}`;

    return { url, filename };
  }
};
