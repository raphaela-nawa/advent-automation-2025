"""Day 17 config settings for legal analytics dashboard."""

import os
from pathlib import Path

DAY17_DEFAULT_DB_PATH = Path("../day10/data/day10_family_office_dw.db")
DAY17_DB_PATH = Path(os.getenv("DAY17_DB_PATH", DAY17_DEFAULT_DB_PATH))

DAY17_JURISDICTIONS = ["US", "EU", "UK", "APAC"]
DAY17_DEADLINE_THRESHOLDS_DAYS = {"critical": 30, "warning": 90}
