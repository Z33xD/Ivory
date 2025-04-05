import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_selection import SelectFromModel
from sklearn.base import BaseEstimator, TransformerMixin
import joblib
import os

class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Custom transformer to create advanced features"""
    
    def __init__(self):
        self.num_features = None
        self.cat_features = None
    
    def fit(self, X, y=None):
        # Store column names if X is a DataFrame, otherwise use indices
        if hasattr(X, 'columns'):
            self.feature_names = list(X.columns)
        else:
            # Just remember the shape for numpy arrays
            self.feature_names = None
        return self
    
    def transform(self, X):
        # Convert to DataFrame if it's a numpy array
        if not hasattr(X, 'columns'):
            if self.feature_names:
                X_copy = pd.DataFrame(X, columns=self.feature_names)
            else:
                # For numpy arrays without known feature names, we can't add meaningful features
                return X
        else:
            X_copy = X.copy()
        
        # Get numeric feature indices
        if 'income' in X_copy.columns:
            income_idx = list(X_copy.columns).index('income')
            income = X_copy.iloc[:, income_idx]
            
            # Add interaction features
            if 'total_expenses' in X_copy.columns:
                expenses_idx = list(X_copy.columns).index('total_expenses')
                expenses = X_copy.iloc[:, expenses_idx]
                X_copy['income_to_expenses_ratio'] = income / expenses.replace(0, 1)
                X_copy['discretionary_income'] = income - expenses
            
            if 'total_needs' in X_copy.columns:
                needs_idx = list(X_copy.columns).index('total_needs')
                X_copy['income_to_needs_ratio'] = income / X_copy.iloc[:, needs_idx].replace(0, 1)
            
            if 'total_wants' in X_copy.columns:
                wants_idx = list(X_copy.columns).index('total_wants')
                X_copy['income_to_wants_ratio'] = income / X_copy.iloc[:, wants_idx].replace(0, 1)
        
        # Add polynomial features for age and income if they exist
        if 'age' in X_copy.columns:
            age_idx = list(X_copy.columns).index('age')
            X_copy['age_squared'] = X_copy.iloc[:, age_idx] ** 2
        
        if 'income' in X_copy.columns:
            X_copy['income_squared'] = income ** 2
            
        # Return DataFrame as numpy array to maintain compatibility
        return X_copy

class DataProcessor:
    def __init__(self):
        # Define expense categories based on actual CSV columns
        self.expense_categories = [
            'rent', 'loan_repayment', 'insurance', 'groceries', 'transport',
            'eating_out', 'entertainment', 'utilities', 'healthcare',
            'education', 'miscellaneous'
        ]
        
        # Define which categories have potential savings in the dataset
        self.savings_categories = [
            'groceries', 'transport', 'eating_out', 'entertainment', 
            'utilities', 'healthcare', 'education', 'miscellaneous'
        ]
        
        # Define different types of expenses (needs vs wants)
        self.needs = ['rent', 'loan_repayment', 'insurance', 'groceries', 
                     'transport', 'utilities', 'healthcare', 'education']
        self.wants = ['eating_out', 'entertainment', 'miscellaneous']
        
        # Models for prediction
        self.models = {}
        
    def load_data(self, file_path='financial_behavior.csv'):
        """Load and preprocess the financial behavior data"""
        # Read the CSV file
        df = pd.read_csv(file_path)
        return df
        
    def preprocess_data(self, df):
        """Prepare data for model training"""
        # Calculate total expenses
        df['total_expenses'] = df[self.expense_categories].sum(axis=1)
        
        # Calculate total needs and wants
        df['total_needs'] = df[self.needs].sum(axis=1)
        df['total_wants'] = df[self.wants].sum(axis=1)
        
        # Calculate expense ratios
        for category in self.expense_categories:
            df[f'{category}_ratio'] = df[category] / df['total_expenses']
        
        # Add savings-related features
        df['savings_amount'] = df['income'] - df['total_expenses']
        df['savings_rate'] = df['savings_amount'] / df['income']
        
        # Add expense-to-income ratios
        df['expense_to_income_ratio'] = df['total_expenses'] / df['income']
        df['needs_to_income_ratio'] = df['total_needs'] / df['income']
        df['wants_to_income_ratio'] = df['total_wants'] / df['income']
            
        return df
    
    def _remove_outliers(self, df, columns, threshold=3):
        """Remove outliers using z-score method"""
        df_clean = df.copy()
        
        for col in columns:
            if col in df.columns:
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                df_clean = df_clean[z_scores < threshold]
                
        return df_clean
    
    def train_savings_models(self, df, categories_to_train=None):
        """Train models to predict potential savings for each category with improved techniques"""
        print("Training AI models to predict potential savings...")
        
        # If no categories specified, train all
        if categories_to_train is None:
            categories_to_train = self.savings_categories
        
        # Features that will be used for predictions
        numeric_features = [
            'income', 'age', 'dependents', 'total_expenses', 
            'total_needs', 'total_wants', 'savings_amount', 'savings_rate',
            'expense_to_income_ratio', 'needs_to_income_ratio', 'wants_to_income_ratio'
        ]
        
        # Add expense ratios
        for category in self.expense_categories:
            numeric_features.append(f'{category}_ratio')
        
        # Categorical features
        categorical_features = ['occupation', 'city_tier']
        
        # Train a model for each savings category
        for category in categories_to_train:
            print(f"Training model for {category}...")
            target = f'potential_savings_{category}'
            
            # Create features and target
            X_full = df[numeric_features + categorical_features]
            y_full = df[target]
            
            # Handle outliers
            outlier_columns = [target] + [cat for cat in self.expense_categories]
            df_cleaned = self._remove_outliers(df, outlier_columns)
            
            X = df_cleaned[numeric_features + categorical_features]
            y = df_cleaned[target]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42)
            
            # Setup preprocessor with better scaling
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', RobustScaler(), numeric_features),
                    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
                ])
            
            # Use a simpler approach for faster training
            # Create pipeline with feature engineering
            pipeline = Pipeline([
                ('preprocessor', preprocessor),
                ('feature_engineer', FeatureEngineer()),
                ('regressor', GradientBoostingRegressor(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=4,
                    random_state=42
                ))
            ])
            
            # Train model directly without hyperparameter tuning
            print(f"  - Training model...")
            pipeline.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = pipeline.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Print improvement if available
            print(f"  - Mean Absolute Error: ₹{mae:.2f}")
            print(f"  - R² Score: {r2:.4f}")
            
            # Store model
            self.models[category] = pipeline
            
            # Save after each model to avoid losing progress
            if not os.path.exists('models'):
                os.makedirs('models')
            joblib.dump(pipeline, os.path.join('models', f'{category}_savings_model.joblib'))
    
    def save_models(self, folder='models'):
        """Save trained models to disk"""
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        for category, model in self.models.items():
            joblib.dump(model, os.path.join(folder, f'{category}_savings_model.joblib'))
    
    def load_models(self, folder='models'):
        """Load saved models from disk"""
        for category in self.savings_categories:
            model_path = os.path.join(folder, f'{category}_savings_model.joblib')
            if os.path.exists(model_path):
                self.models[category] = joblib.load(model_path)
    
    def analyze_user_data(self, user_data):
        """Analyze individual user's financial data and predict potential savings"""
        # Ensure data is in DataFrame format
        if not isinstance(user_data, pd.DataFrame):
            user_data = pd.DataFrame([user_data])
            
        # Calculate total expenses
        user_data['total_expenses'] = user_data[self.expense_categories].sum(axis=1)
        user_data['total_needs'] = user_data[self.needs].sum(axis=1)
        user_data['total_wants'] = user_data[self.wants].sum(axis=1)
        
        # Calculate expense ratios
        for category in self.expense_categories:
            user_data[f'{category}_ratio'] = user_data[category] / user_data['total_expenses']
        
        # Add savings-related features
        user_data['savings_amount'] = user_data['income'] - user_data['total_expenses']
        user_data['savings_rate'] = user_data['savings_amount'] / user_data['income']
        
        # Add expense-to-income ratios
        user_data['expense_to_income_ratio'] = user_data['total_expenses'] / user_data['income']
        user_data['needs_to_income_ratio'] = user_data['total_needs'] / user_data['income']
        user_data['wants_to_income_ratio'] = user_data['total_wants'] / user_data['income']
            
        # Calculate current spending
        analysis = {
            'current_spending': {cat: user_data[cat].iloc[0] for cat in self.expense_categories},
            'total_expenses': user_data['total_expenses'].iloc[0],
            'total_needs': user_data['total_needs'].iloc[0],
            'total_wants': user_data['total_wants'].iloc[0],
            'needs_percentage': (user_data['total_needs'].iloc[0] / user_data['total_expenses'].iloc[0]) * 100,
            'wants_percentage': (user_data['total_wants'].iloc[0] / user_data['total_expenses'].iloc[0]) * 100,
            'savings_amount': user_data['savings_amount'].iloc[0],
            'savings_rate': user_data['savings_rate'].iloc[0] * 100
        }
        
        # Predict potential savings if models are available
        if self.models:
            analysis['predicted_savings'] = {}
            total_potential_savings = 0
            
            for category in self.savings_categories:
                if category in self.models:
                    # Predict potential savings
                    potential_savings = self.models[category].predict(user_data)[0]
                    
                    # Store prediction (ensure non-negative values)
                    analysis['predicted_savings'][category] = max(0, potential_savings)
                    total_potential_savings += max(0, potential_savings)
            
            analysis['total_potential_savings'] = total_potential_savings
            analysis['potential_savings_percentage'] = (total_potential_savings / analysis['total_expenses']) * 100
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis):
        """Generate personalized recommendations based on analysis and predicted savings"""
        recommendations = []
        
        # Check overall spending balance
        if analysis['needs_percentage'] > 75:
            recommendations.append("Your essential expenses are high relative to your income. Review fixed costs like rent or loans.")
        
        if analysis['wants_percentage'] > 35:
            recommendations.append("Your discretionary spending is higher than recommended. Consider cutting back on non-essential expenses.")
        
        # Add savings-based recommendations
        if 'predicted_savings' in analysis:
            # Recommend top 3 savings opportunities
            savings_items = sorted(analysis['predicted_savings'].items(), key=lambda x: x[1], reverse=True)[:3]
            
            for category, amount in savings_items:
                if amount > 0:
                    saving_percentage = (amount / analysis['current_spending'][category]) * 100
                    if saving_percentage >= 5:  # Only recommend meaningful savings (>= 5%)
                        recommendations.append(f"You could save approximately ₹{amount:.2f} ({saving_percentage:.1f}%) on {category} based on similar spending profiles.")
        
        # Add savings rate recommendations
        if analysis.get('savings_rate', 0) < 20:
            recommendations.append("Your savings rate is below the recommended 20%. Try increasing your monthly savings.")
        
        # Add general advice
        if len(recommendations) < 3:
            recommendations.append("Build an emergency fund covering 3-6 months of expenses.")
            
        if len(recommendations) < 3:
            recommendations.append("Consider the 50/30/20 rule: 50% needs, 30% wants, and 20% savings.")
        
        return recommendations 