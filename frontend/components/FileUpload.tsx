'use client';

import { useCallback, useState } from 'react';
import { uploadImages, UploadResponse } from '@/lib/api';

interface FileUploadProps {
  onUploadComplete: (response: UploadResponse) => void;
  onError: (error: string) => void;
}

export default function FileUpload({ onUploadComplete, onError }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      (file) => file.type.startsWith('image/')
    );

    if (droppedFiles.length > 0) {
      setFiles((prev) => [...prev, ...droppedFiles]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []).filter(
      (file) => file.type.startsWith('image/')
    );

    if (selectedFiles.length > 0) {
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  }, []);

  const handleUpload = useCallback(async () => {
    if (files.length === 0) {
      onError('Please select at least one image file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await uploadImages(files);
      setUploadProgress(100);
      onUploadComplete(response);
      setFiles([]);
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed. Please try again.';
      onError(errorMessage);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [files, onUploadComplete, onError]);

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="w-full space-y-6">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed p-12 text-center transition-colors
          ${isDragging ? 'border-brick-red bg-light-grey' : 'border-light-grey hover:border-special-black/30'}
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
          disabled={isUploading}
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center space-y-4"
        >
          <svg
            className="w-16 h-16 text-special-black/40"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>
          <div className="space-y-2">
            <p className="text-special-black font-medium">
              <span className="text-brick-red">Click to upload</span> or drag and drop
            </p>
            <p className="text-sm text-special-black/60 font-light">
              PNG, JPG, GIF, WEBP up to 100MB each
            </p>
          </div>
        </label>
      </div>

      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-special-black">
              Selected Files ({files.length})
            </h3>
            <button
              onClick={() => setFiles([])}
              className="text-sm text-brick-red hover:text-brick-red/80 font-medium"
              disabled={isUploading}
            >
              Clear All
            </button>
          </div>
          <div className="max-h-48 overflow-y-auto space-y-2 border border-light-grey">
            {files.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center justify-between p-4 bg-light-grey/30 border-b border-light-grey last:border-b-0"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-special-black truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-special-black/60 font-light">{formatFileSize(file.size)}</p>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="ml-4 text-brick-red hover:text-brick-red/80 transition-colors"
                  disabled={isUploading}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {isUploading && (
        <div className="w-full bg-light-grey h-1">
          <div
            className="bg-brick-red h-1 transition-all duration-300"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={files.length === 0 || isUploading}
        className={`
          w-full py-4 px-6 font-medium text-white transition-colors
          ${files.length === 0 || isUploading
            ? 'bg-light-grey text-special-black/50 cursor-not-allowed'
            : 'bg-brick-red hover:bg-brick-red/90 text-white'
          }
        `}
      >
        {isUploading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
      </button>
    </div>
  );
}
