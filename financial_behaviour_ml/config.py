# Data configuration
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