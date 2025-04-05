import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from data_processor import DataProcessor

def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

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
    
    # Prepare evaluation results
    eval_results = {
        'Category': [],
        'R² Score': [],
        'MAE': [],  # Mean Absolute Error
        'RMSE': [],  # Root Mean Squared Error
        'MAPE (%)': [],  # Mean Absolute Percentage Error
        'Avg Predicted Savings': [],
        'Avg Actual Savings': []
    }
    
    # Define a consistent random seed for reproducibility
    random_seed = 42
    
    # Evaluate each model
    for category in processor.savings_categories:
        if category in processor.models:
            print(f"Evaluating model for {category}...")
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
            
            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = calculate_mape(y_test, y_pred)
            
            # Store results
            eval_results['Category'].append(category)
            eval_results['R² Score'].append(round(r2, 4))
            eval_results['MAE'].append(round(mae, 2))
            eval_results['RMSE'].append(round(rmse, 2))
            eval_results['MAPE (%)'].append(round(mape, 2))
            eval_results['Avg Predicted Savings'].append(round(y_pred.mean(), 2))
            eval_results['Avg Actual Savings'].append(round(y_test.mean(), 2))
    
    # Create DataFrame from results
    results_df = pd.DataFrame(eval_results)
    
    # Sort by R² Score
    results_df = results_df.sort_values('R² Score', ascending=False)
    
    # Calculate average metrics
    avg_metrics = {
        'Category': 'AVERAGE',
        'R² Score': results_df['R² Score'].mean(),
        'MAE': results_df['MAE'].mean(),
        'RMSE': results_df['RMSE'].mean(),
        'MAPE (%)': results_df['MAPE (%)'].mean(),
        'Avg Predicted Savings': results_df['Avg Predicted Savings'].mean(),
        'Avg Actual Savings': results_df['Avg Actual Savings'].mean()
    }
    
    # Append average row
    results_df = pd.concat([results_df, pd.DataFrame([avg_metrics])], ignore_index=True)
    
    # Print accuracy matrix
    print("\nModel Accuracy Matrix:")
    print("=" * 100)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 1000)
    print(results_df)
    print("=" * 100)
    
    # Print additional insights
    print("\nKey Insights:")
    best_model = results_df.iloc[0]['Category']
    worst_model = results_df.iloc[-2]['Category']  # -2 because -1 is the average row
    print(f"1. Best performing model: {best_model} (R² = {results_df.iloc[0]['R² Score']:.4f})")
    print(f"2. Worst performing model: {worst_model} (R² = {results_df.iloc[-2]['R² Score']:.4f})")
    
    # Calculate bias (systematic over/under prediction)
    prediction_bias = (results_df['Avg Predicted Savings'] - results_df['Avg Actual Savings']).mean()
    bias_percentage = (prediction_bias / results_df['Avg Actual Savings'].mean()) * 100
    print(f"3. Overall prediction bias: {prediction_bias:.2f} ({bias_percentage:.2f}%)")
    
    # Overall model quality assessment
    avg_r2 = results_df.iloc[-1]['R² Score']
    if avg_r2 > 0.7:
        quality = "Excellent"
    elif avg_r2 > 0.5:
        quality = "Good"
    elif avg_r2 > 0.3:
        quality = "Moderate"
    else:
        quality = "Poor"
    
    print(f"4. Overall model quality: {quality} (Avg R² = {avg_r2:.4f})")
    
    return results_df

if __name__ == "__main__":
    evaluate_models() 