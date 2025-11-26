"""
Meta Graph API Extractor for Day 02 - Creator Intelligence System
Handles all API calls to Meta/Instagram Business API
"""

import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd

from . import config


class MetaAPIExtractor:
    """Client for Meta Graph API to extract Instagram Business data"""

    def __init__(self):
        self.access_token = config.META_ACCESS_TOKEN
        self.account_id = config.META_ACCOUNT_ID
        self.base_url = config.META_BASE_URL
        self.session = requests.Session()

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = 'GET'
    ) -> Dict[str, Any]:
        """
        Make API request with retry logic and error handling

        Args:
            endpoint: API endpoint (e.g., '/insights', '/media')
            params: Query parameters
            method: HTTP method (GET, POST)

        Returns:
            JSON response as dictionary

        Raises:
            Exception: If all retries fail
        """
        if params is None:
            params = {}

        # Add access token to all requests
        params['access_token'] = self.access_token

        url = f"{self.base_url}/{endpoint}"

        for attempt in range(config.MAX_RETRIES):
            try:
                if method == 'GET':
                    response = self.session.get(
                        url,
                        params=params,
                        timeout=config.REQUEST_TIMEOUT
                    )
                else:
                    response = self.session.post(
                        url,
                        params=params,
                        timeout=config.REQUEST_TIMEOUT
                    )

                # Check for rate limiting
                if response.status_code == 429:
                    wait_time = config.RETRY_DELAY * (2 ** attempt)
                    print(f"   ⏳ Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()

                return response.json()

            except requests.exceptions.Timeout:
                print(f"   ⏳ Request timeout (attempt {attempt + 1}/{config.MAX_RETRIES})")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY)
                else:
                    raise Exception("Request timeout after all retries")

            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(config.RETRY_DELAY)
                else:
                    raise Exception(f"Request failed after all retries: {e}")

        raise Exception("Unexpected error in _make_request")

    def extract_account_insights(self, days: int = 90) -> pd.DataFrame:
        """
        Extract account-level insights for the past N days

        Args:
            days: Number of days to look back (default: 90)

        Returns:
            DataFrame with daily account metrics
        """
        print(f"   📊 Fetching account insights for {days} days...")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Format dates for API (Unix timestamps)
        since = int(start_date.timestamp())
        until = int(end_date.timestamp())

        # Build metrics string
        metrics = ','.join(config.ACCOUNT_METRICS)

        # Make API request
        endpoint = f"{self.account_id}/insights"
        params = {
            'metric': metrics,
            'period': 'day',
            'since': since,
            'until': until
        }

        try:
            response = self._make_request(endpoint, params)

            # Parse response into DataFrame
            records = []

            if 'data' in response:
                for metric_data in response['data']:
                    metric_name = metric_data['name']
                    values = metric_data.get('values', [])

                    for value_entry in values:
                        date = datetime.fromisoformat(
                            value_entry['end_time'].replace('Z', '+00:00')
                        ).date()
                        value = value_entry['value']

                        # Find or create record for this date
                        record = next(
                            (r for r in records if r['date'] == date),
                            None
                        )
                        if record is None:
                            record = {'date': date}
                            records.append(record)

                        # Map metric name to database column
                        if metric_name == 'follower_count':
                            record['followers'] = value
                        elif metric_name == 'impressions':
                            record['impressions'] = value
                        elif metric_name == 'reach':
                            record['reach'] = value
                        elif metric_name == 'profile_views':
                            record['profile_views'] = value
                        elif metric_name == 'website_clicks':
                            record['website_clicks'] = value

            df = pd.DataFrame(records)

            # Add timestamp
            df['updated_at'] = datetime.now()

            # Sort by date
            df = df.sort_values('date')

            print(f"   ✓ Fetched {len(df)} days of account metrics")

            return df

        except Exception as e:
            print(f"   ❌ Failed to fetch account insights: {e}")
            # Return empty DataFrame with correct schema
            return pd.DataFrame(columns=[
                'date', 'followers', 'impressions', 'reach',
                'profile_views', 'website_clicks', 'updated_at'
            ])

    def extract_recent_posts(self, limit: int = 100) -> pd.DataFrame:
        """
        Extract recent posts with performance metrics

        Args:
            limit: Maximum number of posts to fetch (default: 100)

        Returns:
            DataFrame with post data and metrics
        """
        print(f"   📸 Fetching {limit} most recent posts...")

        # Step 1: Get media IDs
        endpoint = f"{self.account_id}/media"
        params = {
            'fields': 'id,caption,media_type,timestamp,like_count,comments_count',
            'limit': limit
        }

        try:
            media_response = self._make_request(endpoint, params)

            if 'data' not in media_response or not media_response['data']:
                print("   ⚠️  No posts found")
                return pd.DataFrame(columns=[
                    'post_id', 'caption', 'media_type', 'timestamp',
                    'likes', 'comments', 'shares', 'saves',
                    'impressions', 'reach', 'engagement_rate', 'updated_at'
                ])

            posts = []

            # Step 2: Get insights for each post
            for idx, media in enumerate(media_response['data'], 1):
                post_id = media['id']

                # Basic post data
                post = {
                    'post_id': post_id,
                    'caption': media.get('caption', ''),
                    'media_type': media.get('media_type', ''),
                    'timestamp': datetime.fromisoformat(
                        media['timestamp'].replace('Z', '+00:00')
                    ),
                    'likes': media.get('like_count', 0),
                    'comments': media.get('comments_count', 0)
                }

                # Fetch insights (impressions, reach, engagement, saves)
                try:
                    insights_endpoint = f"{post_id}/insights"
                    insights_params = {
                        'metric': 'impressions,reach,engagement,saved'
                    }

                    insights_response = self._make_request(
                        insights_endpoint,
                        insights_params
                    )

                    # Parse insights
                    for metric_data in insights_response.get('data', []):
                        metric_name = metric_data['name']
                        value = metric_data.get('values', [{}])[0].get('value', 0)

                        if metric_name == 'impressions':
                            post['impressions'] = value
                        elif metric_name == 'reach':
                            post['reach'] = value
                        elif metric_name == 'engagement':
                            post['engagement'] = value
                        elif metric_name == 'saved':
                            post['saves'] = value

                    # Note: Instagram API doesn't directly provide shares count
                    # Set to 0 or calculate from engagement if possible
                    post['shares'] = 0

                except Exception as e:
                    print(f"   ⚠️  Could not fetch insights for post {idx}: {e}")
                    post['impressions'] = 0
                    post['reach'] = 0
                    post['engagement'] = 0
                    post['saves'] = 0
                    post['shares'] = 0

                posts.append(post)

                # Progress indicator
                if idx % 20 == 0:
                    print(f"   ... processed {idx}/{limit} posts")

            df = pd.DataFrame(posts)

            # Calculate engagement rate
            df['engagement_rate'] = df.apply(
                lambda row: self._calculate_engagement_rate(row),
                axis=1
            )

            # Add timestamp
            df['updated_at'] = datetime.now()

            print(f"   ✓ Fetched {len(df)} posts with metrics")

            return df

        except Exception as e:
            print(f"   ❌ Failed to fetch posts: {e}")
            return pd.DataFrame(columns=[
                'post_id', 'caption', 'media_type', 'timestamp',
                'likes', 'comments', 'shares', 'saves',
                'impressions', 'reach', 'engagement_rate', 'updated_at'
            ])

    def _calculate_engagement_rate(self, post: pd.Series) -> float:
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

    def test_connection(self) -> bool:
        """
        Test API connection and credentials

        Returns:
            True if connection successful, False otherwise
        """
        try:
            endpoint = self.account_id
            params = {'fields': 'username,followers_count'}

            response = self._make_request(endpoint, params)

            if 'username' in response:
                print(f"✅ Connected to Instagram account: @{response['username']}")
                print(f"   Followers: {response.get('followers_count', 'N/A')}")
                return True
            else:
                print("❌ Unexpected API response")
                return False

        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
