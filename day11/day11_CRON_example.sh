#!/bin/bash
# Day 11 - Cron Job Example
# This script can be used as a cron job to run the daily report

# Example crontab entry:
# 0 8 * * * /path/to/day11/day11_CRON_example.sh >> /path/to/logs/cron.log 2>&1

# Set working directory
cd "$(dirname "$0")"

# Activate virtual environment if you're using one
# source ../.venv/bin/activate

# Set environment variables (optional - if not using config/.env)
# export DAY11_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
# export DAY11_SCHEDULE_CRON="0 8 * * *"
# export DAY11_RUN_ON_WEEKENDS="false"

# Run the orchestrator
echo "==================================="
echo "Day 11 Report - $(date)"
echo "==================================="

python3 day11_ORCHESTRATOR_main.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Report completed successfully"
else
    echo "✗ Report failed with exit code $EXIT_CODE"
fi

echo "==================================="
echo ""

exit $EXIT_CODE
