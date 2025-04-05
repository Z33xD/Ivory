import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

def evaluate_model(model, X, y, test_size=0.2, random_seed=42):
    """
    Evaluate a single model and return key metrics.
    
    Parameters:
    -----------
    model : trained model object
        The model to evaluate (must have a predict method)
    X : DataFrame
        Feature data
    y : Series
        Target data
    test_size : float
        Proportion of data to use for testing (default: 0.2)
    random_seed : int
        Random seed for reproducibility (default: 42)
        
    Returns:
    --------
    dict
        Dictionary containing evaluation metrics
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_seed)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Ensure predictions are non-negative
    y_pred = np.maximum(0, y_pred)
    
    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    # Calculate bias
    avg_pred = y_pred.mean()
    avg_actual = y_test.mean()
    bias = avg_pred - avg_actual
    bias_pct = (bias / avg_actual) * 100 if avg_actual > 0 else 0
    
    # Return metrics
    return {
        'R²': r2,
        'MAE': mae,
        'RMSE': rmse,
        'Avg Prediction': avg_pred,
        'Avg Actual': avg_actual,
        'Bias': bias,
        'Bias %': bias_pct
    }

def evaluate_all_models(processor, df=None, categories=None, test_size=0.2, random_seed=42):
    """
    Evaluate all models in the processor and return a DataFrame with metrics.
    
    Parameters:
    -----------
    processor : DataProcessor
        Instance of DataProcessor with loaded models
    df : DataFrame, optional
        Preprocessed data (if None, will load and preprocess)
    categories : list, optional
        List of categories to evaluate (if None, evaluates all)
    test_size : float
        Proportion of data to use for testing (default: 0.2)
    random_seed : int
        Random seed for reproducibility (default: 42)
        
    Returns:
    --------
    DataFrame
        DataFrame containing evaluation metrics for all models
    """
    # Load data if not provided
    if df is None:
        df = processor.load_data()
        df = processor.preprocess_data(df)
    
    # Use all categories if none specified
    if categories is None:
        categories = processor.savings_categories
    
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
        'Bias': [],
        'Bias %': []
    }
    
    # Evaluate each model
    for category in categories:
        if category in processor.models:
            target = f'potential_savings_{category}'
            
            # Get features and target
            X = df[numeric_features + categorical_features]
            y = df[target]
            
            # Evaluate model
            metrics = evaluate_model(
                processor.models[category], X, y, 
                test_size=test_size, random_seed=random_seed
            )
            
            # Store results
            results['Category'].append(category)
            for key, value in metrics.items():
                results[key].append(value)
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Calculate average metrics
    avg_row = {'Category': 'AVERAGE'}
    for key in results:
        if key != 'Category':
            avg_row[key] = results[key] and sum(results[key]) / len(results[key])
    
    # Add average row
    results_df = pd.concat([results_df, pd.DataFrame([avg_row])], ignore_index=True)
    
    return results_df

def get_model_quality(r2_score):
    """
    Get a qualitative assessment of model quality based on R² score.
    
    Parameters:
    -----------
    r2_score : float
        R² score to evaluate
        
    Returns:
    --------
    str
        Qualitative assessment ("Excellent", "Good", "Moderate", or "Poor")
    """
    if r2_score > 0.7:
        return "Excellent"
    elif r2_score > 0.5:
        return "Good"
    elif r2_score > 0.3:
        return "Moderate"
    else:
        return "Poor" 