# Project 1B: Creator Intelligence System

A data-driven system for Instagram creators to analyze growth metrics, track engagement, and optimize content strategy using Meta Graph API and AI-powered insights.

## Overview

**Client:** Samira (100K Instagram followers → target 200K in 6 months)
**Timeline:** 3-hour rapid prototype
**Deliverable:** Meta API data extraction + LTV analysis + Streamlit dashboard

## Features

### Hour 1: Data Extraction Foundation ✅
- Connect to Meta Graph API (Instagram Business)
- Extract 90 days of account metrics (followers, impressions, reach, profile views, website clicks)
- Extract last 100 posts with performance data
- Calculate engagement rates and growth metrics
- Implement audience segmentation (VIP, High, Medium, Low)
- Identify viral content and best posting times
- Store data in SQLite database

### Hour 2: LTV Calculator + OpenAI Insights (Coming)
- Calculate follower lifetime value metrics
- LLM-powered content insights and recommendations

### Hour 3: Streamlit Dashboard + Automation (Coming)
- Interactive dashboard for metrics visualization
- Daily automated summary reports

## Prerequisites

1. **Facebook Business Account** with Instagram Business Account connected
2. **Meta Access Token** with Instagram permissions
3. **OpenAI API Key** (for Hour 2 insights)
4. **Python 3.10+** installed

## Setup Instructions

### 1. Get Meta API Credentials

#### Step 1: Get Access Token
1. Go to [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app (or create one at [Meta for Developers](https://developers.facebook.com/apps))
3. Click "Generate Access Token"
4. Select these permissions:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_read_engagement`
   - `pages_show_list`
5. Copy the generated token

#### Step 2: Get Instagram Business Account ID
1. In Graph API Explorer, with your token active
2. Make a GET request to: `me/accounts`
3. Find your Instagram-connected page, copy the `id`
4. Make a GET request to: `{page_id}?fields=instagram_business_account`
5. Copy the `instagram_business_account.id` value

### 2. Get OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)

### 3. Configure Environment

```bash
# Navigate to project directory
cd day02

# Copy the example environment file
cp .env.example_day02 .env

# Edit .env and add your real credentials
# Use your favorite editor (nano, vim, vscode, etc.)
nano .env
```

Your `.env` file should look like:
```env
META_ACCESS_TOKEN=EAABsbCS1234567890abcdefghijklmnop...
META_ACCOUNT_ID=17841234567890
OPENAI_API_KEY=sk-proj-abc123def456ghi789...
```

**IMPORTANT:** The `.env` file is git-ignored and will never be committed. Keep your credentials safe!

### 4. Install Dependencies

From the repository root:
```bash
# Make sure you're in the virtual environment
# (if .venv exists in root, activate it first)

# Install project dependencies
pip install -r day02/requirements.txt
```

### 5. Run the Pipeline

```bash
cd day02
python pipeline.py
```

## Expected Output

```
==================================================
PROJECT 1B: CREATOR INTELLIGENCE - DATA EXTRACTION
==================================================

1. Extracting account insights (90 days)...
   ✓ Fetched 90 days of metrics
   ✓ Saved to database

2. Extracting posts data (100 most recent)...
   ✓ Fetched 100 posts
   ✓ Calculated engagement rates
   ✓ Saved to database

3. Calculating growth metrics...
   ✓ Growth analysis complete

4. Performing audience segmentation...
   ✓ Posts segmented by performance
   ✓ Best posting times identified
   ✓ Viral content identified

==================================================
EXTRACTION COMPLETE - SUMMARY
==================================================
📊 Account Growth:
   Current Followers: 100,234
   Weekly Growth Rate: 2.8%
   Target Rate: 2.74% ✓ ON TRACK
   90-Day Total Reach: 8,500,000

📈 Engagement:
   Average Engagement Rate: 4.2%
   Total Posts Analyzed: 100

⭐ Content Intelligence:
   Best Hours to Post: [18, 20, 21]
   Best Days to Post: ['Tuesday', 'Thursday', 'Sunday']
   Viral Posts (>2x avg): 12

💾 Data Storage:
   Database: day02/data/creator_intel.db
   Account Metrics: 90 days
   Posts Analyzed: 100

==================================================
✅ Hour 1 Complete - Ready for Hour 2 (LTV Analysis)
==================================================
```

## Project Structure

```
day02/
├── .env                          # Your credentials (git ignored) ⚠️
├── .env.example_day02            # Template for credentials ✅
├── requirements.txt              # Project dependencies
├── README.md                     # This file
├── pipeline.py                   # Main execution script
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration loader
│   ├── meta_extractor.py         # Meta Graph API client
│   ├── data_manager.py           # SQLite database operations
│   └── audience_segmentation.py  # Analysis and segmentation logic
└── data/
    └── creator_intel.db          # SQLite database (auto-generated)
```

## Database Schema

### Table: account_metrics
- `date` (PRIMARY KEY): Date of metrics
- `followers`: Total follower count
- `impressions`: Total impressions
- `reach`: Total reach
- `profile_views`: Profile view count
- `website_clicks`: Website click count
- `updated_at`: Last update timestamp

### Table: posts
- `post_id` (PRIMARY KEY): Instagram media ID
- `caption`: Post caption text
- `media_type`: IMAGE, VIDEO, or CAROUSEL_ALBUM
- `timestamp`: Post publication time
- `likes`: Like count
- `comments`: Comment count
- `shares`: Share count
- `saves`: Save count
- `impressions`: Post impressions
- `reach`: Post reach
- `engagement_rate`: Calculated engagement percentage
- `updated_at`: Last update timestamp

## Key Metrics

### Growth Metrics
- **Current Followers**: Latest follower count
- **Weekly Growth Rate**: Percentage change from 7 days ago
- **Target Growth Rate**: 2.74% per week (to reach 200K in 6 months)
- **90-Day Total Reach**: Sum of daily reach over 90 days

### Engagement Metrics
- **Average Engagement Rate**: Mean across all posts
- **Engagement Formula**: `(likes + comments + shares*3 + saves*5) / reach * 100`

### Content Intelligence
- **Best Posting Hours**: Hours with highest average engagement
- **Best Posting Days**: Days of week with highest average engagement
- **Viral Content**: Posts with engagement > 2x average

### Audience Segmentation
Posts are segmented into quartiles by engagement rate:
- **VIP**: Top 25% (highest engagement)
- **High**: 50-75th percentile
- **Medium**: 25-50th percentile
- **Low**: Bottom 25%

## Troubleshooting

### "Missing Meta API credentials" Error
- Make sure you copied `.env.example_day02` to `.env`
- Verify your credentials are correctly pasted in `.env`
- Check that there are no extra spaces or quotes around the values

### "Invalid Access Token" Error
- Your token may have expired (they typically last 60 days)
- Generate a new token from [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- Update your `.env` file with the new token

### "Rate Limit Exceeded" Error
- Meta has rate limits on API calls
- The script includes retry logic with exponential backoff
- If it persists, wait a few minutes and try again

### No Data Returned
- Verify your Instagram account is a Business account (not Personal or Creator)
- Ensure your Facebook page is correctly linked to your Instagram account
- Check that you have sufficient permissions in your access token

## Next Steps

After completing Hour 1:
- **Hour 2**: Implement LTV calculator and OpenAI-powered insights
- **Hour 3**: Build Streamlit dashboard and automated daily reports

## Security Notes

- ✅ `.env` file is git-ignored and never committed
- ✅ `.env.example_day02` is safe to share (no real credentials)
- ✅ All API calls use HTTPS
- ✅ Access tokens should be rotated regularly
- ⚠️ Never share your `.env` file or commit it to version control

## Support

For Meta Graph API documentation: https://developers.facebook.com/docs/instagram-api
For OpenAI API documentation: https://platform.openai.com/docs

## License

This is a prototype project for client delivery.
