"""
Standalone Flask App for Censorly - No Database Required
Simple version for testing core functionality without Supabase
"""

from flask import Flask, request, jsonify
import json
import uuid
from datetime import datetime
import os

# Import our utilities (with fallback if not available)
try:
    from utils.censor_utils import detect_profane_words, initialize_profanity_filter
    from services.abuse_classifier import AbuseClassifier
    HAS_DETECTION = True
    # Initialize profanity filter
    initialize_profanity_filter()
except ImportError as e:
    print(f"Warning: Detection modules not available: {e}")
    HAS_DETECTION = False

app = Flask(__name__)

# Initialize services if available
if HAS_DETECTION:
    try:
        abuse_classifier = AbuseClassifier()
    except Exception as e:
        print(f"Warning: Could not initialize abuse classifier: {e}")
        abuse_classifier = None
else:
    abuse_classifier = None

# In-memory storage for demo (replace with database in production)
users_db = {}
jobs_db = {}
api_keys_db = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Censorly API',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if email in users_db:
        return jsonify({'error': 'User already exists'}), 409
    
    user_id = str(uuid.uuid4())
    users_db[email] = {
        'id': user_id,
        'email': email,
        'full_name': full_name or email.split('@')[0],
        'subscription_tier': 'free',
        'created_at': datetime.utcnow().isoformat(),
        'videos_processed_this_month': 0
    }
    
    return jsonify({
        'message': 'Registration successful',
        'user': users_db[email]
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if email not in users_db:
        return jsonify({'error': 'User not found'}), 404
    
    # In real app, verify password hash
    # For demo, just create a simple token
    token = f"demo_token_{uuid.uuid4().hex[:16]}"
    
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'user': users_db[email]
    })

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    # In real app, decode JWT token
    # For demo, return first user if exists
    if users_db:
        first_user = next(iter(users_db.values()))
        return jsonify({'user': first_user})
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/profanity/check', methods=['POST'])
def check_profanity():
    data = request.get_json()
    text = data.get('text', '')
    mode = data.get('mode', 'regex')  # 'regex' or 'ai'
    language = data.get('language', 'en')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        if mode == 'ai' and abuse_classifier:
            # Use AI classifier
            result = abuse_classifier.predict(text, return_score=True)
            if isinstance(result, dict):
                is_abusive = result.get('is_abusive', False)
                confidence = result.get('confidence', 0.0)
            else:
                is_abusive = bool(result)
                confidence = 1.0 if is_abusive else 0.0
            detected_words = []
        elif HAS_DETECTION:
            # Use regex detection
            detected_words = detect_profane_words(text)
            is_abusive = len(detected_words) > 0
            confidence = 1.0 if is_abusive else 0.0
        else:
            # Fallback simple detection
            profane_words = ['damn', 'hell', 'shit', 'fuck', 'bitch']
            detected_words = [word for word in profane_words if word.lower() in text.lower()]
            is_abusive = len(detected_words) > 0
            confidence = 1.0 if is_abusive else 0.0
        
        return jsonify({
            'text': text,
            'is_abusive': is_abusive,
            'confidence': confidence,
            'detected_words': detected_words,
            'mode': mode,
            'language': language
        })
    
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/process-video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No video file selected'}), 400
    
    # Get parameters
    censoring_mode = request.form.get('censoring_mode', 'beep')
    profanity_threshold = float(request.form.get('profanity_threshold', 0.8))
    languages = json.loads(request.form.get('languages', '["en"]'))
    
    # Create job
    job_id = str(uuid.uuid4())
    job = {
        'id': job_id,
        'filename': video_file.filename,
        'status': 'processing',
        'progress': 0,
        'created_at': datetime.utcnow().isoformat(),
        'censoring_mode': censoring_mode,
        'profanity_threshold': profanity_threshold,
        'languages': languages
    }
    
    jobs_db[job_id] = job
    
    # In real app, process video asynchronously
    # For demo, just return the job
    return jsonify({
        'job_id': job_id,
        'status': 'processing',
        'message': 'Video processing started'
    })

@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    if job_id not in jobs_db:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs_db[job_id])

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify({'jobs': list(jobs_db.values())})

@app.route('/api/keys', methods=['GET'])
def get_api_keys():
    return jsonify({'keys': list(api_keys_db.values())})

@app.route('/api/keys', methods=['POST'])
def create_api_key():
    data = request.get_json()
    name = data.get('name', 'Unnamed Key')
    description = data.get('description', '')
    
    key_id = str(uuid.uuid4())
    api_key = f"ck_{uuid.uuid4().hex}"
    
    api_keys_db[key_id] = {
        'id': key_id,
        'name': name,
        'description': description,
        'key': api_key,
        'created_at': datetime.utcnow().isoformat(),
        'last_used': None
    }
    
    return jsonify({
        'message': 'API key created',
        'key': api_keys_db[key_id]
    })

@app.route('/api/auth/usage', methods=['GET'])
def get_usage():
    # Return demo usage stats
    return jsonify({
        'videos_processed_this_month': 3,
        'videos_limit': 5,
        'subscription_tier': 'free',
        'days_remaining': 20
    })

if __name__ == '__main__':
    print("🚀 Starting Censorly Standalone Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/api/health")
    print("📝 No database required - using in-memory storage")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
