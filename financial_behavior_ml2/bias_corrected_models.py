import numpy as np
import os
import joblib
from data_processor import DataProcessor
from model_evaluator import evaluate_all_models

class BiasCorrectedModel:
    """
    A wrapper class that applies a bias correction factor to model predictions.
    """
    
    def __init__(self, base_model, correction_factor=1.0):
        """
        Initialize a bias-corrected model.
        
        Parameters:
        -----------
        base_model : model object
            The original model to wrap (must have a predict method)
        correction_factor : float
            Multiplicative factor to apply to predictions (default: 1.0)
            e.g., 1.13 means predictions will be increased by 13%
        """
        self.base_model = base_model
        self.correction_factor = correction_factor
    
    def predict(self, X):
        """
        Make predictions with bias correction applied.
        
        Parameters:
        -----------
        X : array-like
            Features to make predictions for
            
        Returns:
        --------
        array
            Bias-corrected predictions
        """
        # Get base predictions
        base_predictions = self.base_model.predict(X)
        
        # Apply correction factor
        corrected_predictions = base_predictions * self.correction_factor
        
        return corrected_predictions
    
    def __getattr__(self, name):
        """
        Delegate attribute access to the base model for any attributes
        not explicitly defined in this class.
        """
        return getattr(self.base_model, name)

def create_bias_corrected_models(processor=None, bias_factors=None, save_models=True):
    """
    Create bias-corrected versions of all models.
    
    Parameters:
    -----------
    processor : DataProcessor object, optional
        If None, a new processor will be created and models loaded
    bias_factors : dict, optional
        Dictionary mapping category names to bias correction factors
        If None, factors will be calculated from model evaluation
    save_models : bool
        Whether to save the corrected models to disk (default: True)
        
    Returns:
    --------
    processor : DataProcessor object
        DataProcessor with bias-corrected models
    corrections : dict
        Dictionary of correction factors applied to each model
    """
    # Create processor if not provided
    if processor is None:
        processor = DataProcessor()
        processor.load_models()
    
    # Determine bias correction factors if not provided
    if bias_factors is None:
        # Calculate correction factors from model evaluation
        print("Evaluating models to determine correction factors...")
        eval_results = evaluate_all_models(processor)
        
        # Extract bias percentages and calculate correction factors
        bias_factors = {}
        for _, row in eval_results.iterrows():
            if row['Category'] != 'AVERAGE':
                # Convert from percentage to factor
                # Example: bias of -15% means we multiply by 1.15
                bias_pct = row['Bias %']
                correction_factor = 1.0 - (bias_pct / 100.0)
                bias_factors[row['Category']] = correction_factor
    
    # Apply correction factors to create new models
    corrected_models = {}
    for category, factor in bias_factors.items():
        if category in processor.models:
            print(f"Applying {factor:.2f}x correction factor to {category} model")
            corrected_models[category] = BiasCorrectedModel(
                processor.models[category], 
                correction_factor=factor
            )
    
    # Replace models in processor with corrected versions
    processor.models.update(corrected_models)
    
    # Save models if requested
    if save_models:
        output_dir = 'models_corrected'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for category, model in corrected_models.items():
            output_path = os.path.join(output_dir, f'{category}_savings_model_corrected.joblib')
            joblib.dump(model, output_path)
        print(f"Saved {len(corrected_models)} bias-corrected models to {output_dir}/")
    
    return processor, bias_factors

def load_bias_corrected_models(processor=None, model_dir='models_corrected'):
    """
    Load bias-corrected models from disk.
    
    Parameters:
    -----------
    processor : DataProcessor object, optional
        If None, a new processor will be created
    model_dir : str
        Directory containing the bias-corrected models
        
    Returns:
    --------
    processor : DataProcessor object
        DataProcessor with bias-corrected models loaded
    """
    if processor is None:
        processor = DataProcessor()
    
    # Load corrected models
    for category in processor.savings_categories:
        model_path = os.path.join(model_dir, f'{category}_savings_model_corrected.joblib')
        if os.path.exists(model_path):
            processor.models[category] = joblib.load(model_path)
    
    return processor

# Example usage
if __name__ == "__main__":
    # Create bias-corrected models
    processor, correction_factors = create_bias_corrected_models()
    
    # Print correction factors
    print("\nBias Correction Factors:")
    for category, factor in correction_factors.items():
        print(f"{category:<15}: {factor:.4f}x")
    
    # Evaluate corrected models
    print("\nEvaluating bias-corrected models:")
    corrected_results = evaluate_all_models(processor)
    
    # Print R² scores and bias percentages
    print("\nBias-Corrected Model Evaluation:")
    print("-" * 70)
    print(f"{'Category':<15} {'R²':<8} {'Bias %':<8} {'Status':<10}")
    print("-" * 70)
    
    # Show results for each model
    for _, row in corrected_results.iterrows():
        if row['Category'] != 'AVERAGE':
            category = row['Category']
            r2 = row['R²']
            bias_pct = row['Bias %']
            
            # Determine if bias is significantly improved
            status = "IMPROVED" if abs(bias_pct) < 5.0 else "NEEDS WORK"
            
            print(f"{category:<15} {r2:.4f}  {bias_pct:>6.2f}%  {status}")
    
    # Print average
    avg_row = corrected_results[corrected_results['Category'] == 'AVERAGE'].iloc[0]
    print("-" * 70)
    print(f"{'AVERAGE':<15} {avg_row['R²']:.4f}  {avg_row['Bias %']:>6.2f}%")
    print("-" * 70) 