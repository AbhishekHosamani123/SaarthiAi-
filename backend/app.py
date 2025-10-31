"""
Flask API Server for Intelligent Q&A System
Provides REST API endpoint for answering questions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import pickle

# Add parent directory to path to import qa_system
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import qa_system
    from qa_system import IntelligentQASystem
except ImportError:
    print("Warning: Could not import qa_system. Make sure qa_system.py exists.")

# Import Gemini service
try:
    import gemini_service
    from gemini_service import generate_smart_response, check_gemini_connection, generate_open_response
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI integration available")
except ImportError as e:
    print(f"⚠️ Warning: Gemini service not available: {e}")
    GEMINI_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Warning: Could not initialize Gemini: {e}")
    GEMINI_AVAILABLE = False

# Explicit allowed origins list (env override) used by both Flask-CORS and after_request
env_origins = os.environ.get("ALLOWED_ORIGINS", "")
if env_origins:
    ALLOWED_ORIGINS = [o.strip() for o in env_origins.split(",") if o.strip()]
else:
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://radheradhe.vercel.app"
    ]

# Initialize Flask app
app = Flask(__name__)
# Enable CORS using the computed ALLOWED_ORIGINS
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True)


@app.after_request
def add_cors_headers(response):
    """Ensure CORS headers are present on every response (including preflight)."""
    origin = request.headers.get('Origin')
    if origin and origin in ALLOWED_ORIGINS:
        # Echo back the requesting origin (needed when credentials are used)
        response.headers['Access-Control-Allow-Origin'] = origin
        # Make sure caches vary by Origin
        response.headers['Vary'] = 'Origin'
    else:
        # Don't set a permissive wildcard when credentials are expected
        # For non-matching origins we do not add CORS headers.
        pass

    # Common CORS headers useful for preflight and actual requests
    response.headers.setdefault('Access-Control-Allow-Credentials', 'true')
    response.headers.setdefault('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.setdefault('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Global variable to hold Q&A system
qa_system = None

def init_qa_system():
    """Initialize Q&A system lazily"""
    global qa_system
    if qa_system is None:
        try:
            print("Initializing Q&A System...")
            qa_system = IntelligentQASystem()
            print("✅ Q&A System ready!")
        except Exception as e:
            print(f"❌ Error initializing Q&A system: {e}")
            raise e
    return qa_system

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Intelligent Q&A API Server',
        'status': 'running',
        'gemini_available': GEMINI_AVAILABLE,
        'endpoints': {
            '/query': 'POST - Query the Q&A system',
            '/health': 'GET - Health check'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        qa = init_qa_system()
        return jsonify({
            'status': 'healthy',
            'message': 'Q&A system is running',
            'gemini_available': GEMINI_AVAILABLE
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/query', methods=['POST'])
def query():
    """Handle Q&A queries"""
    try:
        qa = init_qa_system()
        
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing question parameter'
            }), 400
        
        question = data['question']
        top_k = data.get('top_k', 10)  # Increased default to get more results
        use_gemini = data.get('use_gemini', True)  # Gemini enabled by default
        
        print(f"\n🔍 Received question: {question}")

        # Simple chit-chat/greeting detection
        q_lower = (question or "").strip().lower()
        greeting_triggers = [
            'hi', 'hello', 'hey', 'namaste', 'good morning', 'good evening',
            'what is your name', "who are you", 'your name', 'introduce yourself'
        ]
        is_greeting = any(t in q_lower for t in greeting_triggers) or q_lower in ['hi', 'hello', 'hey']
        
        # If greeting or small talk, prefer Gemini open response directly
        if GEMINI_AVAILABLE and use_gemini and is_greeting:
            print("💬 Detected greeting/small talk → using Gemini open response")
            open_resp = generate_open_response(question)
            response = {
                'question': question,
                'answer': open_resp['answer'],
                'confidence': open_resp.get('confidence', 0),
                'sources': [],
                'num_results': 0,
                'ai_enhanced': open_resp.get('ai_enhanced', False)
            }
            return jsonify(response), 200

        # Get answer from Q&A system for domain queries
        result = qa.answer_question(question, top_k=top_k)
        print(f"✅ Q&A system returned answer with {result.get('search_results_count', 0)} results")
        
        # Enhance with Gemini if available and requested AND if we have relevant data
        if GEMINI_AVAILABLE and use_gemini and result.get('search_results_count', 0) > 0 and result.get('confidence', 0) > 0.1:
            try:
                print("🤖 Attempting to enhance with Gemini...")
                enhanced_result = generate_smart_response(question, result)
                response = {
                    'question': question,
                    'answer': enhanced_result['answer'],
                    'confidence': enhanced_result['confidence'],
                    'sources': enhanced_result['sources'],
                    'num_results': result['search_results_count'],
                    'ai_enhanced': enhanced_result.get('ai_enhanced', False)
                }
                print("✅ Response enhanced with Gemini")
            except Exception as e:
                print(f"⚠️ Gemini enhancement failed: {e}")
                # Use basic response
                response = {
                    'question': question,
                    'answer': result['answer'],
                    'confidence': result['confidence'],
                    'sources': result['sources'],
                    'num_results': result['search_results_count'],
                    'ai_enhanced': False,
                    'fallback': True
                }
        else:
            # If no relevant data, try Gemini open response for non-domain questions
            if GEMINI_AVAILABLE and use_gemini and result.get('search_results_count', 0) == 0:
                print("💡 No KB data → using Gemini open response fallback")
                open_resp = generate_open_response(question)
                response = {
                    'question': question,
                    'answer': open_resp['answer'],
                    'confidence': open_resp.get('confidence', 0),
                    'sources': [],
                    'num_results': 0,
                    'ai_enhanced': open_resp.get('ai_enhanced', False)
                }
            else:
                # Use basic response without Gemini (no enhancement or Gemini disabled)
                response = {
                    'question': question,
                    'answer': result['answer'],
                    'confidence': result['confidence'],
                    'sources': result['sources'],
                    'num_results': result['search_results_count'],
                    'ai_enhanced': False
                }
                if result.get('search_results_count', 0) == 0:
                    print("💡 No relevant data found, returning informational message")
                else:
                    print("✅ Using basic Q&A response")
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        print(f"❌ Error in query endpoint: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'details': traceback.format_exc()
        }), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get system statistics"""
    try:
        qa = init_qa_system()
        return jsonify({
            'total_chunks': len(qa.chunks),
            'method': qa.vector_db['method'],
            'gemini_available': GEMINI_AVAILABLE,
            'datasets': {
                'crop_production': 'soil_health_complete_dataset.csv',
                'soil_health': 'soil_health_complete_dataset.csv'
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Starting Q&A API Server...")
    print("=" * 80)
    print("\n📡 API Endpoints:")
    print("  - GET  /          : API information")
    print("  - GET  /health     : Health check")
    print("  - GET  /stats      : System statistics")
    print("  - POST /query      : Query the Q&A system")
    print(f"\n🤖 Gemini AI: {'Available' if GEMINI_AVAILABLE else 'Not available'}")
    print("\n🚀 Server will start on: http://localhost:5000")
    print("=" * 80 + "\n")
    
    # app.run(debug=True, host='0.0.0.0', port=5000)
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
