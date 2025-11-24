"""
OpenAI Content Analyzer for Day 02 - Creator Intelligence System
Uses OpenAI GPT-4 to analyze Instagram content and generate insights
"""

import json
from typing import Dict, List, Optional
import pandas as pd
from openai import OpenAI

from .data_manager import DataManager
from . import config


class OpenAIContentAnalyzer:
    """Analyze Instagram content using OpenAI GPT-4"""

    def __init__(self, data_manager: DataManager):
        """
        Initialize OpenAI analyzer

        Args:
            data_manager: DataManager instance for database access
        """
        self.dm = data_manager

        # Initialize OpenAI client
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Set KEY_OPENAI_DAY02 in config/.env")

        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Using cost-effective model for analysis

    def analyze_viral_content_patterns(self) -> Dict[str, any]:
        """
        Analyze viral posts to identify common patterns and themes

        Returns:
            Dictionary with viral content analysis
        """
        posts = self.dm.get_posts()

        if posts.empty:
            return {'error': 'No posts available for analysis'}

        # Get viral posts (top 10% by engagement)
        engagement_threshold = posts['engagement_rate'].quantile(0.90)
        viral_posts = posts[posts['engagement_rate'] >= engagement_threshold]

        if viral_posts.empty:
            return {'error': 'No viral posts found'}

        # Prepare captions for analysis
        captions_text = "\n\n---\n\n".join([
            f"Post {idx+1} (Engagement: {row['engagement_rate']:.2f}%):\n{row['caption']}"
            for idx, row in viral_posts.head(10).iterrows()
        ])

        # Create prompt for GPT-4
        prompt = f"""Analyze these top-performing Instagram posts and identify common patterns:

{captions_text}

Please provide:
1. Common themes and topics
2. Writing style patterns (tone, length, emoji usage)
3. Hashtag strategies
4. Emotional triggers
5. Call-to-action patterns
6. Key success factors

Format your response as JSON with these keys: themes, writing_style, hashtag_strategy, emotional_triggers, cta_patterns, success_factors"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Instagram content strategist analyzing viral posts. Provide insights in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            # Parse response
            content = response.choices[0].message.content.strip()

            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)
            analysis['analyzed_posts_count'] = len(viral_posts)

            return analysis

        except Exception as e:
            return {
                'error': f'Analysis failed: {str(e)}',
                'analyzed_posts_count': len(viral_posts)
            }

    def generate_content_recommendations(self, current_performance: Dict) -> List[str]:
        """
        Generate personalized content recommendations based on performance data

        Args:
            current_performance: Dictionary with current performance metrics

        Returns:
            List of actionable recommendations
        """
        # Build context from current performance
        context = f"""Current Instagram Performance:
- Average Engagement: {current_performance.get('avg_engagement', 'N/A')}%
- Weekly Growth Rate: {current_performance.get('weekly_growth', 'N/A')}%
- Target Growth Rate: {current_performance.get('target_growth', 2.74)}%
- Best Content Type: {current_performance.get('best_content_type', 'N/A')}
- Total Followers: {current_performance.get('followers', 'N/A')}

Performance Gap: {current_performance.get('growth_gap', 'N/A')} percentage points below target"""

        prompt = f"""{context}

As an Instagram growth strategist, provide 8-10 specific, actionable recommendations to:
1. Increase weekly growth rate to meet the target
2. Improve engagement rates
3. Optimize content strategy

Focus on:
- Content creation tactics
- Posting schedule optimization
- Engagement strategies
- Growth hacks
- Monetization opportunities

Provide recommendations as a JSON array of strings, each being a concise, actionable recommendation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Instagram growth strategist. Provide specific, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1200
            )

            content = response.choices[0].message.content.strip()

            # Try to extract JSON array
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            recommendations = json.loads(content)

            # Ensure it's a list
            if isinstance(recommendations, dict):
                recommendations = recommendations.get('recommendations', [])

            return recommendations

        except Exception as e:
            return [
                f"⚠️ AI analysis unavailable: {str(e)}",
                "Recommendation: Review top performing posts manually",
                "Recommendation: Increase posting frequency during peak hours",
                "Recommendation: Engage with similar accounts in your niche"
            ]

    def analyze_caption_effectiveness(self) -> Dict[str, any]:
        """
        Analyze caption effectiveness across different performance tiers

        Returns:
            Dictionary with caption analysis insights
        """
        posts = self.dm.get_posts()

        if posts.empty:
            return {'error': 'No posts available'}

        # Separate high vs low performing posts
        median_engagement = posts['engagement_rate'].median()
        high_performers = posts[posts['engagement_rate'] >= median_engagement]
        low_performers = posts[posts['engagement_rate'] < median_engagement]

        # Sample captions from each group
        high_captions = high_performers['caption'].head(5).tolist()
        low_captions = low_performers['caption'].head(5).tolist()

        prompt = f"""Compare these Instagram captions from high-performing vs low-performing posts:

HIGH ENGAGEMENT POSTS:
{chr(10).join([f'{i+1}. {cap[:200]}...' for i, cap in enumerate(high_captions)])}

LOW ENGAGEMENT POSTS:
{chr(10).join([f'{i+1}. {cap[:200]}...' for i, cap in enumerate(low_captions)])}

Provide analysis as JSON:
{{
    "high_performers_patterns": ["pattern1", "pattern2", ...],
    "low_performers_issues": ["issue1", "issue2", ...],
    "caption_best_practices": ["practice1", "practice2", ...],
    "optimal_caption_length": "range",
    "recommended_elements": ["element1", "element2", ...]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an Instagram content expert analyzing caption effectiveness."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)

        except Exception as e:
            return {
                'error': f'Caption analysis failed: {str(e)}',
                'fallback_advice': 'Focus on storytelling and authentic voice'
            }

    def generate_content_calendar_suggestions(self, weeks: int = 4) -> Dict[str, List[str]]:
        """
        Generate content calendar suggestions based on performance data

        Args:
            weeks: Number of weeks to plan for

        Returns:
            Dictionary with content themes per day/week
        """
        posts = self.dm.get_posts()

        if posts.empty:
            return {'error': 'No historical data available'}

        # Get top performing themes from captions
        top_posts = posts.nlargest(10, 'engagement_rate')
        top_captions = "\n".join([f"- {cap[:150]}..." for cap in top_posts['caption'].head(10)])

        prompt = f"""Based on these successful Instagram posts:

{top_captions}

Create a {weeks}-week content calendar with:
- 3-4 content ideas per week
- Mix of content types (educational, entertaining, inspirational, promotional)
- Aligned with identified successful themes
- Varied but consistent tone

Provide as JSON:
{{
    "week_1": ["idea1", "idea2", "idea3", "idea4"],
    "week_2": [...],
    ...
    "content_pillars": ["pillar1", "pillar2", ...],
    "posting_schedule": "recommendation"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content strategist creating Instagram content calendars."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # More creative for content ideas
                max_tokens=1500
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)

        except Exception as e:
            return {
                'error': f'Content calendar generation failed: {str(e)}',
                'fallback_suggestion': 'Plan content around your top performing themes'
            }

    def generate_comprehensive_strategy(self, ltv_data: Dict, growth_scenarios: Dict) -> Dict[str, any]:
        """
        Generate comprehensive growth strategy combining all insights

        Args:
            ltv_data: LTV calculation results
            growth_scenarios: Growth projection scenarios

        Returns:
            Dictionary with strategic recommendations
        """
        # Build context
        context = f"""Instagram Account Analysis:

MONETIZATION:
- Account Value: ${ltv_data.get('total_account_value', 0):,.2f}
- LTV per Follower: ${ltv_data.get('ltv_per_follower', 0):.2f}

GROWTH SCENARIOS (6 months):
- Optimistic: {growth_scenarios.get('optimistic', {}).get('projected_followers', 0):,.0f} followers
- Realistic: {growth_scenarios.get('realistic', {}).get('projected_followers', 0):,.0f} followers
- Pessimistic: {growth_scenarios.get('pessimistic', {}).get('projected_followers', 0):,.0f} followers

TARGET: 200,000 followers in 6 months"""

        prompt = f"""{context}

As a senior Instagram strategist, create a comprehensive 6-month growth plan:

1. **Immediate Actions** (Next 30 days)
2. **Content Strategy** (Themes, formats, frequency)
3. **Engagement Tactics** (Community building)
4. **Monetization Strategy** (Leveraging LTV)
5. **Growth Hacks** (Specific to Instagram algorithm)
6. **Key Metrics to Track**

Provide as detailed JSON with these sections."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior Instagram growth strategist creating comprehensive growth plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)

        except Exception as e:
            return {
                'error': f'Strategy generation failed: {str(e)}',
                'fallback': 'Focus on consistent posting and engagement'
            }
