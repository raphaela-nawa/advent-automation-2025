"""
Pipeline for Day 02 Hour 2 - Creator Intelligence System
LTV Analysis + OpenAI Insights
"""

import sys
from datetime import datetime
import json

# Import project modules
from src.data_manager import DataManager
from src.audience_segmentation import AudienceAnalyzer
from src.ltv_calculator_day02 import LTVCalculator
from src.openai_analyzer_day02 import OpenAIContentAnalyzer
from src import config


def print_banner():
    """Print pipeline banner"""
    print("\n" + "=" * 60)
    print("DAY 02 - HOUR 2: LTV ANALYSIS + AI INSIGHTS")
    print("=" * 60 + "\n")


def print_ltv_summary(ltv_summary: dict):
    """Print LTV analysis summary"""
    print("\n" + "=" * 60)
    print("💰 LIFETIME VALUE (LTV) ANALYSIS")
    print("=" * 60)

    follower_ltv = ltv_summary.get('follower_ltv', {})

    print("\n📊 Follower Economics:")
    print(f"   LTV per Follower: ${follower_ltv.get('ltv_per_follower', 0):.2f}")
    print(f"   Monthly Value per Follower: ${follower_ltv.get('monthly_value_per_follower', 0):.4f}")
    print(f"   Annual Value per Follower: ${follower_ltv.get('annual_value_per_follower', 0):.2f}")
    print(f"   Total Account Value: ${follower_ltv.get('total_account_value', 0):,.2f}")

    revenue_breakdown = follower_ltv.get('revenue_breakdown', {})
    if revenue_breakdown:
        print("\n💵 Revenue Breakdown (Monthly per Follower):")
        print(f"   Ad Revenue: ${revenue_breakdown.get('ad_revenue_monthly', 0):.4f}")
        print(f"   Sales Revenue: ${revenue_breakdown.get('sales_revenue_monthly', 0):.4f}")
        print(f"   Sponsored Posts: ${revenue_breakdown.get('sponsored_revenue_monthly', 0):.4f}")

    print(f"\n📅 Posting Cadence: {follower_ltv.get('posting_cadence_per_day', 0):.2f} posts/day")
    print(f"📈 Monthly Impressions per Follower: {follower_ltv.get('monthly_impressions_per_follower', 0):,.0f}")


def print_content_roi(content_roi: list):
    """Print content ROI analysis"""
    print("\n" + "=" * 60)
    print("📊 CONTENT ROI ANALYSIS")
    print("=" * 60 + "\n")

    if not content_roi:
        print("No content ROI data available")
        return

    for idx, roi in enumerate(content_roi, 1):
        print(f"{idx}. {roi['content_type']} ({roi['post_count']} posts)")
        print(f"   Value per Post: ${roi['value_per_post']:.2f}")
        print(f"   Production Cost: ${roi['production_cost']}")
        print(f"   ROI: {roi['roi_percentage']:.2f}%")
        print(f"   Net Profit: ${roi['net_profit_per_post']:.2f}")
        print(f"   Avg Engagement: {roi['avg_engagement_rate']:.2f}%")
        print()


def print_growth_scenarios(scenarios: dict):
    """Print growth projection scenarios"""
    print("\n" + "=" * 60)
    print("🚀 GROWTH PROJECTIONS (6 Months)")
    print("=" * 60 + "\n")

    for scenario_name, scenario in scenarios.items():
        icon = "📈" if scenario_name == "optimistic" else "📊" if scenario_name == "realistic" else "📉"

        print(f"{icon} {scenario_name.upper()}")
        print(f"   {scenario.get('description', '')}")
        print(f"   Weekly Growth: {scenario.get('weekly_growth_rate', 0):.2f}%")
        print(f"   Projected Followers: {scenario.get('projected_followers', 0):,.0f}")
        print(f"   Total Growth: +{scenario.get('total_growth', 0):,.0f}")
        print(f"   Months to 200K: {scenario.get('months_to_200k', 'N/A')}")

        if scenario.get('will_reach_200k_in_6_months'):
            print(f"   ✅ WILL REACH 200K TARGET")
        else:
            print(f"   ⚠️ Will NOT reach 200K in 6 months")
        print()


def print_ai_insights(ai_insights: dict):
    """Print AI-generated insights"""
    print("\n" + "=" * 60)
    print("🤖 AI-POWERED INSIGHTS")
    print("=" * 60)

    # Viral content patterns
    if 'viral_patterns' in ai_insights and 'error' not in ai_insights['viral_patterns']:
        print("\n⚡ Viral Content Patterns:")
        viral = ai_insights['viral_patterns']

        if 'themes' in viral:
            print(f"\n   Themes: {', '.join(viral['themes'][:3]) if isinstance(viral['themes'], list) else viral['themes']}")

        if 'success_factors' in viral:
            factors = viral['success_factors']
            if isinstance(factors, list):
                for factor in factors[:3]:
                    print(f"   • {factor}")

    # Content recommendations
    if 'recommendations' in ai_insights and ai_insights['recommendations']:
        print("\n💡 Strategic Recommendations:")
        for idx, rec in enumerate(ai_insights['recommendations'][:8], 1):
            print(f"   {idx}. {rec}")

    # Caption effectiveness
    if 'caption_analysis' in ai_insights and 'error' not in ai_insights['caption_analysis']:
        caption = ai_insights['caption_analysis']
        if 'caption_best_practices' in caption:
            print("\n✍️ Caption Best Practices:")
            practices = caption['caption_best_practices']
            if isinstance(practices, list):
                for practice in practices[:3]:
                    print(f"   • {practice}")


def main():
    """Main pipeline execution for Hour 2"""
    try:
        print_banner()

        # Initialize components
        print("Initializing components...")
        data_manager = DataManager()
        analyzer = AudienceAnalyzer(data_manager)
        ltv_calculator = LTVCalculator(data_manager)

        # Check if data exists
        print("\nChecking database...")
        db_summary = data_manager.get_database_summary()

        if db_summary['account_metrics_count'] == 0 or db_summary['posts_count'] == 0:
            print("\n❌ No data found in database!")
            print("\n💡 Please run: python experimental/day02_PIPELINE_synthetic_data_loader.py")
            sys.exit(1)

        print(f"   ✓ Found {db_summary['account_metrics_count']} days of metrics")
        print(f"   ✓ Found {db_summary['posts_count']} posts")

        # Phase 1: LTV Analysis
        print("\n" + "=" * 60)
        print("PHASE 1: CALCULATING LIFETIME VALUE METRICS")
        print("=" * 60)

        print("\n1. Calculating follower LTV...")
        ltv_summary = ltv_calculator.generate_ltv_summary()
        print("   ✓ LTV calculations complete")

        print("\n2. Analyzing content ROI...")
        content_roi = ltv_summary.get('content_roi', [])
        print(f"   ✓ Analyzed {len(content_roi)} content types")

        print("\n3. Generating growth projections...")
        growth_scenarios = ltv_summary.get('growth_scenarios', {})
        print(f"   ✓ Generated {len(growth_scenarios)} scenarios")

        # Print LTV results
        print_ltv_summary(ltv_summary)
        print_content_roi(content_roi)
        print_growth_scenarios(growth_scenarios)

        # Phase 2: AI-Powered Insights
        print("\n" + "=" * 60)
        print("PHASE 2: AI-POWERED CONTENT ANALYSIS")
        print("=" * 60)

        try:
            print("\nInitializing OpenAI analyzer...")
            openai_analyzer = OpenAIContentAnalyzer(data_manager)
            print("   ✓ OpenAI client initialized")

            # Gather current performance data
            growth_metrics = data_manager.get_growth_metrics()
            engagement_stats = data_manager.get_engagement_stats()
            insights = analyzer.generate_insights_summary()

            current_performance = {
                'avg_engagement': engagement_stats.get('avg_engagement_rate', 0),
                'weekly_growth': growth_metrics.get('weekly_growth_rate', 0),
                'target_growth': config.TARGET_WEEKLY_GROWTH_RATE,
                'best_content_type': 'VIDEO',  # From Hour 1 results
                'followers': growth_metrics.get('current_followers', 0),
                'growth_gap': config.TARGET_WEEKLY_GROWTH_RATE - growth_metrics.get('weekly_growth_rate', 0)
            }

            print("\n1. Analyzing viral content patterns...")
            viral_patterns = openai_analyzer.analyze_viral_content_patterns()
            print(f"   ✓ Analyzed {viral_patterns.get('analyzed_posts_count', 0)} viral posts")

            print("\n2. Generating strategic recommendations...")
            recommendations = openai_analyzer.generate_content_recommendations(current_performance)
            print(f"   ✓ Generated {len(recommendations)} recommendations")

            print("\n3. Analyzing caption effectiveness...")
            caption_analysis = openai_analyzer.analyze_caption_effectiveness()
            print("   ✓ Caption analysis complete")

            print("\n4. Creating content calendar suggestions...")
            content_calendar = openai_analyzer.generate_content_calendar_suggestions(weeks=4)
            print("   ✓ 4-week content calendar generated")

            # Compile AI insights
            ai_insights = {
                'viral_patterns': viral_patterns,
                'recommendations': recommendations,
                'caption_analysis': caption_analysis,
                'content_calendar': content_calendar
            }

            # Print AI insights
            print_ai_insights(ai_insights)

            # Generate comprehensive strategy
            print("\n5. Generating comprehensive growth strategy...")
            strategy = openai_analyzer.generate_comprehensive_strategy(
                ltv_summary.get('follower_ltv', {}),
                growth_scenarios
            )
            print("   ✓ Growth strategy generated")

            # Save results to JSON
            results = {
                'timestamp': datetime.now().isoformat(),
                'ltv_analysis': ltv_summary,
                'ai_insights': ai_insights,
                'growth_strategy': strategy
            }

            output_file = 'data/day02_DATA_ltv_analysis.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Results saved to: {output_file}")

        except ValueError as e:
            if "OpenAI API key not found" in str(e):
                print("\n⚠️  OpenAI API key not configured")
                print("   Skipping AI-powered insights...")
                print("   To enable: Set KEY_OPENAI_DAY02 in config/.env")
            else:
                raise

        # Final summary
        print("\n" + "=" * 60)
        print("✅ HOUR 2 COMPLETE")
        print("=" * 60)

        print("\n📊 Summary:")
        print(f"   Account Value: ${ltv_summary.get('follower_ltv', {}).get('total_account_value', 0):,.2f}")
        print(f"   LTV per Follower: ${ltv_summary.get('follower_ltv', {}).get('ltv_per_follower', 0):.2f}")
        print(f"   Best ROI Content: {content_roi[0]['content_type'] if content_roi else 'N/A'}")
        print(f"   Optimistic Projection: {growth_scenarios.get('optimistic', {}).get('projected_followers', 0):,.0f} followers")

        print("\n🎯 Next Steps:")
        print("   • Review AI recommendations")
        print("   • Implement content calendar")
        print("   • Monitor ROI by content type")
        print("   • Track growth toward optimistic scenario")

        print("\n" + "=" * 60 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return 1

    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
