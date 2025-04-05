import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from config import *

class DataProcessor:
    def __init__(self):
        self.df = self.load_and_preprocess()
    
    def load_and_preprocess(self):
        """Load and preprocess the dataset"""
        df = pd.read_csv(DATA_PATH)
        
        # Calculate totals
        df['total_needs'] = df[NEEDS].sum(axis=1)
        df['total_wants'] = df[WANTS].sum(axis=1)
        df['total_spending'] = df['total_needs'] + df['total_wants']
        
        # Create target variable
        df[TARGET] = np.where(
            df['total_wants'] > WANTS_THRESHOLD * df['total_spending'],
            'want-driven',
            'need-driven'
        )
        
        # Calculate ratios
        df['savings_ratio'] = df['desired_savings'] / df['income']
        df['disposable_ratio'] = df['disposable_income'] / df['income']
        
        return df
    
    def get_train_test(self):
        """Split data into train and test sets"""
        features = [
            'income', 'age', 'dependents', 'occupation', 'city_tier',
            'total_needs', 'total_wants', 'savings_ratio', 'disposable_ratio'
        ]
        
        X = self.df[features]
        y = self.df[TARGET]
        
        return train_test_split(
            X, y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE
        )
    
    def get_user_data(self, user_id):
        """Get data for a specific user"""
        return self.df[self.df['user_id'] == user_id].iloc[0].to_dict()