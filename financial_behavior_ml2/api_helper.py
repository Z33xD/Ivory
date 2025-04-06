import os
import sys
import json
import requests
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApiHelper:
    """Helper class to interact with the financial API"""
    
    def __init__(self):
        # Try to import from API if available
        self.api_imported = False
        try:
            # Add parent directory to path
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.append(parent_dir)
            
            # Try importing from financial_behaviour_ml (note British spelling)
            from financial_behaviour_ml.src.api import generate_user_profile
            self.generate_user_profile = generate_user_profile
            self.api_imported = True
            logger.info("Successfully imported generate_user_profile from financial_behaviour_ml")
        except ImportError as e:
            logger.warning(f"Could not import from financial_behaviour_ml.src.api: {e}")
            self.generate_user_profile = None
    
    def get_generated_profile(self):
        """Get a generated user profile from API"""
        try:
            if self.api_imported and self.generate_user_profile:
                # Use imported function directly
                user_id = "chatbot_user"
                response = self.generate_user_profile(user_id)
                
                # Handle different response types
                if isinstance(response, tuple) and len(response) == 2:
                    # Function returned (jsonify(data), status_code)
                    profile_data = response[0].json
                elif hasattr(response, 'json'):
                    # Response is a Flask response object
                    profile_data = response.json
                else:
                    # Response is already a dictionary
                    profile_data = response
                
                if 'profile' in profile_data:
                    profile = profile_data['profile']
                else:
                    profile = profile_data
                
                logger.info("Successfully generated user profile using API function")
                return profile
            else:
                # Fallback to direct API call using requests
                logger.info("Attempting to call API endpoint directly")
                
                # Try to get API configuration from config file
                try:
                    from financial_behaviour_ml.config import MOCKAROO_API_KEY, MOCKAROO_ENDPOINT
                    response = requests.get(f"{MOCKAROO_ENDPOINT}?count=1&key={MOCKAROO_API_KEY}")
                    
                    if response.status_code == 200:
                        profile = response.json()[0]
                        
                        # Add calculated fields as the API would do
                        income = float(profile.get('Income', 0))
                        expenses = sum([
                            float(profile.get('Rent', 0)),
                            float(profile.get('Loan_Repayment', 0)),
                            float(profile.get('Insurance', 0)),
                            float(profile.get('Groceries', 0)),
                            float(profile.get('Transport', 0)),
                            float(profile.get('Eating_Out', 0)),
                            float(profile.get('Entertainment', 0)),
                            float(profile.get('Utilities', 0)),
                            float(profile.get('Healthcare', 0)),
                            float(profile.get('Education', 0)),
                            float(profile.get('Miscellaneous', 0))
                        ])
                        
                        savings_percentage = float(profile.get('Desired_Savings_Percentage', 10))
                        desired_savings = round(income * (savings_percentage / 100), 2)
                        disposable_income = round(income - expenses, 2)
                        
                        # Add calculated fields
                        profile['Desired_Savings'] = desired_savings
                        profile['Disposable_Income'] = disposable_income
                        
                        # Calculate potential savings for each category (30% of current spending)
                        for category in ['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 
                                        'Utilities', 'Healthcare', 'Education', 'Miscellaneous']:
                            savings_field = f'Potential_Savings_{category}'
                            profile[savings_field] = round(float(profile.get(category, 0)) * 0.3, 2)
                        
                        logger.info("Successfully generated profile using direct API call")
                        return profile
                    else:
                        logger.error(f"API returned error code: {response.status_code}")
                except Exception as e:
                    logger.error(f"Error calling API directly: {e}")
        
        except Exception as e:
            logger.error(f"Error generating profile: {e}")
        
        # If all methods fail, return None
        return None
    
    def convert_profile_to_dataframe(self, profile):
        """Convert a profile dictionary to a DataFrame for model prediction"""
        if not profile:
            return None
            
        # Create a DataFrame with the financial data
        try:
            df = pd.DataFrame({
                'income': [float(profile.get('Income', 30000))],
                'age': [int(profile.get('Age', 35))],
                'dependents': [int(profile.get('Dependents', 2))],
                'occupation': [profile.get('Occupation', 'Professional')],
                'city_tier': [profile.get('City_Tier', 'Tier_2')],
                'rent': [float(profile.get('Rent', 6000))],
                'loan_repayment': [float(profile.get('Loan_Repayment', 0))],
                'insurance': [float(profile.get('Insurance', 1000))],
                'groceries': [float(profile.get('Groceries', 4500))],
                'transport': [float(profile.get('Transport', 2000))],
                'eating_out': [float(profile.get('Eating_Out', 1800))],
                'entertainment': [float(profile.get('Entertainment', 1500))],
                'utilities': [float(profile.get('Utilities', 2000))],
                'healthcare': [float(profile.get('Healthcare', 1000))],
                'education': [float(profile.get('Education', 0))],
                'miscellaneous': [float(profile.get('Miscellaneous', 1200))]
            })
            
            return df
        except Exception as e:
            logger.error(f"Error converting profile to DataFrame: {e}")
            return None

# Test function
if __name__ == "__main__":
    helper = ApiHelper()
    profile = helper.get_generated_profile()
    if profile:
        print("Generated profile:")
        print(json.dumps(profile, indent=2))
        
        df = helper.convert_profile_to_dataframe(profile)
        if df is not None:
            print("\nConverted to DataFrame:")
            print(df.head())
    else:
        print("Failed to generate profile") 