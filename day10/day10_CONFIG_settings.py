"""
Day 10: Family Office Data Warehouse - Configuration Settings

Configuration for synthetic data generation and business logic.
All settings use DAY10_ prefix for isolation.
"""

from datetime import datetime, date

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DAY10_DATABASE_PATH = "data/day10_family_office_dw.db"

# ============================================================================
# SYNTHETIC DATA PARAMETERS
# ============================================================================

# Time Range
DAY10_DATA_START_DATE = date(2023, 1, 1)
DAY10_DATA_END_DATE = date(2024, 12, 31)  # 24 months
DAY10_DATA_FREQUENCY = "monthly"  # Holdings snapshot frequency

# Family Office Clients
DAY10_FAMILIES = [
    {
        "client_id": "FAM_001",
        "client_name": "Smith Family",
        "client_type": "Traditional Investments",
        "description": "Traditional investments (stocks, bonds, funds)"
    },
    {
        "client_id": "FAM_002",
        "client_name": "Johnson Family",
        "client_type": "Real Estate Focus",
        "description": "Real estate focused portfolio"
    },
    {
        "client_id": "FAM_003",
        "client_name": "MFG Owner Family",
        "client_type": "Manufacturing Owner",
        "description": "Owns European manufacturing company - CRITICAL FOR DAY 16"
    },
    {
        "client_id": "FAM_004",
        "client_name": "Lee Family",
        "client_type": "Technology Investments",
        "description": "Technology sector investments"
    },
    {
        "client_id": "FAM_005",
        "client_name": "Garcia Family",
        "client_type": "Diversified",
        "description": "Diversified portfolio across asset classes"
    }
]

# Asset Distribution (Total: 100 assets)
DAY10_ASSET_COUNTS = {
    "financial": 50,  # Stocks, bonds, funds
    "operating_stakes": 20,  # Operating company ownership stakes
    "mfg_equipment": 10,  # MFG company equipment (CRITICAL FOR DAY 16)
    "mfg_ip": 10,  # MFG company IP assets (CRITICAL FOR DAY 16)
    "mfg_certifications": 10  # MFG company certifications (CRITICAL FOR DAY 16)
}

# ============================================================================
# MFG COMPANY OPERATIONAL ASSETS (CRITICAL FOR DAY 16)
# ============================================================================

# Equipment Assets (10 total)
DAY10_MFG_EQUIPMENT = [
    {
        "asset_id": "EQ_MFG_001",
        "asset_name": "CNC Machine Haas VF-2",
        "location": "UK",
        "market_value": 85000,
        "asset_type": "CNC Machine"
    },
    {
        "asset_id": "EQ_MFG_002",
        "asset_name": "3D Printer HP Multi Jet Fusion",
        "location": "Netherlands",
        "market_value": 120000,
        "asset_type": "3D Printer"
    },
    {
        "asset_id": "EQ_MFG_003",
        "asset_name": "Injection Molding Machine",
        "location": "Germany",
        "market_value": 200000,
        "asset_type": "Molding Machine"
    },
    {
        "asset_id": "EQ_MFG_004",
        "asset_name": "Laser Cutting System Trumpf",
        "location": "France",
        "market_value": 150000,
        "asset_type": "Laser Cutter"
    },
    {
        "asset_id": "EQ_MFG_005",
        "asset_name": "Automated Assembly Line",
        "location": "Poland",
        "market_value": 450000,
        "asset_type": "Assembly System"
    },
    {
        "asset_id": "EQ_MFG_006",
        "asset_name": "Quality Inspection System Zeiss",
        "location": "UK",
        "market_value": 95000,
        "asset_type": "QC Equipment"
    },
    {
        "asset_id": "EQ_MFG_007",
        "asset_name": "Robotic Welding Cell Fanuc",
        "location": "Germany",
        "market_value": 180000,
        "asset_type": "Robotic Welder"
    },
    {
        "asset_id": "EQ_MFG_008",
        "asset_name": "CNC Lathe Machine DMG Mori",
        "location": "Czech Republic",
        "market_value": 110000,
        "asset_type": "CNC Lathe"
    },
    {
        "asset_id": "EQ_MFG_009",
        "asset_name": "Material Handling AGV System",
        "location": "Netherlands",
        "market_value": 75000,
        "asset_type": "AGV System"
    },
    {
        "asset_id": "EQ_MFG_010",
        "asset_name": "Powder Coating System",
        "location": "Spain",
        "market_value": 65000,
        "asset_type": "Coating System"
    }
]

# IP Assets (10 total)
DAY10_MFG_IP = [
    {
        "asset_id": "IP_MFG_001",
        "asset_name": "Patent EP12345 - Rapid Tooling Method",
        "jurisdiction": "European Union",
        "market_value": 500000,
        "asset_type": "Patent"
    },
    {
        "asset_id": "IP_MFG_002",
        "asset_name": "Trademark MFG QuickFab",
        "jurisdiction": "European Union",
        "market_value": 50000,
        "asset_type": "Trademark"
    },
    {
        "asset_id": "IP_MFG_003",
        "asset_name": "Patent GB98765 - Lightweight Composite Material",
        "jurisdiction": "United Kingdom",
        "market_value": 350000,
        "asset_type": "Patent"
    },
    {
        "asset_id": "IP_MFG_004",
        "asset_name": "Design Patent DE54321 - Modular Housing System",
        "jurisdiction": "Germany",
        "market_value": 120000,
        "asset_type": "Design Patent"
    },
    {
        "asset_id": "IP_MFG_005",
        "asset_name": "Trade Secret - Precision Coating Formula",
        "jurisdiction": "Multi-jurisdictional",
        "market_value": 200000,
        "asset_type": "Trade Secret"
    },
    {
        "asset_id": "IP_MFG_006",
        "asset_name": "Patent FR11223 - Energy Efficient Process",
        "jurisdiction": "France",
        "market_value": 280000,
        "asset_type": "Patent"
    },
    {
        "asset_id": "IP_MFG_007",
        "asset_name": "Copyright - CAD Software Suite",
        "jurisdiction": "European Union",
        "market_value": 80000,
        "asset_type": "Copyright"
    },
    {
        "asset_id": "IP_MFG_008",
        "asset_name": "Patent NL33445 - Automated Quality Control System",
        "jurisdiction": "Netherlands",
        "market_value": 310000,
        "asset_type": "Patent"
    },
    {
        "asset_id": "IP_MFG_009",
        "asset_name": "Trademark MFG ProTech",
        "jurisdiction": "United Kingdom",
        "market_value": 45000,
        "asset_type": "Trademark"
    },
    {
        "asset_id": "IP_MFG_010",
        "asset_name": "Patent ES77889 - Sustainable Manufacturing Process",
        "jurisdiction": "Spain",
        "market_value": 260000,
        "asset_type": "Patent"
    }
]

# Certification Assets (10 total)
DAY10_MFG_CERTIFICATIONS = [
    {
        "asset_id": "CERT_MFG_001",
        "asset_name": "CE Marking - Product Line A",
        "jurisdiction": "European Union",
        "market_value": 10000,
        "asset_type": "Product Certification"
    },
    {
        "asset_id": "CERT_MFG_002",
        "asset_name": "ISO 9001 - UK Facility",
        "jurisdiction": "United Kingdom",
        "market_value": 15000,
        "asset_type": "Quality Management"
    },
    {
        "asset_id": "CERT_MFG_003",
        "asset_name": "REACH Compliance - DE Operations",
        "jurisdiction": "Germany",
        "market_value": 8000,
        "asset_type": "Regulatory Compliance"
    },
    {
        "asset_id": "CERT_MFG_004",
        "asset_name": "ISO 14001 - Environmental Management",
        "jurisdiction": "European Union",
        "market_value": 12000,
        "asset_type": "Environmental"
    },
    {
        "asset_id": "CERT_MFG_005",
        "asset_name": "ISO 45001 - Occupational Health & Safety",
        "jurisdiction": "European Union",
        "market_value": 11000,
        "asset_type": "Safety"
    },
    {
        "asset_id": "CERT_MFG_006",
        "asset_name": "CE Marking - Product Line B",
        "jurisdiction": "European Union",
        "market_value": 9000,
        "asset_type": "Product Certification"
    },
    {
        "asset_id": "CERT_MFG_007",
        "asset_name": "ISO 27001 - Information Security",
        "jurisdiction": "Multi-jurisdictional",
        "market_value": 13000,
        "asset_type": "Cybersecurity"
    },
    {
        "asset_id": "CERT_MFG_008",
        "asset_name": "RoHS Compliance Certification",
        "jurisdiction": "European Union",
        "market_value": 7000,
        "asset_type": "Regulatory Compliance"
    },
    {
        "asset_id": "CERT_MFG_009",
        "asset_name": "ISO 50001 - Energy Management",
        "jurisdiction": "Germany",
        "market_value": 10000,
        "asset_type": "Energy"
    },
    {
        "asset_id": "CERT_MFG_010",
        "asset_name": "IATF 16949 - Automotive Quality",
        "jurisdiction": "Multi-jurisdictional",
        "market_value": 18000,
        "asset_type": "Industry Specific"
    }
]

# ============================================================================
# ASSET CLASS MAPPING
# ============================================================================

DAY10_ASSET_CLASS_MAPPING = {
    "Equity": ["Stock", "Bond", "Fund", "ETF"],
    "Equipment": ["CNC Machine", "3D Printer", "Molding Machine", "Laser Cutter",
                  "Assembly System", "QC Equipment", "Robotic Welder", "CNC Lathe",
                  "AGV System", "Coating System"],
    "IP": ["Patent", "Trademark", "Copyright", "Trade Secret", "Design Patent"],
    "Certification": ["Product Certification", "Quality Management", "Regulatory Compliance",
                     "Environmental", "Safety", "Cybersecurity", "Energy", "Industry Specific"]
}

# ============================================================================
# SCD TYPE 2 EXAMPLES
# ============================================================================

# Asset reclassification events for SCD Type 2 demonstration
DAY10_SCD_EXAMPLES = [
    {
        "asset_id": "EQ_MFG_001",
        "changes": [
            {"date": "2023-01-01", "status": "Active"},
            {"date": "2024-07-01", "status": "Maintenance"},
            {"date": "2024-10-01", "status": "Active"}
        ]
    },
    {
        "asset_id": "CERT_MFG_001",
        "changes": [
            {"date": "2023-01-01", "requirements": "Standard v1.0"},
            {"date": "2025-01-01", "requirements": "Standard v2.0"}
        ]
    }
]

# ============================================================================
# ACCOUNT CONFIGURATION
# ============================================================================

DAY10_ACCOUNTS_PER_FAMILY = {
    "FAM_001": ["Investment Account", "Trust Account"],
    "FAM_002": ["Real Estate Holdings", "Development Fund"],
    "FAM_003": ["MFG Company Operating Account", "Investment Account", "Reserve Fund"],
    "FAM_004": ["Tech Portfolio", "Venture Fund"],
    "FAM_005": ["Diversified Holdings", "Tactical Account"]
}

# ============================================================================
# BUSINESS LOGIC
# ============================================================================

# Fiscal year configuration
DAY10_FISCAL_YEAR_START_MONTH = 1  # January (calendar year)

# Value ranges for synthetic data (in EUR)
DAY10_VALUE_RANGES = {
    "financial_min": 50000,
    "financial_max": 5000000,
    "operating_stake_min": 500000,
    "operating_stake_max": 20000000
}

# ============================================================================
# DATA QUALITY
# ============================================================================

DAY10_REQUIRED_FIELDS = [
    "asset_key",
    "client_key",
    "account_key",
    "date_key",
    "market_value"
]

DAY10_VALIDATION_RULES = {
    "min_assets": 100,
    "min_families": 5,
    "min_mfg_assets": 30,
    "min_months": 24
}
