"""
Day 14: Local API Proxy for Querido Diário
Uses synthetic data because Cloudflare blocks automated API access (403 Forbidden)

Run this locally, then n8n calls localhost to get transport KPI data
"""

from flask import Flask, jsonify, request
from day14_SYNTHETIC_data_generator import day14_generate_synthetic_report
import os

app = Flask(__name__)

# Simple API key for basic security
API_KEY = os.getenv('DAY14_PROXY_API_KEY', 'day14-local-proxy-key')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'day14-api-proxy',
        'data_source': 'synthetic',
        'reason': 'Querido Diário API blocked by Cloudflare'
    })


@app.route('/kpis', methods=['GET'])
def get_kpis():
    """
    Fetch daily KPIs using synthetic data

    Query params:
    - days_back: Number of days to look back (default: 1)
    - api_key: Authentication key
    - regenerate: Force regenerate data (default: false)
    """
    # Simple API key check
    api_key = request.args.get('api_key', '')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get parameters
    days_back = int(request.args.get('days_back', 1))
    regenerate = request.args.get('regenerate', 'false').lower() == 'true'

    try:
        # Generate synthetic data
        # Each call generates fresh realistic data
        print(f"[API] Generating synthetic KPIs (days_back={days_back})")
        result = day14_generate_synthetic_report(
            days_back=days_back,
            save_to_file=True  # Always save for caching
        )

        print(f"[API] KPIs generated successfully:")
        print(f"  - New Regulations: {result['kpis']['new_regulations']}")
        print(f"  - Active Municipalities: {result['kpis']['active_municipalities']}")
        print(f"  - Compliance Mentions: {result['kpis']['compliance_mentions']}")
        print(f"  - Safety Incidents: {result['kpis']['safety_incidents']}")

        return jsonify(result)

    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Day 14 API Proxy Server (SYNTHETIC DATA)")
    print("=" * 60)
    print()
    print("⚠️  NOTE: Using SYNTHETIC data because:")
    print("    Querido Diário API is protected by Cloudflare")
    print("    and blocks automated requests (403 Forbidden)")
    print()
    print("✅  Synthetic data is:")
    print("    - Based on real API structure")
    print("    - Realistic transport regulation patterns")
    print("    - Perfect for portfolio demonstration")
    print()
    print("=" * 60)
    print(f"Running on: http://localhost:5014")
    print(f"API Key: {API_KEY}")
    print()
    print("Endpoints:")
    print("  GET /health")
    print("  GET /kpis?days_back=1&api_key=YOUR_KEY")
    print()
    print("Press CTRL+C to stop")
    print("=" * 60)

    # Run on port 5014 (avoid conflicts)
    app.run(host='0.0.0.0', port=5014, debug=False)
