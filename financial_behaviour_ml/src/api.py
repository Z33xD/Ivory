from flask import Flask, request, jsonify, session
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import jwt
import hashlib
from functools import wraps
import requests
import sys
import logging
import uuid
from finance_chatbot import FinanceChatbot
import os

# Initialize chatbot
API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDMQ0Tv2uyrDgPN7loV2Zg8cWMOAjSU0zM')
chatbot = FinanceChatbot(API_KEY)

@app.route('/chat', methods=['POST'])
@token_required
def chat(current_user):
    """Handle chat messages"""
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Get user's financial data for context
        user_profile = user_profiles.get(current_user, {})
        
        # Initialize chatbot with user data if not already done
        if not chatbot.analysis_result:
            chatbot.run_analysis(user_profile)

        # Generate response using Gemini
        response = chatbot.get_response(data['message'])
        
        return jsonify({
            "reply": response,
            "status": "success"
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    JWT_SECRET, 
    MOCKAROO_API_KEY, 
    MOCKAROO_ENDPOINT,
    SPENDING_THRESHOLDS
)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory storage (replace with database in production)
users = {}
user_profiles = {}
transactions = {}
user_preferences = {}

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
            
        if token.startswith('Bearer '):
            token = token[7:]  # Remove 'Bearer ' prefix
            
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated

# Hash function for passwords (basic, use more secure in production)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to get recent transactions (last 7 days)
def get_recent_transactions(user_id):
    if user_id not in transactions:
        return []
    
    one_week_ago = datetime.now() - timedelta(days=7)
    return [
        tx for tx in transactions[user_id] 
        if datetime.fromisoformat(tx['timestamp']) >= one_week_ago
    ]

# Function to update user profile based on a transaction
def update_user_profile(user_id, transaction):
    if user_id not in user_profiles:
        return
    
    profile = user_profiles[user_id]
    category = transaction.get('category', 'miscellaneous')
    amount = float(transaction.get('amount', 0))
    
    # Map transaction category to profile field
    category_map = {
        'groceries': 'Groceries',
        'transport': 'Transport',
        'eating_out': 'Eating_Out',
        'entertainment': 'Entertainment',
        'utilities': 'Utilities',
        'healthcare': 'Healthcare',
        'education': 'Education',
        'miscellaneous': 'Miscellaneous'
    }
    
    profile_category = category_map.get(category.lower(), 'Miscellaneous')
    
    # Update the spending in that category
    if profile_category in profile:
        profile[profile_category] += amount
    
    # Update disposable income
    if 'Disposable_Income' in profile:
        profile['Disposable_Income'] -= amount
    
    # Recalculate potential savings based on new spending patterns
    update_potential_savings(user_id)

# Function to calculate potential savings for each category
def update_potential_savings(user_id):
    if user_id not in user_profiles:
        return
    
    profile = user_profiles[user_id]
    
    # Simple logic: potential savings is 10% of current spending in each category
    for category in ['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 
                    'Utilities', 'Healthcare', 'Education', 'Miscellaneous']:
        if category in profile:
            savings_field = f'Potential_Savings_{category}'
            profile[savings_field] = round(profile[category] * 0.1, 2)
    
    # Update desired savings based on income
    if 'Income' in profile and 'Desired_Savings_Percentage' in profile:
        profile['Desired_Savings'] = round(profile['Income'] * (profile['Desired_Savings_Percentage'] / 100), 2)

# Routes
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
        
    username = data['username']
    password = data['password']
    
    # Mock authentication (replace with database in production)
    if username not in users:
        # For demo, create user if not exists
        users[username] = {
            'password': hash_password(password),
            'user_id': str(len(users) + 1)
        }
        
        # Generate initial profile for new user
        try:
            generate_user_profile(username)
        except Exception as e:
            logger.error(f"Error generating user profile: {e}")
    
    stored_password = users[username]['password']
    
    if hash_password(password) == stored_password:
        # Generate JWT token
        token = jwt.encode(
            {'user_id': username, 'exp': datetime.utcnow().timestamp() + 3600},
            JWT_SECRET,
            algorithm="HS256"
        )
        
        return jsonify({
            'token': token,
            'user_id': username,
            'profile': user_profiles.get(username, {})
        })
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/generate_profile', methods=['GET'])
@token_required
def generate_user_profile(current_user):
    """Generate a financial profile for the user using Mockaroo"""
    try:
        # Define the fields we need from Mockaroo
        fields = [
            "Income", "Age", "Dependents", "Occupation", "City_Tier", 
            "Rent", "Loan_Repayment", "Insurance", "Groceries", 
            "Transport", "Eating_Out", "Entertainment", "Utilities", 
            "Healthcare", "Education", "Miscellaneous", 
            "Desired_Savings_Percentage"
        ]
        
        # Make request to Mockaroo for a single record
        headers = {'X-API-Key': MOCKAROO_API_KEY}
        response = requests.get(f"{MOCKAROO_ENDPOINT}?count=1&key={MOCKAROO_API_KEY}")
        
        if response.status_code == 200:
            profile_data = response.json()[0]
            
            # Calculate derived fields
            income = float(profile_data.get('Income', 0))
            expenses = sum([
                float(profile_data.get('Rent', 0)),
                float(profile_data.get('Loan_Repayment', 0)),
                float(profile_data.get('Insurance', 0)),
                float(profile_data.get('Groceries', 0)),
                float(profile_data.get('Transport', 0)),
                float(profile_data.get('Eating_Out', 0)),
                float(profile_data.get('Entertainment', 0)),
                float(profile_data.get('Utilities', 0)),
                float(profile_data.get('Healthcare', 0)),
                float(profile_data.get('Education', 0)),
                float(profile_data.get('Miscellaneous', 0))
            ])
            
            savings_percentage = float(profile_data.get('Desired_Savings_Percentage', 10))
            desired_savings = round(income * (savings_percentage / 100), 2)
            disposable_income = round(income - expenses, 2)
            
            # Add calculated fields
            profile_data['Desired_Savings'] = desired_savings
            profile_data['Disposable_Income'] = disposable_income
            
            # Calculate potential savings for each category (10% of current spending)
            for category in ['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 
                            'Utilities', 'Healthcare', 'Education', 'Miscellaneous']:
                savings_field = f'Potential_Savings_{category}'
                profile_data[savings_field] = round(float(profile_data.get(category, 0)) * 0.3, 2)
            
            # Store the profile
            user_profiles[current_user] = profile_data
            
            # Initialize transactions list for the user
            if current_user not in transactions:
                transactions[current_user] = []
            
            return jsonify({
                "message": "User profile generated successfully",
                "profile": profile_data
            })
        else:
            return jsonify({"error": f"Mockaroo API returned status code {response.status_code}"}), 400
            
    except Exception as e:
        logger.error(f"Error generating user profile: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get the user's financial profile"""
    if current_user not in user_profiles:
        return jsonify({"error": "Profile not found"}), 404
        
    return jsonify(user_profiles[current_user])

@app.route('/submit_transaction', methods=['POST'])
@token_required
def submit_transaction(current_user):
    data = request.json
    
    if not data:
        return jsonify({"error": "No transaction data provided"}), 400
        
    # Process single transaction or batch
    if isinstance(data, list):
        new_transactions = data
    else:
        new_transactions = [data]
    
    result_transactions = []
    
    # Initialize user transaction list if not exists
    if current_user not in transactions:
        transactions[current_user] = []
    
    for tx in new_transactions:
        # Add timestamp and transaction ID if not provided
        if 'timestamp' not in tx:
            tx['timestamp'] = datetime.now().isoformat()
        if 'transaction_id' not in tx:
            tx['transaction_id'] = str(uuid.uuid4())
            
        # Update the user profile based on this transaction
        update_user_profile(current_user, tx)
            
        # Add to list of processed transactions
        result_transactions.append(tx)
            
    # Add transactions to user history
    transactions[current_user].extend(result_transactions)
    
    # Save transactions to processed data folder
    try:
        df = pd.DataFrame(transactions[current_user])
        os.makedirs('data/processed', exist_ok=True)
        df.to_csv(f'data/processed/user_{current_user}_transactions.csv', index=False)
    except Exception as e:
        logger.error(f"Error saving transactions: {e}")
    
    return jsonify({
        "message": f"{len(result_transactions)} transaction(s) added successfully",
        "transactions": result_transactions,
        "updated_profile": user_profiles.get(current_user, {})
    })

@app.route('/get_transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    """Get all transactions for the user"""
    if current_user not in transactions:
        return jsonify([])
    
    # Optional: filter by date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    user_txs = transactions[current_user]
    
    if start_date:
        start = datetime.fromisoformat(start_date)
        user_txs = [tx for tx in user_txs if datetime.fromisoformat(tx['timestamp']) >= start]
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        user_txs = [tx for tx in user_txs if datetime.fromisoformat(tx['timestamp']) <= end]
    
    return jsonify(user_txs)

@app.route('/get_recent_transactions', methods=['GET'])
@token_required
def get_user_recent_transactions(current_user):
    """Get transactions from the last 7 days"""
    recent_txs = get_recent_transactions(current_user)
    return jsonify(recent_txs)

@app.route('/get_alerts', methods=['GET'])
@token_required
def get_alerts(current_user):
    """Get spending alerts based on recent transactions"""
    if current_user not in user_profiles:
        return jsonify([])
        
    # Check if user has opted out
    if current_user in user_preferences and user_preferences[current_user].get('opted_out', False):
        return jsonify({"message": "User has opted out of tracking"}), 403
    
    profile = user_profiles[current_user]
    recent_txs = get_recent_transactions(current_user)
    
    # Calculate spending by category in the last week
    spending_by_category = {}
    for tx in recent_txs:
        category = tx.get('category', 'other').lower()
        amount = float(tx.get('amount', 0))
        
        if category not in spending_by_category:
            spending_by_category[category] = 0
        spending_by_category[category] += amount
    
    alerts = []
    
    # Generate alerts based on thresholds
    for category, spent in spending_by_category.items():
        if category in SPENDING_THRESHOLDS and spent > SPENDING_THRESHOLDS[category]:
            alerts.append({
                "category": category,
                "amount_spent": spent,
                "threshold": SPENDING_THRESHOLDS[category],
                "message": f"You've spent ₹{spent:.2f} on {category} this week, which exceeds your ₹{SPENDING_THRESHOLDS[category]} threshold!"
            })
    
    # Check if user is on track for their savings goal
    if 'Desired_Savings' in profile and 'Income' in profile:
        weekly_savings_goal = profile['Desired_Savings'] / 4  # Assuming monthly savings goal
        
        total_spent_this_week = sum(spending_by_category.values())
        weekly_income = profile['Income'] / 4  # Assuming monthly income
        
        actual_saved = weekly_income - total_spent_this_week
        
        if actual_saved < weekly_savings_goal:
            shortfall = weekly_savings_goal - actual_saved
            alerts.append({
                "category": "savings",
                "shortfall": shortfall,
                "goal": weekly_savings_goal,
                "message": f"You're ₹{shortfall:.2f} short of your weekly savings goal of ₹{weekly_savings_goal:.2f}."
            })
    
    return jsonify(alerts)

@app.route('/get_suggestions', methods=['GET'])
@token_required
def get_suggestions(current_user):
    """Get personalized savings suggestions"""
    if current_user not in user_profiles:
        return jsonify([])
        
    # Check if user has opted out
    if current_user in user_preferences and user_preferences[current_user].get('opted_out', False):
        return jsonify({"message": "User has opted out of tracking"}), 403
    
    profile = user_profiles[current_user]
    suggestions = []
    
    # Generate suggestions based on potential savings
    for category in ['Groceries', 'Transport', 'Eating_Out', 'Entertainment', 
                    'Utilities', 'Healthcare', 'Education', 'Miscellaneous']:
        savings_field = f'Potential_Savings_{category}'
        
        if savings_field in profile and profile[savings_field] > 100:  # Only suggest meaningful savings
            category_name = category.replace('_', ' ')
            suggestions.append({
                "category": category,
                "potential_savings": profile[savings_field],
                "message": f"Save ₹{profile[savings_field]:.2f} on {category_name} this month to unlock rewards!"
            })
    
    # Prioritize top 3 suggestions with highest potential savings
    suggestions.sort(key=lambda x: x['potential_savings'], reverse=True)
    top_suggestions = suggestions[:3]
    
    # Add gamification element
    if top_suggestions:
        top_category = top_suggestions[0]['category']
        total_potential = sum(s['potential_savings'] for s in top_suggestions)
        
        top_suggestions.append({
            "category": "challenge",
            "potential_savings": total_potential,
            "message": f"SAVINGS CHALLENGE: Cut your {top_category} spending by 15% this week to earn 50 bonus points!"
        })
    
    return jsonify(top_suggestions)

@app.route('/opt_out', methods=['POST'])
@token_required
def opt_out(current_user):
    data = request.json
    
    if data is None:
        return jsonify({"error": "No data provided"}), 400
        
    opted_out = data.get('opted_out', True)
    
    if current_user not in user_preferences:
        user_preferences[current_user] = {}
        
    user_preferences[current_user]['opted_out'] = opted_out
    
    message = "Opted out of financial tracking" if opted_out else "Opted in to financial tracking"
    return jsonify({"message": message})

@app.route('/manual_transaction', methods=['POST'])
@token_required
def manual_transaction(current_user):
    """For opted-out users to manually enter transactions"""
    data = request.json
    
    if not data:
        return jsonify({"error": "No transaction data provided"}), 400
    
    # Add timestamp and transaction ID if not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    if 'transaction_id' not in data:
        data['transaction_id'] = str(uuid.uuid4())
        
    # Initialize user transaction list if not exists
    if current_user not in transactions:
        transactions[current_user] = []
        
    # Add the manual transaction
    transactions[current_user].append(data)
    
    # If user has opted back in, update their profile
    if current_user not in user_preferences or not user_preferences[current_user].get('opted_out', False):
        update_user_profile(current_user, data)
    
    return jsonify({
        "message": "Manual transaction added successfully", 
        "transaction": data,
        "updated_profile": user_profiles.get(current_user, {})
    })

@app.route('/dashboard_stats', methods=['GET'])
@token_required
def dashboard_stats(current_user):
    """Get summary statistics for the user dashboard"""
    if current_user not in user_profiles:
        return jsonify({"error": "Profile not found"}), 404
    
    profile = user_profiles[current_user]
    recent_txs = get_recent_transactions(current_user)
    
    # Calculate recent spending
    total_recent_spending = sum(float(tx.get('amount', 0)) for tx in recent_txs)
    
    # Calculate category breakdown
    category_spending = {}
    for tx in recent_txs:
        category = tx.get('category', 'other')
        amount = float(tx.get('amount', 0))
        
        if category not in category_spending:
            category_spending[category] = 0
        category_spending[category] += amount
    
    # Calculate savings progress
    weekly_income = profile.get('Income', 0) / 4  # Assuming monthly income
    weekly_savings_goal = profile.get('Desired_Savings', 0) / 4  # Assuming monthly savings goal
    actual_saved = weekly_income - total_recent_spending
    savings_progress = (actual_saved / weekly_savings_goal * 100) if weekly_savings_goal > 0 else 0
    
    # Truncate to 100% if exceeded
    savings_progress = min(savings_progress, 100)
    
    stats = {
        "recent_spending": total_recent_spending,
        "category_breakdown": category_spending,
        "savings_goal": weekly_savings_goal,
        "actual_saved": actual_saved,
        "savings_progress": savings_progress,
        "alert_count": len(get_alerts(current_user).json),
        "disposable_income": profile.get('Disposable_Income', 0)
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)