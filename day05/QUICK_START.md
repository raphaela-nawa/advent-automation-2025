# Day 05: Quick Start Guide

## ⚡ TL;DR - Run This

```bash
# 1. Add your 5 podcast MP3 files to:
day05/data/raw/audio/
# Name them: episode_01.mp3, episode_02.mp3, ..., episode_05.mp3

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Edit config/.env and set:
#   KEY_OPENAI_DAY05="your-key"
#   DAY05_GCP_PROJECT_ID="your-project"

# 4. Run the pipeline
cd day05

python day05_DATA_transcribe_whisper.py          # 30 min

python day05_PIPELINE_extract_items.py           # 25 min

# STOP! Open data/processed/items_to_validate.csv
# Mark validated='yes' for items to search, then save

python day05_DATA_search_tainacan.py             # 40 min

python day05_DATA_load_bigquery.py               # 5 min

# Done! Check BigQuery for results
```

---

## 🎯 What Gets Created

### Files Generated:
```
day05/data/raw/transcripts/
  ├── episode_01_transcript.json
  ├── episode_01_transcript.txt
  └── ... (5 episodes)

day05/data/processed/
  ├── items_to_validate.csv  ← YOU EDIT THIS
  └── matched_items.csv
```

### BigQuery Table:
```
Project: advent2025-day05
Dataset: cultural_data
Table: podcast_museum_mentions
```

---

## 🔑 Required Environment Variables

```bash
# In config/.env
KEY_OPENAI_DAY05="sk-proj-..."           # OpenAI API key
DAY05_GCP_PROJECT_ID="your-project-id"   # GCP project
```

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| No audio files found | Place MP3s in `day05/data/raw/audio/` |
| OpenAI error | Set `KEY_OPENAI_DAY05` in `config/.env` |
| BigQuery auth failed | Run `gcloud auth application-default login` |
| No validated items | Open `items_to_validate.csv`, mark some as `yes` |

---

## 📊 Final Output Schema

```sql
episode_id           STRING    -- "01", "02", etc.
item_mention         STRING    -- "Independência ou Morte"
timestamp            STRING    -- "00:12:45"
context              STRING    -- Additional context
matched              BOOLEAN   -- true/false
match_confidence     FLOAT     -- 0.0 to 1.0
tainacan_title       STRING    -- Official museum title
tainacan_description STRING    -- Item description
tainacan_url         STRING    -- Museum catalog URL
loaded_at            TIMESTAMP -- Load timestamp
```

---

**See [README.md](README.md) for full documentation**
