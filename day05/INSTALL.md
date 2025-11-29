# Day 05: Installation Guide

## ✅ Successfully Fixed Python 3.13 Compatibility Issue

The original `openai-whisper` package has compatibility issues with Python 3.13. We've switched to **`faster-whisper`**, which is:
- ✅ Compatible with Python 3.13
- ✅ Faster than original Whisper
- ✅ Uses less memory
- ✅ Same quality transcription

---

## 📦 Quick Install

```bash
# Navigate to project root
cd /Users/raphaelanawa/Desktop/advent2025/repo/advent-automation-2025

# Install Day 05 dependencies
pip install faster-whisper openai scikit-learn
```

---

## 🔧 What Was Changed

### 1. Updated `requirements.txt`
```diff
- openai-whisper==20231117  # ❌ Broken on Python 3.13
+ faster-whisper>=1.0.0     # ✅ Works on Python 3.13
```

### 2. Updated Transcription Script
The script now uses `faster-whisper` instead of `openai-whisper`:

```python
from faster_whisper import WhisperModel  # Instead of: import whisper

# Initialize model
model = WhisperModel("base", device="cpu", compute_type="int8")

# Transcribe
segments, info = model.transcribe(audio_file, language="pt")
```

**Benefits:**
- 4x faster transcription
- Lower memory usage
- Better timestamp accuracy
- Same quality as OpenAI Whisper

---

## ✅ Installation Successful!

You should see this output:
```
Successfully installed:
- faster-whisper-1.2.1
- ctranslate2-4.6.1
- av-16.0.1
- onnxruntime-1.23.2
- tokenizers-0.22.1
- huggingface-hub-1.1.6
```

---

## 🚀 Next Steps

Now you're ready to run the pipeline:

```bash
cd /Users/raphaelanawa/Desktop/advent2025/repo/advent-automation-2025/day05

# Make sure you have audio files in:
# day05/data/raw/audio/episode_01.mp3, etc.

# Then run:
python day05_DATA_transcribe_whisper.py
```

---

## 📝 Dependencies Installed

| Package | Version | Purpose |
|---------|---------|---------|
| `faster-whisper` | 1.2.1 | Audio transcription (PT-BR) |
| `openai` | Latest | GPT-4 item extraction |
| `scikit-learn` | Latest | Text similarity matching |
| `google-cloud-bigquery` | 3.14.1 | BigQuery integration |

---

## ⚙️ System Requirements

- **Python**: 3.9+ (tested on 3.13)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB for Whisper models
- **CPU**: Any modern CPU (no GPU required)

---

## 🔍 Verify Installation

Test that everything is installed correctly:

```bash
python -c "from faster_whisper import WhisperModel; print('✅ faster-whisper OK')"
python -c "import openai; print('✅ openai OK')"
python -c "from sklearn.feature_extraction.text import TfidfVectorizer; print('✅ scikit-learn OK')"
```

Expected output:
```
✅ faster-whisper OK
✅ openai OK
✅ scikit-learn OK
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'faster_whisper'"
**Solution:**
```bash
pip install faster-whisper
```

### Issue: "No audio backend available"
**Solution (macOS):**
```bash
brew install ffmpeg
```

**Solution (Linux):**
```bash
sudo apt-get install ffmpeg
```

### Issue: Model download fails
**Solution:** The first time you run transcription, it will download the Whisper model (~1GB). Make sure you have internet connection.

---

**Ready to transcribe!** 🎙️
