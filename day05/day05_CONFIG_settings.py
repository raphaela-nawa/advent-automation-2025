"""
Day 05 Configuration Settings
Museu Ipiranga Cultural Data Pipeline
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root config/.env
day05_config_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(day05_config_path)

# Tainacan API Configuration
day05_TAINACAN_API_URL = os.getenv("DAY05_TAINACAN_API_URL", "https://acervoonline.mp.usp.br/wp-json/tainacan/v2/")
day05_WHISPER_MODEL = os.getenv("DAY05_WHISPER_MODEL", "base")
day05_AUDIO_LANGUAGE = os.getenv("DAY05_AUDIO_LANGUAGE", "pt")

# BigQuery Configuration
day05_GCP_PROJECT_ID = os.getenv("DAY05_GCP_PROJECT_ID", "advent2025-day05")
day05_BQ_DATASET = os.getenv("DAY05_BQ_DATASET", "cultural_data")
day05_BQ_TABLE = os.getenv("DAY05_BQ_TABLE", "podcast_museum_mentions")
day05_BQ_LOCATION = os.getenv("DAY05_BQ_LOCATION", "US")

# OpenAI Configuration
day05_OPENAI_API_KEY = os.getenv("KEY_OPENAI_DAY05") or os.getenv("KEY_OPENAI")

# Matching Configuration
day05_SIMILARITY_THRESHOLD = float(os.getenv("DAY05_SIMILARITY_THRESHOLD", "0.6"))
day05_MAX_SEARCH_RESULTS = int(os.getenv("DAY05_MAX_SEARCH_RESULTS", "10"))

# File Paths
day05_BASE_DIR = Path(__file__).parent
day05_DATA_DIR = day05_BASE_DIR / "data"
day05_RAW_DIR = day05_DATA_DIR / "raw"
day05_AUDIO_DIR = day05_RAW_DIR / "audio"
day05_TRANSCRIPTS_DIR = day05_RAW_DIR / "transcripts"
day05_PROCESSED_DIR = day05_DATA_DIR / "processed"

# Episode Configuration
day05_EPISODE_IDS = ["01", "02", "03", "04", "05"]
day05_AUDIO_EXTENSIONS = [".mp3", ".wav", ".m4a", ".flac", ".ogg"]

def day05_ensure_directories():
    """Ensure all required directories exist"""
    day05_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    day05_TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    day05_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directories verified: {day05_DATA_DIR}")

def day05_get_audio_files():
    """Get list of audio files in the audio directory"""
    audio_files = []
    for ext in day05_AUDIO_EXTENSIONS:
        audio_files.extend(day05_AUDIO_DIR.glob(f"*{ext}"))
    return sorted(audio_files)

if __name__ == "__main__":
    # Test configuration
    print("=" * 60)
    print("Day 05 Configuration Test")
    print("=" * 60)
    print(f"Tainacan API URL: {day05_TAINACAN_API_URL}")
    print(f"Whisper Model: {day05_WHISPER_MODEL}")
    print(f"Audio Language: {day05_AUDIO_LANGUAGE}")
    print(f"GCP Project: {day05_GCP_PROJECT_ID}")
    print(f"BigQuery Dataset: {day05_BQ_DATASET}")
    print(f"BigQuery Table: {day05_BQ_TABLE}")
    print(f"OpenAI Key: {'✅ Set' if day05_OPENAI_API_KEY else '❌ Missing'}")
    print(f"Base Directory: {day05_BASE_DIR}")
    print(f"Audio Directory: {day05_AUDIO_DIR}")
    print()
    day05_ensure_directories()
    print()
    audio_files = day05_get_audio_files()
    print(f"Audio files found: {len(audio_files)}")
    for f in audio_files:
        print(f"  - {f.name}")
