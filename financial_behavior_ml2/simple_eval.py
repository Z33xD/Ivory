import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from data_processor import DataProcessor

def evaluate_models():
    # Initialize data processor
    processor = DataProcessor()
    
    # Load and preprocess data
    print("Loading financial behavior data...")
    df = processor.load_data()
    print("Preprocessing data...")
    df = processor.preprocess_data(df)
    
    # Load all models
    print("Loading all trained models...")
    processor.load_models()
    
    # Features for prediction
    numeric_features = [
        'income', 'age', 'dependents', 'total_expenses', 
        'total_needs', 'total_wants', 'savings_amount', 'savings_rate',
        'expense_to_income_ratio', 'needs_to_income_ratio', 'wants_to_income_ratio'
    ]
    
    # Add expense ratios
    for category in processor.expense_categories:
        numeric_features.append(f'{category}_ratio')
    
    # Categorical features
    categorical_features = ['occupation', 'city_tier']
    
    # Define a consistent random seed for reproducibility
    random_seed = 42
    
    print("\nModel Accuracy Matrix:")
    print("=" * 70)
    print(f"{'Category':<15} {'R²':<10} {'MAE':<10} {'RMSE':<10} {'Bias %':<10}")
    print("-" * 70)
    
    # Track metrics for average calculation
    all_r2 = []
    all_mae = []
    all_rmse = []
    all_bias_pct = []
    
    # Evaluate each model
    for category in processor.savings_categories:
        if category in processor.models:
            target = f'potential_savings_{category}'
            
            # Create features and target
            X = df[numeric_features + categorical_features]
            y = df[target]
            
            # Split data with consistent random seed
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=random_seed)
            
            # Predict using model
            y_pred = processor.models[category].predict(X_test)
            
            # Ensure predictions are non-negative
            y_pred = np.maximum(0, y_pred)
            
            # Calculate metrics
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Calculate bias
            avg_pred = y_pred.mean()
            avg_actual = y_test.mean()
            bias_pct = ((avg_pred - avg_actual) / avg_actual) * 100 if avg_actual != 0 else 0
            
            # Print results
            print(f"{category:<15} {r2:.4f}     {mae:.2f}      {rmse:.2f}      {bias_pct:.2f}%")
            
            # Store for average calculation
            all_r2.append(r2)
            all_mae.append(mae)
            all_rmse.append(rmse)
            all_bias_pct.append(bias_pct)
    
    # Print average
    print("-" * 70)
    avg_r2 = sum(all_r2) / len(all_r2)
    avg_mae = sum(all_mae) / len(all_mae)
    avg_rmse = sum(all_rmse) / len(all_rmse)
    avg_bias_pct = sum(all_bias_pct) / len(all_bias_pct)
    print(f"{'AVERAGE':<15} {avg_r2:.4f}     {avg_mae:.2f}      {avg_rmse:.2f}      {avg_bias_pct:.2f}%")
    print("=" * 70)
    
    # Print key insights
    print("\nKey Insights:")
    best_idx = all_r2.index(max(all_r2))
    worst_idx = all_r2.index(min(all_r2))
    best_model = processor.savings_categories[best_idx]
    worst_model = processor.savings_categories[worst_idx]
    
    print(f"1. Best performing model: {best_model} (R² = {all_r2[best_idx]:.4f})")
    print(f"2. Worst performing model: {worst_model} (R² = {all_r2[worst_idx]:.4f})")
    print(f"3. Average bias percentage: {avg_bias_pct:.2f}%")
    
    # Overall model quality assessment
    if avg_r2 > 0.7:
        quality = "Excellent"
    elif avg_r2 > 0.5:
        quality = "Good"
    elif avg_r2 > 0.3:
        quality = "Moderate"
    else:
        quality = "Poor"
    
    print(f"4. Overall model quality: {quality} (Avg R² = {avg_r2:.4f})")

if __name__ == "__main__":
    evaluate_models() 