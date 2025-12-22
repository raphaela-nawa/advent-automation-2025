import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, SkipBack, SkipForward } from 'lucide-react';

export default function AudioPlayer({ audioSrc, onTimeUpdate, onDurationChange, externalSeekTime }) {
    const audioRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);

    useEffect(() => {
        if (externalSeekTime !== null && audioRef.current) {
            audioRef.current.currentTime = externalSeekTime;
            if (!isPlaying) {
                audioRef.current.play().then(() => setIsPlaying(true)).catch(e => console.error("Play error", e));
            }
        }
    }, [externalSeekTime]);

    const togglePlay = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
            } else {
                audioRef.current.play().catch(e => console.error("Play failed:", e));
            }
            setIsPlaying(!isPlaying);
        }
    };

    const handleTimeUpdate = () => {
        if (audioRef.current) {
            const current = audioRef.current.currentTime;
            setProgress(current);
            onTimeUpdate(current);
        }
    };

    const handleLoadedMetadata = () => {
        if (audioRef.current) {
            setDuration(audioRef.current.duration);
            onDurationChange(audioRef.current.duration);
        }
    };

    const handleSeek = (e) => {
        const time = parseFloat(e.target.value);
        if (audioRef.current) {
            audioRef.current.currentTime = time;
            setProgress(time);
            onTimeUpdate(time);
        }
    };

    const formatTime = (time) => {
        if (!time) return "0:00";
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    return (
        <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-200 p-4 z-50 shadow-lg">
            <div className="max-w-4xl mx-auto flex flex-col gap-2">
                <div className="flex items-center justify-between gap-4">

                    <div className="flex items-center gap-4">
                        <button
                            onClick={togglePlay}
                            className="w-12 h-12 flex items-center justify-center rounded-full bg-black text-white hover:bg-gray-800 transition-colors"
                            aria-label={isPlaying ? "Pause" : "Play"}
                        >
                            {isPlaying ? <Pause size={24} /> : <Play size={24} fill="currentColor" className="ml-1" />}
                        </button>

                        <div className="text-sm font-medium tabular-nums">
                            {formatTime(progress)} / {formatTime(duration)}
                        </div>
                    </div>

                    <div className="flex-1 mx-4">
                        <input
                            type="range"
                            min="0"
                            max={duration || 100}
                            value={progress}
                            onChange={handleSeek}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-black"
                        />
                    </div>

                </div>
                <audio
                    ref={audioRef}
                    src={audioSrc}
                    onTimeUpdate={handleTimeUpdate}
                    onLoadedMetadata={handleLoadedMetadata}
                    onEnded={() => setIsPlaying(false)}
                />
            </div>
        </div>
    );
}
