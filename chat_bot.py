from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os


class ChatBot:
    def __init__(self, temperature=0.7):
        load_dotenv()
        # Try primary API key first, then backup key
        openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_BACKUP")
        
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set OPENAI_API_KEY or OPENAI_API_KEY_BACKUP in your .env file."
            )

        self.master_prompt = (
            "You are a friendly and knowledgeable restaurant assistant for TKR Restaurant (Tahir Khan Restaurant) in Islamabad. "
            "Your role is to help customers with questions about the restaurant's menu, services, food items, specialties, and general information.\n\n"
            "IMPORTANT GUIDELINES:\n"
            "1. Always be warm, conversational, and helpful in your responses. Use a friendly, welcoming tone as if you're speaking to a valued guest.\n"
            "2. When context is provided, use it to give detailed, accurate answers about TKR Restaurant.\n"
            "3. When specific information isn't available in the context, still try to be helpful by:\n"
            "   - Sharing general knowledge about similar restaurants or dishes if relevant\n"
            "   - Suggesting related menu items or services that might interest the customer\n"
            "   - Offering to help with other questions about the menu or restaurant\n"
            "   - Being encouraging and positive\n"
            "4. Never say 'I don't have that information' or 'I can't help with that' - instead, be creative and helpful.\n"
            "5. Focus on making the customer feel welcomed and valued.\n"
            "6. Format your responses clearly with proper paragraphs, but keep them conversational and easy to read.\n"
            "7. If asked about something not in the context, provide a helpful response based on general restaurant knowledge and suggest they might want to contact the restaurant directly for specific details."
        )

        self.api_key = openai_api_key
        self.backup_api_key = os.getenv("OPENAI_API_KEY_BACKUP")
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature,
            api_key=openai_api_key
        )

    def generate_response(self, context, user_prompt, history=None):
        # Check if context is empty or indicates no context found
        if not context or context.strip() == "No specific context found in the knowledge base for this query.":
            system_prompt = (
                f"{self.master_prompt}\n\n"
                "NOTE: Limited specific context was found for this query. However, you should still provide a helpful, friendly response. "
                "Use your knowledge about restaurants, Pakistani cuisine, and general hospitality to give a warm and useful answer. "
                "Be conversational, suggest related topics you can help with, and maintain a positive, welcoming tone. "
                "Make the customer feel valued and offer to help with other questions about TKR Restaurant's menu or services."
            )
        else:
            system_prompt = (
                f"{self.master_prompt}\n\n"
                "RELEVANT CONTEXT FROM TKR RESTAURANT DOCUMENTATION:\n"
                f"{context}\n\n"
                "Use the above context to provide a detailed, friendly answer to the user's question. "
                "If the context doesn't fully answer the question, provide what information you can from the context, "
                "and then offer additional helpful suggestions or related information in a warm, conversational manner."
            )

        messages = [
            SystemMessage(content=system_prompt)
        ]

        # Add history if provided
        if history:
            for msg in history:
                if msg["sender"] == "user":
                    messages.append(HumanMessage(content=msg["message"]))
                else:
                    messages.append(HumanMessage(content=f"Assistant: {msg['message']}")) # Or AIMessage if imported

        # Finally add current user prompt
        messages.append(HumanMessage(content=user_prompt))

        try:
            response = self.model.invoke(messages)
            return response.content
        except Exception as e:
            # Import OpenAI exceptions for proper error handling
            try:
                from openai import RateLimitError, APIError, AuthenticationError
            except ImportError:
                # Fallback if openai module structure is different
                RateLimitError = None
                APIError = None
                AuthenticationError = None
            
            error_type = type(e).__name__
            error_msg = str(e)
            error_str_lower = error_msg.lower()
            
            # Log detailed error information for debugging
            print(f"Error generating response - Type: {error_type}, Message: {error_msg}")
            
            # Check for specific OpenAI exception types
            if RateLimitError and isinstance(e, RateLimitError):
                print("Detected RateLimitError - Quota exceeded")
                # Try switching to backup API key if available and different from current
                if self.backup_api_key and self.backup_api_key != self.api_key:
                    print("Attempting to use backup API key...")
                    try:
                        self.model = ChatOpenAI(
                            model="gpt-4o-mini",
                            temperature=0.7,
                            api_key=self.backup_api_key
                        )
                        self.api_key = self.backup_api_key
                        # Retry the request with backup key
                        response = self.model.invoke(messages)
                        print("Successfully used backup API key")
                        return response.content
                    except Exception as backup_error:
                        print(f"Backup API key also failed: {backup_error}")
                
                return (
                    "The AI service quota has been exceeded. Please check your OpenAI account billing and quota limits. "
                    "Visit https://platform.openai.com/account/billing to add credits or check your usage. "
                    "The service will resume once the quota is restored. "
                    "Alternatively, you can set OPENAI_API_KEY_BACKUP in your .env file with a different API key."
                )
            
            if APIError and isinstance(e, APIError):
                # Check if it's a 429 status code (quota exceeded)
                if hasattr(e, 'status_code') and e.status_code == 429:
                    print("Detected APIError with status 429 - Quota exceeded")
                    quota_msg = (
                        "The AI service quota has been exceeded. Please check your OpenAI account billing and quota limits. "
                        "Visit https://platform.openai.com/account/billing to add credits or check your usage. "
                        "The service will resume once the quota is restored. "
                        "Alternatively, you can set OPENAI_API_KEY_BACKUP in your .env file with a different API key."
                    )
                    return quota_msg
                # Check error body for insufficient_quota
                if hasattr(e, 'body') and isinstance(e.body, dict):
                    error_body = e.body.get('error', {})
                    if error_body.get('code') == 'insufficient_quota' or 'insufficient_quota' in str(error_body).lower():
                        print("Detected insufficient_quota in APIError body")
                        quota_msg = (
                            "The AI service quota has been exceeded. Please check your OpenAI account billing and quota limits. "
                            "Visit https://platform.openai.com/account/billing to add credits or check your usage. "
                            "The service will resume once the quota is restored. "
                            "Alternatively, you can set OPENAI_API_KEY_BACKUP in your .env file with a different API key."
                        )
                        return quota_msg
            
            # Fallback: Check error message string for quota-related keywords
            if ("rate limit" in error_str_lower or 
                "429" in error_msg or 
                "insufficient_quota" in error_str_lower or
                "quota" in error_str_lower and "exceeded" in error_str_lower):
                print("Detected quota error in error message")
                quota_msg = (
                    "The AI service quota has been exceeded. Please check your OpenAI account billing and quota limits. "
                    "Visit https://platform.openai.com/account/billing to add credits or check your usage. "
                    "The service will resume once the quota is restored. "
                    "Alternatively, you can set OPENAI_API_KEY_BACKUP in your .env file with a different API key."
                )
                return quota_msg
            
            # Check for authentication errors
            if AuthenticationError and isinstance(e, AuthenticationError):
                print("Detected AuthenticationError")
                return "I'm having trouble connecting to the AI service. Please check the API configuration and ensure your API key is valid."
            
            if "API key" in error_str_lower or "authentication" in error_str_lower or "unauthorized" in error_str_lower:
                return "I'm having trouble connecting to the AI service. Please check the API configuration."
            
            # Generic error fallback
            print(f"Unhandled error type: {error_type}")
            return f"I encountered an error while processing your request. Please try again or rephrase your question. (Error: {error_type})"
