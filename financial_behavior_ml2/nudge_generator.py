import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class NudgeGenerator:
    def __init__(self, spending_thresholds=None):
        self.spending_thresholds = spending_thresholds or {
            'dining_out': 2000,  # Weekly threshold
            'shopping': 5000,    # Weekly threshold
            'entertainment': 3000 # Weekly threshold
        }
        
    def analyze_spending_patterns(self, df):
        """Analyze spending patterns and generate insights"""
        # Convert to weekly data
        df['week'] = df['date'].dt.isocalendar().week
        weekly_spending = df.groupby(['week', 'category'])['amount'].sum().reset_index()
        
        insights = []
        
        # Analyze each category
        for category, threshold in self.spending_thresholds.items():
            category_spending = weekly_spending[weekly_spending['category'] == category]
            if not category_spending.empty:
                current_week = datetime.now().isocalendar()[1]
                current_spending = category_spending[category_spending['week'] == current_week]['amount'].sum()
                
                if current_spending > threshold:
                    insights.append({
                        'type': 'alert',
                        'category': category,
                        'message': f"You've spent ₹{current_spending} on {category} this week, which is above your threshold of ₹{threshold}",
                        'suggestion': f"Consider reducing your {category} expenses for the rest of the week"
                    })
        
        return insights
    
    def generate_savings_nudges(self, df, savings_goal):
        """Generate nudges related to savings goals"""
        total_spending = df['amount'].sum()
        wants_spending = df[df['category_type'] == 'wants']['amount'].sum()
        
        potential_savings = wants_spending * 0.2  # Assuming 20% of wants can be saved
        
        nudges = []
        
        if potential_savings > savings_goal:
            nudges.append({
                'type': 'savings_opportunity',
                'message': f"You could save ₹{potential_savings:.2f} by reducing discretionary spending by 20%",
                'suggestion': "Try to identify non-essential expenses you can cut back on"
            })
        else:
            nudges.append({
                'type': 'savings_goal',
                'message': f"To reach your savings goal of ₹{savings_goal}, you need to find additional ways to save",
                'suggestion': "Consider reviewing your essential expenses for potential savings"
            })
        
        return nudges
    
    def generate_personalized_nudges(self, df, user_preferences=None):
        """Generate personalized nudges based on spending patterns and user preferences"""
        user_preferences = user_preferences or {}
        
        # Get spending insights
        spending_insights = self.analyze_spending_patterns(df)
        
        # Get savings nudges
        savings_goal = user_preferences.get('savings_goal', 5000)  # Default savings goal
        savings_nudges = self.generate_savings_nudges(df, savings_goal)
        
        # Combine all nudges
        all_nudges = spending_insights + savings_nudges
        
        # Sort nudges by priority
        priority_order = {'alert': 1, 'savings_opportunity': 2, 'savings_goal': 3}
        all_nudges.sort(key=lambda x: priority_order.get(x['type'], 4))
        
        return all_nudges 