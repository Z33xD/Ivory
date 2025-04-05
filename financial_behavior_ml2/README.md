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

## Usage

### Run Financial Analysis

To run just the financial analysis:

```
python main.py
```

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

## How It Works

The system uses a two-stage approach:

1. ML models analyze your financial data to identify potential savings
2. Gemini AI uses this analysis to provide personalized financial advice through an interactive chat interface
