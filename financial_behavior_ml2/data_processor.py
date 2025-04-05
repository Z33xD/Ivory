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
        
    def load_data(self, file_path=None):
        """Load and preprocess the financial behavior data"""
        # If file_path is not provided, try different locations
        if file_path is None:
            possible_paths = [
                'financial_behavior.csv',                     # In the current directory
                os.path.join('financial_behavior_ml2', 'financial_behavior.csv'),  # In the project subdirectory
                os.path.abspath(os.path.join(os.path.dirname(__file__), 'financial_behavior.csv'))  # Same directory as script
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = path
                    print(f"Found CSV file at: {path}")
                    break
            
            if file_path is None:
                raise FileNotFoundError("Could not find financial_behavior.csv in any expected location")
        
        # Read the CSV file
        print(f"Loading CSV from: {file_path}")
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
        loaded_models = 0
        missing_models = []
        
        for category in self.savings_categories:
            model_path = os.path.join(folder, f'{category}_savings_model.joblib')
            if os.path.exists(model_path):
                self.models[category] = joblib.load(model_path)
                loaded_models += 1
            else:
                missing_models.append(category)
        
        if loaded_models == 0 and len(missing_models) > 0:
            print(f"Warning: No models could be loaded from '{folder}' directory.")
            print(f"Missing models: {', '.join(missing_models)}")
            
            # Check if models exist in alternative directory
            alt_folder = 'models_corrected' if folder == 'models' else 'models'
            if os.path.exists(alt_folder):
                print(f"Checking alternative directory: {alt_folder}")
                for category in missing_models:
                    model_path = os.path.join(alt_folder, f'{category}_savings_model.joblib')
                    if os.path.exists(model_path):
                        self.models[category] = joblib.load(model_path)
                        print(f"Loaded {category} model from {alt_folder}")
                        loaded_models += 1
        
        print(f"Successfully loaded {loaded_models} out of {len(self.savings_categories)} models.")
    
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
            user_data[f'{category}_ratio'] = 0 if user_data['total_expenses'].iloc[0] == 0 else user_data[category] / user_data['total_expenses']
        
        # Add savings-related features
        user_data['savings_amount'] = user_data['income'] - user_data['total_expenses']
        user_data['savings_rate'] = 0 if user_data['income'].iloc[0] == 0 else user_data['savings_amount'] / user_data['income']
        
        # Add expense-to-income ratios
        user_data['expense_to_income_ratio'] = 0 if user_data['income'].iloc[0] == 0 else user_data['total_expenses'] / user_data['income']
        user_data['needs_to_income_ratio'] = 0 if user_data['income'].iloc[0] == 0 else user_data['total_needs'] / user_data['income']
        user_data['wants_to_income_ratio'] = 0 if user_data['income'].iloc[0] == 0 else user_data['total_wants'] / user_data['income']
            
        # Create the analysis dictionary
        analysis = {
            'current_spending': {},
            'income': user_data['income'].iloc[0],
            'total_expenses': user_data['total_expenses'].iloc[0],
            'total_needs': user_data['total_needs'].iloc[0],
            'total_wants': user_data['total_wants'].iloc[0],
            'needs_percentage': 0 if user_data['total_expenses'].iloc[0] == 0 else (user_data['total_needs'].iloc[0] / user_data['total_expenses'].iloc[0]) * 100,
            'wants_percentage': 0 if user_data['total_expenses'].iloc[0] == 0 else (user_data['total_wants'].iloc[0] / user_data['total_expenses'].iloc[0]) * 100,
        }
        
        # Add current spending for each category
        for category in self.expense_categories:
            analysis['current_spending'][category] = user_data[category].iloc[0]
        
        # Predict potential savings using the trained models
        if self.models:
            analysis['predicted_savings'] = {}
            total_potential_savings = 0
            
            # Make sure all models are checked
            for category in self.savings_categories:
                # Check if model exists for this category
                if category in self.models:
                    # Predict potential savings
                    try:
                        predicted_savings = self.models[category].predict(user_data)[0]
                        if predicted_savings > 0:  # Only include positive savings
                            analysis['predicted_savings'][category] = predicted_savings
                            total_potential_savings += predicted_savings
                    except Exception as e:
                        print(f"Error predicting savings for {category}: {str(e)}")
                        # Use a fallback value or continue
                        analysis['predicted_savings'][category] = 0
            
            # Add total potential savings and percentage
            analysis['total_potential_savings'] = total_potential_savings
            analysis['potential_savings_percentage'] = 0 if analysis['total_expenses'] == 0 else (total_potential_savings / analysis['total_expenses']) * 100
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis):
        """Generate personalized recommendations based on the analysis"""
        recommendations = []
        
        # Check overall expense-to-income ratio
        if 'income' in analysis:
            if analysis['total_expenses'] / analysis['income'] > 0.7:
                recommendations.append(
                    "Your essential expenses are high relative to your income. Review fixed costs like rent or loans."
                )
        else:
            # Default recommendation if income isn't available
            recommendations.append(
                "Your essential expenses are high relative to your income. Review fixed costs like rent or loans."
            )
        
        # Add savings recommendations
        if 'predicted_savings' in analysis:
            # Get top categories by potential savings amount
            sorted_savings = sorted(
                [(category, amount) for category, amount in analysis['predicted_savings'].items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            # Add top 3-5 savings recommendations
            for category, amount in sorted_savings[:4]:  # Limit to top 4
                if amount > 0:  # Only include positive savings
                    percentage = (amount / analysis['current_spending'][category]) * 100
                    recommendations.append(
                        f"You could save approximately ₹{amount:.2f} ({percentage:.1f}%) on {category} based on similar spending profiles."
                    )
        
        return recommendations 