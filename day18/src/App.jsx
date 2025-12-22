import React, { useState, useEffect } from 'react';
import AudioPlayer from './components/AudioPlayer';
import ArtworkGallery from './components/ArtworkGallery';
import DeepZoom from './components/DeepZoom';
import { useSyncEngine } from './hooks/useSyncEngine';
import metadata from './data/temporal-metadata.json';

// Placeholder audio path - assumes file placed in public/audio/
const AUDIO_SRC = "/audio/museum-tour.mp3";

function App() {
  const [audioTime, setAudioTime] = useState(0);
  const [seekTime, setSeekTime] = useState(null);

  // Use the sync engine to find the *supposed* active item based on time
  const syncedActiveItem = useSyncEngine(audioTime);

  // We can also have a "user selected" state if we want to separate "what is clicked" vs "what is playing"
  // For bi-directional sync:
  // 1. Audio time updates -> updates syncedActiveItem -> updates View.
  // 2. User clicks Item -> updates seekTime -> updates Audio -> updates Audio time -> updates View.
  // So a single point of truth (Time) is best.

  // However, for "Deep Zoom", we usually want it to stay open on the active item.
  // syncedActiveItem handles "Auto-Highlight".

  const handleItemClick = (item) => {
    // Seek audio to item start
    setSeekTime(item.start);
    // Reset seekTime immediately after passing it down so it doesn't lock
    // Actually standard pattern is passing a value that changes or a trigger.
    // AudioPlayer useEffect listens to seekTime changes. 
    // If we click the same item twice, seeking to same time is fine.
    // But we need to make sure AudioPlayer reacts.
  };

  return (
    <div className="min-h-screen bg-white font-sans text-gray-900">

      {/* Intro / Hero / Active Item View */}
      <DeepZoom activeItem={syncedActiveItem} />

      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-lg font-bold tracking-wide uppercase text-gray-400">Collection Highlights</h2>
          <span className="text-sm text-gray-400">{metadata.length} Artifacts</span>
        </div>

        <ArtworkGallery
          items={metadata}
          activeItemId={syncedActiveItem?.id}
          onItemClick={handleItemClick}
        />
      </main>

      <AudioPlayer
        audioSrc={AUDIO_SRC}
        onTimeUpdate={(t) => setAudioTime(t)}
        onDurationChange={() => { }}
        externalSeekTime={seekTime}
      />
    </div>
  );
}

export default App;
