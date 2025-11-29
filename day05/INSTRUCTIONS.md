# 📁 Day 05 Audio File Instructions

## 🎧 Where to Put Your Podcast Audio Files

Place your 5 podcast episode audio files in the following location:

```
day05/data/raw/audio/
```

## 📝 How to Name Your Files

Use this exact naming convention:

```
episode_01.mp3
episode_02.mp3
episode_03.mp3
episode_04.mp3
episode_05.mp3
```

**Supported formats**: `.mp3`, `.wav`, `.m4a`, `.flac`

(If your files are in a different format, just use the same naming pattern: `episode_01.wav`, etc.)

## 📂 Final Structure Should Look Like:

```
day05/
├── data/
│   ├── raw/
│   │   ├── audio/
│   │   │   ├── episode_01.mp3  ← YOUR FILES HERE
│   │   │   ├── episode_02.mp3
│   │   │   ├── episode_03.mp3
│   │   │   ├── episode_04.mp3
│   │   │   └── episode_05.mp3
│   │   └── transcripts/  (will be generated)
│   └── processed/  (will be generated)
```

## ✅ Next Steps After Adding Files

1. **Add your audio files** to `day05/data/raw/audio/`
2. **Run the transcription script**:
   ```bash
   python day05_DATA_transcribe_whisper.py
   ```
3. **Review the generated transcripts** in `day05/data/processed/items_to_validate.csv`
4. **Manually validate** which mentions are actual museum items
5. **Run the search script** to match with Tainacan API
6. **Load to BigQuery**

---

## ⚠️ Important Notes

- Files should be **Brazilian Portuguese** audio
- Whisper will use the **"base" model** (good balance of speed/accuracy)
- Each file will generate a JSON transcript with timestamps
- The pipeline will extract potential museum item mentions automatically
- You'll need to manually validate which mentions are real items before searching

## 🔧 Troubleshooting

If you have files with different names:
- You can rename them to match the convention above, OR
- Update the script to read your specific filenames

**Ready? Add your files and let me know when they're in place!** 🚀
