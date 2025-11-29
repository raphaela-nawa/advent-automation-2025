"""
Day 05: Whisper Audio Transcription Script
Transcribes 5 podcast episodes in Brazilian Portuguese with timestamps

Usage:
    python day05_DATA_transcribe_whisper.py
"""

from faster_whisper import WhisperModel
import json
from pathlib import Path
from datetime import datetime
import sys

# Import day05 configuration
from day05_CONFIG_settings import (
    day05_AUDIO_DIR,
    day05_TRANSCRIPTS_DIR,
    day05_WHISPER_MODEL,
    day05_AUDIO_LANGUAGE,
    day05_ensure_directories,
    day05_get_audio_files
)


class day05_WhisperTranscriber:
    """Handles transcription of podcast episodes using Faster Whisper"""

    def __init__(self):
        """Initialize Faster Whisper model"""
        print(f"🔄 Loading Faster Whisper model: {day05_WHISPER_MODEL}")
        print("   (This may take a few moments on first run...)")

        # Use CPU by default for compatibility
        self.model = WhisperModel(
            day05_WHISPER_MODEL,
            device="cpu",
            compute_type="int8"
        )
        print(f"✅ Whisper model loaded successfully")

    def day05_transcribe_audio(self, audio_path: Path) -> dict:
        """
        Transcribe a single audio file with timestamps

        Args:
            audio_path: Path to audio file

        Returns:
            dict with transcription data including segments with timestamps
        """
        print(f"\n🎙️  Transcribing: {audio_path.name}")
        print(f"   Language: {day05_AUDIO_LANGUAGE}")

        # Transcribe with faster-whisper
        segments, info = self.model.transcribe(
            str(audio_path),
            language=day05_AUDIO_LANGUAGE,
            word_timestamps=False,  # faster-whisper uses different API
            vad_filter=True  # Voice Activity Detection for better segmentation
        )

        # Convert generator to list
        segments_list = list(segments)

        # Build full text
        full_text = " ".join([seg.text.strip() for seg in segments_list])

        # Extract metadata
        transcript_data = {
            "file_name": audio_path.name,
            "transcription_date": datetime.now().isoformat(),
            "language": day05_AUDIO_LANGUAGE,
            "model": day05_WHISPER_MODEL,
            "full_text": full_text,
            "segments": []
        }

        # Process segments with timestamps
        for idx, segment in enumerate(segments_list):
            segment_data = {
                "id": idx,
                "start": self.day05_format_timestamp(segment.start),
                "end": self.day05_format_timestamp(segment.end),
                "start_seconds": segment.start,
                "end_seconds": segment.end,
                "text": segment.text.strip()
            }
            transcript_data["segments"].append(segment_data)

        print(f"   ✅ Transcribed {len(transcript_data['segments'])} segments")
        if segments_list:
            print(f"   ⏱️  Duration: {self.day05_format_timestamp(segments_list[-1].end)}")

        return transcript_data

    @staticmethod
    def day05_format_timestamp(seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def day05_save_transcript(self, transcript_data: dict, episode_id: str):
        """Save transcript to JSON file"""
        output_path = day05_TRANSCRIPTS_DIR / f"episode_{episode_id}_transcript.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        print(f"   💾 Saved to: {output_path.name}")

        # Also save plain text version
        txt_path = day05_TRANSCRIPTS_DIR / f"episode_{episode_id}_transcript.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Episode {episode_id} - Transcription\n")
            f.write(f"Generated: {transcript_data['transcription_date']}\n")
            f.write(f"Model: {transcript_data['model']}\n")
            f.write("=" * 80 + "\n\n")

            for segment in transcript_data["segments"]:
                f.write(f"[{segment['start']}] {segment['text']}\n")

        print(f"   📝 Plain text: {txt_path.name}")

        return output_path


def day05_main():
    """Main transcription pipeline"""
    print("=" * 80)
    print("Day 05: Podcast Transcription Pipeline")
    print("Museu Ipiranga Cultural Data - Faster Whisper")
    print("=" * 80)

    # Ensure directories exist
    day05_ensure_directories()

    # Get audio files
    audio_files = day05_get_audio_files()

    if not audio_files:
        print("\n❌ ERROR: No audio files found!")
        print(f"   Expected location: {day05_AUDIO_DIR}")
        print(f"   Expected naming: episode_01.mp3, episode_02.mp3, etc.")
        print(f"   Supported formats: .mp3, .wav, .m4a, .flac, .ogg")
        sys.exit(1)

    print(f"\n📂 Found {len(audio_files)} audio file(s):")
    for f in audio_files:
        print(f"   - {f.name}")

    # Initialize transcriber
    transcriber = day05_WhisperTranscriber()

    # Process each audio file
    results = []
    for audio_file in audio_files:
        # Extract episode ID from filename (e.g., episode_01.mp3 -> 01)
        episode_id = audio_file.stem.split('_')[-1] if '_' in audio_file.stem else audio_file.stem

        try:
            transcript_data = transcriber.day05_transcribe_audio(audio_file)
            output_path = transcriber.day05_save_transcript(transcript_data, episode_id)

            results.append({
                "episode_id": episode_id,
                "audio_file": audio_file.name,
                "transcript_file": output_path.name,
                "status": "success",
                "segments": len(transcript_data["segments"])
            })

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append({
                "episode_id": episode_id,
                "audio_file": audio_file.name,
                "status": "failed",
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 80)
    print("📊 Transcription Summary")
    print("=" * 80)

    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")

    if successful:
        print(f"\n📁 Transcripts saved to: {day05_TRANSCRIPTS_DIR}")
        for r in successful:
            print(f"   - Episode {r['episode_id']}: {r['segments']} segments")

    if failed:
        print("\n⚠️  Failed transcriptions:")
        for r in failed:
            print(f"   - {r['audio_file']}: {r['error']}")

    print("\n✅ Transcription pipeline complete!")
    print(f"📂 Next step: Review transcripts in {day05_TRANSCRIPTS_DIR}")
    print(f"🔜 Then run: python day05_PIPELINE_extract_items.py")


if __name__ == "__main__":
    day05_main()
