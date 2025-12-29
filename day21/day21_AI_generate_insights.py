"""
Day 21: AI Insights Layer - Executive Summary Generator
Uses Claude API to generate strategic insights from validated SaaS metrics
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Local imports
from day21_DATA_fetch_metrics import day21_fetch_all_metrics

# Load environment variables
root_dir = Path(__file__).parent.parent
env_path = root_dir / "config" / ".env"
load_dotenv(env_path)

# Load configuration
config_path = Path(__file__).parent / "config" / "day21_CONFIG_insight_settings.yaml"
with open(config_path, 'r') as f:
    day21_CONFIG = yaml.safe_load(f)

# Initialize Anthropic client
day21_ANTHROPIC_API_KEY = os.getenv("DAY21_ANTHROPIC_API_KEY")
if not day21_ANTHROPIC_API_KEY:
    raise ValueError("DAY21_ANTHROPIC_API_KEY not found in .env file")

day21_anthropic_client = anthropic.Anthropic(api_key=day21_ANTHROPIC_API_KEY)


def day21_load_prompt_template():
    """Load the AI prompt template"""
    template_path = Path(__file__).parent / "day21_AI_prompt_template.txt"
    with open(template_path, 'r') as f:
        return f.read()


def day21_format_alerts(alerts):
    """Format alerts for prompt"""
    if not alerts:
        return "✅ No automated alerts triggered - all metrics within healthy thresholds."

    alert_text = f"⚠️  {len(alerts)} AUTOMATED ALERT(S) TRIGGERED:\n\n"
    for i, alert in enumerate(alerts, 1):
        severity_emoji = "🔴" if alert['severity'] == 'high' else "🟡"
        alert_text += f"{i}. {severity_emoji} [{alert['severity'].upper()}] {alert['type']}\n"
        alert_text += f"   {alert['message']}\n\n"

    return alert_text


def day21_generate_insights(metrics_data):
    """Generate AI insights from metrics data"""
    print("=" * 70)
    print("DAY 21: GENERATING AI INSIGHTS")
    print("=" * 70)

    # Load prompt template
    print("\n📝 Loading prompt template...")
    prompt_template = day21_load_prompt_template()

    # Format alerts
    alerts_summary = day21_format_alerts(metrics_data.get('alerts', []))

    # Format metrics as JSON string
    metrics_json = json.dumps({
        "kpis": metrics_data['kpis'],
        "mrr_growth": metrics_data['mrr_growth'],
        "retention": metrics_data['retention'],
        "at_risk_customers": metrics_data['at_risk_customers']
    }, indent=2, default=str)

    # Fill in prompt template
    prompt = prompt_template.format(
        metrics_json=metrics_json,
        alerts_summary=alerts_summary
    )

    # Get AI configuration
    model = day21_CONFIG['insight_generation']['model']
    max_tokens = day21_CONFIG['insight_generation']['max_tokens']
    temperature = day21_CONFIG['insight_generation']['temperature']

    print(f"\n🤖 Calling Claude API...")
    print(f"   Model: {model}")
    print(f"   Max Tokens: {max_tokens}")
    print(f"   Temperature: {temperature}")

    # Call Claude API
    message = day21_anthropic_client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract response
    insights_text = message.content[0].text

    print(f"\n✅ Insights generated successfully!")
    print(f"   Response length: {len(insights_text)} characters")
    print(f"   Tokens used: {message.usage.input_tokens} input, {message.usage.output_tokens} output")

    return insights_text, message.usage


def day21_save_insights(insights_text, metrics_data, usage_stats):
    """Save insights to markdown file with metadata"""
    output_dir = Path(__file__).parent / day21_CONFIG['output']['save_to']
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime(day21_CONFIG['output']['timestamp_format'])
    output_file = output_dir / f"{day21_CONFIG['output']['file_prefix']}{timestamp}.md"

    # Build complete markdown document
    markdown_content = f"""# SaaS Health Metrics - Executive Insights Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Data Source:** BigQuery ({day21_CONFIG['bigquery']['project_id']}.{day21_CONFIG['bigquery']['dataset_id']})
**AI Model:** {day21_CONFIG['insight_generation']['model']}

---

{insights_text}

---

## Metadata

### Data Snapshot
- **Fetched At:** {metrics_data['metadata']['fetched_at']}
- **Current MRR:** ${metrics_data['kpis']['current_mrr']:,.2f}
- **Active Customers:** {metrics_data['kpis']['active_customers']}
- **Churn Rate:** {metrics_data['kpis']['churn_rate_pct']:.2f}%

### AI Generation Stats
- **Input Tokens:** {usage_stats.input_tokens:,}
- **Output Tokens:** {usage_stats.output_tokens:,}
- **Total Tokens:** {usage_stats.input_tokens + usage_stats.output_tokens:,}
- **Model:** {day21_CONFIG['insight_generation']['model']}
- **Temperature:** {day21_CONFIG['insight_generation']['temperature']}

### Automated Alerts
{day21_format_alerts(metrics_data.get('alerts', []))}

---

*This report was generated automatically by the Day 21 AI Insights Layer.*
*For questions or to modify analysis parameters, see `day21_CONFIG_insight_settings.yaml`*
"""

    # Write to file
    with open(output_file, 'w') as f:
        f.write(markdown_content)

    print(f"\n💾 Insights saved to: {output_file}")

    return output_file


def day21_main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("DAY 21: AI INSIGHTS LAYER - FULL PIPELINE")
    print("=" * 70)

    # Step 1: Fetch metrics
    print("\n[STEP 1/3] Fetching metrics from BigQuery...")
    metrics_data, metrics_file = day21_fetch_all_metrics()

    # Step 2: Generate insights
    print("\n[STEP 2/3] Generating AI insights...")
    insights_text, usage_stats = day21_generate_insights(metrics_data)

    # Step 3: Save insights
    print("\n[STEP 3/3] Saving insights report...")
    output_file = day21_save_insights(insights_text, metrics_data, usage_stats)

    # Summary
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n📊 Metrics Data: {metrics_file}")
    print(f"📝 Insights Report: {output_file}")

    # Show first 500 characters of insights
    print("\n📖 PREVIEW OF INSIGHTS:\n")
    print("-" * 70)
    print(insights_text[:500] + "...\n")
    print("-" * 70)
    print(f"\nFull report saved to: {output_file}")
    print("\n" + "=" * 70)

    return output_file


if __name__ == "__main__":
    day21_main()
