import os
import subprocess
import json
import sys
import google.generativeai as genai
from data_processor import DataProcessor
import pandas as pd
import re
# Import our new helper
from api_helper import ApiHelper

# Fix for Unicode handling in Windows terminals
if sys.platform == 'win32':
    # Override the Unicode encoding issues in Windows
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # Don't try to set locale directly as it's not supported on all Windows setups

class FinanceChatbot:
    def __init__(self, api_key):
        # Initialize Gemini API
        genai.configure(api_key=api_key)
        
        # List available models to find the right one
        try:
            available_models = [m.name for m in genai.list_models()]
            print("Available models:", available_models)
            
            # Find an appropriate model - try newer naming conventions first
            if "models/gemini-1.5-pro" in available_models:
                model_name = "models/gemini-1.5-pro"
            elif "models/gemini-1.0-pro" in available_models:
                model_name = "models/gemini-1.0-pro"
            elif "gemini-pro" in available_models:
                model_name = "gemini-pro"
            else:
                # Fallback to basic model name
                model_name = "gemini-pro"
                
            print(f"Using model: {model_name}")
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            print(f"Error initializing model list: {str(e)}")
            print("Falling back to default model name 'gemini-pro'")
            # Fallback to default model name
            self.model = genai.GenerativeModel("gemini-pro")
        
        self.chat = None
        self.user_data = None
        self.analysis_result = None
        
    def run_analysis(self, user_data=None):
        """Run the financial analysis using generated data if None provided"""
        if user_data is not None:
            # Store user data for future reference
            self.user_data = user_data
            # TODO: Implement custom user data analysis
            print("Custom user data analysis not yet implemented")
            return None
        else:
            # Run financial analysis directly using DataProcessor
            try:
                print("Running financial analysis directly...")
                processor = DataProcessor()
                
                # Load models from either models or models_corrected directory
                model_dir = 'models'
                if not os.path.exists('models') or len(os.listdir('models')) == 0:
                    if os.path.exists('models_corrected'):
                        model_dir = 'models_corrected'
                        print(f"Using models from {model_dir} directory...")
                
                # Load all the models
                print("Loading all trained models...")
                processor.load_models(folder=model_dir)
                
                # Use ApiHelper to generate realistic user data instead of using test data
                print("Generating user profile from API...")
                api_helper = ApiHelper()
                profile = api_helper.get_generated_profile()
                
                if profile:
                    # Convert profile to DataFrame for analysis
                    user_data = api_helper.convert_profile_to_dataframe(profile)
                    print("Successfully created user data from generated profile")
                else:
                    print("Failed to get generated profile, falling back to sample data")
                    # Load the data as fallback
                    print("Loading financial behavior data...")
                    df = processor.load_data()
                    
                    # Preprocess data
                    print("Preprocessing data...")
                    df = processor.preprocess_data(df)
                    
                    # Create a sample user for analysis by randomly selecting a row
                    import random
                    sample_idx = random.randint(0, len(df) - 1)
                    user_data = df.iloc[[sample_idx]].copy()
                
                # Generate user profile data for our structured format
                analysis = {
                    "user_profile": {
                        "income": f"{user_data['income'].iloc[0]:,.2f}",
                        "age": str(user_data['age'].iloc[0]),
                        "dependents": str(user_data['dependents'].iloc[0]),
                        "occupation": str(user_data['occupation'].iloc[0]),
                        "city_tier": str(user_data['city_tier'].iloc[0])
                    },
                    "expense_analysis": {
                        "needs": {},
                        "wants": {}
                    },
                    "summary": {},
                    "potential_savings": {},
                    "recommendations": []
                }
                
                # Analyze user's data
                print("Analyzing user's financial data...")
                full_analysis = processor.analyze_user_data(user_data)
                
                # Fill in the expense analysis
                for category in processor.needs:
                    amount = full_analysis['current_spending'][category]
                    analysis["expense_analysis"]["needs"][category] = f"{amount:,.2f}"
                
                for category in processor.wants:
                    amount = full_analysis['current_spending'][category]
                    analysis["expense_analysis"]["wants"][category] = f"{amount:,.2f}"
                
                # Fill in the summary
                analysis["summary"]["total_needs"] = f"{full_analysis['total_needs']:,.2f}"
                analysis["summary"]["needs_percentage"] = f"{full_analysis['needs_percentage']:.1f}"
                analysis["summary"]["total_wants"] = f"{full_analysis['total_wants']:,.2f}"
                analysis["summary"]["wants_percentage"] = f"{full_analysis['wants_percentage']:.1f}"
                
                # Fill in the potential savings
                if 'predicted_savings' in full_analysis:
                    for category, amount in full_analysis['predicted_savings'].items():
                        saving_percentage = (amount / full_analysis['current_spending'][category]) * 100
                        analysis["potential_savings"][category] = {
                            "amount": f"{amount:,.2f}",
                            "percentage": f"{saving_percentage:.1f}"
                        }
                
                    analysis["summary"]["total_potential_savings"] = f"{full_analysis['total_potential_savings']:,.2f}"
                    analysis["summary"]["potential_savings_percentage"] = f"{full_analysis['potential_savings_percentage']:.1f}"
                
                # Fill in the recommendations
                if 'recommendations' in full_analysis:
                    analysis["recommendations"] = full_analysis['recommendations']
                
                self.analysis_result = analysis
                return analysis
                
            except Exception as e:
                print(f"Error running direct analysis: {str(e)}")
                print("Falling back to parsing output from main.py")
                
                # Fall back to running main.py as a subprocess
                try:
                    # Use ascii encoding to avoid Unicode issues
                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "ascii"
                    
                    result = subprocess.run(['python', 'main.py'], 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        encoding='ascii',
                                        errors='replace',
                                        env=env)
                    
                    # Parse the output
                    output = result.stdout
                    self.analysis_result = self._parse_analysis_output(output)
                    return self.analysis_result
                except Exception as e:
                    print(f"Error with fallback method: {str(e)}")
                    # Create a minimal default analysis
                    self.analysis_result = self._create_default_analysis()
                    return self.analysis_result
    
    def _create_default_analysis(self):
        """Create a default analysis when actual analysis fails"""
        return {
            "user_profile": {
                "income": "30,000.00",
                "age": "35",
                "dependents": "2",
                "occupation": "Professional",
                "city_tier": "Tier_2"
            },
            "expense_analysis": {
                "needs": {
                    "Rent": "6,000.00",
                    "Groceries": "4,500.00",
                    "Utilities": "2,000.00",
                    "Transport": "2,000.00"
                },
                "wants": {
                    "Entertainment": "1,500.00",
                    "Eating_Out": "1,800.00",
                    "Miscellaneous": "1,200.00"
                }
            },
            "summary": {
                "total_needs": "14,500.00",
                "needs_percentage": "70.0",
                "total_wants": "4,500.00",
                "wants_percentage": "30.0",
                "total_potential_savings": "2,000.00",
                "potential_savings_percentage": "10.5"
            },
            "potential_savings": {
                "Groceries": {
                    "amount": "800.00",
                    "percentage": "17.8"
                },
                "Eating_Out": {
                    "amount": "350.00",
                    "percentage": "19.4"
                },
                "Entertainment": {
                    "amount": "300.00",
                    "percentage": "20.0"
                }
            },
            "recommendations": [
                "Your essential expenses are high relative to your income. Review fixed costs like rent or loans.",
                "You could save approximately 800.00 (17.8%) on groceries based on similar spending profiles.",
                "You could save approximately 350.00 (19.4%) on eating out based on similar spending profiles."
            ]
        }
    
    def _parse_analysis_output(self, output):
        """Parse the output from main.py into a structured format"""
        analysis = {
            "user_profile": {},
            "expense_analysis": {
                "needs": {},
                "wants": {}
            },
            "summary": {},
            "potential_savings": {},
            "recommendations": []
        }
        
        # Extract user profile
        profile_match = re.search(r'User Profile:(.*?)Analyzing', output, re.DOTALL)
        if profile_match:
            profile_text = profile_match.group(1)
            # Replace rupee symbol with Rs.
            income_match = re.search(r'Income: [Rs\.]?([\d,]+\.\d+)', profile_text)
            if income_match:
                analysis["user_profile"]["income"] = income_match.group(1)
            
            age_match = re.search(r'Age: (\d+)', profile_text)
            if age_match:
                analysis["user_profile"]["age"] = age_match.group(1)
            
            dependents_match = re.search(r'Dependents: (\d+)', profile_text)
            if dependents_match:
                analysis["user_profile"]["dependents"] = dependents_match.group(1)
            
            occupation_match = re.search(r'Occupation: (\w+)', profile_text)
            if occupation_match:
                analysis["user_profile"]["occupation"] = occupation_match.group(1)
            
            city_tier_match = re.search(r'City Tier: (\w+_\d+)', profile_text)
            if city_tier_match:
                analysis["user_profile"]["city_tier"] = city_tier_match.group(1)
        
        # Extract essential expenses
        needs_match = re.search(r'Essential Expenses \(Needs\):(.*?)Discretionary Expenses', output, re.DOTALL)
        if needs_match:
            needs_text = needs_match.group(1)
            for line in needs_text.strip().split('\n'):
                if ': ' in line:
                    parts = line.split(': ')
                    if len(parts) == 2:
                        category = parts[0].strip() 
                        # Extract just the number
                        amount_match = re.search(r'[Rs\.]?([\d,]+\.\d+)', parts[1])
                        if amount_match:
                            analysis["expense_analysis"]["needs"][category] = amount_match.group(1)
        
        # Extract discretionary expenses
        wants_match = re.search(r'Discretionary Expenses \(Wants\):(.*?)Summary', output, re.DOTALL)
        if wants_match:
            wants_text = wants_match.group(1)
            for line in wants_text.strip().split('\n'):
                if ': ' in line:
                    parts = line.split(': ')
                    if len(parts) == 2:
                        category = parts[0].strip()
                        # Extract just the number
                        amount_match = re.search(r'[Rs\.]?([\d,]+\.\d+)', parts[1])
                        if amount_match:
                            analysis["expense_analysis"]["wants"][category] = amount_match.group(1)
        
        # Extract summary
        summary_match = re.search(r'Summary:(.*?)AI-Predicted Potential Savings', output, re.DOTALL)
        if summary_match:
            summary_text = summary_match.group(1)
            
            total_needs_match = re.search(r'Total Needs: [Rs\.]?([\d,]+\.\d+) \((\d+\.\d+)%\)', summary_text)
            if total_needs_match:
                analysis["summary"]["total_needs"] = total_needs_match.group(1)
                analysis["summary"]["needs_percentage"] = total_needs_match.group(2)
            
            total_wants_match = re.search(r'Total Wants: [Rs\.]?([\d,]+\.\d+) \((\d+\.\d+)%\)', summary_text)
            if total_wants_match:
                analysis["summary"]["total_wants"] = total_wants_match.group(1)
                analysis["summary"]["wants_percentage"] = total_wants_match.group(2)
        
        # Extract potential savings
        savings_match = re.search(r'AI-Predicted Potential Savings:(.*?)Total Potential Savings', output, re.DOTALL)
        if savings_match:
            savings_text = savings_match.group(1)
            for line in savings_text.strip().split('\n'):
                if ': ' in line:
                    parts = line.split(': ')
                    if len(parts) == 2:
                        category = parts[0].strip()
                        saving_info = parts[1].strip()
                        amount_match = re.search(r'[Rs\.]?([\d,]+\.\d+) \((\d+\.\d+)%', saving_info)
                        if amount_match:
                            analysis["potential_savings"][category] = {
                                "amount": amount_match.group(1),
                                "percentage": amount_match.group(2)
                            }
        
        # Extract total potential savings
        total_savings_match = re.search(r'Total Potential Savings: [Rs\.]?([\d,]+\.\d+)', output)
        if total_savings_match:
            analysis["summary"]["total_potential_savings"] = total_savings_match.group(1)
        
        savings_pct_match = re.search(r'This represents (\d+\.\d+)% of your total expenses', output)
        if savings_pct_match:
            analysis["summary"]["potential_savings_percentage"] = savings_pct_match.group(1)
        
        # Extract recommendations
        recommendations_match = re.search(r'AI-Powered Recommendations:(.*?)$', output, re.DOTALL)
        if recommendations_match:
            recommendations_text = recommendations_match.group(1)
            for line in recommendations_text.strip().split('\n'):
                # Look for numbered recommendations
                if re.match(r'\d+\.', line.strip()):
                    recommendation = re.sub(r'^\d+\.\s+', '', line.strip())
                    analysis["recommendations"].append(recommendation)
        
        # Check if we have a valid analysis, otherwise use default
        if (not analysis["user_profile"] or 
            not analysis["expense_analysis"]["needs"] or 
            not analysis["summary"] or 
            not analysis["recommendations"]):
            print("Incomplete analysis results, using default values")
            return self._create_default_analysis()
            
        return analysis
    
    def start_chat(self):
        """Start a new chat session with context from the financial analysis"""
        if not self.analysis_result:
            print("No analysis results found. Running analysis first...")
            self.run_analysis()
            
        if not self.analysis_result:
            print("Failed to generate financial analysis. Cannot start chat.")
            return
        
        # Prepare context for the chatbot
        system_prompt = """
You are a professional but approachable financial advisor. You provide useful information with a balanced tone - neither overly enthusiastic nor too cold and direct. Show some empathy when appropriate, but remain focused on delivering value.

Your communication style:
- Be clear and concise, but not abrupt
- Show some warmth when discussing personal financial concerns
- Use a professional but conversational tone
- Allow some personality to come through in your responses
- Maintain an appropriate level of formality without being stiff
- Be helpful without excessive enthusiasm
- Keep answers focused but not unnecessarily terse

Here's the financial analysis for this user:
"""
        system_prompt += f"""
USER PROFILE:
- Income: Rs.{self.analysis_result.get("user_profile", {}).get("income", "N/A")}
- Age: {self.analysis_result.get("user_profile", {}).get("age", "N/A")}
- Dependents: {self.analysis_result.get("user_profile", {}).get("dependents", "N/A")}
- Occupation: {self.analysis_result.get("user_profile", {}).get("occupation", "N/A")}
- City Tier: {self.analysis_result.get("user_profile", {}).get("city_tier", "N/A")}

EXPENSE ANALYSIS:
Essential Expenses (Needs):
{self._format_dict_items(self.analysis_result.get("expense_analysis", {}).get("needs", {}))}

Discretionary Expenses (Wants):
{self._format_dict_items(self.analysis_result.get("expense_analysis", {}).get("wants", {}))}

SUMMARY:
- Total Needs: Rs.{self.analysis_result.get("summary", {}).get("total_needs", "N/A")} ({self.analysis_result.get("summary", {}).get("needs_percentage", "N/A")}%)
- Total Wants: Rs.{self.analysis_result.get("summary", {}).get("total_wants", "N/A")} ({self.analysis_result.get("summary", {}).get("wants_percentage", "N/A")}%)
- Total Potential Savings: Rs.{self.analysis_result.get("summary", {}).get("total_potential_savings", "N/A")} ({self.analysis_result.get("summary", {}).get("potential_savings_percentage", "N/A")}% of total expenses)

POTENTIAL SAVINGS:
{self._format_savings_items(self.analysis_result.get("potential_savings", {}))}

RECOMMENDATIONS:
{self._format_list_items(self.analysis_result.get("recommendations", []))}

Based on this analysis, provide factual information and answer questions.
"""
        
        # Super minimal output - just a welcome message and nothing else
        print("\nFinancial Advisor here. How can I assist with your finances today? Type 'exit' when done.")
        
        try:
            # Initialize the chat history but don't display anything
            chat_history = []
            chat_history.append({"role": "user", "content": system_prompt})
            chat_history.append({"role": "model", "content": "Ready to provide financial guidance."})
            
            # Chat loop
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    print("Financial Advisor: Thanks for the discussion. Feel free to return when you need more financial guidance.")
                    break
                
                try:
                    # Add user input to history
                    chat_history.append({"role": "user", "content": user_input})
                    
                    # Create context with history
                    context = []
                    # Include only the last 10 exchanges to avoid exceeding context limits
                    for item in chat_history[-10:]:
                        context.append(item["content"])
                    
                    # Generate response
                    response = self.model.generate_content(context)
                    response_text = response.text
                    
                    print(f"\nFinancial Advisor: {response_text}\n")
                    
                    # Add response to history
                    chat_history.append({"role": "model", "content": response_text})
                    
                except Exception as e:
                    print(f"\nI'm having some trouble processing that: {str(e)}")
                    print("Let me try a different approach.\n")
                    
                    try:
                        # Try simplified generation without full history
                        simplified_context = [system_prompt, user_input]
                        simplified_response = self.model.generate_content(simplified_context)
                        simplified_text = simplified_response.text
                        
                        print(f"\nFinancial Advisor: {simplified_text}\n")
                        
                        # Reset history with this successful exchange
                        chat_history = [
                            {"role": "user", "content": system_prompt},
                            {"role": "model", "content": simplified_text}
                        ]
                        
                    except Exception as retry_error:
                        print(f"Sorry, we're experiencing technical difficulties: {str(retry_error)}")
                        print("Please try asking your question in a different way.")
        
        except Exception as e:
            print(f"Unable to continue the conversation: {str(e)}")
            
            # Try a fallback approach with direct content generation
            try:
                print("\nLet me provide some general guidance instead...")
                response = self.model.generate_content(
                    "You are a balanced and professional financial advisor with a warm tone. Provide concise but helpful general information about personal finance.",
                    generation_config={"temperature": 0.2}
                )
                print(f"\nFinancial Advisor: {response.text}")
                print("\nNote: I couldn't access your specific financial data at this time.")
                print("Please check your connection and try again later.")
            except Exception as fallback_error:
                print(f"Still having trouble connecting: {str(fallback_error)}")
                print("Please verify your API key and internet connection.")
    
    def _format_dict_items(self, items_dict):
        """Format dictionary items for the prompt"""
        result = ""
        for key, value in items_dict.items():
            result += f"- {key}: Rs.{value}\n"
        return result
    
    def _format_savings_items(self, savings_dict):
        """Format savings items for the prompt"""
        result = ""
        for category, details in savings_dict.items():
            result += f"- {category}: Rs.{details.get('amount', '0.00')} ({details.get('percentage', '0.0')}% of current spending)\n"
        return result
    
    def _format_list_items(self, items_list):
        """Format list items for the prompt"""
        result = ""
        for i, item in enumerate(items_list, 1):
            result += f"{i}. {item}\n"
        return result

if __name__ == "__main__":
    # Gemini API key
    API_KEY = "AIzaSyDMQ0Tv2uyrDgPN7loV2Zg8cWMOAjSU0zM"
    
    # Create chatbot
    chatbot = FinanceChatbot(API_KEY)
    
    # Run financial analysis
    chatbot.run_analysis()
    
    # Start chat interface
    chatbot.start_chat()

def get_response(self, message):
    """Generate a single response to a user message"""
    if not self.analysis_result:
        self.run_analysis()
        
    try:
        # Create context with system prompt and user message
        context = [
            self._create_system_prompt(),
            message
        ]
        
        # Generate response
        response = self.model.generate_content(context)
        return response.text
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I apologize, but I'm having trouble generating a response. Please try again."

def _create_system_prompt(self):
    """Create the system prompt with financial analysis context"""
    return f"""
You are a helpful and knowledgeable financial advisor chatbot. You have analyzed the user's financial data and will provide personalized advice based on this analysis:

USER PROFILE:
Income: Rs.{self.analysis_result.get("user_profile", {}).get("income", "N/A")}
Age: {self.analysis_result.get("user_profile", {}).get("age", "N/A")}
Dependents: {self.analysis_result.get("user_profile", {}).get("dependents", "N/A")}

EXPENSE SUMMARY:
Total Needs: Rs.{self.analysis_result.get("summary", {}).get("total_needs", "N/A")}
Total Wants: Rs.{self.analysis_result.get("summary", {}).get("total_wants", "N/A")}
Potential Savings: Rs.{self.analysis_result.get("summary", {}).get("total_potential_savings", "N/A")}

Provide specific, actionable financial advice based on this data.
"""