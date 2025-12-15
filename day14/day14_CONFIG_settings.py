"""
Day 14: Transport Regulatory KPIs Configuration
Andrea - Policy & Transport Analytics

Configuration settings for Querido Diário API integration and transport regulatory reporting.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Querido Diário API Configuration
DAY14_API_BASE_URL = "https://api.queridodiario.ok.org.br"
DAY14_API_GAZETTES_ENDPOINT = f"{DAY14_API_BASE_URL}/gazettes"
DAY14_API_RATE_LIMIT = 60  # requests per minute

# Major Brazilian cities IBGE codes for transport monitoring
DAY14_TERRITORY_IDS = {
    'Sao_Paulo': '3550308',
    'Rio_de_Janeiro': '3304557',
    'Brasilia': '5300108',
    'Salvador': '2927408',
    'Fortaleza': '2304400',
    'Belo_Horizonte': '3106200',
    'Manaus': '1302603',
    'Curitiba': '4106902',
    'Recife': '2611606',
    'Porto_Alegre': '4314902'
}

# Transport/Policy Keywords (Portuguese)
DAY14_SEARCH_KEYWORDS = [
    'transporte',     # transport
    'mobilidade',     # mobility
    'trânsito',       # traffic
    'veículo',        # vehicle
    'ônibus',         # bus
    'regulação',      # regulation
    'segurança viária',  # road safety
    'estacionamento', # parking
    'infraestrutura', # infrastructure
    'política pública',  # public policy
    'passageiros'     # passengers
]

# API Query Parameters
DAY14_EXCERPT_SIZE = 500  # characters per excerpt
DAY14_NUMBER_OF_EXCERPTS = 3  # excerpts per result
DAY14_RESULTS_SIZE = 10  # results per query

# Email Configuration
DAY14_SENDER_EMAIL = os.getenv('DAY14_SENDER_EMAIL', 'reports@transport-analytics.example.com')
DAY14_SENDER_NAME = os.getenv('DAY14_SENDER_NAME', 'Transport Analytics')
DAY14_RECIPIENT_EMAILS = os.getenv('DAY14_RECIPIENT_EMAILS', 'andrea@example.com').split(',')

# Report Configuration
DAY14_REPORT_TITLE = os.getenv('DAY14_REPORT_TITLE', 'Daily Transport Regulatory KPIs - Brazil')
DAY14_SCHEDULE_CRON = os.getenv('DAY14_SCHEDULE_CRON', '0 8 * * *')  # 8am daily
DAY14_TIMEZONE = os.getenv('DAY14_TIMEZONE', 'America/Sao_Paulo')

# Data Paths
DAY14_DATA_PATH = os.getenv('DAY14_DATA_PATH', './data/day14_querido_diario_cache.json')
DAY14_LOG_PATH = os.getenv('DAY14_LOG_PATH', './logs/day14_execution.log')

# KPI Definitions
DAY14_KPI_DEFINITIONS = {
    'new_regulations': {
        'name': 'New Transport Regulations Published',
        'description': 'Count of new transport/mobility regulations across monitored municipalities',
        'unit': 'documents',
        'keywords': ['transporte', 'mobilidade', 'regulação']
    },
    'active_municipalities': {
        'name': 'Municipalities with Transport Updates',
        'description': 'Number of cities publishing transport-related regulations',
        'unit': 'cities',
        'keywords': DAY14_SEARCH_KEYWORDS
    },
    'compliance_mentions': {
        'name': 'Compliance & Deadline Mentions',
        'description': 'Frequency of compliance requirements and deadlines',
        'unit': 'mentions',
        'keywords': ['prazo', 'cumprimento', 'obrigatoriedade', 'fiscalização']
    },
    'safety_incidents': {
        'name': 'Safety Incident Reports',
        'description': 'Mentions of traffic/transport safety incidents',
        'unit': 'reports',
        'keywords': ['acidente', 'segurança viária', 'infração', 'multa']
    }
}

# Testing/Development
DAY14_TEST_MODE = os.getenv('DAY14_TEST_MODE', 'false').lower() == 'true'
DAY14_DRY_RUN = os.getenv('DAY14_DRY_RUN', 'false').lower() == 'true'
