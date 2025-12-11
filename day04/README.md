# Day 04: Cardano Blockchain Transparency Pipeline

> **One-line pitch:** Dockerized data pipeline that extracts on-chain transparency metrics from Cardano blockchain via Blockfrost API and loads to BigQuery for verifiable analysis.

**Part of:** [Advent Automation 2025 - 25 Days of Data Engineering](../README.md)

---

## Executive Summary

**Business Problem:** Crypto/blockchain teams need verifiable on-chain data to prove network decentralization, fee transparency, and real adoption metrics beyond marketing claims.

**Solution Delivered:** Containerized Python pipeline extracting Cardano network metrics (3000+ stake pools, $0.17 avg fees, transaction volumes) from Blockfrost API to BigQuery with full transparency trail.

**Business Impact:** Enables data-driven verification of blockchain values - decentralization proof (3000 pools vs Bitcoin's 5), accessibility proof (avg $0.17 fees vs Ethereum's $5-50), and real adoption metrics.

**For:** Blockchain/Crypto Analyst | **Industry:** Crypto/Blockchain | **Time:** 3 hours | **Status:** ✅ Complete

---

## Why Transparency Matters

Pedro teaches that **Cardano's core value is transparency**:
- Every transaction is public and verifiable
- No hidden fees, no opaque processes
- Anyone can audit network activity in real-time

But raw blockchain data is hard to query. This pipeline makes transparency **accessible**.

### Traditional Finance vs. Cardano

| Metric | Traditional Bank | Cardano Blockchain |
|--------|------------------|-------------------|
| Transaction history | Private (only yours) | **Public (everyone's)** |
| Network fees | Hidden in fine print | **On-chain, auditable** |
| Centralization | Few entities control | **3000+ stake pools** |
| Verification | "Trust us" | **"Verify yourself"** |

### What You Can Prove With This Data

**1. "Cardano is actually decentralized"**
```sql
SELECT AVG(stake_pools_active) as avg_active_pools
FROM `project.cardano_data.cardano_network_activity`;
-- Result: ~3000 pools (vs. Bitcoin's 4-5 mining pools controlling 51%)
```

**2. "Fees are actually low"**
```sql
SELECT AVG(avg_transaction_fee) as avg_fee_usd
FROM `project.cardano_data.cardano_network_activity`;
-- Result: ~$0.17 per transaction (vs. Ethereum $5-50)
```

**3. "The network is actually used"**
```sql
SELECT SUM(total_transactions) as total_txs
FROM `project.cardano_data.cardano_network_activity`
WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY);
-- Result: Real adoption numbers, not marketing claims
```

---

## Architecture

```
┌─────────────────────┐
│  Blockfrost API     │  ← Official Cardano infrastructure
│  (On-chain data)    │     Free: 50K requests/day
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Docker Container   │  ← Containerized extraction
│  - Extract script   │
│  - Load script      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  BigQuery           │  ← Queryable transparency metrics
│  cardano_data       │     Enable SQL analysis
└─────────────────────┘
```

---

## Project Structure

```
day04/
├── data/
│   ├── raw/                          # Raw API responses (if needed)
│   └── processed/
│       └── cardano_transparency.csv  # Local backup of metrics
│
├── day04_CONFIG_settings.py          # Configuration management
├── day04_DATA_extract_blockfrost.py  # Extract on-chain metrics
├── day04_DATA_load_bigquery.py       # Load to BigQuery
│
├── Dockerfile                         # Container definition
├── docker-compose.yml                 # Orchestration config
├── day04_requirements.txt             # Python dependencies
├── .env.example                       # Environment template
└── README.md                          # This file
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Google Cloud account (free tier)
- Blockfrost API key (free, 50K requests/day)

### 1. Get Blockfrost API Key (5 minutes)

```bash
# Visit: https://blockfrost.io
# Sign up (email only, no credit card)
# Copy your API key (starts with "mainnet")
```

### 2. Configure Environment

```bash
# Navigate to day04
cd day04

# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

Required variables in root [../config/.env](../config/.env):
```bash
DAY04_BLOCKFROST_API_KEY=mainnetXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DAY04_BLOCKFROST_NETWORK=mainnet
DAY04_GCP_PROJECT_ID=your-gcp-project-id
DAY04_BQ_DATASET=cardano_data
DAY04_BQ_TABLE=cardano_network_activity
```

### 3. Authenticate with Google Cloud

```bash
# Install gcloud CLI if needed
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### 4. Run with Docker

#### Option A: Extract Only (Local CSV)
```bash
docker-compose up --build
```

This will:
- Build the Docker container
- Extract Cardano transparency metrics from Blockfrost
- Save to `data/processed/cardano_transparency.csv`
- Exit when complete

#### Option B: Full Pipeline (Extract + Load to BigQuery)
```bash
# Extract
docker-compose up

# Load to BigQuery
docker-compose run cardano-transparency python day04_DATA_load_bigquery.py
```

#### Option C: Run Locally (Without Docker)
```bash
# Install dependencies
pip install -r day04_requirements.txt

# Extract metrics
python day04_DATA_extract_blockfrost.py

# Load to BigQuery
python day04_DATA_load_bigquery.py
```

---

## What Gets Extracted

The pipeline extracts these **transparency metrics** every run:

| Metric | Description | Why It Matters |
|--------|-------------|----------------|
| `timestamp` | When data was collected | Time-series analysis |
| `total_transactions` | Total transactions in epoch | Network usage (transparency) |
| `active_addresses` | Estimated active addresses | Real adoption |
| `block_count` | Blocks produced in epoch | Network activity |
| `epoch` | Cardano epoch number (~5 days) | Time reference |
| `stake_pools_active` | Number of active stake pools | **Decentralization proof** |
| `total_ada_staked` | Total ADA staked | Trust in network |
| `avg_transaction_fee` | Average fee in USD | **Accessibility proof** |

---

## Example Output

```
============================================================
🔗 EXTRACTING CARDANO BLOCKCHAIN TRANSPARENCY METRICS
============================================================

📊 Fetching latest epoch data...
   ✓ Epoch 450
   ✓ Transactions: 2,847,391
   ✓ Blocks: 21,567

🌐 Fetching network information...
   ✓ Circulating supply: 34,567,890,123 ADA
   ✓ Active stake: 23,456,789,012 ADA

🏊 Counting active stake pools...
   ✓ Active stake pools: ~3,000
   ℹ️  This demonstrates decentralization vs. Bitcoin's ~5 mining pools

------------------------------------------------------------
📈 TRANSPARENCY METRICS SUMMARY
------------------------------------------------------------
Timestamp:              2024-11-28 14:30:00
Epoch:                  450
Total Transactions:     2,847,391
Active Addresses:       ~3,456,789
Blocks Produced:        21,567
Active Stake Pools:     3,000 (decentralization)
Total ADA Staked:       23,456,789,012 ADA
Avg Transaction Fee:    $0.17 USD
------------------------------------------------------------

✅ SUCCESS! Cardano transparency metrics extracted.
```

---

## BigQuery Schema

```sql
CREATE TABLE `project.cardano_data.cardano_network_activity` (
  timestamp TIMESTAMP NOT NULL,
  total_transactions INT64 NOT NULL,
  active_addresses INT64,
  block_count INT64 NOT NULL,
  epoch INT64 NOT NULL,
  stake_pools_active INT64 NOT NULL,
  total_ada_staked FLOAT64 NOT NULL,
  avg_transaction_fee FLOAT64 NOT NULL
);
```

---

## Analysis Examples

Once data is in BigQuery, you can run powerful analyses:

### 1. Decentralization Trend
```sql
SELECT
  DATE(timestamp) as date,
  AVG(stake_pools_active) as avg_pools
FROM `project.cardano_data.cardano_network_activity`
GROUP BY date
ORDER BY date DESC
LIMIT 30;
```

### 2. Network Activity Growth
```sql
SELECT
  epoch,
  SUM(total_transactions) as total_txs,
  AVG(total_ada_staked) / 1e9 as billions_ada_staked
FROM `project.cardano_data.cardano_network_activity`
GROUP BY epoch
ORDER BY epoch DESC;
```

### 3. Fee Comparison
```sql
SELECT
  'Cardano' as network,
  AVG(avg_transaction_fee) as avg_fee_usd
FROM `project.cardano_data.cardano_network_activity`

UNION ALL

SELECT
  'Ethereum' as network,
  25.00 as avg_fee_usd  -- Approximate
ORDER BY avg_fee_usd;
```

---

## Troubleshooting

### Error: "BLOCKFROST_API_KEY not found"
```bash
# Check your .env file
cat ../config/.env | grep DAY04_BLOCKFROST

# Make sure you copied .env.example to .env and filled in your API key
```

### Error: "Could not authenticate with BigQuery"
```bash
# Re-authenticate with gcloud
gcloud auth application-default login

# Verify project is set
gcloud config get-value project
```

### Error: "API rate limit exceeded"
```bash
# Blockfrost free tier: 50K requests/day, 10 req/sec
# Wait a few seconds and retry
# Or upgrade to paid plan at blockfrost.io
```

### Docker Issues
```bash
# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## Tech Stack

- **API**: [Blockfrost](https://blockfrost.io) - Official Cardano data provider
- **Language**: Python 3.11
- **Containerization**: Docker + Docker Compose
- **Data Warehouse**: Google BigQuery
- **Libraries**:
  - `requests` - HTTP requests to Blockfrost API
  - `pandas` - Data processing
  - `google-cloud-bigquery` - BigQuery integration
  - `python-dotenv` - Environment management

---

## Key Learnings

This project demonstrates:

✅ **Blockchain philosophy** - Transparency isn't just marketing, it's verifiable
✅ **API integration** - Working with real blockchain data providers
✅ **Docker containerization** - Reproducible data pipelines
✅ **Cloud data warehousing** - Making raw data queryable
✅ **Day-scoped isolation** - All code prefixed with `day04_` to avoid conflicts

---

## Portfolio Narrative

> "I built a data pipeline that proves Cardano's values (transparency, decentralization, accessibility) through on-chain metrics - not just marketing claims, but real blockchain data."

**Why this matters:**
- Traditional "crypto price tracker" → Generic, forgettable
- **This project** → Demonstrates understanding of blockchain philosophy + data engineering

---

## Next Steps (Optional Extensions - NOT required for 3-hour delivery)

These are ideas for future enhancement, NOT part of the core deliverable:

- [ ] Add scheduling (Airflow/Cloud Scheduler) for daily runs
- [ ] Create Looker Studio dashboard for metrics visualization
- [ ] Compare Cardano vs. Ethereum vs. Bitcoin metrics
- [ ] Add alerting for unusual network activity
- [ ] Track metrics across multiple epochs for trend analysis

---

## Resources

- **Blockfrost API Docs**: https://docs.blockfrost.io
- **Cardano Official**: https://cardano.org
- **BigQuery Docs**: https://cloud.google.com/bigquery/docs
- **Docker Docs**: https://docs.docker.com

---

## License

This is a portfolio project for educational purposes.

---

**Built for Advent of Code 2025 - Day 04**
*Demonstrating blockchain transparency through data engineering* 🔗
