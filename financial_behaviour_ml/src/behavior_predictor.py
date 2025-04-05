import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from config import *

class BehaviorPredictor:
    def __init__(self):
        self.model = self.build_model()
    
    def build_model(self):
        """Build the ML pipeline"""
        numeric_features = ['income', 'age', 'dependents', 'total_needs', 'total_wants', 'savings_ratio', 'disposable_ratio']
        categorical_features = ['occupation', 'city_tier']
        
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        return Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(random_state=RANDOM_STATE))
        ])
    
    def train_and_save(self, X_train, y_train):
        """Train and save the model"""
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, MODEL_PATH)
    
    def predict_behavior(self, user_data):
        """Predict a user's savings behavior"""
        # Prepare features
        features = pd.DataFrame([{
            'income': user_data['income'],
            'age': user_data['age'],
            'dependents': user_data['dependents'],
            'occupation': user_data['occupation'],
            'city_tier': user_data['city_tier'],
            'total_needs': user_data['total_needs'],
            'total_wants': user_data['total_wants'],
            'savings_ratio': user_data['savings_ratio'],
            'disposable_ratio': user_data['disposable_ratio']
        }])
        
        return self.model.predict(features)[0]