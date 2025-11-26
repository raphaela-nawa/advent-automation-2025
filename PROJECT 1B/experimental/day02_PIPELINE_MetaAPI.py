"""
Main Pipeline for Day 02 - Creator Intelligence System
Orchestrates data extraction, storage, and analysis
"""

import sys
from datetime import datetime

# Import project modules
from src.meta_extractor import MetaAPIExtractor
from src.data_manager import DataManager
from src.audience_segmentation import AudienceAnalyzer
from src.ltv_calculator_day02 import LTVCalculator
from src import config


def print_banner():
    """Print pipeline banner"""
    print("\n" + "=" * 50)
    print("PROJECT 1B: CREATOR INTELLIGENCE - DATA EXTRACTION")
    print("=" * 50 + "\n")


def print_summary(
    growth_metrics: dict,
    engagement_stats: dict,
    insights: dict,
    db_summary: dict,
    ltv_summary: dict
):
    """Print final summary"""
    print("\n" + "=" * 50)
    print("EXTRACTION COMPLETE - SUMMARY")
    print("=" * 50)

    # Account Growth
    print("\n📊 Account Growth:")
    print(f"   Current Followers: {growth_metrics['current_followers']:,}")
    print(f"   Weekly Growth Rate: {growth_metrics['weekly_growth_rate']}%")

    status = "✓ ON TRACK" if growth_metrics['on_track'] else "⚠️ BELOW TARGET"
    print(f"   Target Rate: {growth_metrics['target_rate']}% {status}")
    print(f"   90-Day Total Reach: {growth_metrics['total_reach_90d']:,}")

    # Engagement
    print("\n📈 Engagement:")
    print(f"   Average Engagement Rate: {engagement_stats['avg_engagement_rate']}%")
    print(f"   Total Posts Analyzed: {engagement_stats['total_posts']}")

    # Content Intelligence
    print("\n⭐ Content Intelligence:")

    if insights['best_posting_times']['hours']:
        hours = insights['best_posting_times']['hours']
        print(f"   Best Hours to Post: {hours}")

    if insights['best_posting_times']['days']:
        days = insights['best_posting_times']['days']
        print(f"   Best Days to Post: {days}")

    print(f"   Viral Posts (>2x avg): {insights['viral_posts_count']}")

    # Engagement Trend
    trend = insights['engagement_trend']
    if trend['trend'] == 'improving':
        print(f"   Trend: 📈 Improving (+{trend['change_pct']}%)")
    elif trend['trend'] == 'declining':
        print(f"   Trend: 📉 Declining ({trend['change_pct']}%)")
    else:
        print(f"   Trend: ➡️ Stable")

    # Data Storage
    print("\n💾 Data Storage:")
    print(f"   Database: {config.DB_PATH}")
    print(f"   Account Metrics: {db_summary['account_metrics_count']} days")
    print(f"   Posts Analyzed: {db_summary['posts_count']}")

    # LTV & Revenue
    follower_ltv = ltv_summary.get('follower_ltv', {}) if ltv_summary else {}
    content_roi = ltv_summary.get('content_roi', []) if ltv_summary else []
    growth_scenarios = ltv_summary.get('growth_scenarios', {}) if ltv_summary else {}

    print("\n💰 LTV & Revenue:")
    if follower_ltv:
        print(f"   LTV per Follower: ${follower_ltv.get('ltv_per_follower', 0):,.2f}")
        print(f"   Monthly Value/Follower: ${follower_ltv.get('monthly_value_per_follower', 0):,.4f}")
        print(f"   Annual Value/Follower: ${follower_ltv.get('annual_value_per_follower', 0):,.2f}")
        print(f"   Total Account Value: ${follower_ltv.get('total_account_value', 0):,.2f}")
        print(f"   Posting Cadence: {follower_ltv.get('posting_cadence_per_day', 0)} posts/day")
    else:
        print("   ⚠️  LTV unavailable (no data)")

    if content_roi:
        best_roi = content_roi[0]
        print(f"   Best ROI Content: {best_roi.get('content_type', 'N/A')} "
              f"({best_roi.get('roi_percentage', 0)}% ROI, "
              f"${best_roi.get('value_per_post', 0):,.2f} value/post)")

    if growth_scenarios:
        optimistic = growth_scenarios.get('optimistic', {})
        print("   Growth Scenario (Optimistic): "
              f"{optimistic.get('projected_followers', 'N/A'):,} followers in 6 months; "
              f"Reach 200K in ~{optimistic.get('months_to_200k', 'N/A')} months")

    print("\n" + "=" * 50)
    print("✅ Hour 1 Complete - Ready for Hour 2 (LTV Analysis)")
    print("=" * 50 + "\n")


def main():
    """Main pipeline execution"""
    try:
        print_banner()

        # Validate credentials first
        config.validate_credentials()

        # Initialize components
        print("Initializing components...")
        extractor = MetaAPIExtractor()
        data_manager = DataManager()
        analyzer = AudienceAnalyzer(data_manager)
        ltv_calculator = LTVCalculator(data_manager)

        # Test API connection
        print("\nTesting Meta API connection...")
        if not extractor.test_connection():
            print("\n❌ Failed to connect to Meta API. Please check your credentials.")
            print("   See README.md for setup instructions.")
            sys.exit(1)

        # Step 1: Extract account insights
        print("\n1. Extracting account insights (90 days)...")
        account_metrics = extractor.extract_account_insights(
            days=config.LOOKBACK_DAYS
        )

        if not account_metrics.empty:
            data_manager.save_account_metrics(account_metrics)
        else:
            print("   ⚠️ No account metrics extracted")

        # Step 2: Extract posts data
        print("\n2. Extracting posts data (100 most recent)...")
        posts = extractor.extract_recent_posts(limit=config.MAX_POSTS)

        if not posts.empty:
            data_manager.save_posts(posts)
        else:
            print("   ⚠️ No posts extracted")

        # Step 3: Calculate growth metrics
        print("\n3. Calculating growth metrics...")
        growth_metrics = data_manager.get_growth_metrics()
        print("   ✓ Growth analysis complete")

        # Step 4: Perform audience segmentation and analysis
        insights = analyzer.generate_insights_summary()

        # Get engagement stats
        engagement_stats = data_manager.get_engagement_stats()

        # Get database summary
        db_summary = data_manager.get_database_summary()

        # LTV analysis
        ltv_summary = ltv_calculator.generate_ltv_summary()

        # Print comprehensive summary
        print_summary(growth_metrics, engagement_stats, insights, db_summary, ltv_summary)

        # Print actionable recommendations
        print("💡 Actionable Recommendations:")
        recommendations = analyzer.get_actionable_recommendations()
        for rec in recommendations:
            print(f"   • {rec}")

        print("\n" + "=" * 50)

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return 1

    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
