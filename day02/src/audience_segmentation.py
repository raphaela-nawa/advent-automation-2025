"""
Audience Segmentation and Content Intelligence for Day 02
Analyzes post performance and identifies patterns
"""

from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

from . import config
from .data_manager import DataManager


class AudienceAnalyzer:
    """Performs audience segmentation and content intelligence analysis"""

    def __init__(self, data_manager: DataManager):
        """
        Initialize analyzer

        Args:
            data_manager: DataManager instance for database access
        """
        self.dm = data_manager

    def segment_posts_by_performance(self) -> Dict[str, pd.DataFrame]:
        """
        Segment posts into quartiles based on engagement rate

        Returns:
            Dictionary with segments: 'vip', 'high', 'medium', 'low'
        """
        posts = self.dm.get_posts()

        if posts.empty:
            print("   ⚠️  No posts to segment")
            return {
                'vip': pd.DataFrame(),
                'high': pd.DataFrame(),
                'medium': pd.DataFrame(),
                'low': pd.DataFrame()
            }

        # Calculate quartiles
        q25 = posts['engagement_rate'].quantile(0.25)
        q50 = posts['engagement_rate'].quantile(0.50)
        q75 = posts['engagement_rate'].quantile(0.75)

        # Segment posts
        segments = {
            'vip': posts[posts['engagement_rate'] >= q75].copy(),
            'high': posts[
                (posts['engagement_rate'] >= q50) &
                (posts['engagement_rate'] < q75)
            ].copy(),
            'medium': posts[
                (posts['engagement_rate'] >= q25) &
                (posts['engagement_rate'] < q50)
            ].copy(),
            'low': posts[posts['engagement_rate'] < q25].copy()
        }

        print(f"   ✓ Segmented posts:")
        print(f"      VIP (Top 25%): {len(segments['vip'])} posts")
        print(f"      High (50-75%): {len(segments['high'])} posts")
        print(f"      Medium (25-50%): {len(segments['medium'])} posts")
        print(f"      Low (Bottom 25%): {len(segments['low'])} posts")

        return segments

    def identify_best_posting_times(self) -> Dict[str, List[int]]:
        """
        Identify best hours and days for posting based on engagement

        Returns:
            Dictionary with 'hours' and 'days' lists
        """
        posts = self.dm.get_posts()

        if posts.empty:
            print("   ⚠️  No posts to analyze for timing")
            return {'hours': [], 'days': []}

        # Extract hour and day of week
        posts['hour'] = pd.to_datetime(posts['timestamp']).dt.hour
        posts['day_of_week'] = pd.to_datetime(posts['timestamp']).dt.day_name()

        # Calculate average engagement by hour
        hour_engagement = posts.groupby('hour')['engagement_rate'].mean()
        best_hours = hour_engagement.nlargest(3).index.tolist()

        # Calculate average engagement by day
        day_engagement = posts.groupby('day_of_week')['engagement_rate'].mean()
        best_days = day_engagement.nlargest(3).index.tolist()

        print(f"   ✓ Best posting hours: {best_hours}")
        print(f"   ✓ Best posting days: {best_days}")

        return {
            'hours': best_hours,
            'days': best_days
        }

    def identify_viral_content(self) -> pd.DataFrame:
        """
        Identify viral posts (engagement > 2x average)

        Returns:
            DataFrame with viral posts
        """
        posts = self.dm.get_posts()

        if posts.empty:
            print("   ⚠️  No posts to analyze for viral content")
            return pd.DataFrame()

        # Calculate average engagement
        avg_engagement = posts['engagement_rate'].mean()
        threshold = avg_engagement * config.VIRAL_THRESHOLD_MULTIPLIER

        # Filter viral posts
        viral_posts = posts[posts['engagement_rate'] >= threshold].copy()
        viral_posts = viral_posts.sort_values('engagement_rate', ascending=False)

        print(f"   ✓ Identified {len(viral_posts)} viral posts (>{threshold:.2f}% engagement)")

        return viral_posts

    def analyze_content_types(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze performance by content type (IMAGE, VIDEO, CAROUSEL_ALBUM)

        Returns:
            Dictionary with stats for each media type
        """
        posts = self.dm.get_posts()

        if posts.empty:
            print("   ⚠️  No posts to analyze by content type")
            return {}

        # Group by media type
        type_stats = posts.groupby('media_type').agg({
            'engagement_rate': ['mean', 'count'],
            'reach': 'mean',
            'impressions': 'mean'
        }).round(2)

        results = {}

        for media_type in type_stats.index:
            results[media_type] = {
                'avg_engagement_rate': type_stats.loc[media_type, ('engagement_rate', 'mean')],
                'count': int(type_stats.loc[media_type, ('engagement_rate', 'count')]),
                'avg_reach': type_stats.loc[media_type, ('reach', 'mean')],
                'avg_impressions': type_stats.loc[media_type, ('impressions', 'mean')]
            }

        print(f"   ✓ Analyzed {len(results)} content types")

        return results

    def get_top_posts(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N posts by engagement rate

        Args:
            n: Number of top posts to return (default: 10)

        Returns:
            DataFrame with top posts
        """
        posts = self.dm.get_posts()

        if posts.empty:
            return pd.DataFrame()

        # Check which column name is used for post ID
        id_column = 'post_id' if 'post_id' in posts.columns else 'id'

        columns_to_select = [id_column, 'caption', 'media_type', 'timestamp',
                            'likes', 'comments', 'saves', 'reach', 'engagement_rate']

        top_posts = posts.nlargest(n, 'engagement_rate')[columns_to_select].copy()

        return top_posts

    def calculate_engagement_trends(self) -> Dict[str, any]:
        """
        Calculate engagement trends over time

        Returns:
            Dictionary with trend analysis
        """
        posts = self.dm.get_posts()

        if posts.empty or len(posts) < 2:
            return {
                'trend': 'insufficient_data',
                'recent_avg': 0.0,
                'older_avg': 0.0,
                'change_pct': 0.0
            }

        # Sort by timestamp
        posts = posts.sort_values('timestamp')

        # Split into recent (last 30 days) and older
        cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
        posts['timestamp_dt'] = pd.to_datetime(posts['timestamp'])
        recent_posts = posts[posts['timestamp_dt'] >= cutoff_date]
        older_posts = posts[posts['timestamp_dt'] < cutoff_date]

        if recent_posts.empty or older_posts.empty:
            return {
                'trend': 'insufficient_data',
                'recent_avg': 0.0,
                'older_avg': 0.0,
                'change_pct': 0.0
            }

        recent_avg = recent_posts['engagement_rate'].mean()
        older_avg = older_posts['engagement_rate'].mean()

        change_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0

        trend = 'improving' if change_pct > 5 else ('declining' if change_pct < -5 else 'stable')

        return {
            'trend': trend,
            'recent_avg': round(recent_avg, 2),
            'older_avg': round(older_avg, 2),
            'change_pct': round(change_pct, 2)
        }

    def generate_insights_summary(self) -> Dict[str, any]:
        """
        Generate comprehensive insights summary

        Returns:
            Dictionary with all key insights
        """
        print("\n4. Performing audience segmentation...")

        # Get all analyses
        segments = self.segment_posts_by_performance()
        best_times = self.identify_best_posting_times()
        viral_posts = self.identify_viral_content()
        content_types = self.analyze_content_types()
        trends = self.calculate_engagement_trends()
        top_posts = self.get_top_posts(10)

        print("   ✓ Analysis complete")

        return {
            'segments': {
                'vip_count': len(segments['vip']),
                'high_count': len(segments['high']),
                'medium_count': len(segments['medium']),
                'low_count': len(segments['low'])
            },
            'best_posting_times': best_times,
            'viral_posts_count': len(viral_posts),
            'content_type_performance': content_types,
            'engagement_trend': trends,
            'top_posts': top_posts
        }

    def get_actionable_recommendations(self) -> List[str]:
        """
        Generate actionable recommendations based on analysis

        Returns:
            List of recommendation strings
        """
        posts = self.dm.get_posts()

        if posts.empty:
            return ["Insufficient data for recommendations"]

        recommendations = []

        # Best posting times
        best_times = self.identify_best_posting_times()
        if best_times['hours']:
            hours_str = ', '.join([f"{h}:00" for h in best_times['hours']])
            recommendations.append(
                f"📅 Post during peak engagement hours: {hours_str}"
            )

        if best_times['days']:
            days_str = ', '.join(best_times['days'])
            recommendations.append(
                f"📅 Focus on posting on: {days_str}"
            )

        # Content type recommendations
        content_types = self.analyze_content_types()
        if content_types:
            best_type = max(
                content_types.items(),
                key=lambda x: x[1]['avg_engagement_rate']
            )
            recommendations.append(
                f"🎬 {best_type[0]} content performs best "
                f"({best_type[1]['avg_engagement_rate']:.2f}% avg engagement)"
            )

        # Viral content patterns
        viral_posts = self.identify_viral_content()
        if not viral_posts.empty:
            recommendations.append(
                f"⚡ You've created {len(viral_posts)} viral posts - "
                f"analyze what made them successful"
            )

        # Engagement trend
        trends = self.calculate_engagement_trends()
        if trends['trend'] == 'improving':
            recommendations.append(
                f"📈 Engagement is improving (+{trends['change_pct']:.1f}%) - "
                f"keep doing what you're doing!"
            )
        elif trends['trend'] == 'declining':
            recommendations.append(
                f"📉 Engagement is declining ({trends['change_pct']:.1f}%) - "
                f"time to experiment with new content"
            )

        return recommendations
