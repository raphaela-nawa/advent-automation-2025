# Day 05: Museu Ipiranga Cultural Data Pipeline

**Project 1E - Paula's Museum Podcast Analysis**

A complete pipeline that transcribes podcast episodes about the Museu do Ipiranga, extracts mentioned artifacts using AI, matches them with the museum's digital catalog via Tainacan API, and loads enriched data to BigQuery.

---

## 🎯 What This Project Does

1. **Transcribes** 5 podcast episodes in Brazilian Portuguese using Whisper AI
2. **Extracts** museum artifact mentions using GPT-4 with timestamps
3. **Matches** mentions with Tainacan API using fuzzy text similarity
4. **Loads** enriched data to BigQuery for analysis

---

## 📊 Final Output

### BigQuery Table: `podcast_museum_mentions`

| Column | Description |
|--------|-------------|
| `episode_id` | Episode number (01-05) |
| `item_mention` | How the artifact was mentioned in the podcast |
| `timestamp` | When it was mentioned (HH:MM:SS) |
| `context` | Additional context from the transcript |
| `confidence` | GPT extraction confidence (high/medium/low) |
| `matched` | Whether a match was found in Tainacan API |
| `match_confidence` | Similarity score (0.0-1.0) |
| `match_type` | Type of match (fuzzy_match/no_match) |
| `tainacan_item_id` | Museum catalog item ID |
| `tainacan_title` | Official artifact title |
| `tainacan_description` | Artifact description |
| `tainacan_url` | URL to museum catalog |
| `tainacan_metadata` | Additional metadata (JSON) |
| `loaded_at` | Timestamp of data load |

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with pip
2. **Google Cloud Project** with BigQuery enabled
3. **OpenAI API Key** for GPT-4
4. **5 podcast audio files** in MP3/WAV/M4A format

### 1. Install Dependencies

```bash
cd /path/to/advent-automation-2025
pip install -r requirements.txt
```

This installs:
- `openai-whisper` - Audio transcription
- `openai` - GPT-4 for item extraction
- `google-cloud-bigquery` - BigQuery integration
- `scikit-learn` - Text similarity matching
- `requests`, `pandas` - Data processing

### 2. Configure Environment

Edit `config/.env` and set:

```bash
# OpenAI API Key (required for item extraction)
KEY_OPENAI_DAY05="sk-proj-your-key-here"

# BigQuery Configuration
DAY05_GCP_PROJECT_ID="your-gcp-project-id"
DAY05_BQ_DATASET="cultural_data"
DAY05_BQ_TABLE="podcast_museum_mentions"

# Whisper Configuration
DAY05_WHISPER_MODEL="base"  # Options: tiny, base, small, medium, large
DAY05_AUDIO_LANGUAGE="pt"   # Portuguese

# Tainacan API (default - no key needed)
DAY05_TAINACAN_API_URL="https://acervoonline.mp.usp.br/wp-json/tainacan/v2/"

# Matching Configuration
DAY05_SIMILARITY_THRESHOLD="0.6"  # 0.0 to 1.0 (higher = stricter)
DAY05_MAX_SEARCH_RESULTS="10"
```

### 3. Add Your Podcast Audio Files

Place your 5 podcast episodes in:

```
day05/data/raw/audio/
```

Name them:
```
episode_01.mp3
episode_02.mp3
episode_03.mp3
episode_04.mp3
episode_05.mp3
```

Supported formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

### 4. Run the Pipeline

```bash
cd day05

# Step 1: Transcribe audio files (30 min)
python day05_DATA_transcribe_whisper.py

# Step 2: Extract museum item mentions (25 min)
python day05_PIPELINE_extract_items.py

# Step 3: MANUAL VALIDATION (15 min)
# Open: day05/data/processed/items_to_validate.csv
# Mark 'validated' column as 'yes' for items to search
# Save the file

# Step 4: Search Tainacan API for matches (40 min)
python day05_DATA_search_tainacan.py

# Step 5: Load to BigQuery (5 min)
python day05_DATA_load_bigquery.py
```

---

## 📂 Project Structure

```
day05/
├── data/
│   ├── raw/
│   │   ├── audio/                    # Your podcast MP3 files
│   │   └── transcripts/              # Generated Whisper transcripts (JSON + TXT)
│   └── processed/
│       ├── items_to_validate.csv     # Extracted items (manual validation needed)
│       └── matched_items.csv         # Items matched with Tainacan API
├── day05_CONFIG_settings.py          # Configuration loader
├── day05_DATA_transcribe_whisper.py  # Whisper transcription script
├── day05_PIPELINE_extract_items.py   # GPT-4 item extraction
├── day05_DATA_search_tainacan.py     # Tainacan API fuzzy search
├── day05_DATA_load_bigquery.py       # BigQuery loading
├── .env.example                       # Environment variables template
├── INSTRUCTIONS.md                    # Audio file setup guide
└── README.md                          # This file
```

---

## 🔧 Detailed Pipeline Steps

### Step 1: Transcription (day05_DATA_transcribe_whisper.py)

**What it does:**
- Loads Whisper AI model (configurable: tiny/base/small/medium/large)
- Transcribes each podcast episode in Brazilian Portuguese
- Generates timestamps for each segment
- Saves both JSON (structured) and TXT (readable) versions

**Output:**
```
day05/data/raw/transcripts/
├── episode_01_transcript.json
├── episode_01_transcript.txt
├── episode_02_transcript.json
├── episode_02_transcript.txt
...
```

**Sample JSON structure:**
```json
{
  "file_name": "episode_01.mp3",
  "transcription_date": "2024-11-29T10:30:00",
  "language": "pt",
  "model": "base",
  "full_text": "Complete transcript...",
  "segments": [
    {
      "id": 0,
      "start": "00:00:12",
      "end": "00:00:18",
      "start_seconds": 12.5,
      "end_seconds": 18.3,
      "text": "Hoje vamos falar sobre o quadro Independência ou Morte..."
    }
  ]
}
```

---

### Step 2: Item Extraction (day05_PIPELINE_extract_items.py)

**What it does:**
- Uses GPT-4 to analyze transcripts
- Identifies mentions of museum artifacts (paintings, sculptures, objects, etc.)
- Extracts mention text, timestamp, and context
- Generates a CSV for manual validation

**GPT Prompt Strategy:**
The script uses a specialized prompt that identifies:
- Pinturas e quadros (Paintings)
- Fotografias (Photographs)
- Esculturas e estátuas (Sculptures)
- Objetos históricos (Historical objects)
- Documentos e manuscritos (Documents)
- Peças do acervo (Catalog items)
- And more...

**Output:**
```
day05/data/processed/items_to_validate.csv
```

**Columns:**
- `episode_id`: Episode number
- `item_mention`: How the item was described
- `timestamp`: When it was mentioned
- `context`: Additional context
- `confidence`: high/medium/low
- `validated`: **← YOU FILL THIS (yes/no)**
- `notes`: Optional notes

---

### Step 3: Manual Validation (YOU!)

**Required Action:**

1. Open `day05/data/processed/items_to_validate.csv`
2. Review each `item_mention`
3. Mark `validated` as:
   - `yes` - Real museum item, should be searched
   - `no` - Not a museum item (false positive)
4. Add optional `notes` if needed
5. **Save the file**

**Example:**

| episode_id | item_mention | timestamp | validated | notes |
|------------|-------------|-----------|-----------|-------|
| 01 | Independência ou Morte | 00:12:45 | yes | Famous painting |
| 01 | a história do Brasil | 00:15:20 | no | Not a specific item |
| 02 | retrato de Dom Pedro | 00:08:10 | yes | |

---

### Step 4: Tainacan Search (day05_DATA_search_tainacan.py)

**What it does:**
- Fetches museum catalog items from Tainacan API
- For each validated item:
  1. Tries direct API search first
  2. Falls back to fuzzy matching using TF-IDF similarity
- Calculates confidence scores
- Only matches items above threshold (default: 0.6)

**Matching Strategy:**
- Combines item title + description for better matching
- Uses n-gram (1-2) TF-IDF vectorization
- Calculates cosine similarity
- Returns best match if confidence ≥ threshold

**Output:**
```
day05/data/processed/matched_items.csv
```

Adds columns:
- `matched`: true/false
- `match_confidence`: 0.0-1.0
- `match_type`: fuzzy_match/no_match
- `tainacan_item_id`
- `tainacan_title`
- `tainacan_description`
- `tainacan_url`
- `tainacan_metadata`

---

### Step 5: BigQuery Load (day05_DATA_load_bigquery.py)

**What it does:**
- Creates BigQuery dataset (if needed)
- Creates/replaces table with defined schema
- Loads matched items from CSV
- Verifies data with summary query

**Requirements:**
- Google Cloud credentials configured
- BigQuery API enabled
- Permissions on GCP project

**Verification Query:**
After loading, the script runs:
```sql
SELECT
    COUNT(*) as total_mentions,
    COUNTIF(matched) as matched_items,
    COUNTIF(NOT matched) as unmatched_items,
    ROUND(AVG(IF(matched, match_confidence, NULL)), 3) as avg_confidence
FROM `advent2025-day05.cultural_data.podcast_museum_mentions`
```

---

## 📈 Example Queries

### Top Matched Items
```sql
SELECT
    episode_id,
    item_mention,
    timestamp,
    tainacan_title,
    match_confidence
FROM `advent2025-day05.cultural_data.podcast_museum_mentions`
WHERE matched = TRUE
ORDER BY match_confidence DESC
LIMIT 10;
```

### Unmatched Items (Need Manual Review)
```sql
SELECT
    episode_id,
    item_mention,
    timestamp,
    context
FROM `advent2025-day05.cultural_data.podcast_museum_mentions`
WHERE matched = FALSE
ORDER BY episode_id, timestamp;
```

### Items by Episode
```sql
SELECT
    episode_id,
    COUNT(*) as total_mentions,
    COUNTIF(matched) as matched_count,
    ROUND(AVG(IF(matched, match_confidence, NULL)), 3) as avg_confidence
FROM `advent2025-day05.cultural_data.podcast_museum_mentions`
GROUP BY episode_id
ORDER BY episode_id;
```

---

## 🔍 Testing the Configuration

Test your setup before running the full pipeline:

```bash
# Test configuration loading
python day05_CONFIG_settings.py

# Expected output:
# ✅ Directories verified
# ✅ OpenAI Key: Set
# Audio files found: 5
```

---

## ⚙️ Configuration Options

### Whisper Model Options

| Model | Speed | Accuracy | Memory |
|-------|-------|----------|--------|
| `tiny` | Fastest | Lowest | ~1 GB |
| `base` | Fast | Good | ~1 GB |
| `small` | Medium | Better | ~2 GB |
| `medium` | Slow | High | ~5 GB |
| `large` | Slowest | Highest | ~10 GB |

**Recommendation:** Use `base` for good balance of speed/accuracy.

### Similarity Threshold

- `0.5` - Lenient (more matches, some false positives)
- `0.6` - Balanced (default)
- `0.7` - Strict (fewer matches, higher precision)
- `0.8+` - Very strict (only very similar items)

---

## 🐛 Troubleshooting

### "No audio files found"
- Check files are in `day05/data/raw/audio/`
- Ensure naming: `episode_01.mp3`, `episode_02.mp3`, etc.
- Supported formats: .mp3, .wav, .m4a, .flac

### "OpenAI API key not found"
- Set `KEY_OPENAI_DAY05` in `config/.env`
- Or set general `KEY_OPENAI`

### "BigQuery authentication failed"
- Run: `gcloud auth application-default login`
- Or set `GOOGLE_APPLICATION_CREDENTIALS` env var
- Ensure project ID is correct

### "No validated items found"
- Open `day05/data/processed/items_to_validate.csv`
- Mark at least one item as `validated=yes`
- Save the file

### Whisper is slow
- Use smaller model: `DAY05_WHISPER_MODEL="tiny"`
- Or reduce audio quality before transcription

---

## 📚 Data Sources

- **Tainacan API**: [https://acervoonline.mp.usp.br/](https://acervoonline.mp.usp.br/)
- **Museu Paulista**: University of São Paulo museum catalog
- **API Documentation**: [Tainacan REST API](https://tainacan.org/wp-content/uploads/2019/08/Tainacan-API-Documentation.pdf)

---

## ⏱️ Estimated Time

| Task | Time |
|------|------|
| Setup + dependencies | 10 min |
| Transcription (5 episodes) | 30 min |
| Item extraction (GPT-4) | 25 min |
| Manual validation | 15 min |
| Tainacan search | 40 min |
| BigQuery load | 5 min |
| **Total** | **~2h 5min** |

---

## 🎓 What You Learn

- ✅ Audio transcription with Whisper AI
- ✅ LLM-based content extraction with GPT-4
- ✅ REST API integration (Tainacan)
- ✅ Fuzzy text matching (TF-IDF similarity)
- ✅ BigQuery schema design and loading
- ✅ Data pipeline orchestration
- ✅ Day-scoped naming conventions

---

## 📝 Notes

- This is a **portfolio project** (3-hour scope)
- Focused on **functionality over perfection**
- Manual validation step ensures data quality
- Fuzzy matching handles variations in item names
- All code follows `day05_` naming convention

---

## 🚀 Next Steps (Out of Scope)

**Not included (to stay within 3 hours):**
- ❌ Dashboard/visualization (Pilar D)
- ❌ Automated scheduling (Pilar C)
- ❌ AI analysis of correlations (Pilar E)
- ❌ Data modeling (Pilar B)

**Future enhancements could include:**
- Streamlit dashboard to explore matches
- Scheduled daily/weekly podcast processing
- RAG system for semantic search
- Named Entity Recognition (NER) for better extraction

---

## 📄 License

Part of the Advent Calendar 2025 project.

---

**Generated with Claude Code** 🤖
