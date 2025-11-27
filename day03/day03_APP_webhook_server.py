"""
Day 03 - GDPR Lead Ingestion Webhook Server
Flask application that receives GDPR-compliant lead data via POST requests.
"""

import logging
from flask import Flask, request, jsonify
from datetime import datetime

from day03_CONFIG_settings import DAY03_WEBHOOK_HOST, DAY03_WEBHOOK_PORT
from day03_PIPELINE_gdpr_validator import day03_GDPRValidator, day03_format_lead_for_bigquery
from day03_DATA_load_bigquery import day03_BigQueryLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize validator and BigQuery loader
validator = day03_GDPRValidator()
bq_loader = day03_BigQueryLoader()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Day 03 - GDPR Lead Ingestion Webhook",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.route('/leads', methods=['POST'])
def day03_receive_lead():
    """
    Receives and processes a GDPR-compliant lead.

    Expected JSON payload:
    {
        "name": "João Silva",
        "email": "joao@example.com",
        "consent_given": true,
        "consent_purpose": "marketing_communications",
        "ip_address": "192.168.1.1",
        "timestamp": "2024-11-26T10:30:00Z"
    }

    Returns:
        JSON response with success/error status
    """
    try:
        # Get JSON payload
        if not request.is_json:
            logger.warning("Received non-JSON request")
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400

        payload = request.get_json()
        logger.info(f"Received lead submission for: {payload.get('email', 'unknown')}")

        # Validate the lead
        is_valid, error_message, processed_lead = validator.validate_lead(payload)

        if not is_valid:
            logger.warning(f"Validation failed: {error_message}")
            return jsonify({
                "error": error_message,
                "status": "validation_failed"
            }), 400

        # Format for BigQuery
        bq_lead = day03_format_lead_for_bigquery(processed_lead)

        # Insert into BigQuery
        success = bq_loader.day03_insert_lead(bq_lead)

        if not success:
            logger.error("Failed to insert lead into BigQuery")
            return jsonify({
                "error": "Failed to store lead data",
                "status": "storage_failed"
            }), 500

        # Success response
        logger.info(f"Successfully processed lead: {processed_lead['lead_id']}")
        return jsonify({
            "status": "success",
            "message": "Lead processed and stored successfully",
            "lead_id": processed_lead['lead_id'],
            "consent_given": processed_lead['consent_given'],
            "data_retention_date": processed_lead['data_retention_date'].split('T')[0]
        }), 201

    except Exception as e:
        logger.error(f"Unexpected error processing lead: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "status": "error"
        }), 500


@app.route('/leads/stats', methods=['GET'])
def day03_get_stats():
    """
    Returns statistics about stored leads.

    Returns:
        JSON with lead count and recent leads
    """
    try:
        total_count = bq_loader.day03_count_leads()
        recent_leads = bq_loader.day03_query_leads(limit=5)

        return jsonify({
            "total_leads": total_count,
            "recent_leads": recent_leads,
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve statistics"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health",
            "POST /leads",
            "GET /leads/stats"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error"
    }), 500


def day03_start_webhook_server():
    """Starts the Flask webhook server."""
    logger.info(f"Starting GDPR Lead Ingestion Webhook Server...")
    logger.info(f"Server will run on {DAY03_WEBHOOK_HOST}:{DAY03_WEBHOOK_PORT}")
    logger.info(f"POST leads to: http://localhost:{DAY03_WEBHOOK_PORT}/leads")

    # Ensure BigQuery setup is ready
    try:
        logger.info("Verifying BigQuery setup...")
        bq_loader.day03_ensure_dataset_exists()
        bq_loader.day03_ensure_table_exists()
        logger.info("BigQuery setup verified successfully")
    except Exception as e:
        logger.warning(f"BigQuery setup verification failed: {str(e)}")
        logger.warning("Server will start, but BigQuery operations may fail")

    # Start Flask server
    app.run(
        host=DAY03_WEBHOOK_HOST,
        port=DAY03_WEBHOOK_PORT,
        debug=False
    )


if __name__ == "__main__":
    day03_start_webhook_server()
