"""
Data Manager for Day 02 - Creator Intelligence System
Handles all SQLite database operations
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

from . import config


class DataManager:
    """Manages SQLite database operations for creator intelligence data"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file (defaults to config.DB_PATH)
        """
        self.db_path = db_path or config.DB_PATH
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create account_metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_metrics (
                date DATE PRIMARY KEY,
                followers INTEGER,
                impressions INTEGER,
                reach INTEGER,
                profile_views INTEGER,
                website_clicks INTEGER,
                updated_at TIMESTAMP
            )
        """)

        # Create posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                caption TEXT,
                media_type TEXT,
                timestamp TIMESTAMP,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                saves INTEGER,
                impressions INTEGER,
                reach INTEGER,
                engagement_rate REAL,
                updated_at TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

        print(f"✅ Database initialized: {self.db_path}")

    def save_account_metrics(self, df: pd.DataFrame) -> int:
        """
        Save account metrics to database (upsert)

        Args:
            df: DataFrame with account metrics

        Returns:
            Number of rows inserted/updated
        """
        if df.empty:
            print("   ⚠️  No account metrics to save")
            return 0

        conn = sqlite3.connect(self.db_path)

        try:
            # Use replace to upsert (insert or update if exists)
            df.to_sql(
                'account_metrics',
                conn,
                if_exists='replace',
                index=False,
                method='multi'
            )

            rows = len(df)
            print(f"   ✓ Saved {rows} days of account metrics")

            return rows

        except Exception as e:
            print(f"   ❌ Failed to save account metrics: {e}")
            return 0

        finally:
            conn.close()

    def save_posts(self, df: pd.DataFrame) -> int:
        """
        Save posts data to database (upsert)

        Args:
            df: DataFrame with posts data

        Returns:
            Number of rows inserted/updated
        """
        if df.empty:
            print("   ⚠️  No posts to save")
            return 0

        conn = sqlite3.connect(self.db_path)

        try:
            # Use replace to upsert
            df.to_sql(
                'posts',
                conn,
                if_exists='replace',
                index=False,
                method='multi'
            )

            rows = len(df)
            print(f"   ✓ Saved {rows} posts to database")

            return rows

        except Exception as e:
            print(f"   ❌ Failed to save posts: {e}")
            return 0

        finally:
            conn.close()

    def get_account_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Retrieve account metrics from database

        Args:
            start_date: Filter from this date (inclusive)
            end_date: Filter to this date (inclusive)

        Returns:
            DataFrame with account metrics
        """
        conn = sqlite3.connect(self.db_path)

        try:
            query = "SELECT * FROM account_metrics"
            params = []

            if start_date or end_date:
                conditions = []
                if start_date:
                    conditions.append("date >= ?")
                    params.append(start_date.date())
                if end_date:
                    conditions.append("date <= ?")
                    params.append(end_date.date())

                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY date"

            df = pd.read_sql_query(query, conn, params=params)

            # Convert date column to datetime
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            print(f"   ❌ Failed to retrieve account metrics: {e}")
            return pd.DataFrame()

        finally:
            conn.close()

    def get_posts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Retrieve posts from database

        Args:
            start_date: Filter from this date (inclusive)
            end_date: Filter to this date (inclusive)
            limit: Maximum number of posts to return

        Returns:
            DataFrame with posts data
        """
        conn = sqlite3.connect(self.db_path)

        try:
            query = "SELECT * FROM posts"
            params = []

            if start_date or end_date:
                conditions = []
                if start_date:
                    conditions.append("timestamp >= ?")
                    params.append(start_date)
                if end_date:
                    conditions.append("timestamp <= ?")
                    params.append(end_date)

                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY timestamp DESC"

            if limit:
                query += f" LIMIT {limit}"

            df = pd.read_sql_query(query, conn, params=params)

            # Convert timestamp column to datetime
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            return df

        except Exception as e:
            print(f"   ❌ Failed to retrieve posts: {e}")
            return pd.DataFrame()

        finally:
            conn.close()

    def get_growth_metrics(self) -> Dict[str, any]:
        """
        Calculate growth metrics from stored data

        Returns:
            Dictionary with growth metrics
        """
        conn = sqlite3.connect(self.db_path)

        try:
            # Get latest and week-ago follower counts
            query = """
                SELECT date, followers
                FROM account_metrics
                WHERE followers IS NOT NULL
                ORDER BY date DESC
                LIMIT 1
            """

            df_latest = pd.read_sql_query(query, conn)

            if df_latest.empty:
                return {
                    'current_followers': 0,
                    'weekly_growth_rate': 0.0,
                    'on_track': False,
                    'target_rate': config.TARGET_WEEKLY_GROWTH_RATE
                }

            current_followers = int(df_latest.iloc[0]['followers'])
            latest_date = pd.to_datetime(df_latest.iloc[0]['date'])

            # Get follower count from 7 days ago
            week_ago = latest_date - timedelta(days=7)

            query_week_ago = """
                SELECT followers
                FROM account_metrics
                WHERE date <= ? AND followers IS NOT NULL
                ORDER BY date DESC
                LIMIT 1
            """

            df_week_ago = pd.read_sql_query(
                query_week_ago,
                conn,
                params=[week_ago.date()]
            )

            if not df_week_ago.empty:
                followers_week_ago = int(df_week_ago.iloc[0]['followers'])
                weekly_growth_rate = (
                    (current_followers - followers_week_ago) / followers_week_ago * 100
                )
            else:
                weekly_growth_rate = 0.0

            # Check if on track
            on_track = weekly_growth_rate >= config.TARGET_WEEKLY_GROWTH_RATE

            # Calculate total reach (90 days)
            query_reach = """
                SELECT SUM(reach) as total_reach
                FROM account_metrics
                WHERE reach IS NOT NULL
            """

            df_reach = pd.read_sql_query(query_reach, conn)
            total_reach = int(df_reach.iloc[0]['total_reach']) if not df_reach.empty else 0

            return {
                'current_followers': current_followers,
                'weekly_growth_rate': round(weekly_growth_rate, 2),
                'on_track': on_track,
                'target_rate': config.TARGET_WEEKLY_GROWTH_RATE,
                'total_reach_90d': total_reach
            }

        except Exception as e:
            print(f"   ❌ Failed to calculate growth metrics: {e}")
            return {
                'current_followers': 0,
                'weekly_growth_rate': 0.0,
                'on_track': False,
                'target_rate': config.TARGET_WEEKLY_GROWTH_RATE,
                'total_reach_90d': 0
            }

        finally:
            conn.close()

    def get_engagement_stats(self) -> Dict[str, any]:
        """
        Calculate engagement statistics from posts

        Returns:
            Dictionary with engagement stats
        """
        conn = sqlite3.connect(self.db_path)

        try:
            query = """
                SELECT
                    AVG(engagement_rate) as avg_engagement_rate,
                    COUNT(*) as total_posts,
                    MAX(engagement_rate) as max_engagement_rate,
                    MIN(engagement_rate) as min_engagement_rate
                FROM posts
                WHERE engagement_rate IS NOT NULL
            """

            df = pd.read_sql_query(query, conn)

            if df.empty or df.iloc[0]['total_posts'] is None:
                return {
                    'avg_engagement_rate': 0.0,
                    'total_posts': 0,
                    'max_engagement_rate': 0.0,
                    'min_engagement_rate': 0.0
                }

            return {
                'avg_engagement_rate': round(float(df.iloc[0]['avg_engagement_rate']), 2),
                'total_posts': int(df.iloc[0]['total_posts']),
                'max_engagement_rate': round(float(df.iloc[0]['max_engagement_rate']), 2),
                'min_engagement_rate': round(float(df.iloc[0]['min_engagement_rate']), 2)
            }

        except Exception as e:
            print(f"   ❌ Failed to calculate engagement stats: {e}")
            return {
                'avg_engagement_rate': 0.0,
                'total_posts': 0,
                'max_engagement_rate': 0.0,
                'min_engagement_rate': 0.0
            }

        finally:
            conn.close()

    def get_database_summary(self) -> Dict[str, any]:
        """
        Get summary of data in database

        Returns:
            Dictionary with database summary
        """
        conn = sqlite3.connect(self.db_path)

        try:
            # Count account metrics
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM account_metrics")
            metrics_count = cursor.fetchone()[0]

            # Count posts
            cursor.execute("SELECT COUNT(*) FROM posts")
            posts_count = cursor.fetchone()[0]

            # Get date range
            cursor.execute("""
                SELECT MIN(date) as min_date, MAX(date) as max_date
                FROM account_metrics
            """)
            date_range = cursor.fetchone()

            return {
                'account_metrics_count': metrics_count,
                'posts_count': posts_count,
                'date_range_start': date_range[0] if date_range[0] else 'N/A',
                'date_range_end': date_range[1] if date_range[1] else 'N/A'
            }

        except Exception as e:
            print(f"   ❌ Failed to get database summary: {e}")
            return {
                'account_metrics_count': 0,
                'posts_count': 0,
                'date_range_start': 'N/A',
                'date_range_end': 'N/A'
            }

        finally:
            conn.close()
