'use client';

interface ProgressBarProps {
  progress: number;
  status: string;
  totalImages: number;
  processedImages: number;
}

export default function ProgressBar({
  progress,
  status,
  totalImages,
  processedImages,
}: ProgressBarProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-brick-red';
      case 'failed':
        return 'bg-special-black';
      case 'processing':
        return 'bg-brick-red';
      default:
        return 'bg-light-grey';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return 'COMPLETED';
      case 'failed':
        return 'FAILED';
      case 'processing':
        return 'PROCESSING';
      default:
        return 'PENDING';
    }
  };

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="font-bold text-special-black tracking-wide">{getStatusText()}</span>
        <span className="text-special-black/70 font-light">
          {processedImages} / {totalImages} images
        </span>
      </div>
      <div className="w-full bg-light-grey h-1">
        <div
          className={`${getStatusColor()} h-1 transition-all duration-300`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <p className="text-xs text-special-black/60 font-light">{Math.round(progress)}% complete</p>
    </div>
  );
}
