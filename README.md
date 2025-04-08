# **Ivory: AI-Powered Financial Assistant**

**Ivory** is our submission for the **Tech Solstice Codeathon** at **MAHE Bangalore** on **5th February 2025**.

This project aims to simplify personal finance management using ML-based insights and a conversational AI interface powered by **Google Gemini**. It combines automated financial analysis, personalized nudges, and an interactive chatbot — making smart financial decision-making accessible to everyone.

---

## Inspiration

Managing personal finances is often overwhelming — from tracking expenses to budgeting and making sense of spending habits. As students, we saw how many of our peers struggle with this. Ivory was born from this challenge — to create a **smart financial assistant** that:

- Tracks and analyzes expenses
    
- Predicts spending behavior
    
- Offers personalized savings suggestions
    
- Provides interactive financial advice via AI

---

## Tech Stack & Architecture

Ivory is built with a modular structure to ensure scalability and ease of development.

### **Backend**

- **Python** with **Flask** for serving API endpoints.
    
- **Gemini API** for conversational AI.
    
- **Pandas/Numpy/Scikit-learn** for data handling and ML analysis.
    
- **Mockaroo** used during development for realistic sample financial datasets.

### **Core Features**

- Financial data processing & feature engineering
    
- ML models for behavior prediction and savings suggestions
    
- Categorization and anomaly detection
    
- Interactive chatbot for AI-powered insights

---

## Project Structure

```
Ivory/
├── backend/
│   ├── financial_behavior_ml2/
│   │   ├── models/
│   │   ├── models_corrected/
│   │   ├── analyze_csv.py
│   │   ├── api_helper.py
│   │   ├── basic_eval.py
│   │   ├── bias_corrected_models.py
│   │   ├── data_processor.py
│   │   ├── evaluate_models.py
│   │   ├── finance_chatbot.py
│   │   ├── main.py
│   │   ├── model_evaluator.py
│   │   ├── model_trainer.py
│   │   ├── nudge_generator.py
│   │   ├── simple_eval.py
│   │   ├── test_gemini_api.py
│   │   ├── financial_behavior.csv
│   │   ├── model_accuracy.csv
│   │   └── model_accuracy_matrix.csv
│   └── requirements.txt
│
├── financial_behaviour_ml/
│   ├── calendar/
│   ├── models/
│   ├── src/
│   │   ├── api.py
│   │   ├── behavior_predictor.py
│   │   ├── data_processor.py
│   │   ├── expense_categorizer.py
│   │   └── savings_optimizer.py
│   ├── tests/
│   │   ├── test_categorizer.py
│   │   ├── test_optimizer.py
│   │   └── test_predictor.py
│   ├── app.py
│   ├── config.py
│   ├── financial_behavior.csv
│   └── requirements.txt
│
├── frontend/
│   ├── page/
│   │   ├── images/
│   │   ├── calendar.html
│   │   ├── index.html
│   │   ├── landing.html / .css / .js
│   │   ├── opt_out.html / .js
│   │   ├── rewards.html / .css
│   │   ├── stats.html / .js
│   │   └── style.css
│
├── models/
│   ├── eating_out_savings_model.joblib
│   ├── education_savings_model.joblib
│   ├── groceries_savings_model.joblib
│   ├── healthcare_savings_model.joblib
│   ├── miscellaneous_savings_model.joblib
│   ├── transport_savings_model.joblib
│   ├── utilities_savings_model.joblib
│   └── entertainment_savings_model.joblib

├── .gitignore
└── README.md
```

---

## Setup Instructions

1. **Install Dependencies:**
    
    ```
    pip install -r requirements.txt
    ```
    
2. **Add Financial Dataset:** Ensure `financial_behavior.csv` is placed in the appropriate directory.
    
3. **Set Up Gemini API Key:**
    
    - Get one from [Google AI Studio](https://ai.google.dev/)
        
    - Replace the default key in `finance_chatbot.py` if needed

---

## Usage

### Run Financial Analysis:

```bash
python main.py
```

### Test Gemini API:

```bash
python test_gemini_api.py [YOUR_API_KEY]
```

### Start Chatbot:

```bash
python finance_chatbot.py
```

The chatbot will:

- Run analysis
    
- Parse ML results
    
- Answer finance-related queries with personalized insights

---

## Sample Questions for Chatbot

- “How can I improve my savings?”
    
- “What are the biggest drains on my finances?”
    
- “Can you recommend a budget?”
    
- “Am I spending too much on food?”
    
- “How do I optimize transportation costs?”

---

## How It Works

1. **ML Layer:**
    
    - Models evaluate spending patterns and highlight potential savings.
        
    - Includes bias correction and savings optimization logic.
        
2. **AI Layer (Gemini):**
    
    - Parses model output
        
    - Provides contextual, user-specific responses via chat
        
3. **Frontend Layer:**
    
    - HTML/CSS-based dashboard for visualization
        
    - User-friendly interface for input & recommendations

---

## What We Learned

- Handling real-world Flask backend architecture
    
- Integrating external APIs (Mockaroo, Gemini)
    
- ML model training & evaluation under time constraints
    
- Team collaboration with Git under pressure
    
- Designing scalable, modular systems

---

## Challenges Faced

- Merge conflicts during rapid development
    
- Gemini model changes requiring updates
    
- Data inconsistencies from mock sources
    
- Limited time to implement full ML pipeline

---

## What’s Next?

- Replace rule-based insights with fully trained ML models
    
- Add manual entry & opt-out options
    
- Launch a fully interactive dashboard
    
- Integrate more advanced NLP techniques for conversation analysis

---