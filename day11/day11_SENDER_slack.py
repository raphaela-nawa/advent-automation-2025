"""
Day 11 Slack Sender
Sends formatted messages to Slack using webhooks

This module handles the actual delivery of messages to Slack,
including retry logic and error handling.

Author: Gleyson - Retail Marketing Automation Specialist
"""

import requests
import logging
import time
from typing import Dict, Optional
from day11_CONFIG_settings import (
    DAY11_SLACK_WEBHOOK_URL,
    DAY11_RETRY_ATTEMPTS,
    DAY11_RETRY_DELAY_SECONDS,
    DAY11_DRY_RUN
)

logger = logging.getLogger(__name__)


class Day11SlackSender:
    """Handles sending messages to Slack via webhooks."""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize the Slack sender.

        Args:
            webhook_url: Slack webhook URL. If None, uses config value.
        """
        self.webhook_url = webhook_url or DAY11_SLACK_WEBHOOK_URL

        if not self.webhook_url:
            logger.warning("No Slack webhook URL configured!")

    def day11_send_message(self, payload: Dict, retry: bool = True) -> bool:
        """
        Send a message to Slack.

        Args:
            payload: Slack message payload (with blocks)
            retry: Whether to retry on failure

        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.error("Cannot send message: No webhook URL configured")
            return False

        if DAY11_DRY_RUN:
            logger.info("[DRY RUN] Would send to Slack:")
            logger.info(f"Webhook: {self.webhook_url[:50]}...")
            logger.info(f"Payload: {payload.get('text', 'No fallback text')}")
            return True

        attempts = DAY11_RETRY_ATTEMPTS if retry else 1

        for attempt in range(1, attempts + 1):
            try:
                logger.info(f"Sending to Slack (attempt {attempt}/{attempts})...")

                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                if response.status_code == 200:
                    logger.info("✓ Message sent successfully to Slack")
                    return True
                else:
                    logger.warning(
                        f"Slack API returned status {response.status_code}: {response.text}"
                    )

                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        logger.error("Client error - not retrying")
                        return False

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt}: {e}")
                return False

            # Wait before retry (except on last attempt)
            if attempt < attempts:
                wait_time = DAY11_RETRY_DELAY_SECONDS * attempt  # Exponential backoff
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        logger.error(f"Failed to send message after {attempts} attempts")
        return False

    def day11_test_connection(self) -> bool:
        """
        Test the Slack webhook connection with a simple message.

        Returns:
            True if connection works, False otherwise
        """
        test_payload = {
            "text": "🧪 Day 11 Connection Test",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This is a connection test from Day 11 automated reporting system. ✅"
                    }
                }
            ]
        }

        return self.day11_send_message(test_payload, retry=False)


def day11_send_to_slack(payload: Dict, webhook_url: Optional[str] = None) -> bool:
    """
    Convenience function to send a message to Slack.

    Args:
        payload: Slack message payload
        webhook_url: Optional webhook URL override

    Returns:
        True if successful, False otherwise
    """
    sender = Day11SlackSender(webhook_url)
    return sender.day11_send_message(payload)


if __name__ == "__main__":
    # Test the Slack sender
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Day 11 Slack Sender Test")
    print("=" * 60)

    sender = Day11SlackSender()

    if not sender.webhook_url:
        print("\n❌ No webhook URL configured!")
        print("Set DAY11_SLACK_WEBHOOK_URL in config/.env to test")
    else:
        print(f"\n✓ Webhook URL configured: {sender.webhook_url[:50]}...")

        user_input = input("\nSend test message to Slack? (y/n): ")
        if user_input.lower() == 'y':
            success = sender.day11_test_connection()
            if success:
                print("\n✓ Test message sent successfully!")
            else:
                print("\n❌ Failed to send test message")
        else:
            print("\nTest skipped")

    print("=" * 60)
