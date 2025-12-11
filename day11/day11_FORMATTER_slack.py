"""
Day 11 Slack Message Formatter
Formats performance metrics into rich Slack Block Kit messages

This module creates visually appealing Slack messages using Block Kit.
It supports markdown formatting, emojis, and structured layouts.

Author: Gleyson - Retail Marketing Automation Specialist
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class Day11SlackFormatter:
    """Formats performance data into Slack Block Kit messages."""

    @staticmethod
    def day11_format_daily_report(metrics: Dict, source_message: str) -> Dict:
        """
        Format metrics into a Slack message using Block Kit.

        Args:
            metrics: Dictionary of calculated metrics
            source_message: Message about data source used

        Returns:
            Slack webhook payload with blocks
        """
        blocks = []

        # Header Block
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Daily Retail Performance Report",
                "emoji": True
            }
        })

        # Date Range Context
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 *Report Period:* {metrics['start_date']} to {metrics['end_date']} ({metrics['days_in_period']} days)"
                }
            ]
        })

        blocks.append({"type": "divider"})

        # GA4 Section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🌐 Website Traffic (GA4)*"
            }
        })

        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Sessions:*\n{metrics['total_sessions']:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Conversions:*\n{metrics['total_conversions_ga4']:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Avg Bounce Rate:*\n{metrics['avg_bounce_rate']:.1%}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Top Source:*\n{metrics['top_source'].title()} ({metrics['top_source_sessions']:,} sessions)"
                }
            ]
        })

        # Bounce rate warning
        if metrics['avg_bounce_rate'] > 0.60:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "⚠️ *Warning:* Bounce rate is above 60%"
                    }
                ]
            })

        blocks.append({"type": "divider"})

        # Google Ads Section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💰 Paid Advertising (Google Ads)*"
            }
        })

        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Spend:*\n${metrics['total_spend']:,.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Conversions:*\n{metrics['total_conversions_ads']:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Cost per Conversion:*\n${metrics['cost_per_conversion']:.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Avg CPC:*\n${metrics['avg_cpc']:.2f}"
                }
            ]
        })

        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Clicks:*\n{metrics['total_clicks']:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Impressions:*\n{metrics['total_impressions']:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*CTR:*\n{metrics['avg_ctr']:.2f}%"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Top Campaign:*\n{metrics['top_campaign']}"
                }
            ]
        })

        # Performance warnings
        warnings = []
        if metrics['total_conversions_ads'] < 5:
            warnings.append("⚠️ Low conversion count (< 5)")
        if metrics['cost_per_conversion'] > 50:
            warnings.append("⚠️ High cost per conversion (> $50)")

        if warnings:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": " | ".join(warnings)
                    }
                ]
            })

        blocks.append({"type": "divider"})

        # Top Campaign Highlight
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🏆 Best Performing Campaign*\n"
                        f"*{metrics['top_campaign']}* generated *{metrics['top_campaign_conversions']}* conversions "
                        f"with ${metrics['top_campaign_spend']:.2f} spend"
            }
        })

        blocks.append({"type": "divider"})

        # Footer with data source and timestamp
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{source_message} | Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                }
            ]
        })

        # Build complete payload
        payload = {
            "blocks": blocks,
            "text": f"Daily Performance Report: {metrics['start_date']} to {metrics['end_date']}"  # Fallback text
        }

        return payload

    @staticmethod
    def day11_format_error_message(error: Exception, context: str = "") -> Dict:
        """
        Format an error message for Slack notification.

        Args:
            error: Exception that occurred
            context: Additional context about the error

        Returns:
            Slack webhook payload for error notification
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "❌ Report Generation Failed",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Type:* `{type(error).__name__}`\n*Message:* {str(error)}"
                }
            }
        ]

        if context:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Context:* {context}"
                }
            })

        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                }
            ]
        })

        return {
            "blocks": blocks,
            "text": f"Report generation failed: {str(error)}"
        }

    @staticmethod
    def day11_format_test_message() -> Dict:
        """Create a simple test message."""
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Day 11 Workflow Test",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a test message from the Day 11 automated reporting system.\n"
                                "If you see this, the Slack integration is working! 🎉"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ],
            "text": "Day 11 Workflow Test Message"
        }


def day11_format_simple_text_report(metrics: Dict) -> str:
    """
    Format metrics into a simple text report (for email or logging).

    Args:
        metrics: Dictionary of calculated metrics

    Returns:
        Formatted text report
    """
    report = f"""
Daily Retail Performance Report
Report Period: {metrics['start_date']} to {metrics['end_date']} ({metrics['days_in_period']} days)

========================================
WEBSITE TRAFFIC (GA4)
========================================
Total Sessions:        {metrics['total_sessions']:,}
Conversions:          {metrics['total_conversions_ga4']:,}
Avg Bounce Rate:      {metrics['avg_bounce_rate']:.1%}
Top Source:           {metrics['top_source'].title()} ({metrics['top_source_sessions']:,} sessions)

========================================
PAID ADVERTISING (Google Ads)
========================================
Total Spend:          ${metrics['total_spend']:,.2f}
Conversions:          {metrics['total_conversions_ads']:,}
Cost per Conversion:  ${metrics['cost_per_conversion']:.2f}
Avg CPC:             ${metrics['avg_cpc']:.2f}
Clicks:              {metrics['total_clicks']:,}
Impressions:         {metrics['total_impressions']:,}
CTR:                 {metrics['avg_ctr']:.2f}%

========================================
TOP PERFORMING CAMPAIGN
========================================
Campaign:            {metrics['top_campaign']}
Conversions:         {metrics['top_campaign_conversions']}
Spend:              ${metrics['top_campaign_spend']:.2f}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
    return report.strip()


if __name__ == "__main__":
    # Test the formatter with sample data
    print("Day 11 Slack Formatter Test")
    print("=" * 60)

    # Sample metrics
    sample_metrics = {
        'total_sessions': 15420,
        'total_conversions_ga4': 342,
        'avg_bounce_rate': 0.45,
        'top_source': 'google',
        'top_source_sessions': 8500,
        'total_spend': 2450.50,
        'total_clicks': 1850,
        'total_impressions': 65000,
        'total_conversions_ads': 125,
        'avg_ctr': 2.85,
        'avg_cpc': 1.32,
        'cost_per_conversion': 19.60,
        'top_campaign': 'Brand Campaign',
        'top_campaign_conversions': 45,
        'top_campaign_spend': 680.00,
        'start_date': '2024-12-01',
        'end_date': '2024-12-07',
        'days_in_period': 7
    }

    formatter = Day11SlackFormatter()

    print("\n--- Slack Block Kit Payload ---")
    slack_payload = formatter.day11_format_daily_report(
        sample_metrics,
        "✓ Data fetched from BigQuery"
    )
    print(f"Number of blocks: {len(slack_payload['blocks'])}")
    print(f"Fallback text: {slack_payload['text']}")

    print("\n--- Simple Text Report ---")
    text_report = day11_format_simple_text_report(sample_metrics)
    print(text_report)

    print("\n--- Error Message ---")
    error_payload = formatter.day11_format_error_message(
        ValueError("Sample error"),
        "Testing error formatting"
    )
    print(f"Error notification blocks: {len(error_payload['blocks'])}")

    print("\n=" * 60)
