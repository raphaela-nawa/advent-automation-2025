"""
Day 11 Test Workflow
Test the complete workflow with synthetic data and no Slack sending

This script demonstrates the full workflow without requiring:
- Real BigQuery data
- Slack webhook configuration
- Day 01 CSV files

Perfect for testing and demonstration purposes.

Author: Gleyson - Retail Marketing Automation Specialist
"""

import logging
import sys
from datetime import datetime
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

from day11_DATA_fetcher import Day11DataFetcher, day11_calculate_metrics
from day11_FORMATTER_slack import Day11SlackFormatter, day11_format_simple_text_report


def day11_test_full_workflow():
    """Test the complete workflow with synthetic data."""

    print("=" * 70)
    print("DAY 11 WORKFLOW TEST - Using Synthetic Data")
    print("=" * 70)
    print()

    # Step 1: Generate synthetic data
    print("Step 1/4: Generating synthetic data...")
    fetcher = Day11DataFetcher()
    ga4_df, ads_df = fetcher._day11_generate_synthetic_data()

    print(f"✓ Generated {len(ga4_df)} GA4 rows and {len(ads_df)} Ads rows")
    print()

    # Show sample data
    print("Sample GA4 Data (first 3 rows):")
    print(ga4_df.head(3).to_string())
    print()

    print("Sample Ads Data (first 3 rows):")
    print(ads_df.head(3).to_string())
    print()

    # Step 2: Calculate metrics
    print("Step 2/4: Calculating performance metrics...")
    metrics = day11_calculate_metrics(ga4_df, ads_df)

    print(f"✓ Calculated {len(metrics)} metrics")
    print()

    # Step 3: Format messages
    print("Step 3/4: Formatting reports...")

    formatter = Day11SlackFormatter()

    # Format Slack message
    slack_payload = formatter.day11_format_daily_report(
        metrics,
        "✓ Using synthetic data for demonstration"
    )

    print(f"✓ Slack message formatted with {len(slack_payload['blocks'])} blocks")
    print()

    # Format text report
    text_report = day11_format_simple_text_report(metrics)

    print("Step 4/4: Displaying reports...")
    print()

    # Display text report
    print("=" * 70)
    print("TEXT REPORT")
    print("=" * 70)
    print(text_report)
    print()

    # Display Slack payload summary
    print("=" * 70)
    print("SLACK MESSAGE STRUCTURE")
    print("=" * 70)
    print(f"Number of blocks: {len(slack_payload['blocks'])}")
    print(f"Fallback text: {slack_payload['text']}")
    print()

    print("Block types:")
    for i, block in enumerate(slack_payload['blocks'], 1):
        block_type = block.get('type', 'unknown')
        print(f"  {i}. {block_type}")

    print()

    # Save Slack payload to file for inspection
    output_file = "day11_sample_slack_payload.json"
    with open(output_file, 'w') as f:
        json.dump(slack_payload, f, indent=2)

    print(f"✓ Full Slack payload saved to: {output_file}")
    print()

    # Display key metrics
    print("=" * 70)
    print("KEY PERFORMANCE INDICATORS")
    print("=" * 70)
    print(f"Report Period:        {metrics['start_date']} to {metrics['end_date']}")
    print(f"Days in Period:       {metrics['days_in_period']}")
    print()
    print("WEBSITE TRAFFIC (GA4):")
    print(f"  Total Sessions:     {metrics['total_sessions']:,}")
    print(f"  Conversions:        {metrics['total_conversions_ga4']:,}")
    print(f"  Avg Bounce Rate:    {metrics['avg_bounce_rate']:.1%}")
    print(f"  Top Source:         {metrics['top_source'].title()} ({metrics['top_source_sessions']:,} sessions)")
    print()
    print("PAID ADVERTISING (Google Ads):")
    print(f"  Total Spend:        ${metrics['total_spend']:,.2f}")
    print(f"  Conversions:        {metrics['total_conversions_ads']:,}")
    print(f"  Cost/Conversion:    ${metrics['cost_per_conversion']:.2f}")
    print(f"  Average CPC:        ${metrics['avg_cpc']:.2f}")
    print(f"  CTR:                {metrics['avg_ctr']:.2f}%")
    print()
    print("TOP CAMPAIGN:")
    print(f"  Name:               {metrics['top_campaign']}")
    print(f"  Conversions:        {metrics['top_campaign_conversions']}")
    print(f"  Spend:              ${metrics['top_campaign_spend']:.2f}")
    print()

    print("=" * 70)
    print("✓ TEST COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Review the Slack payload JSON to see the message structure")
    print("  2. Configure DAY11_SLACK_WEBHOOK_URL in config/.env")
    print("  3. Run: python day11_ORCHESTRATOR_main.py test")
    print("  4. Run: python day11_ORCHESTRATOR_main.py (for full report)")
    print()

    return True


if __name__ == "__main__":
    try:
        success = day11_test_full_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
