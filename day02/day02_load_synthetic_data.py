"""
Load Synthetic Data - Day 02
Loads synthetic Instagram data into the database for testing and development
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

from src.data_manager import DataManager
from src import config

def load_synthetic_data():
    """Load synthetic data from JSON file into database"""

    print("\n" + "="*60)
    print("LOADING SYNTHETIC DATA")
    print("="*60 + "\n")

    # Load JSON data
    data_file = Path(__file__).parent / 'data' / 'synthetic_instagram_data.json'

    if not data_file.exists():
        print(f"❌ File not found: {data_file}")
        return False

    print(f"📂 Loading data from: {data_file}")

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate data structure
    if 'account_metrics' not in data or 'posts' not in data:
        print("❌ Invalid data structure. Expected 'account_metrics' and 'posts' keys")
        return False

    print(f"   ✓ Found {len(data['account_metrics'])} account metrics records")
    print(f"   ✓ Found {len(data['posts'])} posts")

    # Initialize database
    dm = DataManager()

    # Load account metrics
    print("\n1. Loading account metrics...")
    account_df = pd.DataFrame(data['account_metrics'])

    # Convert date to datetime
    account_df['date'] = pd.to_datetime(account_df['date'])

    # Add updated_at timestamp
    account_df['updated_at'] = datetime.now()

    # Save to database
    rows_saved = dm.save_account_metrics(account_df)
    print(f"   ✓ Saved {rows_saved} account metrics records")

    # Load posts
    print("\n2. Loading posts...")
    posts_df = pd.DataFrame(data['posts'])

    # Convert timestamp to datetime
    posts_df['timestamp'] = pd.to_datetime(posts_df['timestamp'])

    # Calculate engagement rate for each post
    print("   → Calculating engagement rates...")
    posts_df['engagement_rate'] = posts_df.apply(
        lambda row: calculate_engagement_rate(row),
        axis=1
    )

    # Add updated_at timestamp
    posts_df['updated_at'] = datetime.now()

    # Save to database
    rows_saved = dm.save_posts(posts_df)
    print(f"   ✓ Saved {rows_saved} posts")

    # Show summary statistics
    print("\n" + "="*60)
    print("DATA SUMMARY")
    print("="*60)

    # Account metrics summary
    print("\n📊 Account Metrics:")
    print(f"   Date Range: {account_df['date'].min().date()} to {account_df['date'].max().date()}")
    print(f"   Starting Followers: {account_df['followers'].iloc[0]:,}")
    print(f"   Ending Followers: {account_df['followers'].iloc[-1]:,}")
    print(f"   Total Growth: {account_df['followers'].iloc[-1] - account_df['followers'].iloc[0]:,}")
    print(f"   Avg Daily Impressions: {account_df['impressions'].mean():,.0f}")
    print(f"   Avg Daily Reach: {account_df['reach'].mean():,.0f}")

    # Posts summary
    print("\n📸 Posts:")
    print(f"   Total Posts: {len(posts_df)}")
    print(f"   Date Range: {posts_df['timestamp'].min().date()} to {posts_df['timestamp'].max().date()}")
    print(f"   Avg Engagement Rate: {posts_df['engagement_rate'].mean():.2f}%")
    print(f"   Max Engagement Rate: {posts_df['engagement_rate'].max():.2f}%")
    print(f"   Min Engagement Rate: {posts_df['engagement_rate'].min():.2f}%")

    # Content type breakdown
    print("\n📊 Content Types:")
    type_counts = posts_df['media_type'].value_counts()
    for media_type, count in type_counts.items():
        pct = (count / len(posts_df)) * 100
        avg_eng = posts_df[posts_df['media_type'] == media_type]['engagement_rate'].mean()
        print(f"   {media_type}: {count} posts ({pct:.1f}%) - Avg Engagement: {avg_eng:.2f}%")

    # Viral posts
    avg_engagement = posts_df['engagement_rate'].mean()
    viral_threshold = avg_engagement * 2
    viral_posts = posts_df[posts_df['engagement_rate'] >= viral_threshold]
    print(f"\n⚡ Viral Posts (>{viral_threshold:.2f}% engagement): {len(viral_posts)}")

    print("\n" + "="*60)
    print("✅ SYNTHETIC DATA LOADED SUCCESSFULLY")
    print("="*60)
    print("\nDatabase location:", config.DB_PATH)
    print("\n💡 Next step: Run 'python pipeline_synthetic.py' to analyze the data")
    print("="*60 + "\n")

    return True

def calculate_engagement_rate(post: pd.Series) -> float:
    """
    Calculate engagement rate for a post

    Formula: (likes + comments + shares*3 + saves*5) / reach * 100

    Args:
        post: Series containing post metrics

    Returns:
        Engagement rate as percentage (0-100)
    """
    reach = post.get('reach', 0)

    if reach == 0:
        return 0.0

    weighted_engagement = (
        post.get('likes', 0) * config.ENGAGEMENT_WEIGHTS['likes'] +
        post.get('comments', 0) * config.ENGAGEMENT_WEIGHTS['comments'] +
        post.get('shares', 0) * config.ENGAGEMENT_WEIGHTS['shares'] +
        post.get('saves', 0) * config.ENGAGEMENT_WEIGHTS['saves']
    )

    engagement_rate = (weighted_engagement / reach) * 100

    return round(engagement_rate, 2)

if __name__ == "__main__":
    try:
        success = load_synthetic_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error loading synthetic data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
