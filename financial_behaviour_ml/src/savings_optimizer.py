from config import *

class SavingsOptimizer:
    @staticmethod
    def get_recommendations(user_data, spending_analysis, behavior_prediction):
        """Generate personalized savings recommendations"""
        recommendations = []
        
        # Basic savings status
        current_savings_rate = user_data['desired_savings'] / user_data['income']
        recommendations.append({
            'type': 'savings_status',
            'current_rate': round(current_savings_rate * 100, 1),
            'target_rate': round(user_data['desired_savings_percentage'], 1),
            'message': (
                f"Current savings rate: {round(current_savings_rate * 100, 1)}% "
                f"(Target: {user_data['desired_savings_percentage']}%)"
            )
        })
        
        # Wants reduction potential
        if behavior_prediction == 'want-driven':
            potential_savings = sum(
                user_data[f'potential_savings_{cat}'] 
                for cat in WANTS
            )
            
            recommendations.append({
                'type': 'wants_reduction',
                'potential': round(potential_savings, 2),
                'message': (
                    f"Potential savings by reducing wants: ₹{round(potential_savings, 2)} "
                    f"per month ({round(potential_savings/user_data['income']*100, 1)}% of income)"
                )
            })
        
        # High-risk transactions
        high_risk_tx = [tx for tx in spending_analysis['transactions'] if tx['high_risk']]
        if high_risk_tx:
            recommendations.append({
                'type': 'high_risk_warning',
                'count': len(high_risk_tx),
                'total_amount': sum(tx['amount'] for tx in high_risk_tx),
                'transactions': high_risk_tx,
                'message': (
                    f"Found {len(high_risk_tx)} high-risk transactions "
                    f"totaling ₹{sum(tx['amount'] for tx in high_risk_tx)}"
                )
            })
        
        # Needs optimization
        needs_potential = sum(
            user_data[f'potential_savings_{cat}'] 
            for cat in NEEDS if cat != 'rent' and cat != 'loan_repayment'
        )
        
        if needs_potential > 0:
            recommendations.append({
                'type': 'needs_optimization',
                'potential': round(needs_potential, 2),
                'message': (
                    f"Potential savings by optimizing needs: ₹{round(needs_potential, 2)} "
                    f"per month ({round(needs_potential/user_data['income']*100, 1)}% of income)"
                )
            })
        
        return recommendations