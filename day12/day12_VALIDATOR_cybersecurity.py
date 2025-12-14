#!/usr/bin/env python3
"""
Day 12 - Cybersecurity Data Quality Validation Framework
Demonstrates Great Expectations concepts with a simpler implementation
Context: Sal (Cybersecurity Analyst) - Security data validation

NOTE: This is a simplified validation framework that demonstrates GE concepts.
Production implementation would use full Great Expectations library once
dependency issues are resolved.
"""

import pandas as pd
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

# Import configuration
from day12_CONFIG_settings import (
    DAY12_SECURITY_EVENTS_PATH,
    DAY12_COMPLIANCE_AUDIT_PATH,
    DAY12_THRESHOLD_NULL_EVENT_IDS,
    DAY12_THRESHOLD_PII_LEAKAGE,
    DAY12_THRESHOLD_FUTURE_TIMESTAMPS,
    DAY12_THRESHOLD_MISSING_CRITICAL_FIELDS,
    DAY12_VALID_SEVERITIES,
    DAY12_VALID_ACTIONS,
    DAY12_VALID_STATUSES,
    DAY12_PII_EMAIL_PATTERN,
    DAY12_MIN_RISK_SCORE,
    DAY12_MAX_RISK_SCORE,
    DAY12_SEVERITY_RISK_MAPPING,
    DAY12_REQUIRED_SECURITY_FIELDS,
    DAY12_VALIDATION_RESULTS_DIR,
    DAY12_LOG_FILE,
    DAY12_LOGS_DIR
)

# Setup logging
DAY12_LOGS_DIR.mkdir(exist_ok=True, parents=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DAY12_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def convert_to_json_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    import numpy as np
    if isinstance(obj, (np.integer, np.bool_)):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


class Day12DataQualityValidator:
    """
    Data Quality Validation Framework for Cybersecurity Data
    Implements Great Expectations-style validation patterns
    """

    def __init__(self, df: pd.DataFrame, dataset_name: str):
        self.df = df
        self.dataset_name = dataset_name
        self.validation_results = {
            'dataset': dataset_name,
            'timestamp': datetime.now().isoformat(),
            'total_rows': len(df),
            'expectations': [],
            'success': True,
            'statistics': {}
        }

    def expect_column_to_exist(self, column_name: str) -> Dict:
        """Expectation 1: Column must exist in dataset"""
        result = {
            'expectation_type': 'expect_column_to_exist',
            'column': column_name,
            'success': bool(column_name in self.df.columns),
            'severity': 'critical'
        }
        logger.info(f"✓ Checking column exists: {column_name} - {'PASS' if result['success'] else 'FAIL'}")
        self.validation_results['expectations'].append(result)
        if not result['success']:
            self.validation_results['success'] = False
        return result

    def expect_column_values_to_not_be_null(
        self,
        column_name: str,
        threshold: float = 0.0
    ) -> Dict:
        """
        Expectation 2: Column values should not be null
        Critical for security event IDs and timestamps
        """
        null_count = self.df[column_name].isna().sum()
        null_percentage = null_count / len(self.df) if len(self.df) > 0 else 0
        success = null_percentage <= threshold

        result = {
            'expectation_type': 'expect_column_values_to_not_be_null',
            'column': column_name,
            'success': bool(success),
            'observed_value': int(null_count),
            'percentage': round(float(null_percentage) * 100, 2),
            'threshold': round(threshold * 100, 2),
            'severity': 'critical' if not success else 'info'
        }

        logger.info(
            f"✓ Checking null values in {column_name}: "
            f"{null_count} nulls ({result['percentage']}%) - "
            f"{'PASS' if success else 'FAIL'}"
        )

        self.validation_results['expectations'].append(result)
        if not success:
            self.validation_results['success'] = False
        return result

    def expect_column_values_to_not_match_regex(
        self,
        column_name: str,
        regex_pattern: str,
        threshold: float = 0.0
    ) -> Dict:
        """
        Expectation 3: Column values should NOT match regex (PII detection)
        Critical for preventing PII leakage in usernames
        """
        matches = self.df[column_name].astype(str).str.match(regex_pattern, na=False)
        match_count = matches.sum()
        match_percentage = match_count / len(self.df) if len(self.df) > 0 else 0
        success = match_percentage <= threshold

        result = {
            'expectation_type': 'expect_column_values_to_not_match_regex',
            'column': column_name,
            'regex': regex_pattern,
            'success': bool(success),
            'observed_value': int(match_count),
            'percentage': round(float(match_percentage) * 100, 2),
            'threshold': round(threshold * 100, 2),
            'severity': 'critical' if not success else 'warning',
            'description': 'PII leakage detection'
        }

        logger.info(
            f"✓ Checking PII pattern in {column_name}: "
            f"{match_count} matches ({result['percentage']}%) - "
            f"{'PASS' if success else 'FAIL'}"
        )

        self.validation_results['expectations'].append(result)
        if not success:
            self.validation_results['success'] = False
        return result

    def expect_column_values_to_be_in_set(
        self,
        column_name: str,
        value_set: List[Any]
    ) -> Dict:
        """
        Expectation 4: Column values must be in allowed set
        Important for categorical fields like severity, status
        """
        valid_mask = self.df[column_name].isin(value_set) | self.df[column_name].isna()
        invalid_count = (~valid_mask).sum()
        success = invalid_count == 0

        invalid_values = self.df.loc[~valid_mask, column_name].unique().tolist()

        result = {
            'expectation_type': 'expect_column_values_to_be_in_set',
            'column': column_name,
            'value_set': value_set,
            'success': bool(success),
            'invalid_count': int(invalid_count),
            'invalid_values': [str(v) for v in invalid_values[:10]],  # First 10 invalid values
            'severity': 'warning' if not success else 'info'
        }

        logger.info(
            f"✓ Checking valid values in {column_name}: "
            f"{invalid_count} invalid - {'PASS' if success else 'FAIL'}"
        )

        self.validation_results['expectations'].append(result)
        if not success and invalid_count > len(self.df) * 0.1:  # > 10% invalid
            self.validation_results['success'] = False
        return result

    def expect_column_values_to_be_between(
        self,
        column_name: str,
        min_value: float,
        max_value: float
    ) -> Dict:
        """
        Expectation 5: Column values must be within range
        Critical for risk scores (0-100)
        """
        out_of_range = (
            (self.df[column_name] < min_value) |
            (self.df[column_name] > max_value)
        ).sum()
        success = out_of_range == 0

        result = {
            'expectation_type': 'expect_column_values_to_be_between',
            'column': column_name,
            'min_value': min_value,
            'max_value': max_value,
            'success': bool(success),
            'out_of_range_count': int(out_of_range),
            'severity': 'warning' if not success else 'info'
        }

        logger.info(
            f"✓ Checking range for {column_name}: "
            f"{out_of_range} out of range - {'PASS' if success else 'FAIL'}"
        )

        self.validation_results['expectations'].append(result)
        return result

    def expect_column_values_timestamp_not_future(
        self,
        column_name: str,
        threshold: float = 0.0,
        tolerance_hours: int = 1
    ) -> Dict:
        """
        Expectation 6: Timestamps should not be in future (beyond tolerance)
        Critical for security log integrity
        """
        max_allowed = datetime.now() + timedelta(hours=tolerance_hours)
        timestamps = pd.to_datetime(self.df[column_name])
        future_count = (timestamps > max_allowed).sum()
        future_percentage = future_count / len(self.df) if len(self.df) > 0 else 0
        success = future_percentage <= threshold

        result = {
            'expectation_type': 'expect_column_values_timestamp_not_future',
            'column': column_name,
            'success': bool(success),
            'future_count': int(future_count),
            'percentage': round(float(future_percentage) * 100, 2),
            'threshold': round(threshold * 100, 2),
            'tolerance_hours': tolerance_hours,
            'severity': 'warning' if not success else 'info'
        }

        logger.info(
            f"✓ Checking future timestamps in {column_name}: "
            f"{future_count} future ({result['percentage']}%) - "
            f"{'PASS' if success else 'FAIL'}"
        )

        self.validation_results['expectations'].append(result)
        if not success:
            self.validation_results['success'] = False
        return result

    def expect_severity_risk_correlation(
        self,
        severity_column: str,
        risk_column: str,
        mapping: Dict[str, Tuple[int, int]],
        tolerance: float = 0.05
    ) -> Dict:
        """
        Expectation 7: Risk score should correlate with severity
        Cybersecurity-specific validation
        """
        mismatches = 0
        for severity, (min_risk, max_risk) in mapping.items():
            severity_mask = self.df[severity_column] == severity
            risk_values = self.df.loc[severity_mask, risk_column]

            out_of_range = (
                (risk_values < min_risk) |
                (risk_values > max_risk)
            ).sum()
            mismatches += out_of_range

        mismatch_percentage = mismatches / len(self.df) if len(self.df) > 0 else 0
        success = mismatch_percentage <= tolerance

        result = {
            'expectation_type': 'expect_severity_risk_correlation',
            'severity_column': severity_column,
            'risk_column': risk_column,
            'success': bool(success),
            'mismatches': int(mismatches),
            'percentage': round(float(mismatch_percentage) * 100, 2),
            'tolerance': round(tolerance * 100, 2),
            'severity': 'warning' if not success else 'info',
            'description': 'Cybersecurity-specific: severity must correlate with risk score'
        }

        logger.info(
            f"✓ Checking severity-risk correlation: "
            f"{mismatches} mismatches ({result['percentage']}%) - "
            f"{'PASS' if success else 'FAIL'}"
        )

        self.validation_results['expectations'].append(result)
        return result

    def expect_table_row_count_to_be_between(
        self,
        min_rows: int,
        max_rows: int = None
    ) -> Dict:
        """
        Expectation 8: Table should have reasonable number of rows
        Detect data pipeline issues
        """
        row_count = len(self.df)
        success = row_count >= min_rows
        if max_rows:
            success = success and (row_count <= max_rows)

        result = {
            'expectation_type': 'expect_table_row_count_to_be_between',
            'success': bool(success),
            'observed_value': int(row_count),
            'min_value': min_rows,
            'max_value': max_rows,
            'severity': 'critical' if not success else 'info'
        }

        logger.info(
            f"✓ Checking row count: {row_count} rows - "
            f"{'PASS' if success else 'FAIL'}"
        )

        self.validation_results['expectations'].append(result)
        if not success:
            self.validation_results['success'] = False
        return result

    def generate_statistics(self) -> Dict:
        """Generate dataset statistics"""
        stats = {
            'total_expectations': len(self.validation_results['expectations']),
            'passed': sum(1 for e in self.validation_results['expectations'] if e['success']),
            'failed': sum(1 for e in self.validation_results['expectations'] if not e['success']),
            'success_rate': 0.0
        }
        if stats['total_expectations'] > 0:
            stats['success_rate'] = round(
                (stats['passed'] / stats['total_expectations']) * 100, 2
            )

        self.validation_results['statistics'] = stats
        return stats

    def save_results(self, output_path: Path = None):
        """Save validation results to JSON"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = DAY12_VALIDATION_RESULTS_DIR / f"validation_{self.dataset_name}_{timestamp}.json"

        output_path.parent.mkdir(exist_ok=True, parents=True)

        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)

        logger.info(f"📄 Validation results saved to: {output_path}")
        return output_path


def day12_validate_security_events() -> Dict:
    """
    Run complete validation suite on security events data
    """
    logger.info("=" * 80)
    logger.info("DAY 12 - SECURITY EVENTS DATA QUALITY VALIDATION")
    logger.info("=" * 80)

    # Load data
    logger.info(f"\n📊 Loading data from: {DAY12_SECURITY_EVENTS_PATH}")
    df = pd.read_csv(DAY12_SECURITY_EVENTS_PATH)
    logger.info(f"✅ Loaded {len(df)} records")

    # Initialize validator
    validator = Day12DataQualityValidator(df, "security_events")

    # Run expectations
    logger.info("\n🔍 Running validation suite...")

    # 1. Check required columns exist
    for col in DAY12_REQUIRED_SECURITY_FIELDS:
        validator.expect_column_to_exist(col)

    # 2. Check for null event IDs (critical field)
    validator.expect_column_values_to_not_be_null(
        'event_id',
        threshold=DAY12_THRESHOLD_NULL_EVENT_IDS
    )

    # 3. Check for PII leakage in usernames
    validator.expect_column_values_to_not_match_regex(
        'username',
        regex_pattern=DAY12_PII_EMAIL_PATTERN,
        threshold=DAY12_THRESHOLD_PII_LEAKAGE
    )

    # 4. Check valid severity values
    validator.expect_column_values_to_be_in_set(
        'severity',
        value_set=DAY12_VALID_SEVERITIES
    )

    # 5. Check valid action values
    validator.expect_column_values_to_be_in_set(
        'action_taken',
        value_set=DAY12_VALID_ACTIONS
    )

    # 6. Check valid status values
    validator.expect_column_values_to_be_in_set(
        'status',
        value_set=DAY12_VALID_STATUSES
    )

    # 7. Check risk score bounds
    validator.expect_column_values_to_be_between(
        'risk_score',
        min_value=DAY12_MIN_RISK_SCORE,
        max_value=DAY12_MAX_RISK_SCORE
    )

    # 8. Check for future timestamps
    validator.expect_column_values_timestamp_not_future(
        'timestamp',
        threshold=DAY12_THRESHOLD_FUTURE_TIMESTAMPS,
        tolerance_hours=1
    )

    # 9. Check severity-risk score correlation (cybersecurity-specific)
    validator.expect_severity_risk_correlation(
        'severity',
        'risk_score',
        mapping=DAY12_SEVERITY_RISK_MAPPING,
        tolerance=0.05
    )

    # 10. Check reasonable row count
    validator.expect_table_row_count_to_be_between(
        min_rows=100,
        max_rows=1000000
    )

    # Generate statistics
    stats = validator.generate_statistics()

    # Save results
    output_path = validator.save_results()

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Dataset: {validator.dataset_name}")
    logger.info(f"Total Rows: {validator.validation_results['total_rows']:,}")
    logger.info(f"Total Expectations: {stats['total_expectations']}")
    logger.info(f"Passed: {stats['passed']} ✓")
    logger.info(f"Failed: {stats['failed']} ✗")
    logger.info(f"Success Rate: {stats['success_rate']}%")
    logger.info(f"Overall Status: {'✅ PASS' if validator.validation_results['success'] else '❌ FAIL'}")
    logger.info("=" * 80)

    return validator.validation_results


if __name__ == "__main__":
    results = day12_validate_security_events()
