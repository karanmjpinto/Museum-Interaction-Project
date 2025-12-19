'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import FileUpload from '@/components/FileUpload';
import ProgressBar from '@/components/ProgressBar';
import ContentCard from '@/components/ContentCard';
import ContentPreview from '@/components/ContentPreview';
import {
  UploadResponse,
  JobStatus,
  getJobStatus,
  startTranscription,
  generateContent,
  downloadFile,
  ContentGenerationRequest,
} from '@/lib/api';

type ContentType = 'flashcards' | 'infographics' | 'video_script' | 'podcast';

export default function Home() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [selectedContentTypes, setSelectedContentTypes] = useState<ContentType[]>([]);
  const [generatedContent, setGeneratedContent] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  // Poll for job status updates
  useEffect(() => {
    if (!currentJobId || !isPolling) return;

    const interval = setInterval(async () => {
      try {
        const status = await getJobStatus(currentJobId);
        setJobStatus(status);

        if (status.status === 'completed' || status.status === 'failed') {
          setIsPolling(false);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to fetch job status');
        setIsPolling(false);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [currentJobId, isPolling]);

  const handleUploadComplete = async (response: UploadResponse) => {
    setCurrentJobId(response.job_id);
    setError(null);
    
    // Start transcription automatically
    try {
      await startTranscription(response.job_id);
      setIsPolling(true);
      
      // Initial status fetch
      const status = await getJobStatus(response.job_id);
      setJobStatus(status);
    } catch (err: any) {
      setError(err.message || 'Failed to start transcription');
    }
  };

  const handleContentTypeToggle = (type: ContentType) => {
    setSelectedContentTypes((prev) =>
      prev.includes(type)
        ? prev.filter((t) => t !== type)
        : [...prev, type]
    );
  };

  const handleGenerateContent = async () => {
    if (!currentJobId || selectedContentTypes.length === 0) {
      setError('Please select at least one content type');
      return;
    }

    try {
      const request: ContentGenerationRequest = {
        job_id: currentJobId,
        content_types: selectedContentTypes,
      };

      const response = await generateContent(request);
      setGeneratedContent(response);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate content');
    }
  };

  const handleDownloadTranscription = () => {
    if (!currentJobId) return;
    const url = downloadFile(currentJobId, 'transcription');
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = ''; // Let browser determine filename from Content-Disposition header
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Main Content */}
      <div className="flex-1">
        <div className="max-w-7xl mx-auto px-8 py-16">
          {/* Header */}
          <header className="mb-16">
            <h1 className="text-5xl font-bold text-special-black mb-4 tracking-wide">
              Museum Interaction Platform
            </h1>
            <p className="text-xl text-special-black/70 font-light max-w-2xl">
              Transform museum exhibits into engaging educational content through AI-powered transcription and content generation.
            </p>
          </header>

          {/* Error Message */}
          {error && (
            <div className="mb-8 p-4 bg-light-grey border-l-4 border-brick-red">
              <p className="text-special-black font-medium">{error}</p>
            </div>
          )}

          {/* Main Content Area */}
          {!currentJobId ? (
            <div className="bg-white border border-light-grey p-8">
              <h2 className="text-2xl font-bold text-special-black mb-6 tracking-wide">
                Upload Images
              </h2>
              <FileUpload
                onUploadComplete={handleUploadComplete}
                onError={setError}
              />
            </div>
          ) : (
            <div className="space-y-8">
              {/* Progress Section */}
              {jobStatus && (
                <div className="bg-white border border-light-grey p-8">
                  <h2 className="text-2xl font-bold text-special-black mb-6 tracking-wide">
                    Transcription Progress
                  </h2>
                  <ProgressBar
                    progress={jobStatus.progress}
                    status={jobStatus.status}
                    totalImages={jobStatus.total_images}
                    processedImages={jobStatus.processed_images}
                  />
                  {jobStatus.message && (
                    <p className="mt-4 text-sm text-special-black/70 font-light">{jobStatus.message}</p>
                  )}
                </div>
              )}

              {/* Content Generation Section */}
              {jobStatus?.status === 'completed' && !generatedContent && (
                <div className="bg-white border border-light-grey p-8">
                  <h2 className="text-2xl font-bold text-special-black mb-4 tracking-wide">
                    Generate Educational Content
                  </h2>
                  <p className="text-special-black/70 mb-8 font-light max-w-2xl">
                    Select the types of content you'd like to generate from your transcription:
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                    <ContentCard
                      type="flashcards"
                      title="Flashcards"
                      description="Create Q&A flashcards for studying key facts and concepts"
                      selected={selectedContentTypes.includes('flashcards')}
                      onToggle={() => handleContentTypeToggle('flashcards')}
                    />
                    <ContentCard
                      type="infographics"
                      title="Infographics"
                      description="Generate structured summaries perfect for visual presentations"
                      selected={selectedContentTypes.includes('infographics')}
                      onToggle={() => handleContentTypeToggle('infographics')}
                    />
                    <ContentCard
                      type="video_script"
                      title="Video Script"
                      description="Create narration scripts for educational videos"
                      selected={selectedContentTypes.includes('video_script')}
                      onToggle={() => handleContentTypeToggle('video_script')}
                    />
                    <ContentCard
                      type="podcast"
                      title="Podcast Script"
                      description="Format content for podcast or audio narration"
                      selected={selectedContentTypes.includes('podcast')}
                      onToggle={() => handleContentTypeToggle('podcast')}
                    />
                  </div>

                  <div className="flex items-center gap-4">
                    <button
                      onClick={handleGenerateContent}
                      disabled={selectedContentTypes.length === 0}
                      className={`
                        px-8 py-3 font-medium text-white transition-colors
                        ${selectedContentTypes.length === 0
                          ? 'bg-light-grey text-special-black/50 cursor-not-allowed'
                          : 'bg-brick-red hover:bg-brick-red/90 text-white'
                        }
                      `}
                    >
                      Generate Content
                    </button>
                    <button
                      onClick={handleDownloadTranscription}
                      className="px-8 py-3 font-medium text-special-black bg-light-grey hover:bg-light-grey/80 transition-colors border border-light-grey"
                    >
                      Download Transcription
                    </button>
                  </div>
                </div>
              )}

              {/* Generated Content Preview */}
              {generatedContent && (
                <div className="bg-white border border-light-grey p-8">
                  <h2 className="text-2xl font-bold text-special-black mb-6 tracking-wide">
                    Your Content is Ready!
                  </h2>
                  <ContentPreview
                    jobId={generatedContent.job_id}
                    contentTypes={generatedContent.content_types}
                    files={generatedContent.files}
                  />
                  <div className="mt-8 pt-8 border-t border-light-grey">
                    <button
                      onClick={() => {
                        setCurrentJobId(null);
                        setJobStatus(null);
                        setSelectedContentTypes([]);
                        setGeneratedContent(null);
                      }}
                      className="px-8 py-3 font-medium text-special-black bg-light-grey hover:bg-light-grey/80 transition-colors"
                    >
                      Start New Project
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* The Studio Logo Footer */}
      <footer className="border-t border-light-grey mt-auto">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <div className="flex items-center">
            <Image
              src="/logo/TheStudio_Logo_Special-Black-RGB.svg"
              alt="The Studio"
              width={120}
              height={40}
              className="h-8 w-auto"
            />
          </div>
        </div>
      </footer>
    </div>
  );
}
