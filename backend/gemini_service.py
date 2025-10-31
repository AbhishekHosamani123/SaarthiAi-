"""
Gemini AI Service for Enhanced Answer Generation
Uses Google's Gemini API to generate natural, conversational responses
"""

try:
    import google.generativeai as genai
    import config
    
    # Configure Gemini
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    # Initialize the model (using stable 2.5-flash model)
    model = genai.GenerativeModel('gemini-2.5-flash')
    GEMINI_READY = True
    print("Gemini model 'gemini-2.5-flash' initialized successfully")
except Exception as e:
    print(f"Warning: Gemini not available: {e}")
    GEMINI_READY = False
    model = None

def generate_smart_response(user_question, retrieved_data):
    """
    Generate a natural, conversational response using Gemini AI
    based on the retrieved data from the Q&A system
    
    Args:
        user_question: The user's original question
        retrieved_data: Dictionary containing retrieved chunks and sources
    
    Returns:
        Enhanced natural language response
    """
    
    # Check if Gemini is available
    if not GEMINI_READY or model is None:
        raise Exception("Gemini not available")
    
    # Check if we have data
    if not retrieved_data or not retrieved_data.get('sources') or len(retrieved_data['sources']) == 0:
        return {
            'answer': "I couldn't find relevant information in the database to answer your question. Could you try rephrasing your question or asking about crop production, soil health, or agriculture data in India?",
            'confidence': 0,
            'sources': []
        }
    
    # Prepare context for Gemini
    context = f"""You are an expert agriculture assistant helping users with questions about Indian agriculture, crop production, and soil health.

User Question: {user_question}

Retrieved Data from Knowledge Base:
"""
    
    # Add retrieved chunks
    for i, source in enumerate(retrieved_data['sources'][:3], 1):
        context += f"\nSource {i}:\n"
        context += f"Dataset: {source['dataset']}\n"
        context += f"Information: {source['chunk']}\n"
        if 'details' in source:
            context += f"Details: {source['details']}\n"
        context += f"Relevance: {source['relevance']}\n"
    
    # Create the prompt
    prompt = f"""{context}

Based on the retrieved information above, provide a helpful, clear, and conversational answer to the user's question. 

Guidelines:
1. Answer naturally and conversationally
2. Use the specific data provided
3. Include relevant numbers and statistics
4. If multiple sources provide data, synthesize them intelligently
5. Be concise but informative
6. If the data is limited, mention it but provide what you can

Your Response:"""

    try:
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        enhanced_answer = response.text.strip()
        
        return {
            'answer': enhanced_answer,
            'confidence': retrieved_data.get('confidence', 0),
            'sources': retrieved_data.get('sources', []),
            'ai_enhanced': True
        }
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        # Fallback to original response
        return {
            'answer': retrieved_data.get('answer', "Sorry, I encountered an error generating the response."),
            'confidence': retrieved_data.get('confidence', 0),
            'sources': retrieved_data.get('sources', []),
            'ai_enhanced': False,
            'fallback': True
        }

def check_gemini_connection():
    """Check if Gemini API is working"""
    try:
        if not GEMINI_READY or model is None:
            return False, "Gemini not initialized"
        test_response = model.generate_content("Say 'Hello' if you're working.")
        return True, test_response.text
    except Exception as e:
        return False, str(e)


def generate_open_response(user_question):
    """Generate a freeform conversational response as SaarthiAI.

    Used for greetings, small talk, or questions outside the knowledge base.
    """
    try:
        if not GEMINI_READY or model is None:
            raise Exception("Gemini not available")

        system_preamble = (
            "You are SaarthiAI, a friendly Indian agriculture assistant. "
            "Introduce yourself as SaarthiAI when appropriate. "
            "You can handle casual greetings and general questions. "
            "For health or lifestyle questions like 'which crop is best for health', "
            "provide balanced, non-medical general advice (e.g., whole grains, millets, pulses), "
            "and include a short disclaimer that recommendations can vary by individual needs. "
            "Keep responses concise and helpful."
        )

        prompt = f"""{system_preamble}

User: {user_question}

Instructions:
- If the user greets or asks your name, briefly introduce yourself as SaarthiAI and offer help.
- If the question is outside agriculture datasets, still answer helpfully at a high level.
- Prefer short, crisp responses (2-5 sentences).
- Do not invent dataset citations.

Assistant:"""

        response = model.generate_content(prompt)
        answer = (response.text or "Hello! I'm SaarthiAI. How can I help you today?").strip()

        return {
            'answer': answer,
            'confidence': 0.5,
            'sources': [],
            'ai_enhanced': True
        }
    except Exception as e:
        # Fallback static identity response
        return {
            'answer': "Hi! I'm SaarthiAI, your agriculture assistant. How can I help you today?",
            'confidence': 0,
            'sources': [],
            'ai_enhanced': False,
            'fallback': True,
            'error': str(e)
        }