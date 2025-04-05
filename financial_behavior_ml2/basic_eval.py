import pandas as pd
import numpy as np
import os
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from data_processor import DataProcessor

def main():
    # Initialize data processor
    processor = DataProcessor()
    
    # Load and preprocess data
    print("Loading data...")
    df = processor.load_data()
    df = processor.preprocess_data(df)
    
    # Check available models
    available_models = []
    for category in processor.savings_categories:
        model_path = os.path.join('models', f'{category}_savings_model.joblib')
        if os.path.exists(model_path):
            available_models.append(category)
    
    print(f"\nFound {len(available_models)} models: {', '.join(available_models)}")
    
    # Load models
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
    
    # Create results structure
    results = {
        'Category': [],
        'R²': [],
        'MAE': [],
        'RMSE': [],
        'Avg Prediction': [],
        'Avg Actual': [],
        'Bias %': []
    }
    
    # Simple evaluation
    print("\nAccuracy metrics for each model:")
    print("-" * 70)
    print(f"{'Category':<15} {'R²':<8} {'MAE':<8} {'RMSE':<8} {'Bias %':<8}")
    print("-" * 70)
    
    for category in available_models:
        if category in processor.models:
            target = f'potential_savings_{category}'
            
            # Create features and target
            X = df[numeric_features + categorical_features]
            y = df[target]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42)
            
            # Predict
            y_pred = processor.models[category].predict(X_test)
            
            # Calculate metrics
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Calculate bias
            avg_pred = y_pred.mean()
            avg_actual = y_test.mean()
            bias_pct = ((avg_pred - avg_actual) / avg_actual) * 100 if avg_actual > 0 else 0
            
            # Store results
            results['Category'].append(category)
            results['R²'].append(r2)
            results['MAE'].append(mae)
            results['RMSE'].append(rmse)
            results['Avg Prediction'].append(avg_pred)
            results['Avg Actual'].append(avg_actual)
            results['Bias %'].append(bias_pct)
            
            # Print results
            print(f"{category:<15} {r2:.4f}  {mae:.2f}  {rmse:.2f}  {bias_pct:.2f}%")
    
    # Calculate average
    for key in results:
        if key != 'Category':
            results[key].append(sum(results[key]) / len(results[key]))
    results['Category'].append('AVERAGE')
    
    # Print average
    print("-" * 70)
    avg_r2 = results['R²'][-1]
    avg_mae = results['MAE'][-1]
    avg_rmse = results['RMSE'][-1]
    avg_bias = results['Bias %'][-1]
    print(f"{'AVERAGE':<15} {avg_r2:.4f}  {avg_mae:.2f}  {avg_rmse:.2f}  {avg_bias:.2f}%")
    
    # Save to CSV
    pd.DataFrame(results).to_csv('model_accuracy_matrix.csv', index=False)
    print("\nFull accuracy matrix saved to model_accuracy_matrix.csv")
    
    # Print model quality assessment
    if avg_r2 > 0.7:
        quality = "Excellent"
    elif avg_r2 > 0.5:
        quality = "Good"
    elif avg_r2 > 0.3:
        quality = "Moderate"
    else:
        quality = "Poor"
    
    print(f"\nOverall model quality: {quality} (Avg R² = {avg_r2:.4f})")

if __name__ == "__main__":
    main() 