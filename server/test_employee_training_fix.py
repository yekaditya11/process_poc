#!/usr/bin/env python3
"""
Test script to verify the employee training chatbot fix
"""

import os
import sys
import logging
from datetime import datetime

# Add the server directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_employee_training_response():
    """Test the employee training response functionality"""
    try:
        # Import the main application
        from main_app import SummarizerApp
        from ai_engine.conversational_ai import ConversationalAI
        
        logger.info("Initializing SummarizerApp...")
        app = SummarizerApp()
        
        logger.info("Initializing ConversationalAI...")
        ai = ConversationalAI(app)
        
        # Start a conversation
        logger.info("Starting conversation...")
        session_id = ai.start_conversation("test_user")
        
        # Test employee training questions
        test_questions = [
            "how many employees with expired trainings?",
            "how many employes with expired traning?",
            "show me employees with expired training",
            "what is the training status?",
            "employee training compliance"
        ]
        
        for question in test_questions:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing question: {question}")
            logger.info(f"{'='*60}")
            
            try:
                # Process the message
                response = ai.process_message(session_id, question)
                
                logger.info(f"Response: {response.content}")
                logger.info(f"Has data context: {bool(response.data_context)}")
                logger.info(f"Has chart data: {bool(response.chart_data)}")
                
                if response.data_context:
                    logger.info(f"Data context keys: {list(response.data_context.keys())}")
                    
                    # Check for employee training data specifically
                    if 'employee_training' in response.data_context:
                        training_data = response.data_context['employee_training']
                        expired_data = training_data.get('expired_trainings', {})
                        total_employees = expired_data.get('total_employees', 0)
                        expired_count = expired_data.get('employees_with_expired_trainings', 0)
                        
                        logger.info(f"Employee training data found:")
                        logger.info(f"  - Total employees: {total_employees}")
                        logger.info(f"  - Employees with expired training: {expired_count}")
                        
                        # Check if the response mentions the actual numbers
                        if str(expired_count) in response.content or str(total_employees) in response.content:
                            logger.info("✅ SUCCESS: Response contains actual data numbers!")
                        else:
                            logger.warning("⚠️  WARNING: Response doesn't contain actual data numbers")
                    else:
                        logger.warning("⚠️  WARNING: No employee_training data in context")
                
                if response.suggested_actions:
                    logger.info(f"Suggested actions: {response.suggested_actions}")
                    
            except Exception as e:
                logger.error(f"Error processing question '{question}': {str(e)}", exc_info=True)
        
        logger.info(f"\n{'='*60}")
        logger.info("Test completed!")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    logger.info("Starting employee training chatbot fix test...")
    test_employee_training_response()
