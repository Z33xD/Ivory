import google.generativeai as genai
import sys

def test_gemini_api(api_key):
    """Test the Gemini API connection and functionality"""
    print("Testing Gemini API connection...")
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    try:
        # List available models
        models = genai.list_models()
        print("\nAvailable models:")
        for model in models:
            print(f"- {model.name}")
        
        # Find the most appropriate model for text generation
        text_models = [model.name for model in models if "generateContent" in model.supported_generation_methods]
        
        if text_models:
            selected_model = text_models[0]
            print(f"\nSelected model for testing: {selected_model}")
            
            # Initialize the model
            model = genai.GenerativeModel(selected_model)
            
            # Test a simple query
            print("\nTesting text generation...")
            response = model.generate_content("Hello, can you provide a one-sentence financial tip?")
            
            print(f"\nAPI Response: {response.text}")
            print("\nAPI test successful!")
            return True
        else:
            print("\nNo suitable text generation models found.")
            return False
    
    except Exception as e:
        print(f"\nError testing Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Gemini API Test Script")
    print("=====================")
    
    # Use command line argument if provided, otherwise use default
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = "AIzaSyDMQ0Tv2uyrDgPN7loV2Zg8cWMOAjSU0zM"
    
    print(f"Using API key: {api_key[:5]}...{api_key[-5:]}")
    
    # Run the test
    success = test_gemini_api(api_key)
    
    if success:
        print("\nYou can now use the finance_chatbot.py script.")
    else:
        print("\nGemini API test failed. Please check your API key and internet connection.")
        print("You might need to obtain a new API key from: https://ai.google.dev/") 