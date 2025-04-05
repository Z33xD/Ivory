import unittest
from src.expense_categorizer import ExpenseCategorizer

class TestExpenseCategorizer(unittest.TestCase):
    def test_categorization(self):
        test_cases = [
            ({'category': 'rent', 'amount': 10000}, 'need'),
            ({'category': 'groceries', 'amount': 5000}, 'need'),
            ({'category': 'eating_out', 'amount': 1500}, 'want'),
            ({'category': 'unknown', 'amount': 600}, 'need'),  # Large amount
            ({'category': 'unknown', 'amount': 100}, 'want')   # Small amount
        ]
        
        for tx, expected in test_cases:
            with self.subTest(tx=tx):
                self.assertEqual(ExpenseCategorizer.categorize(tx), expected)
    
    def test_spending_analysis(self):
        user_data = {
            'disposable_income': 20000
        }
        
        transactions = [
            {'category': 'rent', 'amount': 10000, 'date': '2023-01-01'},
            {'category': 'eating_out', 'amount': 2500, 'date': '2023-01-02'},
            {'category': 'entertainment', 'amount': 3000, 'date': '2023-01-03'}
        ]
        
        analysis = ExpenseCategorizer.analyze_spending(user_data, transactions)
        
        self.assertEqual(analysis['needs_total'], 10000)
        self.assertEqual(analysis['wants_total'], 5500)
        self.assertTrue(analysis['transactions'][2]['high_risk'])  # 3000 > 10% of 20000

if __name__ == '__main__':
    unittest.main()