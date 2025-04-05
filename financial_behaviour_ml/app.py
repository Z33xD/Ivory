from src.data_processor import DataProcessor
from src.expense_categorizer import ExpenseCategorizer
from src.behavior_predictor import BehaviorPredictor
from src.savings_optimizer import SavingsOptimizer

# Initialize components
processor = DataProcessor()
predictor = BehaviorPredictor()
categorizer = ExpenseCategorizer()

# Get user data
user_id = "user_123"  # Example user
user_data = processor.get_user_data(user_id)

# Example transactions
transactions = [
    {'category': 'rent', 'amount': 15000, 'date': '2023-07-01'},
    {'category': 'eating_out', 'amount': 3000, 'date': '2023-07-02'},
    {'category': 'entertainment', 'amount': 5000, 'date': '2023-07-03'}
]

# Analyze spending
spending_analysis = categorizer.analyze_spending(user_data, transactions)

# Predict behavior
behavior_prediction = predictor.predict_behavior(user_data)

# Get recommendations
recommendations = SavingsOptimizer.get_recommendations(
    user_data,
    spending_analysis,
    behavior_prediction
)

print("Behavior Prediction:", behavior_prediction)
print("Recommendations:")
for rec in recommendations:
    print(f"- {rec['message']}")