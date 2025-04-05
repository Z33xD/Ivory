import unittest
from src.savings_optimizer import SavingsOptimizer

class TestSavingsOptimizer(unittest.TestCase):
    def test_recommendations(self):
        user_data = {
            'income': 100000,
            'desired_savings': 20000,
            'desired_savings_percentage': 25,
            'disposable_income': 60000,
            'potential_savings_eating_out': 3000,
            'potential_savings_entertainment': 2000,
            'potential_savings_groceries': 1500,
            'potential_savings_transport': 1000
        }
        
        spending_analysis = {
            'transactions': [
                {'category': 'eating_out', 'amount': 5000, 'high_risk': True},
                {'category': 'groceries', 'amount': 8000, 'high_risk': False}
            ]
        }
        
        recommendations = SavingsOptimizer.get_recommendations(
            user_data,
            spending_analysis,
            'want-driven'
        )
        
        self.assertEqual(len(recommendations), 3)  # savings_status, wants_reduction, high_risk_warning
        self.assertEqual(recommendations[0]['current_rate'], 20.0)
        self.assertIn('Potential savings by reducing wants', recommendations[1]['message'])

if __name__ == '__main__':
    unittest.main()