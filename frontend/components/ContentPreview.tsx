'use client';

import { downloadFile } from '@/lib/api';

interface ContentPreviewProps {
  jobId: string;
  contentTypes: string[];
  files: Record<string, string>;
}

export default function ContentPreview({
  jobId,
  contentTypes,
  files,
}: ContentPreviewProps) {
  const contentLabels: Record<string, string> = {
    flashcards: 'Flashcards',
    infographics: 'Infographics',
    video_script: 'Video Script',
    podcast: 'Podcast Script',
  };

  const handleDownload = (fileType: string) => {
    const url = downloadFile(jobId, fileType);
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = ''; // Let browser determine filename from Content-Disposition header
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-bold text-special-black tracking-wide">Generated Content</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contentTypes.map((type) => (
          <div
            key={type}
            className="p-6 border border-light-grey bg-white"
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-bold text-special-black mb-1 tracking-wide">
                  {contentLabels[type] || type}
                </h4>
                <p className="text-sm text-special-black/70 font-light">Ready for download</p>
              </div>
              <button
                onClick={() => handleDownload(type)}
                className="px-6 py-2 bg-brick-red text-white font-medium hover:bg-brick-red/90 transition-colors"
              >
                Download
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
