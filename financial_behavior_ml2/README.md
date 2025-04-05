# Financial Behavior ML with Gemini-Powered Chatbot

This project analyzes financial behavior data and provides personalized insights and recommendations using machine learning. It now includes a Gemini AI-powered chatbot that can provide interactive financial advice.

## Features

- Financial data analysis with ML models
- Potential savings prediction
- Personalized financial recommendations
- AI-powered chatbot for interactive financial advice

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Make sure you have the `financial_behavior.csv` file in the project directory

3. Get a valid Gemini API key from [Google AI Studio](https://ai.google.dev/)
   - The provided default key may expire or have usage limitations
   - Update the API key in `finance_chatbot.py` if needed

## Usage

### Run Financial Analysis

To run just the financial analysis:

```
python main.py
```

### Test the Gemini API Connection

Before using the chatbot, you can test your API connection:

```
python test_gemini_api.py [YOUR_API_KEY]
```

If you don't provide an API key, it will use the default one in the script.

### Use the Chatbot

To run the financial analysis and start the interactive financial advisor chatbot:

```
python finance_chatbot.py
```

The chatbot will:

1. Run the financial analysis
2. Parse the results
3. Provide an interactive chat interface where you can ask questions about your finances
4. Provide personalized advice and insights based on your financial data

Example questions you can ask the chatbot:

- "How can I improve my savings?"
- "What areas should I prioritize for reducing expenses?"
- "Can you suggest a budget plan for me?"
- "How does my spending compare to recommended ratios?"
- "What's the most effective way to reduce my grocery expenses?"

## Troubleshooting

### API Issues

If you encounter API errors like:

```
404 models/gemini-pro is not found for API version v1beta
```

Try the following solutions:

1. Run the test script (`test_gemini_api.py`) to see available models
2. Get a new API key from [Google AI Studio](https://ai.google.dev/)
3. Check that your internet connection allows access to Google API endpoints
4. Make sure your google-generativeai library is up to date

The script automatically tries to find the best available model, but API models change over time.

## How It Works

The system uses a two-stage approach:

1. ML models analyze your financial data to identify potential savings
2. Gemini AI uses this analysis to provide personalized financial advice through an interactive chat interface
