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
You are a helpful and knowledgeable financial advisor chatbot. You have analyzed the user's financial data and will provide personalized advice and insights based on that analysis.

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

Based on this analysis, provide helpful financial advice, answer questions, and suggest actionable steps to improve the user's financial situation. Be conversational, supportive, and provide specific advice tied to their situation.
"""
        
    # Super minimal output - just a welcome message and nothing else
    print("\nWelcome to the Financial Advisor! How may I help you?")
    print("\nType 'exit' to end conversation.")
    
    try:
        # Initialize the chat history but don't display anything
        chat_history = []
        chat_history.append({"role": "user", "content": system_prompt})
        chat_history.append({"role": "model", "content": "I'm ready to provide financial advice based on your data."})
        
        # Chat loop
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                print("Financial Advisor: Goodbye! Feel free to return if you have more financial questions.")
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
                print(f"\nFinancial Advisor: I apologize, but I encountered an error: {str(e)}")
                print("Let me try to respond again with simplified context.\n")
                
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
                    print(f"Error during retry: {str(retry_error)}")
                    print("I'm having technical difficulties. Please try again with a different question.")
        
    except Exception as e:
        print(f"Error starting chat: {str(e)}")
        
        # Try a fallback approach with direct content generation
        try:
            print("\nAttempting fallback method...")
            response = self.model.generate_content(
                "You are a financial advisor. Provide a general introduction about financial advice.",
                generation_config={"temperature": 0.2}
            )
            print(f"\nFinancial Advisor: {response.text}")
            print("\nNote: Unable to use your specific financial data due to technical difficulties.")
            print("Please check your API key and internet connection.")
        except Exception as fallback_error:
            print(f"Fallback also failed: {str(fallback_error)}")
            print("Please make sure your API key is valid and you have proper internet connectivity.")