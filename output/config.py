"""
Configuration file for Trading Simulation Platform
Centralizes all configuration values for easy maintenance
"""

from decimal import Decimal
from typing import List

# Application Settings
APP_NAME = "Trading Simulation Platform"
APP_VERSION = "1.0.0"
DEBUG = False

# Supported Stock Symbols
SUPPORTED_SYMBOLS: List[str] = ['AAPL', 'TSLA', 'GOOGL']

# Funds Management Settings
MIN_DEPOSIT_AMOUNT = Decimal('1.00')
MAX_DEPOSIT_AMOUNT = Decimal('1000000.00')
MIN_WITHDRAWAL_AMOUNT = Decimal('0.01')
MAX_WITHDRAWAL_AMOUNT = Decimal('1000000.00')

# Price Service Settings
PRICE_CACHE_TTL_MINUTES = 5

# Simulated Stock Prices (for demo purposes)
SIMULATED_PRICES = {
    'AAPL': Decimal('145.00'),
    'TSLA': Decimal('650.00'),
    'GOOGL': Decimal('2800.00')
}

# Transaction History Settings
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "trading_platform.log"

# UI Settings
GRADIO_THEME = "soft"
GRADIO_SHARE = False
GRADIO_SERVER_PORT = 7860

# Business Rules
ALLOW_NEGATIVE_BALANCE = False
REQUIRE_EMAIL_VERIFICATION = False
MAX_DAILY_TRANSACTIONS = 1000
