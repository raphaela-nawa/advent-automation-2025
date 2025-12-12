#!/usr/bin/env python3
"""
Day 12 - Generate Data Docs (HTML Report)
Creates visual documentation of validation results
Simulates Great Expectations Data Docs functionality
"""

import json
from pathlib import Path
from datetime import datetime
from day12_CONFIG_settings import DAY12_VALIDATION_RESULTS_DIR, DAY12_LOGS_DIR

def day12_generate_html_report(results_json_path: Path) -> Path:
    """Generate HTML report from validation results"""

    # Load results
    with open(results_json_path, 'r') as f:
        results = json.load(f)

    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Day 12 - Data Quality Report: {results['dataset']}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f7fa;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 32px;
            }}
            .header .subtitle {{
                opacity: 0.9;
                margin-top: 10px;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .summary-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .summary-card h3 {{
                margin: 0 0 10px 0;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #666;
            }}
            .summary-card .value {{
                font-size: 36px;
                font-weight: bold;
                color: #333;
            }}
            .status-pass {{ color: #10b981; }}
            .status-fail {{ color: #ef4444; }}
            .expectation {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #10b981;
            }}
            .expectation.fail {{
                border-left-color: #ef4444;
            }}
            .expectation-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .expectation-type {{
                font-family: 'Courier New', monospace;
                font-size: 14px;
                color: #667eea;
            }}
            .badge {{
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            .badge-pass {{ background: #d1fae5; color: #065f46; }}
            .badge-fail {{ background: #fee2e2; color: #991b1b; }}
            .badge-critical {{ background: #fef3c7; color: #92400e; }}
            .details {{
                font-size: 14px;
                color: #666;
                margin-top: 10px;
            }}
            .details-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin-top: 10px;
            }}
            .detail-item {{
                background: #f9fafb;
                padding: 8px 12px;
                border-radius: 6px;
            }}
            .detail-label {{
                font-size: 11px;
                text-transform: uppercase;
                color: #9ca3af;
                letter-spacing: 0.5px;
            }}
            .detail-value {{
                font-size: 14px;
                color: #111827;
                font-weight: 600;
                margin-top: 2px;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔐 Data Quality Validation Report</h1>
            <div class="subtitle">
                <strong>Dataset:</strong> {results['dataset']}<br>
                <strong>Validation Time:</strong> {results['timestamp']}<br>
                <strong>Total Records:</strong> {results['total_rows']:,}
            </div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Expectations</h3>
                <div class="value">{results['statistics']['total_expectations']}</div>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <div class="value status-pass">{results['statistics']['passed']}</div>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <div class="value status-fail">{results['statistics']['failed']}</div>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <div class="value {'status-pass' if results['success'] else 'status-fail'}">{results['statistics']['success_rate']}%</div>
            </div>
        </div>

        <h2>Expectation Results</h2>
"""

    # Add expectations
    for exp in results['expectations']:
        status_class = '' if exp['success'] else 'fail'
        badge_class = 'badge-pass' if exp['success'] else 'badge-fail'
        status_text = '✓ PASS' if exp['success'] else '✗ FAIL'

        html += f"""
        <div class="expectation {status_class}">
            <div class="expectation-header">
                <span class="expectation-type">{exp['expectation_type']}</span>
                <span class="badge {badge_class}">{status_text}</span>
            </div>
"""

        # Add expectation-specific details
        if 'column' in exp:
            html += f'<div class="details"><strong>Column:</strong> {exp["column"]}</div>'

        # Add metrics
        if 'percentage' in exp or 'observed_value' in exp or 'invalid_count' in exp:
            html += '<div class="details-grid">'

            if 'observed_value' in exp:
                html += f'''
                <div class="detail-item">
                    <div class="detail-label">Observed</div>
                    <div class="detail-value">{exp["observed_value"]}</div>
                </div>
'''

            if 'percentage' in exp:
                html += f'''
                <div class="detail-item">
                    <div class="detail-label">Percentage</div>
                    <div class="detail-value">{exp["percentage"]}%</div>
                </div>
'''

            if 'threshold' in exp:
                html += f'''
                <div class="detail-item">
                    <div class="detail-label">Threshold</div>
                    <div class="detail-value">{exp["threshold"]}%</div>
                </div>
'''

            if 'invalid_count' in exp:
                html += f'''
                <div class="detail-item">
                    <div class="detail-label">Invalid Count</div>
                    <div class="detail-value">{exp["invalid_count"]}</div>
                </div>
'''

            html += '</div>'

        # Add description if exists
        if 'description' in exp:
            html += f'<div class="details" style="margin-top: 10px;"><em>{exp["description"]}</em></div>'

        # Add severity badge
        html += f'<div class="details" style="margin-top: 5px;"><span class="badge badge-critical">{exp["severity"]} severity</span></div>'

        html += '</div>'

    # Close HTML
    html += f"""
        <div class="footer">
            Generated by Day 12 Data Quality Framework<br>
            Based on Great Expectations concepts<br>
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </body>
    </html>
"""

    # Save HTML
    html_path = results_json_path.parent.parent / "data_docs" / f"{results['dataset']}_report.html"
    html_path.parent.mkdir(exist_ok=True, parents=True)

    with open(html_path, 'w') as f:
        f.write(html)

    print(f"📄 HTML report generated: {html_path}")
    return html_path


if __name__ == "__main__":
    # Find latest validation results
    results_dir = DAY12_VALIDATION_RESULTS_DIR
    results_files = sorted(results_dir.glob("validation_*.json"))

    if results_files:
        latest_results = results_files[-1]
        print(f"📊 Generating HTML report from: {latest_results}")
        html_path = day12_generate_html_report(latest_results)
        print(f"✅ Report saved to: {html_path}")
        print(f"\n🌐 Open in browser: file://{html_path.absolute()}")
    else:
        print("❌ No validation results found. Run day12_VALIDATOR_cybersecurity.py first.")
