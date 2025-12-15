"""
Day 14: Local API Proxy for Querido Diário
Fetches real data from Querido Diário API (Brazilian government gazettes)

Run this locally, then n8n calls localhost to get transport KPI data
"""

from flask import Flask, jsonify, request
from day14_HELPER_querido_diario import day14_fetch_daily_kpis
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
        'data_source': 'querido_diario_api',
        'api_url': 'https://api.queridodiario.ok.org.br'
    })


@app.route('/kpis', methods=['GET'])
def get_kpis():
    """
    Fetch daily KPIs from real Querido Diário API

    Query params:
    - days_back: Number of days to look back (default: 15)
    - api_key: Authentication key
    """
    # Simple API key check
    api_key = request.args.get('api_key', '')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get parameters (default to 15 days for better results)
    days_back = int(request.args.get('days_back', 15))

    try:
        # Fetch real data from Querido Diário API
        print(f"[API] Fetching real KPIs from Querido Diário (days_back={days_back})")
        result = day14_fetch_daily_kpis(days_back=days_back)

        print(f"[API] KPIs fetched successfully:")
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
    print("Day 14 API Proxy Server (REAL DATA)")
    print("=" * 60)
    print()
    print("✅  Using REAL data from:")
    print("    Querido Diário API (Brazilian Government)")
    print("    https://api.queridodiario.ok.org.br")
    print()
    print("📊  Monitoring:")
    print("    - 10 major Brazilian cities")
    print("    - Transport & mobility regulations")
    print("    - Compliance mentions")
    print("    - Safety incidents")
    print()
    print("=" * 60)
    print(f"Running on: http://localhost:5014")
    print(f"API Key: {API_KEY}")
    print()
    print("Endpoints:")
    print("  GET /health")
    print("  GET /kpis?days_back=15&api_key=YOUR_KEY")
    print()
    print("Note: Using days_back=15 for better results")
    print("      (municipalities don't publish daily)")
    print()
    print("Press CTRL+C to stop")
    print("=" * 60)

    # Run on port 5014 (avoid conflicts)
    app.run(host='0.0.0.0', port=5014, debug=False)
