"""
Synthetic Data Pipeline for Day 02 - Creator Intelligence System
Analyzes pre-loaded synthetic data (no API connection required)
"""

import sys
from datetime import datetime

# Import project modules
from src.data_manager import DataManager
from src.audience_segmentation import AudienceAnalyzer
from src import config


def print_banner():
    """Print pipeline banner"""
    print("\n" + "=" * 50)
    print("PROJECT 1B: CREATOR INTELLIGENCE - SYNTHETIC DATA ANALYSIS")
    print("=" * 50 + "\n")


def print_summary(
    growth_metrics: dict,
    engagement_stats: dict,
    insights: dict,
    db_summary: dict
):
    """Print final summary"""
    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE - SUMMARY")
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
    print(f"   Max Engagement: {engagement_stats['max_engagement_rate']}%")
    print(f"   Min Engagement: {engagement_stats['min_engagement_rate']}%")

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

    # Content Type Performance
    if insights['content_type_performance']:
        print("\n🎬 Content Type Performance:")
        for media_type, stats in insights['content_type_performance'].items():
            print(f"   {media_type}:")
            print(f"      Avg Engagement: {stats['avg_engagement_rate']:.2f}%")
            print(f"      Posts: {stats['count']}")
            print(f"      Avg Reach: {stats['avg_reach']:,.0f}")

    # Data Storage
    print("\n💾 Data Storage:")
    print(f"   Database: {config.DB_PATH}")
    print(f"   Account Metrics: {db_summary['account_metrics_count']} days")
    print(f"   Posts Analyzed: {db_summary['posts_count']}")

    print("\n" + "=" * 50)
    print("✅ Hour 1 Complete - Ready for Hour 2 (LTV Analysis)")
    print("=" * 50 + "\n")


def main():
    """Main pipeline execution for synthetic data"""
    try:
        print_banner()

        # Initialize components (no API extractor needed)
        print("Initializing components...")
        data_manager = DataManager()
        analyzer = AudienceAnalyzer(data_manager)

        # Check if data exists in database
        print("\nChecking database...")
        db_summary = data_manager.get_database_summary()

        if db_summary['account_metrics_count'] == 0 or db_summary['posts_count'] == 0:
            print("\n❌ No data found in database!")
            print("\n💡 Please run: python load_synthetic_data.py")
            print("   to load the synthetic data first.\n")
            sys.exit(1)

        print(f"   ✓ Found {db_summary['account_metrics_count']} days of account metrics")
        print(f"   ✓ Found {db_summary['posts_count']} posts")

        # Step 1: Calculate growth metrics
        print("\n1. Calculating growth metrics...")
        growth_metrics = data_manager.get_growth_metrics()
        print("   ✓ Growth analysis complete")

        # Step 2: Get engagement stats
        print("\n2. Analyzing engagement statistics...")
        engagement_stats = data_manager.get_engagement_stats()
        print("   ✓ Engagement analysis complete")

        # Step 3: Perform audience segmentation and analysis
        print("\n3. Performing audience segmentation...")
        insights = analyzer.generate_insights_summary()

        # Print comprehensive summary
        print_summary(growth_metrics, engagement_stats, insights, db_summary)

        # Print actionable recommendations
        print("\n💡 Actionable Recommendations:")
        recommendations = analyzer.get_actionable_recommendations()
        for rec in recommendations:
            print(f"   • {rec}")

        # Print top posts
        print("\n" + "=" * 50)
        print("🏆 TOP 10 PERFORMING POSTS")
        print("=" * 50)
        top_posts = analyzer.get_top_posts(10)

        if not top_posts.empty:
            for idx, post in top_posts.iterrows():
                print(f"\n#{idx + 1} - {post['media_type']}")
                caption_preview = post['caption'][:80] + "..." if len(post['caption']) > 80 else post['caption']
                print(f"   Caption: {caption_preview}")
                print(f"   Engagement: {post['engagement_rate']:.2f}%")
                print(f"   Likes: {post['likes']:,} | Comments: {post['comments']:,} | Saves: {post['saves']:,}")
                print(f"   Reach: {post['reach']:,}")

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
