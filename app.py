import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

# Configuration mapping ensuring all static/dynamic assets are read from root '.'
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.config['SECRET_KEY'] = 'jbs_secure_matrix_secret_key_2026'

# ==============================================================================
# DATABASE LAYERING & FALLBACK ENGINE
# ==============================================================================
# Updates locally to your native MySQL setup automatically
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/jbs_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory registry system acting as a robust fallback for user accounts
USER_REGISTRY = {}

# System database schemas mapping
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(255), default='/default-avatar.png')
    business_name = db.Column(db.String(100), default='JBS Affiliate Partner')
    badge = db.Column(db.String(30), default='Member')

# ==============================================================================
# ROUTING CONTROLLER GATEWAYS (Flat File Routing Matrix)
# ==============================================================================

@app.route('/')
def root_index_gate():
    return render_template('login.html', error=None)

@app.route('/forum.html')
@app.route('/forum')
def serve_forum_view():
    return send_from_directory('.', 'forum.html')

@app.route('/<path:filename>')
def serve_any_flat_file(filename):
    """Dynamically serves any root HTML/CSS/JS file automatically (index, billing, mpesa etc)"""
    if os.path.exists(os.path.join('.', filename)):
        return send_from_directory('.', filename)
    return jsonify({"error": "Resource file not found on system path"}), 404

# ==============================================================================
# CRASH-PROOFED LOGIN & REGISTRATION LOGIC
# ==============================================================================

@app.route('/login-action', methods=['POST'])
def handle_login_action():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    # 1. Hardcoded Master Admin System Bypass Route
    if username == 'admin' and password == 'admin':
        session['user_id'] = 0
        session['username'] = 'admin'
        return redirect('/index.html')

    # 2. Secure Database Lookup (Wrapped inside catch handlers to block 500 crashes)
    try:
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/index.html')
    except Exception as db_error:
        print(f"[SYSTEM LOG] Database pipeline offline. Falling back to active RAM matrix: {db_error}")

    # 3. Memory Registry Secondary Lookup Verification Check
    if username in USER_REGISTRY and USER_REGISTRY[username] == password:
        session['user_id'] = 999
        session['username'] = username
        return redirect('/index.html')

    return render_template('login.html', error="Invalid Secure Key Identification Details.")

@app.route('/register-action', methods=['POST'])
def handle_register_action():
    new_username = request.form.get('new_username', '').strip().lower()
    new_password = request.form.get('new_password', '').strip()

    if new_username == 'admin':
        return render_template('login.html', error="Registration Blocked: Identity Reserved.")

    if new_username in USER_REGISTRY:
        return render_template('login.html', error="Profile Conflict: Identity already active.")

    # Save immediately to backup registry dictionary array
    USER_REGISTRY[new_username] = new_password
    return render_template('login.html', error="Registration Successful! Please login below.")

# ==============================================================================
# REAL-TIME WEBSOCKET PIPELINES
# ==============================================================================

@socketio.on('create-post')
def handle_realtime_post(data):
    uid = session.get('user_id', 0)
    
    # Extract structural profile data safely based on context
    if uid == 0:
        author_username = "admin"
        author_fullname = "System Administrator"
        author_badge = "Admin"
    else:
        author_username = session.get('username', 'user')
        author_fullname = author_username.capitalize()
        author_badge = "Member"

    feed_payload = {
        "id": int(datetime.utcnow().timestamp()),
        "content": data.get('content', ''),
        "image_url": data.get('image_url'),
        "category": data.get('category', 'General Discussions'),
        "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "likes_count": 0,
        "comments_count": 0,
        "user": {
            "username": author_username,
            "full_name": author_fullname,
            "profile_image": "/default-avatar.png",
            "business_name": "JBS Partner Network",
            "badge": author_badge
        }
    }

    emit('new-post-broadcast', feed_payload, broadcast=True)

# ==============================================================================
# SYSTEM BOOT SYSTEM INITIALIZATION
# ==============================================================================
if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("[SUCCESS] MySQL schemas synchronized smoothly.")
        except Exception as e:
            print(f"[WARNING] Local database table synchronization deferred: {e}")
            
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
    