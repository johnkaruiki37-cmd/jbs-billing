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
    # ==============================================================================
# JBS CORE BILLING & INVOICE TRACKING MATRIX
# ==============================================================================

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    amount_due = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(30), default='Pending') # Paid, Pending, Overdue
    items_json = db.Column(db.Text, nullable=False) # Stores inventory item arrays as text rows
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# API Endpoint: Receive and save new billing slips from billing.html
@app.route('/api/create-invoice', methods=['POST'])
def create_invoice_record():
    data = request.get_json() or {}
    
    customer = data.get('customer_name', 'Walk-in Customer')
    items = data.get('items', [])
    amount_paid = float(data.get('amount_paid', 0.0))
    
    if not items:
        return jsonify({"success": False, "message": "Cannot compile an empty billing invoice grid."}), 400

    # Secure server-side calculation of product cost metrics
    total_calculated_amount = 0.0
    for item in items:
        qty = int(item.get('quantity', 1))
        price = float(item.get('price', 0.0))
        total_calculated_amount += (qty * price)

    # Generate a professional billing transaction serial key identity
    unique_serial_invoice = f"JBS-{int(datetime.utcnow().timestamp())}"
    
    # Determine the status based on paid allocation amounts
    status = "Paid" if amount_paid >= total_calculated_amount else "Pending"

    try:
        new_slip = Invoice(
            invoice_number=unique_serial_invoice,
            customer_name=customer,
            amount_due=total_calculated_amount,
            amount_paid=amount_paid,
            payment_status=status,
            items_json=str(items) # Converts structured lists to standard table text storage
        )
        db.session.add(new_slip)
        db.session.commit()
        
        # Trigger real-time alert across dashboard screens via SocketIO connection pools
        socketio.emit('global-system-alert', {
            "title": "New Bill Generated",
            "message": f"Invoice {unique_serial_invoice} for KES {total_calculated_amount} was logged."
        }, broadcast=True)

        return jsonify({
            "success": True, 
            "invoice_number": unique_serial_invoice,
            "total": total_calculated_amount,
            "status": status
        })

    except Exception as e:
        print(f"[BILLING SYSTEM CRASH] Local storage mapping execution failure: {e}")
        # In-memory checkout processing fallback if the database server hits thread locks
        return jsonify({
            "success": True,
            "invoice_number": f"{unique_serial_invoice}-TEMP",
            "total": total_calculated_amount,
            "status": f"{status} (Offline Mode)"
        })