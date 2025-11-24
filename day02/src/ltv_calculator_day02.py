"""
LTV Calculator for Day 02 - Creator Intelligence System
Calculates Lifetime Value metrics for Instagram followers
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

from .data_manager import DataManager
from . import config


class LTVCalculator:
    """Calculate Lifetime Value (LTV) metrics for followers"""

    def __init__(self, data_manager: DataManager):
        """
        Initialize LTV calculator

        Args:
            data_manager: DataManager instance for database access
        """
        self.dm = data_manager

        # Monetization assumptions (can be customized per creator)
        self.avg_cpm = 5.0  # Cost per 1000 impressions ($)
        self.avg_conversion_rate = 0.02  # 2% conversion rate for affiliate/products
        self.avg_order_value = 50.0  # Average order value ($)
        self.sponsored_post_rate = 0.10  # $0.10 per follower for sponsored posts

    def calculate_follower_ltv(self) -> Dict[str, float]:
        """
        Calculate the Lifetime Value of a follower

        Returns:
            Dictionary with LTV metrics
        """
        # Get metrics
        growth_metrics = self.dm.get_growth_metrics()
        engagement_stats = self.dm.get_engagement_stats()
        posts = self.dm.get_posts()

        current_followers = growth_metrics.get('current_followers', 0) or 0

        if posts.empty or current_followers <= 0:
            return {
                'ltv_per_follower': 0.0,
                'monthly_value_per_follower': 0.0,
                'annual_value_per_follower': 0.0,
                'total_account_value': 0.0,
                'revenue_breakdown': {},
                'posting_cadence_per_day': 0.0,
                'monthly_impressions_per_follower': 0.0
            }

        posts = posts.copy()
        posts['timestamp'] = pd.to_datetime(posts['timestamp'])
        posts[['impressions', 'reach']] = posts[['impressions', 'reach']].fillna(0)
        days_span = max((posts['timestamp'].max() - posts['timestamp'].min()).days, 0) + 1
        posts_per_day = len(posts) / days_span

        avg_impressions_per_post = float(np.nan_to_num(posts['impressions'].mean(), nan=0.0))
        monthly_impressions = avg_impressions_per_post * posts_per_day * 30
        monthly_impressions_per_follower = monthly_impressions / current_followers if current_followers else 0

        # Revenue stream 1: Ad revenue (CPM-based)
        monthly_ad_revenue_per_follower = (monthly_impressions_per_follower / 1000) * self.avg_cpm

        # Revenue stream 2: Affiliate/Product sales
        avg_engagement_rate = (engagement_stats.get('avg_engagement_rate') or 0) / 100
        monthly_sales_per_follower = monthly_impressions_per_follower * avg_engagement_rate * self.avg_conversion_rate * self.avg_order_value

        # Revenue stream 3: Sponsored posts (estimate)
        # Assuming 1 sponsored post per week
        monthly_sponsored_revenue_per_follower = self.sponsored_post_rate * 4

        # Total monthly value per follower
        monthly_value = (
            monthly_ad_revenue_per_follower +
            monthly_sales_per_follower +
            monthly_sponsored_revenue_per_follower
        )

        # Annual value
        annual_value = monthly_value * 12

        # LTV (assuming 2-year average follower lifetime)
        ltv_per_follower = annual_value * 2

        # Total account value
        total_account_value = ltv_per_follower * current_followers

        return {
            'ltv_per_follower': round(ltv_per_follower, 2),
            'monthly_value_per_follower': round(monthly_value, 4),
            'annual_value_per_follower': round(annual_value, 2),
            'total_account_value': round(total_account_value, 2),
            'posting_cadence_per_day': round(posts_per_day, 2),
            'monthly_impressions_per_follower': round(monthly_impressions_per_follower, 2),
            'revenue_breakdown': {
                'ad_revenue_monthly': round(monthly_ad_revenue_per_follower, 4),
                'sales_revenue_monthly': round(monthly_sales_per_follower, 4),
                'sponsored_revenue_monthly': round(monthly_sponsored_revenue_per_follower, 4)
            }
        }

    def calculate_content_roi(self) -> List[Dict]:
        """
        Calculate ROI for each content type

        Returns:
            List of dictionaries with ROI per content type
        """
        posts = self.dm.get_posts()

        if posts.empty:
            return []

        roi_data = []

        # Group by media type
        for media_type in posts['media_type'].unique():
            type_posts = posts[posts['media_type'] == media_type].copy()
            type_posts[['impressions', 'reach', 'engagement_rate']] = type_posts[['impressions', 'reach', 'engagement_rate']].fillna(0)

            # Average metrics
            avg_impressions = type_posts['impressions'].mean()
            avg_reach = type_posts['reach'].mean()
            avg_engagement_rate = float(type_posts['engagement_rate'].mean() or 0) / 100

            # Estimated value per post
            # Value from impressions (CPM)
            impression_value = (avg_impressions / 1000) * self.avg_cpm

            # Value from engagement (conversions)
            engagement_value = (
                avg_reach *
                avg_engagement_rate *
                self.avg_conversion_rate *
                self.avg_order_value
            )

            total_value_per_post = impression_value + engagement_value

            # Estimated production cost per content type
            production_costs = {
                'IMAGE': 50,  # $50 per image post
                'VIDEO': 200,  # $200 per video
                'CAROUSEL_ALBUM': 100  # $100 per carousel
            }

            production_cost = production_costs.get(media_type, 100)

            # ROI calculation
            roi_percentage = ((total_value_per_post - production_cost) / production_cost) * 100

            roi_data.append({
                'content_type': media_type,
                'post_count': len(type_posts),
                'avg_impressions': round(avg_impressions, 0),
                'avg_reach': round(avg_reach, 0),
                'avg_engagement_rate': round(avg_engagement_rate * 100, 2),
                'value_per_post': round(total_value_per_post, 2),
                'production_cost': production_cost,
                'roi_percentage': round(roi_percentage, 2),
                'net_profit_per_post': round(total_value_per_post - production_cost, 2)
            })

        # Sort by ROI
        roi_data.sort(key=lambda x: x['roi_percentage'], reverse=True)

        return roi_data

    def predict_growth_scenarios(self, months: int = 6) -> Dict[str, Dict]:
        """
        Predict follower growth under different scenarios

        Args:
            months: Number of months to project (default: 6)

        Returns:
            Dictionary with optimistic, realistic, and pessimistic scenarios
        """
        growth_metrics = self.dm.get_growth_metrics()
        current_followers = growth_metrics.get('current_followers', 0) or 0
        current_weekly_rate = max(growth_metrics.get('weekly_growth_rate', 0) / 100, 0)  # Convert to decimal

        if current_followers <= 0:
            return {}

        # Default to a modest baseline if no growth data
        if current_weekly_rate == 0:
            current_weekly_rate = 0.01  # 1% weekly baseline

        # Define scenarios
        scenarios = {
            'pessimistic': {
                'weekly_growth_rate': max(current_weekly_rate * 0.5, 0.001),  # 50% of current
                'description': 'Conservative - half current growth rate'
            },
            'realistic': {
                'weekly_growth_rate': current_weekly_rate * 1.5,  # 50% improvement
                'description': 'Moderate improvement with optimizations'
            },
            'optimistic': {
                'weekly_growth_rate': max(config.TARGET_WEEKLY_GROWTH_RATE / 100, current_weekly_rate * 2),
                'description': 'Aggressive - meeting target growth rate'
            }
        }

        results = {}

        for scenario_name, scenario_data in scenarios.items():
            weekly_rate = scenario_data['weekly_growth_rate']
            weeks = months * 4  # Approximate weeks per month

            # Compound growth calculation
            projected_followers = current_followers * ((1 + weekly_rate) ** weeks)
            total_growth = projected_followers - current_followers
            growth_percentage = (total_growth / current_followers) * 100

            # Calculate time to reach 200K
            if weekly_rate > 0:
                weeks_to_200k = np.log(200000 / current_followers) / np.log(1 + weekly_rate)
                months_to_200k = weeks_to_200k / 4
            else:
                weeks_to_200k = float('inf')
                months_to_200k = float('inf')

            results[scenario_name] = {
                'description': scenario_data['description'],
                'weekly_growth_rate': round(weekly_rate * 100, 2),
                'projected_followers': round(projected_followers, 0),
                'total_growth': round(total_growth, 0),
                'growth_percentage': round(growth_percentage, 2),
                'months_to_200k': round(months_to_200k, 1) if months_to_200k != float('inf') else 'Never',
                'will_reach_200k_in_6_months': projected_followers >= 200000 if months == 6 else None
            }

        return results

    def calculate_engagement_value(self) -> Dict[str, float]:
        """
        Calculate the monetary value of different engagement actions

        Returns:
            Dictionary with value per engagement type
        """
        posts = self.dm.get_posts()

        if posts.empty:
            return {}

        posts = posts.copy()
        posts[['likes', 'comments', 'saves', 'shares', 'reach']] = posts[['likes', 'comments', 'saves', 'shares', 'reach']].fillna(0)

        # Average reach
        avg_reach = posts['reach'].mean()

        # Conversion assumptions
        like_conversion = 0.001  # 0.1% of likes lead to value
        comment_conversion = 0.01  # 1% of comments lead to value
        save_conversion = 0.05  # 5% of saves lead to value (high intent)
        share_conversion = 0.02  # 2% of shares lead to value

        # Value per action (based on average order value and conversion)
        value_per_like = self.avg_order_value * like_conversion
        value_per_comment = self.avg_order_value * comment_conversion
        value_per_save = self.avg_order_value * save_conversion
        value_per_share = self.avg_order_value * share_conversion

        # Calculate total engagement value per post
        avg_likes = posts['likes'].mean()
        avg_comments = posts['comments'].mean()
        avg_saves = posts['saves'].mean()
        avg_shares = posts['shares'].mean()

        total_value_per_post = (
            (avg_likes * value_per_like) +
            (avg_comments * value_per_comment) +
            (avg_saves * value_per_save) +
            (avg_shares * value_per_share)
        )

        return {
            'value_per_like': round(value_per_like, 4),
            'value_per_comment': round(value_per_comment, 4),
            'value_per_save': round(value_per_save, 4),
            'value_per_share': round(value_per_share, 4),
            'avg_engagement_value_per_post': round(total_value_per_post, 2),
            'monthly_engagement_value': round(total_value_per_post * 30, 2)  # Assuming daily posts
        }

    def generate_ltv_summary(self) -> Dict:
        """
        Generate comprehensive LTV analysis summary

        Returns:
            Dictionary with all LTV metrics and analyses
        """
        return {
            'follower_ltv': self.calculate_follower_ltv(),
            'content_roi': self.calculate_content_roi(),
            'growth_scenarios': self.predict_growth_scenarios(months=6),
            'engagement_value': self.calculate_engagement_value()
        }
