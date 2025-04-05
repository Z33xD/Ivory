from config import *

class ExpenseCategorizer:
    @staticmethod
    def categorize(transaction):
        """Categorize a transaction as need or want"""
        category = transaction['category'].lower()
        
        if category in NEEDS:
            return 'need'
        elif category in WANTS:
            return 'want'
        else:
            # Fallback for unknown categories
            if transaction['amount'] > 500:  # Large amounts more likely to be needs
                return 'need'
            return 'want'
    
    @staticmethod
    def analyze_spending(user_data, transactions):
        """Analyze a user's spending pattern"""
        analysis = {
            'needs_total': 0,
            'wants_total': 0,
            'transactions': []
        }
        
        for tx in transactions:
            tx_type = ExpenseCategorizer.categorize(tx)
            if tx_type == 'need':
                analysis['needs_total'] += tx['amount']
            else:
                analysis['wants_total'] += tx['amount']
            
            analysis['transactions'].append({
                **tx,
                'type': tx_type,
                'high_risk': (
                    tx_type == 'want' and 
                    tx['amount'] > HIGH_RISK_THRESHOLD * user_data['disposable_income']
                )
            })
        
        return analysis