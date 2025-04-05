from data_processor import DataProcessor
import pandas as pd
import os
import random

def evaluate_models(processor, df):
    """Evaluate all models without retraining them"""
    print("\nEvaluating all models for R² scores:")
    
    # Features that will be used for predictions
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
    
    # Evaluate each model
    for category in processor.savings_categories:
        target = f'potential_savings_{category}'
        
        # Create features and target
        X = df[numeric_features + categorical_features]
        y = df[target]
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)
        
        # Predict using trained model
        if category in processor.models:
            y_pred = processor.models[category].predict(X_test)
            from sklearn.metrics import r2_score
            r2 = r2_score(y_test, y_pred)
            print(f"{category}: R² Score: {r2:.4f}")

def main():
    # Initialize data processor
    processor = DataProcessor()
    
    # Load the actual CSV data
    print("Loading financial behavior data...")
    df = processor.load_data()
    
    # Preprocess data
    print("Preprocessing data...")
    df = processor.preprocess_data(df)
    
    # Create models directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')
    
    # Check which models need to be trained
    missing_models = []
    for category in processor.savings_categories:
        if not os.path.exists(f"models/{category}_savings_model.joblib"):
            missing_models.append(category)
    
    if missing_models:
        print(f"Training models for: {', '.join(missing_models)}")
        # Train only the missing models
        processor.train_savings_models(df, categories_to_train=missing_models)
    
    # Load all the models
    print("Loading all trained models...")
    processor.load_models()
    
    # Evaluate all models
    evaluate_models(processor, df)
    
    # Create a test case by sampling a real record from the dataset
    sample_idx = random.randint(0, len(df) - 1)
    user_data = df.iloc[[sample_idx]].copy()
    
    # Display user profile
    print("\nUser Profile:")
    print(f"Income: ₹{user_data['income'].iloc[0]:,.2f}")
    print(f"Age: {user_data['age'].iloc[0]}")
    print(f"Dependents: {user_data['dependents'].iloc[0]}")
    print(f"Occupation: {user_data['occupation'].iloc[0]}")
    print(f"City Tier: {user_data['city_tier'].iloc[0]}")
    
    # Analyze user's financial data using AI predictions
    print("\nAnalyzing user's financial data...")
    analysis = processor.analyze_user_data(user_data)
    
    # Display expense analysis
    print("\nExpense Analysis:")
    print("\nEssential Expenses (Needs):")
    for category in processor.needs:
        amount = analysis['current_spending'][category]
        print(f"{category.title()}: ₹{amount:,.2f}")
    
    print("\nDiscretionary Expenses (Wants):")
    for category in processor.wants:
        amount = analysis['current_spending'][category]
        print(f"{category.title()}: ₹{amount:,.2f}")
    
    # Display summary
    print("\nSummary:")
    print(f"Total Needs: ₹{analysis['total_needs']:,.2f} ({analysis['needs_percentage']:.1f}%)")
    print(f"Total Wants: ₹{analysis['total_wants']:,.2f} ({analysis['wants_percentage']:.1f}%)")
    
    # Display AI-predicted savings
    print("\nAI-Predicted Potential Savings:")
    if 'predicted_savings' in analysis:
        for category, amount in sorted(analysis['predicted_savings'].items(), 
                                     key=lambda x: x[1], reverse=True):
            if amount > 0:
                saving_percentage = (amount / analysis['current_spending'][category]) * 100
                print(f"{category.title()}: ₹{amount:,.2f} ({saving_percentage:.1f}% of current spending)")
        
        print(f"\nTotal Potential Savings: ₹{analysis['total_potential_savings']:,.2f}")
        print(f"This represents {analysis['potential_savings_percentage']:.1f}% of your total expenses")
    else:
        print("No AI predictions available. Please train the models first.")
    
    # Display AI-powered recommendations
    print("\nAI-Powered Recommendations:")
    for i, recommendation in enumerate(analysis['recommendations'], 1):
        print(f"{i}. {recommendation}")

if __name__ == "__main__":
    main() 