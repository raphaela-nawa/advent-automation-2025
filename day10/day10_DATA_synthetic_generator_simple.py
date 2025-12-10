"""
Day 10: Family Office Data Warehouse - Synthetic Data Generator (Simple Version)

Generates synthetic family office data using only Python built-in libraries.
No pandas/numpy required - pure Python + sqlite3.

All functions and variables use day10_ prefix for isolation.
"""

import sqlite3
import random
from datetime import datetime, timedelta, date
from pathlib import Path
import sys

# Import configuration
from day10_CONFIG_settings import (
    DAY10_DATABASE_PATH,
    DAY10_DATA_START_DATE,
    DAY10_DATA_END_DATE,
    DAY10_FAMILIES,
    DAY10_MFG_EQUIPMENT,
    DAY10_MFG_IP,
    DAY10_MFG_CERTIFICATIONS,
    DAY10_ACCOUNTS_PER_FAMILY,
    DAY10_VALUE_RANGES
)


def day10_create_database_connection():
    """Create SQLite database connection."""
    db_path = Path(DAY10_DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing database to start fresh
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    print(f"✅ Database connection created: {DAY10_DATABASE_PATH}")
    return conn


def day10_create_tables(conn):
    """Create all star schema tables."""
    print("\n📋 Creating star schema tables...")

    cursor = conn.cursor()

    # Create tables directly (simpler and more reliable)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date DATE NOT NULL,
            year INTEGER NOT NULL,
            quarter INTEGER NOT NULL,
            month INTEGER NOT NULL,
            fiscal_quarter INTEGER NOT NULL,
            fiscal_year INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_clients (
            client_key INTEGER PRIMARY KEY,
            client_id VARCHAR(50) NOT NULL UNIQUE,
            client_name VARCHAR(200) NOT NULL,
            client_type VARCHAR(50) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_accounts (
            account_key INTEGER PRIMARY KEY,
            account_id VARCHAR(50) NOT NULL UNIQUE,
            account_name VARCHAR(200) NOT NULL,
            account_type VARCHAR(50) NOT NULL,
            parent_client_key INTEGER NOT NULL,
            FOREIGN KEY (parent_client_key) REFERENCES dim_clients(client_key)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_assets (
            asset_key INTEGER PRIMARY KEY,
            asset_id VARCHAR(50) NOT NULL,
            asset_name VARCHAR(200) NOT NULL,
            asset_class VARCHAR(50) NOT NULL,
            asset_type VARCHAR(50),
            valid_from DATE NOT NULL,
            valid_to DATE,
            is_current BOOLEAN NOT NULL DEFAULT TRUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fct_holdings (
            holding_key INTEGER PRIMARY KEY,
            client_key INTEGER NOT NULL,
            asset_key INTEGER NOT NULL,
            account_key INTEGER NOT NULL,
            date_key INTEGER NOT NULL,
            quantity DECIMAL(18, 4) NOT NULL,
            market_value DECIMAL(18, 2) NOT NULL,
            cost_basis DECIMAL(18, 2),
            FOREIGN KEY (client_key) REFERENCES dim_clients(client_key),
            FOREIGN KEY (asset_key) REFERENCES dim_assets(asset_key),
            FOREIGN KEY (account_key) REFERENCES dim_accounts(account_key),
            FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
        )
    """)

    conn.commit()
    print("   ✓ Star schema tables created")


def day10_generate_date_dimension(conn):
    """Generate date dimension with fiscal attributes."""
    print("\n📅 Generating date dimension...")

    cursor = conn.cursor()
    dates = []
    current_date = DAY10_DATA_START_DATE

    while current_date <= DAY10_DATA_END_DATE:
        date_key = int(current_date.strftime("%Y%m%d"))
        fiscal_year = current_date.year
        fiscal_quarter = (current_date.month - 1) // 3 + 1

        dates.append((
            date_key,
            current_date.strftime("%Y-%m-%d"),
            current_date.year,
            (current_date.month - 1) // 3 + 1,
            current_date.month,
            fiscal_quarter,
            fiscal_year
        ))

        current_date += timedelta(days=1)

    cursor.executemany("""
        INSERT INTO dim_date (date_key, full_date, year, quarter, month, fiscal_quarter, fiscal_year)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, dates)

    conn.commit()
    print(f"   ✓ Generated {len(dates)} date records ({DAY10_DATA_START_DATE} to {DAY10_DATA_END_DATE})")


def day10_generate_clients_dimension(conn):
    """Generate client (family) dimension."""
    print("\n👨‍👩‍👧‍👦 Generating clients dimension...")

    cursor = conn.cursor()
    clients = []

    for idx, family in enumerate(DAY10_FAMILIES, start=1):
        clients.append((
            idx,
            family["client_id"],
            family["client_name"],
            family["client_type"]
        ))

    cursor.executemany("""
        INSERT INTO dim_clients (client_key, client_id, client_name, client_type)
        VALUES (?, ?, ?, ?)
    """, clients)

    conn.commit()
    print(f"   ✓ Generated {len(clients)} family clients")
    for client in clients:
        marker = "⭐" if "MFG" in client[2] else "  "
        print(f"      {marker} {client[2]} ({client[3]})")


def day10_generate_accounts_dimension(conn):
    """Generate accounts dimension."""
    print("\n🏦 Generating accounts dimension...")

    cursor = conn.cursor()

    # Get clients
    cursor.execute("SELECT client_key, client_id FROM dim_clients")
    clients = cursor.fetchall()

    accounts = []
    account_key = 1

    for client_key, client_id in clients:
        account_names = DAY10_ACCOUNTS_PER_FAMILY.get(client_id, ["Investment Account"])

        for account_name in account_names:
            account_id = f"ACC_{client_id}_{account_key:03d}"
            account_type = "Operating" if "Operating" in account_name else "Investment"

            accounts.append((
                account_key,
                account_id,
                account_name,
                account_type,
                client_key
            ))

            account_key += 1

    cursor.executemany("""
        INSERT INTO dim_accounts (account_key, account_id, account_name, account_type, parent_client_key)
        VALUES (?, ?, ?, ?, ?)
    """, accounts)

    conn.commit()
    print(f"   ✓ Generated {len(accounts)} accounts")

    # Find MFG account
    cursor.execute("SELECT account_key FROM dim_accounts WHERE account_name LIKE '%MFG%'")
    mfg_account = cursor.fetchone()
    if mfg_account:
        print(f"      ⭐ MFG Company Operating Account created (account_key={mfg_account[0]})")


def day10_generate_financial_assets():
    """Generate 50 financial assets."""
    assets = []
    asset_key = 1

    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "BAC", "GS",
               "VOO", "VTI", "SPY", "QQQ", "IVV", "AGG", "BND", "LQD", "HYG", "EMB"]

    for i in range(50):
        ticker = random.choice(tickers)
        asset_type = random.choice(["Stock", "Bond", "Fund", "ETF"])

        if asset_type == "Stock":
            name = f"{ticker} Common Stock"
        elif asset_type == "Bond":
            name = f"{ticker} Corporate Bond"
        elif asset_type == "Fund":
            name = f"{ticker} Mutual Fund"
        else:
            name = f"{ticker} ETF"

        assets.append((
            asset_key,
            f"FIN_{asset_key:03d}",
            name,
            "Equity",
            asset_type,
            DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            None,
            1  # is_current = TRUE
        ))

        asset_key += 1

    return assets, asset_key


def day10_generate_operating_stakes(start_key):
    """Generate 20 operating company stakes."""
    assets = []
    asset_key = start_key

    companies = [
        "European Tech Ventures", "Latin American Holdings", "Asian Manufacturing Corp",
        "African Agriculture Group", "North American Real Estate Trust", "European Logistics",
        "Tech Startup Portfolio", "Renewable Energy Fund", "Healthcare Services Group",
        "E-Commerce Platform", "Financial Services Holding", "Media & Entertainment Group",
        "Hospitality Chain", "Education Technology", "Biotech Research Lab",
        "Clean Energy Infrastructure", "Telecom Services", "Aerospace Components",
        "Food & Beverage Group", "Automotive Parts Supplier"
    ]

    for company in companies:
        assets.append((
            asset_key,
            f"OP_{asset_key:03d}",
            f"{company} (Operating Stake)",
            "Operating Company",
            "Equity Stake",
            DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            None,
            1
        ))

        asset_key += 1

    return assets, asset_key


def day10_generate_mfg_assets(start_key):
    """Generate 30 MFG operational assets (CRITICAL FOR DAY 16)."""
    assets = []
    asset_key = start_key

    print("\n⭐ Generating MFG operational assets (CRITICAL FOR DAY 16)...")

    # Equipment assets (10)
    for equipment in DAY10_MFG_EQUIPMENT:
        assets.append((
            asset_key,
            equipment["asset_id"],
            equipment["asset_name"],
            "Equipment",
            equipment["asset_type"],
            DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            None,
            1
        ))
        asset_key += 1

    print(f"   ✓ Generated 10 Equipment assets (EQ_MFG_001 to EQ_MFG_010)")

    # IP assets (10)
    for ip_asset in DAY10_MFG_IP:
        assets.append((
            asset_key,
            ip_asset["asset_id"],
            ip_asset["asset_name"],
            "IP",
            ip_asset["asset_type"],
            DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            None,
            1
        ))
        asset_key += 1

    print(f"   ✓ Generated 10 IP assets (IP_MFG_001 to IP_MFG_010)")

    # Certification assets (10)
    for cert in DAY10_MFG_CERTIFICATIONS:
        assets.append((
            asset_key,
            cert["asset_id"],
            cert["asset_name"],
            "Certification",
            cert["asset_type"],
            DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            None,
            1
        ))
        asset_key += 1

    print(f"   ✓ Generated 10 Certification assets (CERT_MFG_001 to CERT_MFG_010)")
    print(f"   ✅ Total MFG assets: 30 (ready for Day 16 reuse)")

    return assets, asset_key


def day10_generate_assets_dimension(conn):
    """Generate complete assets dimension (100 assets)."""
    print("\n💰 Generating assets dimension...")

    all_assets = []

    # Financial assets (50)
    financial, next_key = day10_generate_financial_assets()
    all_assets.extend(financial)
    print(f"   ✓ Generated 50 financial assets")

    # Operating stakes (20)
    operating, next_key = day10_generate_operating_stakes(next_key)
    all_assets.extend(operating)
    print(f"   ✓ Generated 20 operating company stakes")

    # MFG operational assets (30)
    mfg_assets, next_key = day10_generate_mfg_assets(next_key)
    all_assets.extend(mfg_assets)

    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO dim_assets (asset_key, asset_id, asset_name, asset_class, asset_type, valid_from, valid_to, is_current)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, all_assets)

    conn.commit()
    print(f"\n   ✅ Total assets generated: {len(all_assets)}")


def day10_generate_fact_holdings(conn):
    """Generate fact table with holdings data."""
    print("\n📊 Generating fact holdings...")

    cursor = conn.cursor()

    # Get MFG Owner Family client and MFG Operating Account
    cursor.execute("SELECT client_key FROM dim_clients WHERE client_name = 'MFG Owner Family'")
    mfg_client = cursor.fetchone()
    if not mfg_client:
        print("ERROR: MFG Owner Family not found!")
        return
    mfg_client_key = mfg_client[0]

    cursor.execute("""
        SELECT account_key FROM dim_accounts
        WHERE parent_client_key = ? AND account_name LIKE '%MFG Company Operating%'
    """, (mfg_client_key,))
    mfg_account = cursor.fetchone()
    if not mfg_account:
        print("ERROR: MFG Operating Account not found!")
        return
    mfg_account_key = mfg_account[0]

    # Get all clients, accounts, assets, and monthly dates
    cursor.execute("SELECT client_key, client_name FROM dim_clients")
    clients = cursor.fetchall()

    cursor.execute("SELECT date_key FROM dim_date WHERE full_date LIKE '%-01' ORDER BY date_key")
    monthly_dates = [row[0] for row in cursor.fetchall()]

    print(f"   Generating holdings for {len(monthly_dates)} months...")

    holdings = []
    holding_key = 1

    for date_key in monthly_dates:
        for client_key, client_name in clients:
            if client_name == "MFG Owner Family":
                # MFG Owner Family gets MFG operational assets
                cursor.execute("""
                    SELECT asset_key, asset_id, asset_class FROM dim_assets
                    WHERE (asset_id LIKE 'EQ_MFG_%' OR asset_id LIKE 'IP_MFG_%' OR asset_id LIKE 'CERT_MFG_%')
                      AND is_current = 1
                """)
                mfg_assets = cursor.fetchall()

                for asset_key, asset_id, asset_class in mfg_assets:
                    # Get base value
                    if asset_class == "Equipment":
                        base_value = next((e["market_value"] for e in DAY10_MFG_EQUIPMENT
                                         if e["asset_id"] == asset_id), 100000)
                    elif asset_class == "IP":
                        base_value = next((ip["market_value"] for ip in DAY10_MFG_IP
                                         if ip["asset_id"] == asset_id), 200000)
                    else:  # Certification
                        base_value = next((c["market_value"] for c in DAY10_MFG_CERTIFICATIONS
                                         if c["asset_id"] == asset_id), 10000)

                    market_value = base_value * random.uniform(0.95, 1.05)

                    holdings.append((
                        holding_key,
                        client_key,
                        asset_key,
                        mfg_account_key,
                        date_key,
                        1.0,  # quantity
                        round(market_value, 2),
                        round(base_value, 2)
                    ))
                    holding_key += 1

                # Add some financial assets to other MFG accounts
                cursor.execute("""
                    SELECT account_key FROM dim_accounts
                    WHERE parent_client_key = ? AND account_key != ?
                    LIMIT 1
                """, (client_key, mfg_account_key))
                other_account = cursor.fetchone()

                if other_account:
                    cursor.execute("SELECT asset_key FROM dim_assets WHERE asset_class = 'Equity' LIMIT 10")
                    financial_assets = cursor.fetchall()

                    for (asset_key,) in financial_assets:
                        quantity = random.uniform(100, 10000)
                        price = random.uniform(50, 500)
                        market_value = quantity * price

                        holdings.append((
                            holding_key,
                            client_key,
                            asset_key,
                            other_account[0],
                            date_key,
                            round(quantity, 2),
                            round(market_value, 2),
                            round(market_value * random.uniform(0.8, 1.2), 2)
                        ))
                        holding_key += 1

            else:
                # Other families get financial and operating assets
                num_assets = random.randint(8, 15)

                cursor.execute("""
                    SELECT asset_key, asset_class FROM dim_assets
                    WHERE NOT (asset_id LIKE 'EQ_MFG_%' OR asset_id LIKE 'IP_MFG_%' OR asset_id LIKE 'CERT_MFG_%')
                      AND is_current = 1
                    ORDER BY RANDOM()
                    LIMIT ?
                """, (num_assets,))
                family_assets = cursor.fetchall()

                cursor.execute("SELECT account_key FROM dim_accounts WHERE parent_client_key = ? LIMIT 1", (client_key,))
                account = cursor.fetchone()
                if not account:
                    continue
                account_key = account[0]

                for asset_key, asset_class in family_assets:
                    if asset_class == "Operating Company":
                        market_value = random.uniform(
                            DAY10_VALUE_RANGES["operating_stake_min"],
                            DAY10_VALUE_RANGES["operating_stake_max"]
                        )
                        quantity = random.uniform(10, 50)
                    else:
                        quantity = random.uniform(100, 10000)
                        price = random.uniform(50, 500)
                        market_value = quantity * price

                    holdings.append((
                        holding_key,
                        client_key,
                        asset_key,
                        account_key,
                        date_key,
                        round(quantity, 2),
                        round(market_value, 2),
                        round(market_value * random.uniform(0.8, 1.2), 2)
                    ))
                    holding_key += 1

    cursor.executemany("""
        INSERT INTO fct_holdings (holding_key, client_key, asset_key, account_key, date_key, quantity, market_value, cost_basis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, holdings)

    conn.commit()
    print(f"   ✅ Generated {len(holdings):,} holding records")


def day10_validate_data(conn):
    """Validate generated data meets requirements."""
    print("\n✅ Validating generated data...")

    cursor = conn.cursor()
    validations = []

    # 1. Check total assets = 100
    cursor.execute("SELECT COUNT(*) FROM dim_assets WHERE is_current = 1")
    asset_count = cursor.fetchone()[0]
    validations.append(("Total assets", asset_count, 100, asset_count == 100))

    # 2. Check MFG assets = 30
    cursor.execute("""
        SELECT COUNT(*) FROM dim_assets
        WHERE is_current = 1
        AND (asset_id LIKE 'EQ_MFG_%' OR asset_id LIKE 'IP_MFG_%' OR asset_id LIKE 'CERT_MFG_%')
    """)
    mfg_count = cursor.fetchone()[0]
    validations.append(("MFG operational assets", mfg_count, 30, mfg_count == 30))

    # 3. Check families = 5
    cursor.execute("SELECT COUNT(*) FROM dim_clients")
    family_count = cursor.fetchone()[0]
    validations.append(("Family clients", family_count, 5, family_count == 5))

    # 4. Check date range
    cursor.execute("SELECT COUNT(*) FROM dim_date")
    date_count = cursor.fetchone()[0]
    validations.append(("Date records", date_count, ">700", date_count > 700))

    # 5. Check holdings exist
    cursor.execute("SELECT COUNT(*) FROM fct_holdings")
    holding_count = cursor.fetchone()[0]
    validations.append(("Holdings records", holding_count, ">0", holding_count > 0))

    # Print validation results
    all_passed = True
    for name, actual, expected, passed in validations:
        status = "✅" if passed else "❌"
        print(f"   {status} {name}: {actual} (expected: {expected})")
        if not passed:
            all_passed = False

    return all_passed


def main():
    """Main execution function."""
    print("=" * 80)
    print("DAY 10: FAMILY OFFICE DATA WAREHOUSE - SYNTHETIC DATA GENERATOR")
    print("=" * 80)

    try:
        # Create database connection
        conn = day10_create_database_connection()

        # Create tables
        day10_create_tables(conn)

        # Generate dimensions
        day10_generate_date_dimension(conn)
        day10_generate_clients_dimension(conn)
        day10_generate_accounts_dimension(conn)
        day10_generate_assets_dimension(conn)

        # Generate fact table
        day10_generate_fact_holdings(conn)

        # Validate
        validation_passed = day10_validate_data(conn)

        # Close connection
        conn.close()

        if validation_passed:
            print("\n" + "=" * 80)
            print("✅ SUCCESS: Family Office Data Warehouse created successfully!")
            print(f"   Database: {DAY10_DATABASE_PATH}")
            print(f"   Ready for SQL models and queries")
            print(f"   MFG assets ready for Day 16 reuse ⭐")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("⚠️  WARNING: Some validations failed. Review output above.")
            print("=" * 80)
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
