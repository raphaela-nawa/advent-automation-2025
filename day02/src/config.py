"""
Configuration module for Day 02 - Creator Intelligence System
Loads environment variables from shared config/.env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load from shared config/.env (repository-level)
project_dir = Path(__file__).parent.parent
repo_root = project_dir.parent
config_env_path = repo_root / 'config' / '.env'

# Load environment variables from shared config
load_dotenv(config_env_path)

# Meta API Configuration (Day 02 specific variables)
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN_day02')
META_ACCOUNT_ID = os.getenv('META_ACCOUNT_ID_day02')
OPENAI_API_KEY = os.getenv('KEY_OPENAI_DAY02')

def validate_credentials():
    """Validate that required credentials are present"""
    if not META_ACCESS_TOKEN or not META_ACCOUNT_ID:
        raise ValueError(
            "\n" + "="*60 + "\n"
            "❌ MISSING META API CREDENTIALS\n"
            "="*60 + "\n"
            "Please add your credentials to config/.env:\n\n"
            "Required variables:\n"
            "   - META_ACCESS_TOKEN_day02: Get from https://developers.facebook.com/tools/explorer/\n"
            "   - META_ACCOUNT_ID_day02: Your Instagram Business Account ID\n"
            "   - KEY_OPENAI_DAY02: Your OpenAI API key\n\n"
            "Example:\n"
            "   META_ACCESS_TOKEN_day02=\"your_token_here\"\n"
            "   META_ACCOUNT_ID_day02=\"17841234567890\"\n"
            "   KEY_OPENAI_DAY02=\"sk-proj-...\"\n\n"
            "See README.md for detailed setup instructions\n"
            "="*60
        )

# Meta API Settings
META_API_VERSION = 'v24.0'  # Updated to latest version
META_BASE_URL = f'https://graph.facebook.com/{META_API_VERSION}'

# Metrics Configuration
ACCOUNT_METRICS = [
    'impressions',
    'reach',
    'follower_count',
    'profile_views',
    'website_clicks'
]

POST_METRICS = [
    'impressions',
    'reach',
    'engagement',
    'like_count',
    'comments_count',
    'shares',
    'saved'
]

# Database Configuration
DB_PATH = project_dir / 'data' / 'creator_intel.db'

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Rate Limiting Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 30  # seconds

# Analysis Configuration
LOOKBACK_DAYS = 90  # Account metrics lookback period
MAX_POSTS = 100  # Number of recent posts to analyze
VIRAL_THRESHOLD_MULTIPLIER = 2.0  # Posts with engagement > 2x average are "viral"

# Engagement Weight Configuration (for calculating engagement rate)
ENGAGEMENT_WEIGHTS = {
    'likes': 1,
    'comments': 1,
    'shares': 3,
    'saves': 5
}

# Growth Target (to reach 200K from 100K in 6 months)
TARGET_WEEKLY_GROWTH_RATE = 2.74  # percentage

print(f"✅ Config loaded successfully from: {config_env_path}")
print(f"📊 Meta API Version: {META_API_VERSION}")
print(f"💾 Database path: {DB_PATH}")
