"""
Day 14: Transport KPI Automation - Complete Python Solution
Andrea - Policy & Transport Analytics

This script replaces the n8n workflow with a pure Python solution.
Runs daily to fetch transport regulations and send email reports.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from day14_HELPER_querido_diario import day14_fetch_daily_kpis
import os
from dotenv import load_dotenv

# Load environment variables from config/.env
import sys
from pathlib import Path
root_dir = Path(__file__).parent.parent
env_path = root_dir / 'config' / '.env'
load_dotenv(dotenv_path=env_path)


def build_html_email(kpis_data):
    """Build professional HTML email from KPI data."""

    kpis = kpis_data['kpis']
    date_range = kpis_data['date_range']

    # Calculate period days
    since_date = datetime.strptime(date_range['since'], '%Y-%m-%d')
    until_date = datetime.strptime(date_range['until'], '%Y-%m-%d')
    period_days = (until_date - since_date).days

    # Build city details
    city_details = []
    raw_transport = kpis_data['raw_data']['transport']

    for city_name, data in raw_transport.items():
        count = data.get('total_gazettes', 0)
        if count > 0:
            city_details.append({
                'name': city_name.replace('_', ' '),
                'regulations': count
            })

    # Sort by regulation count
    city_details.sort(key=lambda x: x['regulations'], reverse=True)

    # Generate city badges HTML
    if city_details:
        city_badges_html = ''.join([
            f'<span class="city-badge">{c["name"]} ({c["regulations"]})</span>'
            for c in city_details
        ])
    else:
        city_badges_html = '<span class="city-badge">No active cities</span>'

    # Generate dynamic insights
    insights = []

    if kpis['new_regulations'] == 0:
        insights.append('📊 Nenhuma regulamentação de transporte publicada no período')
    elif kpis['new_regulations'] > 50:
        insights.append('📈 Volume alto de regulamentações publicadas')
    elif kpis['new_regulations'] > 20:
        insights.append('📊 Atividade regulatória moderada')

    if kpis['active_municipalities'] >= 7:
        insights.append('🌟 Atividade distribuída em múltiplos municípios')
    elif kpis['active_municipalities'] > 0:
        insights.append(f'📍 {kpis["active_municipalities"]} município(s) ativo(s)')

    if kpis['safety_incidents'] > 20:
        insights.append('⚠️ Volume alto de menções a segurança')
    elif kpis['safety_incidents'] > 0:
        insights.append(f'⚠️ {kpis["safety_incidents"]} menção(ões) a segurança')

    if kpis['compliance_mentions'] > 50:
        insights.append('✅ Foco significativo em conformidade')
    elif kpis['compliance_mentions'] > 0:
        insights.append(f'✅ {kpis["compliance_mentions"]} menção(ões) a conformidade')

    if not insights:
        insights.append('📊 Período sem atividade regulatória')

    insights_html = ''.join([f'<li>{i}</li>' for i in insights])

    # Build complete HTML
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      margin: 0;
      padding: 40px 20px;
    }}
    .email-container {{
      max-width: 700px;
      margin: 0 auto;
      background: white;
      border-radius: 16px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
    }}
    .header {{
      background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
      color: white;
      padding: 40px 30px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0 0 10px 0;
      font-size: 32px;
      font-weight: 700;
    }}
    .header p {{
      margin: 5px 0;
      opacity: 0.9;
      font-size: 16px;
    }}
    .content {{
      padding: 40px 30px;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 30px;
    }}
    .kpi-card {{
      background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
      padding: 25px;
      border-radius: 12px;
      text-align: center;
      border: 2px solid #d1d5db;
    }}
    .kpi-value {{
      font-size: 42px;
      font-weight: 700;
      color: #1e3a8a;
      margin: 10px 0;
    }}
    .kpi-label {{
      font-size: 14px;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 600;
    }}
    .section-title {{
      font-size: 20px;
      color: #1f2937;
      margin: 30px 0 15px 0;
      font-weight: 600;
      border-bottom: 3px solid #3b82f6;
      padding-bottom: 10px;
    }}
    .city-badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 30px;
    }}
    .city-badge {{
      background: #dbeafe;
      color: #1e40af;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid #93c5fd;
    }}
    .insights {{
      background: #fef3c7;
      border-left: 4px solid #f59e0b;
      padding: 20px;
      border-radius: 8px;
      margin-top: 20px;
    }}
    .insights h3 {{
      margin: 0 0 10px 0;
      color: #92400e;
    }}
    .insights ul {{
      margin: 10px 0 0 0;
      padding-left: 20px;
    }}
    .insights li {{
      margin: 8px 0;
      color: #78350f;
      font-weight: 500;
    }}
    .footer {{
      background: #f9fafb;
      padding: 25px 30px;
      text-align: center;
      color: #6b7280;
      font-size: 13px;
      border-top: 1px solid #e5e7eb;
    }}
    .footer a {{
      color: #3b82f6;
      text-decoration: none;
    }}
    @media (max-width: 600px) {{
      .kpi-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>🚦 Transport KPI Report</h1>
      <p>Brazilian Municipal Regulations</p>
      <p><strong>{date_range['since']}</strong> to <strong>{date_range['until']}</strong></p>
      <p>({period_days} days)</p>
    </div>

    <div class="content">
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">New Regulations</div>
          <div class="kpi-value">{kpis['new_regulations']}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Active Municipalities</div>
          <div class="kpi-value">{kpis['active_municipalities']}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Compliance Mentions</div>
          <div class="kpi-value">{kpis['compliance_mentions']}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Safety Incidents</div>
          <div class="kpi-value">{kpis['safety_incidents']}</div>
        </div>
      </div>

      <h2 class="section-title">📍 Active Municipalities</h2>
      <div class="city-badges">
        {city_badges_html}
      </div>

      <div class="insights">
        <h3>💡 Key Insights</h3>
        <ul>
          {insights_html}
        </ul>
      </div>
    </div>

    <div class="footer">
      <p><strong>Day 14: Transport Regulatory KPIs</strong></p>
      <p>Data source: <a href="https://queridodiario.ok.org.br">Querido Diário</a> (Brazilian Municipal Official Gazettes)</p>
      <p>Report generated: {date_range['until']} • Automated with Python</p>
    </div>
  </div>
</body>
</html>
"""

    subject = f"🚦 Transport KPI Report - {date_range['until']} ({kpis['new_regulations']} regulations, {kpis['active_municipalities']} cities)"

    return subject, html_body


def send_email(subject, html_body, from_email, to_email, smtp_password):
    """Send HTML email via Gmail SMTP."""

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Attach HTML
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)

    # Send via Gmail SMTP
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, smtp_password)
            server.send_message(msg)

        print(f"✅ Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def main():
    """Main automation function."""

    print("=" * 60)
    print("DAY 14: Transport KPI Automation")
    print("=" * 60)

    # Configuration
    DAYS_BACK = 30
    FROM_EMAIL = os.getenv('DAY14_SMTP_USER', 'your-email@gmail.com')
    TO_EMAIL = os.getenv('DAY14_SMTP_TO', FROM_EMAIL)
    SMTP_PASSWORD = os.getenv('DAY14_SMTP_PASSWORD', '')

    if not SMTP_PASSWORD:
        print("\n⚠️  DAY14_SMTP_PASSWORD not found in config/.env file!")
        print("Please add to config/.env:")
        print("  DAY14_SMTP_USER=your-email@gmail.com")
        print("  DAY14_SMTP_PASSWORD=your-gmail-app-password")
        print("  DAY14_SMTP_TO=your-email@gmail.com")
        return

    # Step 1: Fetch KPIs
    print(f"\n📊 Fetching KPIs (last {DAYS_BACK} days)...")
    kpis_data = day14_fetch_daily_kpis(days_back=DAYS_BACK)

    print("\n✅ KPI Summary:")
    print(f"   - New Regulations: {kpis_data['kpis']['new_regulations']}")
    print(f"   - Active Municipalities: {kpis_data['kpis']['active_municipalities']}")
    print(f"   - Compliance Mentions: {kpis_data['kpis']['compliance_mentions']}")
    print(f"   - Safety Incidents: {kpis_data['kpis']['safety_incidents']}")

    # Step 2: Build email
    print("\n📧 Building HTML email...")
    subject, html_body = build_html_email(kpis_data)

    # Step 3: Send email
    print(f"\n📤 Sending email to {TO_EMAIL}...")
    success = send_email(subject, html_body, FROM_EMAIL, TO_EMAIL, SMTP_PASSWORD)

    if success:
        print("\n" + "=" * 60)
        print("✅ AUTOMATION COMPLETE!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ AUTOMATION FAILED - Check SMTP settings")
        print("=" * 60)


if __name__ == '__main__':
    main()
