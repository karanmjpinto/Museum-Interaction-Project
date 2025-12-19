'use client';

interface ContentCardProps {
  type: 'flashcards' | 'infographics' | 'video_script' | 'podcast';
  title: string;
  description: string;
  selected: boolean;
  onToggle: () => void;
}

export default function ContentCard({
  type,
  title,
  description,
  selected,
  onToggle,
}: ContentCardProps) {
  const icons = {
    flashcards: '📚',
    infographics: '📊',
    video_script: '🎬',
    podcast: '🎙️',
  };

  return (
    <button
      onClick={onToggle}
      className={`
        w-full p-6 text-left transition-all border-2
        ${selected
          ? 'border-brick-red bg-light-grey'
          : 'border-light-grey bg-white hover:border-special-black/30'
        }
      `}
    >
      <div className="flex items-start space-x-4">
        <div className="text-3xl">{icons[type]}</div>
        <div className="flex-1">
          <h3 className="font-bold text-special-black mb-2 tracking-wide">{title}</h3>
          <p className="text-sm text-special-black/70 font-light leading-relaxed">{description}</p>
        </div>
        <div
          className={`
            w-6 h-6 flex items-center justify-center border-2 flex-shrink-0
            ${selected ? 'border-brick-red bg-brick-red' : 'border-light-grey bg-white'}
          `}
        >
          {selected && (
            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
      </div>
    </button>
  );
}
