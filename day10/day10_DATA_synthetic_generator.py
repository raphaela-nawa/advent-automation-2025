"""
Day 10: Family Office Data Warehouse - Synthetic Data Generator

Generates synthetic family office data for 5 families with 100 assets
including 30 MFG operational assets (critical for Day 16 reuse).

All functions and variables use day10_ prefix for isolation.
"""

import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
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
    DAY10_VALUE_RANGES,
    DAY10_ASSET_COUNTS
)


def day10_create_database_connection():
    """Create SQLite database connection."""
    db_path = Path(DAY10_DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    print(f"✅ Database connection created: {DAY10_DATABASE_PATH}")
    return conn


def day10_generate_date_dimension(conn):
    """Generate date dimension with fiscal attributes."""
    print("\n📅 Generating date dimension...")

    dates = []
    current_date = DAY10_DATA_START_DATE

    while current_date <= DAY10_DATA_END_DATE:
        date_key = int(current_date.strftime("%Y%m%d"))

        # Calculate fiscal year (assuming calendar year = fiscal year)
        fiscal_year = current_date.year
        fiscal_quarter = (current_date.month - 1) // 3 + 1

        dates.append({
            "date_key": date_key,
            "full_date": current_date.strftime("%Y-%m-%d"),
            "year": current_date.year,
            "quarter": (current_date.month - 1) // 3 + 1,
            "month": current_date.month,
            "fiscal_quarter": fiscal_quarter,
            "fiscal_year": fiscal_year
        })

        current_date += timedelta(days=1)

    df_dates = pd.DataFrame(dates)
    df_dates.to_sql("dim_date", conn, if_exists="replace", index=False)

    print(f"   ✓ Generated {len(dates)} date records ({DAY10_DATA_START_DATE} to {DAY10_DATA_END_DATE})")
    return df_dates


def day10_generate_clients_dimension(conn):
    """Generate client (family) dimension."""
    print("\n👨‍👩‍👧‍👦 Generating clients dimension...")

    clients = []
    for idx, family in enumerate(DAY10_FAMILIES, start=1):
        clients.append({
            "client_key": idx,
            "client_id": family["client_id"],
            "client_name": family["client_name"],
            "client_type": family["client_type"]
        })

    df_clients = pd.DataFrame(clients)
    df_clients.to_sql("dim_clients", conn, if_exists="replace", index=False)

    print(f"   ✓ Generated {len(clients)} family clients")
    for client in clients:
        marker = "⭐" if "MFG" in client["client_name"] else "  "
        print(f"      {marker} {client['client_name']} ({client['client_type']})")

    return df_clients


def day10_generate_accounts_dimension(conn, df_clients):
    """Generate accounts dimension."""
    print("\n🏦 Generating accounts dimension...")

    accounts = []
    account_key = 1

    for _, client in df_clients.iterrows():
        client_id = client["client_id"]
        client_key = client["client_key"]

        # Get account names for this family
        account_names = DAY10_ACCOUNTS_PER_FAMILY.get(client_id, ["Investment Account"])

        for account_name in account_names:
            account_id = f"ACC_{client_id}_{account_key:03d}"

            accounts.append({
                "account_key": account_key,
                "account_id": account_id,
                "account_name": account_name,
                "account_type": "Operating" if "Operating" in account_name else "Investment",
                "parent_client_key": client_key
            })

            account_key += 1

    df_accounts = pd.DataFrame(accounts)
    df_accounts.to_sql("dim_accounts", conn, if_exists="replace", index=False)

    print(f"   ✓ Generated {len(accounts)} accounts")
    mfg_account = df_accounts[df_accounts["account_name"].str.contains("MFG", na=False)]
    if not mfg_account.empty:
        print(f"      ⭐ MFG Company Operating Account created (account_key={mfg_account.iloc[0]['account_key']})")

    return df_accounts


def day10_generate_financial_assets():
    """Generate 50 financial assets (stocks, bonds, funds)."""
    assets = []
    asset_key = 1

    # Sample ticker symbols
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

        assets.append({
            "asset_key": asset_key,
            "asset_id": f"FIN_{asset_key:03d}",
            "asset_name": name,
            "asset_class": "Equity",
            "asset_type": asset_type,
            "valid_from": DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            "valid_to": None,
            "is_current": True
        })

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

    for i, company in enumerate(companies, start=1):
        assets.append({
            "asset_key": asset_key,
            "asset_id": f"OP_{asset_key:03d}",
            "asset_name": f"{company} (Operating Stake)",
            "asset_class": "Operating Company",
            "asset_type": "Equity Stake",
            "valid_from": DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            "valid_to": None,
            "is_current": True
        })

        asset_key += 1

    return assets, asset_key


def day10_generate_mfg_assets(start_key):
    """Generate 30 MFG operational assets (CRITICAL FOR DAY 16)."""
    assets = []
    asset_key = start_key

    print("\n⭐ Generating MFG operational assets (CRITICAL FOR DAY 16)...")

    # Equipment assets (10)
    for equipment in DAY10_MFG_EQUIPMENT:
        assets.append({
            "asset_key": asset_key,
            "asset_id": equipment["asset_id"],
            "asset_name": equipment["asset_name"],
            "asset_class": "Equipment",
            "asset_type": equipment["asset_type"],
            "valid_from": DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            "valid_to": None,
            "is_current": True
        })
        asset_key += 1

    print(f"   ✓ Generated 10 Equipment assets (EQ_MFG_001 to EQ_MFG_010)")

    # IP assets (10)
    for ip_asset in DAY10_MFG_IP:
        assets.append({
            "asset_key": asset_key,
            "asset_id": ip_asset["asset_id"],
            "asset_name": ip_asset["asset_name"],
            "asset_class": "IP",
            "asset_type": ip_asset["asset_type"],
            "valid_from": DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            "valid_to": None,
            "is_current": True
        })
        asset_key += 1

    print(f"   ✓ Generated 10 IP assets (IP_MFG_001 to IP_MFG_010)")

    # Certification assets (10)
    for cert in DAY10_MFG_CERTIFICATIONS:
        assets.append({
            "asset_key": asset_key,
            "asset_id": cert["asset_id"],
            "asset_name": cert["asset_name"],
            "asset_class": "Certification",
            "asset_type": cert["asset_type"],
            "valid_from": DAY10_DATA_START_DATE.strftime("%Y-%m-%d"),
            "valid_to": None,
            "is_current": True
        })
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

    df_assets = pd.DataFrame(all_assets)
    df_assets.to_sql("dim_assets", conn, if_exists="replace", index=False)

    print(f"\n   ✅ Total assets generated: {len(all_assets)}")

    return df_assets


def day10_generate_fact_holdings(conn, df_clients, df_accounts, df_assets, df_dates):
    """Generate fact table with holdings data."""
    print("\n📊 Generating fact holdings...")

    holdings = []
    holding_key = 1

    # Get MFG Owner Family client and MFG Operating Account
    mfg_client = df_clients[df_clients["client_name"] == "MFG Owner Family"].iloc[0]
    mfg_account = df_accounts[
        (df_accounts["parent_client_key"] == mfg_client["client_key"]) &
        (df_accounts["account_name"].str.contains("MFG Company Operating", na=False))
    ].iloc[0]

    # Get monthly dates only (reduce fact table size)
    monthly_dates = df_dates[df_dates["full_date"].str.endswith("-01")].copy()

    print(f"   Generating holdings for {len(monthly_dates)} months...")

    for _, date_row in monthly_dates.iterrows():
        date_key = date_row["date_key"]

        # Assign assets to families
        for _, client in df_clients.iterrows():
            client_key = client["client_key"]
            client_name = client["client_name"]

            # Get accounts for this client
            client_accounts = df_accounts[df_accounts["parent_client_key"] == client_key]

            if client_name == "MFG Owner Family":
                # MFG Owner Family gets:
                # - MFG operational assets (in MFG Operating Account)
                # - Some financial assets (in other accounts)

                mfg_assets = df_assets[
                    df_assets["asset_id"].str.startswith(("EQ_MFG_", "IP_MFG_", "CERT_MFG_"))
                ]

                for _, asset in mfg_assets.iterrows():
                    # Determine market value based on asset class
                    if asset["asset_class"] == "Equipment":
                        base_value = next((e["market_value"] for e in DAY10_MFG_EQUIPMENT
                                          if e["asset_id"] == asset["asset_id"]), 100000)
                    elif asset["asset_class"] == "IP":
                        base_value = next((ip["market_value"] for ip in DAY10_MFG_IP
                                          if ip["asset_id"] == asset["asset_id"]), 200000)
                    else:  # Certification
                        base_value = next((c["market_value"] for c in DAY10_MFG_CERTIFICATIONS
                                          if c["asset_id"] == asset["asset_id"]), 10000)

                    # Add small variation over time
                    market_value = base_value * random.uniform(0.95, 1.05)

                    holdings.append({
                        "holding_key": holding_key,
                        "client_key": client_key,
                        "asset_key": asset["asset_key"],
                        "account_key": mfg_account["account_key"],
                        "date_key": date_key,
                        "quantity": 1.0,  # One unit for equipment/IP/certs
                        "market_value": round(market_value, 2),
                        "cost_basis": round(base_value, 2)
                    })
                    holding_key += 1

                # Add some financial assets to other MFG family accounts
                other_accounts = client_accounts[client_accounts["account_key"] != mfg_account["account_key"]]
                financial_assets = df_assets[df_assets["asset_class"] == "Equity"].sample(n=10)

                for _, asset in financial_assets.iterrows():
                    account = other_accounts.sample(n=1).iloc[0] if not other_accounts.empty else mfg_account

                    quantity = random.uniform(100, 10000)
                    price = random.uniform(50, 500)
                    market_value = quantity * price

                    holdings.append({
                        "holding_key": holding_key,
                        "client_key": client_key,
                        "asset_key": asset["asset_key"],
                        "account_key": account["account_key"],
                        "date_key": date_key,
                        "quantity": round(quantity, 2),
                        "market_value": round(market_value, 2),
                        "cost_basis": round(market_value * random.uniform(0.8, 1.2), 2)
                    })
                    holding_key += 1

            else:
                # Other families get financial and operating assets
                num_assets = random.randint(8, 15)
                available_assets = df_assets[
                    ~df_assets["asset_id"].str.startswith(("EQ_MFG_", "IP_MFG_", "CERT_MFG_"))
                ]

                if len(available_assets) < num_assets:
                    num_assets = len(available_assets)

                family_assets = available_assets.sample(n=num_assets)

                for _, asset in family_assets.iterrows():
                    account = client_accounts.sample(n=1).iloc[0]

                    if asset["asset_class"] == "Operating Company":
                        market_value = random.uniform(
                            DAY10_VALUE_RANGES["operating_stake_min"],
                            DAY10_VALUE_RANGES["operating_stake_max"]
                        )
                        quantity = random.uniform(10, 50)  # Percentage ownership
                    else:
                        quantity = random.uniform(100, 10000)
                        price = random.uniform(50, 500)
                        market_value = quantity * price

                    holdings.append({
                        "holding_key": holding_key,
                        "client_key": client_key,
                        "asset_key": asset["asset_key"],
                        "account_key": account["account_key"],
                        "date_key": date_key,
                        "quantity": round(quantity, 2),
                        "market_value": round(market_value, 2),
                        "cost_basis": round(market_value * random.uniform(0.8, 1.2), 2)
                    })
                    holding_key += 1

    df_holdings = pd.DataFrame(holdings)
    df_holdings.to_sql("fct_holdings", conn, if_exists="replace", index=False)

    print(f"   ✅ Generated {len(holdings):,} holding records")

    # Validate MFG assets in holdings
    mfg_holdings = df_holdings[df_holdings["account_key"] == mfg_account["account_key"]]
    print(f"   ✅ MFG operational assets in holdings: {len(mfg_holdings) // len(monthly_dates)} assets × {len(monthly_dates)} months")

    return df_holdings


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

        # Generate dimensions
        df_dates = day10_generate_date_dimension(conn)
        df_clients = day10_generate_clients_dimension(conn)
        df_accounts = day10_generate_accounts_dimension(conn, df_clients)
        df_assets = day10_generate_assets_dimension(conn)

        # Generate fact table
        df_holdings = day10_generate_fact_holdings(conn, df_clients, df_accounts, df_assets, df_dates)

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
