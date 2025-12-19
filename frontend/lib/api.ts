/** API client for backend communication */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Remove Content-Type header for FormData requests (browser sets it automatically with boundary)
api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

// Remove Content-Type header for FormData requests (browser sets it automatically with boundary)
api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

export interface UploadResponse {
  job_id: string;
  message: string;
  files_uploaded: number;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total_images: number;
  processed_images: number;
  message?: string;
}

export interface TranscriptionResult {
  filename: string;
  text: string;
  success: boolean;
  error?: string;
}

export interface JobResults {
  job_id: string;
  status: string;
  results: TranscriptionResult[];
  compiled_text?: string;
}

export interface ContentGenerationRequest {
  job_id: string;
  content_types: ('flashcards' | 'infographics' | 'video_script' | 'podcast')[];
  customizations?: Record<string, any>;
}

export interface ContentGenerationResponse {
  job_id: string;
  content_types: string[];
  files: Record<string, string>;
  message: string;
}

export const uploadImages = async (files: File[]): Promise<UploadResponse> => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  // Don't set Content-Type header - browser will set it automatically with boundary
  const response = await api.post<UploadResponse>('/api/upload', formData);

  return response.data;
};

export const startTranscription = async (jobId: string): Promise<void> => {
  await api.post(`/api/transcribe/${jobId}`);
};

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await api.get<JobStatus>(`/api/job/${jobId}/status`);
  return response.data;
};

export const getJobResults = async (jobId: string): Promise<JobResults> => {
  const response = await api.get<JobResults>(`/api/job/${jobId}/results`);
  return response.data;
};

export const generateContent = async (
  request: ContentGenerationRequest
): Promise<ContentGenerationResponse> => {
  const response = await api.post<ContentGenerationResponse>(
    '/api/generate-content',
    request
  );
  return response.data;
};

export const downloadFile = (jobId: string, fileType: string): string => {
  return `${API_URL}/api/download/${jobId}/${fileType}`;
};

