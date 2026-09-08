import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'ghosttrace.db')}"

RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
LOG_DIR = os.path.join(BASE_DIR, "logs")
STORAGE_DIR= os.path.join(BASE_DIR, "storage")

# Create directories if they don't exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)

# JWT secret for authentication
JWT_SECRET = "ghosttrace_secret_key"
JWT_ALGORITHM = "HS256"

# Stripe configuration
STRIPE_SECRET_KEY = "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"
STRIPE_PUBLISHABLE_KEY = "pk_live_51U8zxGQcBIIZXfeMvmEswgcRNiVGD8lV3aVeES7YYh29DxVwC0AXbrhiW4R2ojYeSymDMBAeOOocubNUWn2CZUzC00fYPmTBWv"

# Stripe subscription tiers (monthly + yearly)
PRICE_BASIC_MONTHLY = "price_1U92s8QcBIIZXfeMWboTdXjL"
PRICE_BASIC_YEARLY = "price_1U9JczQcBIIZXfeMOZTnA94y"

PRICE_PRO_MONTHLY = "price_1U9JkZQcBIIZXfeMjwDT1meU"
PRICE_PRO_YEARLY = "price_1U9JkZQcBIIZXfeMDfiuUnqH"

PRICE_ULTRA_MONTHLY = "price_1U9JmyQcBIIZXfeMcyR9azlP"
PRICE_ULTRA_YEARLY = "price_1U9JmyQcBIIZXfeMUJ9BOXK9"

PRICE_ENTERPRISE = "price_1U9L1PQcBIIZXfeMcvoIvK7w"

# Add-ons
PRICE_EXTRA_TARGETS = "price_1U9L57QcBIIZXfeMFl89oE9D"
PRICE_EXTRA_REPORTS = "price_1U9L6pQcBIIZXfeMM9EmCsJA"
PRICE_SMS_ALERTS = "price_1U9L8JQcBIIZXfeMQAI1aP6C"
