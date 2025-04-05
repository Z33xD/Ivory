import os

# Security
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev_secret_key_change_in_production')

# Mockaroo API settings
MOCKAROO_API_KEY = os.environ.get('MOCKAROO_API_KEY', 'a1055fe0')
MOCKAROO_ENDPOINT = 'https://my.api.mockaroo.com/expenditures_and_savings.json'

# Spending thresholds for alerts (₹)
SPENDING_THRESHOLDS = {
    'groceries': 5000,
    'transport': 1000,
    'eating_out': 2000,
    'entertainment': 1500,
    'utilities': 3000,
    'healthcare': 2000,
    'education': 1500,
    'miscellaneous': 1000
}

# Category mapping
CATEGORY_MAP = {
    'groceries': 'Groceries',
    'transport': 'Transport',
    'eating_out': 'Eating_Out',
    'entertainment': 'Entertainment',
    'utilities': 'Utilities',
    'healthcare': 'Healthcare',
    'education': 'Education',
    'miscellaneous': 'Miscellaneous'
}

# Transaction categories
TRANSACTION_CATEGORIES = [
    'groceries',
    'transport',
    'eating_out',
    'entertainment',
    'utilities',
    'healthcare',
    'education',
    'miscellaneous'
]# Data configuration
DATA_PATH = "financial_behavior.csv"

# Expense categories
NEEDS = ['rent', 'groceries', 'transport', 'utilities', 'healthcare', 'education', 'loan_repayment']
WANTS = ['eating_out', 'entertainment', 'miscellaneous']

# Model configuration
MODEL_PATH = "models/behavior_model.pkl"
TARGET = 'savings_behavior'
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Thresholds
WANTS_THRESHOLD = 0.3  # 30% of total spending
HIGH_RISK_THRESHOLD = 0.1  # 10% of disposable income