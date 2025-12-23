"""
Day 20 Data Export Script
Exports Day 09 property operations data to JSON format for portfolio visualization module
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

def day20_export_data():
    """Export Day 09 database to JSON for portfolio module"""

    # Connect to Day 09 database
    db_path = Path(__file__).parent.parent / 'day09' / 'data' / 'day09_property_operations.db'

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)

    print("✅ Connected to Day 09 database")

    # Export portfolio overview
    portfolio_overview_query = """
        SELECT
            AVG(day09_occupancy_rate_pct) as occupancy_rate,
            SUM(day09_total_revenue) as total_revenue,
            AVG(day09_avg_daily_rate) as average_daily_rate,
            AVG(day09_revpar) as revpar,
            COUNT(DISTINCT day09_property_id) as property_count
        FROM metrics_portfolio_public
    """

    portfolio_overview = conn.execute(portfolio_overview_query).fetchone()

    # Export revenue by day (last 90 days from latest date in data)
    revenue_by_day_query = """
        SELECT
            day09_check_in_date as date,
            SUM(day09_total_price) as revenue
        FROM fct_reservations_unified
        WHERE day09_check_in_date >= date((SELECT MAX(day09_check_in_date) FROM fct_reservations_unified), '-90 days')
        GROUP BY day09_check_in_date
        ORDER BY day09_check_in_date
    """

    revenue_by_day = conn.execute(revenue_by_day_query).fetchall()

    # Export occupancy by day (calculated from bookings - last 90 days from latest date in data)
    # For simplicity, we'll calculate daily occupancy as percentage of properties booked
    occupancy_by_day_query = """
        SELECT
            day09_check_in_date as date,
            COUNT(DISTINCT day09_property_id) * 100.0 /
                (SELECT COUNT(DISTINCT day09_property_id) FROM metrics_portfolio_public) as occupancy_pct
        FROM fct_reservations_unified
        WHERE day09_check_in_date >= date((SELECT MAX(day09_check_in_date) FROM fct_reservations_unified), '-90 days')
        GROUP BY day09_check_in_date
        ORDER BY day09_check_in_date
    """

    occupancy_by_day = conn.execute(occupancy_by_day_query).fetchall()

    # Export properties with their performance metrics
    properties_query = """
        SELECT DISTINCT
            day09_property_id,
            day09_occupancy_rate_pct,
            day09_total_revenue,
            day09_avg_daily_rate
        FROM metrics_portfolio_public
        ORDER BY day09_total_revenue DESC
        LIMIT 6
    """

    properties_data = conn.execute(properties_query).fetchall()

    # For each property, get recent bookings and platform stats
    properties_with_details = []

    for prop in properties_data:
        property_id = prop[0]

        # Get recent bookings for this property
        bookings_query = """
            SELECT
                day09_booking_id,
                day09_platform,
                day09_check_in_date,
                day09_num_guests,
                day09_total_price
            FROM fct_reservations_unified
            WHERE day09_property_id = ?
            ORDER BY day09_check_in_date DESC
            LIMIT 10
        """

        bookings = conn.execute(bookings_query, (property_id,)).fetchall()

        # Get platform stats for this property
        platform_stats_query = """
            SELECT
                day09_platform,
                COUNT(*) as bookings,
                SUM(day09_total_price) as revenue,
                AVG(day09_total_price) as avg_price
            FROM fct_reservations_unified
            WHERE day09_property_id = ?
            GROUP BY day09_platform
        """

        platform_stats = conn.execute(platform_stats_query, (property_id,)).fetchall()

        # Build platform stats dictionary
        platform_stats_dict = {}
        for stat in platform_stats:
            platform_name = stat[0].lower().replace(' ', '_')
            platform_stats_dict[platform_name] = {
                "bookings": stat[1],
                "revenue": round(stat[2], 2),
                "avg_price": round(stat[3], 2)
            }

        properties_with_details.append({
            "property_id": property_id,
            "property_name": f"Property {property_id}",  # Could be enhanced with actual names
            "occupancy_rate": round(prop[1], 1) if prop[1] else 0,
            "total_revenue": round(prop[2], 2) if prop[2] else 0,
            "average_price": round(prop[3], 2) if prop[3] else 0,
            "bookings": [
                {
                    "booking_id": booking[0],
                    "platform": booking[1],
                    "check_in": booking[2],
                    "guest_count": booking[3],
                    "total_price": round(booking[4], 2) if booking[4] else 0
                }
                for booking in bookings
            ],
            "platform_stats": platform_stats_dict
        })

    # Build final JSON structure
    data = {
        "portfolio_overview": {
            "occupancy_rate": round(portfolio_overview[0], 1) if portfolio_overview[0] else 0,
            "total_revenue": round(portfolio_overview[1], 2) if portfolio_overview[1] else 0,
            "average_daily_rate": round(portfolio_overview[2], 2) if portfolio_overview[2] else 0,
            "revpar": round(portfolio_overview[3], 2) if portfolio_overview[3] else 0,
            "property_count": portfolio_overview[4] if portfolio_overview[4] else 0
        },
        "revenue_by_day": [
            {"date": row[0], "revenue": round(row[1], 2) if row[1] else 0}
            for row in revenue_by_day
        ],
        "occupancy_by_day": [
            {"date": row[0], "occupancy_pct": round(row[1], 1) if row[1] else 0}
            for row in occupancy_by_day
        ],
        "properties": properties_with_details
    }

    # Save to output file (will be moved to Next.js public folder later)
    output_path = Path(__file__).parent / 'portfolio_data.json'

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Data exported successfully to {output_path}")
    print(f"\nPortfolio Summary:")
    print(f"  - Properties: {data['portfolio_overview']['property_count']}")
    print(f"  - Occupancy Rate: {data['portfolio_overview']['occupancy_rate']}%")
    print(f"  - Total Revenue: ${data['portfolio_overview']['total_revenue']:,.2f}")
    print(f"  - Average Daily Rate: ${data['portfolio_overview']['average_daily_rate']:.2f}")
    print(f"  - RevPAR: ${data['portfolio_overview']['revpar']:.2f}")
    print(f"  - Revenue data points: {len(data['revenue_by_day'])}")

    conn.close()

if __name__ == "__main__":
    day20_export_data()
