import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates', static_folder='static')

# Flask Session Security Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'jbs_quantum_cipher_key_2026')

# In-Memory Database Registry & Brute-Force Monitoring Cache Tracks
USER_DATABASE = {
    "admin": {
        "username": "admin",
        "email": "admin@jbs.co.ke",
        # Default passkey encrypted string of 'jbs2026'
        "password_hash": generate_password_hash("jbs2026")
    }
}

FAILED_ATTEMPTS_CACHE = {}
MAX_LOCK_LIMIT = 3

@app.route('/')
def home():
    if 'operator_user' in session:
        return f"<h1>JBS Landing Platform - Active Session: {session['operator_user']}</h1><br><a href='/logout'>Terminate Session</a>"
    return redirect(url_for('login_gateway'))

@app.route('/login', methods=['GET', 'POST'])
def login_gateway():
    if request.method == 'GET':
        if 'operator_user' in session:
            return redirect(url_for('dashboard_gateway'))
        return render_template('login.html')
        
    # POST Execution Layer Routing Processes
    username_or_email = request.form.get('username', '').strip()
    password_input = request.form.get('password', '').strip()
    
    if not username_or_email or not password_input:
        flash("Handshake Blocked: All system input grids required.", "error")
        return redirect(url_for('login_gateway'))

    # Checking Bruteforce Intrusion Blockades
    if FAILED_ATTEMPTS_CACHE.get(username_or_email, 0) >= MAX_LOCK_LIMIT:
        flash("Account Locked: Multiple authentication errors. Contact Support Center.", "error")
        return redirect(url_for('login_gateway'))

    # Identity Registry Evaluation Loops
    target_account = USER_DATABASE.get(username_or_email)
    
    # Optional check: scan by matching nested email accounts instead
    if not target_account:
        for user_key, profile in USER_DATABASE.items():
            if profile['email'] == username_or_email:
                target_account = profile
                break

    if target_account and check_password_hash(target_account['password_hash'], password_input):
        # Reset failed tracking markers upon successful matching
        FAILED_ATTEMPTS_CACHE[username_or_email] = 0
        
        # Session Token Placement Initialization
        session['operator_user'] = target_account['username']
        session['authenticated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return redirect(url_for('dashboard_gateway'))
    else:
        # Increment threat telemetry indexes
        FAILED_ATTEMPTS_CACHE[username_or_email] = FAILED_ATTEMPTS_CACHE.get(username_or_email, 0) + 1
        remaining_chances = MAX_LOCK_LIMIT - FAILED_ATTEMPTS_CACHE[username_or_email]
        
        if remaining_chances <= 0:
            flash("Account Locked: Brute-force threshold breached.", "error")
        else:
            flash(f"Invalid Identity Matrix. {remaining_chances} access cycles remaining.", "error")
            
        return redirect(url_for('login_gateway'))

@app.route('/dashboard')
def dashboard_gateway():
    if 'operator_user' not in session:
        flash("Access Denied: Initialize login sequence first.", "error")
        return redirect(url_for('login_gateway'))
    return render_template('dashboard.html', operator=session['operator_user'])

@app.route('/logout')
def logout():
    session.pop('operator_user', None)
    session.pop('authenticated_at', None)
    flash("Session terminated smoothly. Clearance tokens purged.", "success")
    return redirect(url_for('login_gateway'))

# Static Navigation Fallback Nodes
@app.route('/about')
def about(): return "<h1>Corporate Profile - Under Construction</h1>"
@app.route('/contact')
def contact(): return "<h1>Contact Routing Gateway - Under Construction</h1>"
@app.route('/support')
def support(): return "<h1>Support Center Matrix - Hotline 0798770325</h1>"
@app.route('/forgot-password')
def forgot_password(): return "<h1>Password Reset Infrastructure Recovery Channel</h1>"

if __name__ == '__main__':
    print("================================================================")
    print(" JBS PYTHON FLASK ENGINE INITIALIZED")
    print(" Listening channel mapped on locally address: http://127.0.0.1:5000")
    print("================================================================")
    app.run(debug=True, port=5000)
    import os
import datetime
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='.', template_folder='.')

# --------------------------------------------------------------------------
# SECURE CENTRAL DATASTORE REGISTRY (Thread-Safe Simulation Model)
# --------------------------------------------------------------------------
INVENTORY_DATABASE = {
    "JBS-SKU-401": {
        "product_id": "PRD-001",
        "name": "Amoxicillin 500mg Matrix Pack",
        "barcode": "JBS-SKU-401",
        "serial_number": "SN-AMX-9941A",
        "qty": 820,
        "date_added": "2026-01-10 10:00",
        "last_scanned": "2026-06-15 09:12",
        "supplier": "Biomed Central Africa",
        "category": "Medical / Pharmacy",
        "unit_value": 120
    },
    "JBS-SKU-902": {
        "product_id": "PRD-002",
        "name": "Portland Cement Type I 50KG Bags",
        "barcode": "JBS-SKU-902",
        "serial_number": "SN-CMT-1102X",
        "qty": 15,
        "date_added": "2026-02-14 08:30",
        "last_scanned": "2026-06-15 08:45",
        "supplier": "Bamburi Structural Supply",
        "category": "Hardware Supply",
        "unit_value": 850
    }
}

STOCK_MOVEMENT_LOGS = []
TODAY_SCANNED_SET = set()

# Helper function to sanitize user string inputs safely
def sanitize_input(value):
    if not value:
        return ""
    return str(value).strip().replace("<", "&lt;").replace(">", "&gt;")

# --------------------------------------------------------------------------
# API PIPELINE ENDPOINTS
# --------------------------------------------------------------------------

@app.route('/scan-product', methods=['POST'])
def api_scan_product():
    """
    Core Optical Target Receiver Router Node. Receives real-time scans,
    validates database matches, increments stock levels or initializes records.
    """
    data = request.get_json() or {}
    raw_code = data.get('code', '')
    scan_method = sanitize_input(data.get('method', 'Optical Scanner'))

    if not raw_code:
        return jsonify({"success": False, "message": "Missing alphanumeric token reference key."}), 400

    barcode_key = sanitize_input(raw_code)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Match or Initialize Product Entry Row Data Matrix
    if barcode_key in INVENTORY_DATABASE:
        product = INVENTORY_DATABASE[barcode_key]
        product["qty"] += 1
        product["last_scanned"] = timestamp_str
        action_performed = "Stock Incremented Automatically"
    else:
        # Dynamic Registration of undocumented elements discovered by hardware pass
        generated_id = f"PRD-NEW-{len(INVENTORY_DATABASE) + 1:03d}"
        product = {
            "product_id": generated_id,
            "name": f"Discovered Scan Asset ({barcode_key})",
            "barcode": barcode_key,
            "serial_number": f"SN-GEN-{barcode_key.upper()}",
            "qty": 1,
            "date_added": timestamp_str,
            "last_scanned": timestamp_str,
            "supplier": "Pending Classification Registry",
            "category": "Unassigned Scanner Imports",
            "unit_value": 450
        }
        INVENTORY_DATABASE[barcode_key] = product
        action_performed = "New Registry Initialized"

    # Log operational transaction entry
    STOCK_MOVEMENT_LOGS.append({
        "barcode": barcode_key,
        "product_name": product["name"],
        "timestamp": timestamp_str,
        "action": action_performed,
        "method": scan_method
    })
    
    TODAY_SCANNED_SET.add(barcode_key)

    return jsonify({
        "success": True,
        "action": action_performed,
        "timestamp": timestamp_str,
        "product": product
    }), 200

@app.route('/add-product', methods=['POST'])
def api_add_product():
    """
    Explicitly adds completely new core master inventory rows from desktop configurations.
    """
    data = request.get_json() or {}
    barcode = sanitize_input(data.get('barcode'))
    name = sanitize_input(data.get('name'))
    category = sanitize_input(data.get('category', 'General Goods'))
    unit_value = int(data.get('unit_value', 0))
    initial_qty = int(data.get('qty', 0))
    supplier = sanitize_input(data.get('supplier', 'Unknown Vendor'))

    if not barcode or not name:
        return jsonify({"success": False, "message": "Barcode and Product Name parameters are required fields."}), 400

    if barcode in INVENTORY_DATABASE:
        return jsonify({"success": False, "message": "Asset code token key already exists in database registry entries."}), 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_item = {
        "product_id": f"PRD-{len(INVENTORY_DATABASE) + 1:03d}",
        "name": name,
        "barcode": barcode,
        "serial_number": f"SN-MAN-{barcode.upper()}",
        "qty": initial_qty,
        "date_added": timestamp,
        "last_scanned": "Never Scanned",
        "supplier": supplier,
        "category": category,
        "unit_value": unit_value
    }

    INVENTORY_DATABASE[barcode] = new_item
    return jsonify({"success": True, "message": "Product successfully added", "product": new_item}), 201

@app.route('/update-stock', methods=['POST'])
def api_update_stock():
    """
    Manual adjustments channel endpoint override loop.
    """
    data = request.get_json() or {}
    barcode = sanitize_input(data.get('barcode'))
    delta_qty = int(data.get('delta_qty', 0))

    if barcode not in INVENTORY_DATABASE:
        return jsonify({"success": False, "message": "Product asset matching code sequence target missing."}), 404

    INVENTORY_DATABASE[barcode]["qty"] += delta_qty
    INVENTORY_DATABASE[barcode]["last_scanned"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify({"success": True, "current_qty": INVENTORY_DATABASE[barcode]["qty"]}), 200

@app.route('/inventory-data', methods=['GET'])
def api_inventory_data():
    """
    Provides global dashboard aggregation data metrics and binary data output streams.
    """
    # Check for binary downstream report exports
    if request.args.get('export') == 'pdf':
        return export_manifest_report_stream()

    total_products = len(INVENTORY_DATABASE)
    scanned_today = len(TODAY_SCANNED_SET)
    
    low_stock_count = sum(1 for item in INVENTORY_DATABASE.values() if item["qty"] <= 5)
    total_value = sum(item["qty"] * item["unit_value"] for item in INVENTORY_DATABASE.values())

    return jsonify({
        "total_products": total_products,
        "scanned_today": scanned_today,
        "low_stock_count": low_stock_count,
        "total_value": total_value,
        "inventory": list(INVENTORY_DATABASE.values())
    }), 200

def export_manifest_report_stream():
    """Generates an on-the-fly downloadable transaction manifest file"""
    report_path = os.path.join(os.path.dirname(__file__), "JBS_Manifest_Audit.txt")
    with open(report_path, "w") as f:
        f.write("========================================================\n")
        f.write("           JOHN BILLING SYSTEM LOGISTICS AUDIT          \n")
        f.write(f"Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("========================================================\n\n")
        for barcode, item in INVENTORY_DATABASE.items():
            f.write(f"SKU: {item['barcode']} | Asset: {item['name']} | Vault Count: {item['qty']} Units | Value: Ksh {item['unit_value'] * item['qty']}\n")
            
    return send_file(report_path, as_attachment=True, download_name="JBS_Logistics_Manifest.pdf")

# --------------------------------------------------------------------------
# UI SITE PAGES ROUTER MATCHING
# --------------------------------------------------------------------------
@app.route('/scanner')
def ui_scanner_console():
    return render_template('scanner.html')

@app.route('/')
def ui_dashboard_fallback():
    return "<h1>John Billing System Flask Core Active</h1><p>Navigate directly to <a href='/scanner'>/scanner</a> to test hardware emulation pipelines.</p>"

if __name__ == '__main__':
    # Launch local debugging loop framework safely
    app.run(host='0.0.0.0', port=5000, debug=True)
    import os
import re
import base64
import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import cv2
import numpy as np

# ==========================================================================
# SYSTEM CORE CONFIGURATION ARCHITECTURE ENGINE
# ==========================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'JBS_ENTERPRISE_SYSTEM_CORE_HYPERLEVEL_TOKEN_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/john_billing_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB Explicit Memory Boundary Safety Shield
app.config['ACCOUNT_MAX_ATTEMPTS'] = 5

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# ==========================================================================
# SECURE RECOGNITION MODELS INITIALIZATION SYSTEM
# ==========================================================================
# Instantiating high-performance CPU-friendly facial vector models 
haar_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade_classifier = cv2.CascadeClassifier(haar_cascade_path)
lbph_biometric_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Fallback setup: Generate an empty array vector template index calibration registry if no training binary profile matches
BIOMETRIC_PROFILE_TRAINED = False

def calibrate_admin_biometrics():
    """ Runs system indexing routines across files matching the admin profile prefix mapping parameters """
    global BIOMETRIC_PROFILE_TRAINED
    training_samples_matrix = []
    assigned_labels_vector = []
    
    # We inspect system storage paths for administrative reference frames
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith('admin_ref_') and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            gray_img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            if gray_img is not None:
                detected_faces = face_cascade_classifier.detectMultiScale(gray_img, 1.2, 5)
                for (x, y, w, h) in detected_faces:
                    training_samples_matrix.append(gray_img[y:y+h, x:x+w])
                    assigned_labels_vector.append(1001) # Explicit ID designation for Superuser admin profiles
                    
    if len(training_samples_matrix) > 0:
        lbph_biometric_recognizer.train(training_samples_matrix, np.array(assigned_labels_vector))
        BIOMETRIC_PROFILE_TRAINED = True

# ==========================================================================
# SYSTEM CORE RECONCILIATION DATA REGISTRY SCHEMAS (ORMs)
# ==========================================================================
class UserProfileRegistry(db.Model):
    __tablename__ = 'jbs_users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    business_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(32), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_path = db.Column(db.String(255), nullable=True)
    failed_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    last_login_timestamp = db.Column(db.DateTime, nullable=True)
    is_admin_flag = db.Column(db.Boolean, default=False)

class AuditActivityLogger(db.Model):
    __tablename__ = 'jbs_audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    identity_context = db.Column(db.String(64), nullable=False)
    action_signature = db.Column(db.String(255), nullable=False)
    network_ip_origin = db.Column(db.String(45), nullable=False)
    timestamp_marker = db.Column(db.DateTime, default=datetime.datetime.utcnow)

def emit_audit_log(identity, action):
    try:
        log_entry = AuditActivityLogger(
            identity_context=identity,
            action_signature=action,
            network_ip_origin=request.remote_addr or '127.0.0.1'
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception:
        db.session.rollback()

# ==========================================================================
# ROUTING CORE MIDDLEWARES AND API ENDPOINTS EXECUTIONS
# ==========================================================================
@app.route('/register', methods=['POST'])
def register_pipeline():
    try:
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        business_name = request.form.get('business_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        avatar_file = request.files.get('avatar')

        if not all([full_name, username, business_name, email, phone, password, avatar_file]):
            return jsonify({'success': False, 'message': 'Payload schema violation: Missing structural variables.'}), 400

        # Enforce pure validation structures on email addresses via system regular patterns
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'success': False, 'message': 'Email addresses constraints schema evaluation mismatch.'}), 400

        # Identify structural username intersection duplicates securely
        existing_check = UserProfileRegistry.query.filter(
            (UserProfileRegistry.username == username) | (UserProfileRegistry.email == email)
        ).first()
        if existing_check:
            return jsonify({'success': False, 'message': 'Account identifier conflict: Profile record already allocated.'}), 409

        # Handle profile attachment file processing securely
        extension = os.path.splitext(avatar_file.filename)[1].lower()
        if extension not in ['.jpg', '.jpeg', '.png']:
            return jsonify({'success': False, 'message': 'Asset type prohibited: Profile avatars require image files.'}), 400

        filename_constructed = secure_filename(f"avatar_{username}{extension}")
        storage_destination_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_constructed)
        avatar_file.save(storage_destination_path)

        # Hash credentials securely prior to committing transactional records
        secured_hash = generate_password_hash(password, method='scrypt')
        
        # Determine if account configuration satisfies structural administrative keys (e.g. tracking specific superuser keys)
        is_admin = True if username.lower() == 'admin' or username.lower() == 'dr_kabuthi' else False

        # If it's a superuser profile tracking pattern, save an administrative facial frame baseline
        if is_admin:
            admin_facial_filename = secure_filename(f"admin_ref_{username}{extension}")
            facial_frame_storage_path = os.path.join(app.config['UPLOAD_FOLDER'], admin_facial_filename)
            # Create system duplicate file for internal biometric loop execution indexes
            import shutil
            shutil.copyfile(storage_destination_path, facial_frame_storage_path)
            # Recalibrate tracking parameters on model registry instantly
            calibrate_admin_biometrics()

        new_account_record = UserProfileRegistry(
            full_name=full_name,
            username=username,
            business_name=business_name,
            email=email,
            phone=phone,
            password_hash=secured_hash,
            avatar_path=filename_constructed,
            is_admin_flag=is_admin
        )

        db.session.add(new_account_record)
        db.session.commit()
        
        emit_audit_log(username, f"Account record provisioned successfully. Master Privilege Level Assigned: {is_admin}")
        return jsonify({'success': True, 'message': 'Account provisioned cleanly inside cloud server matrix maps.'}), 201

    except Exception as error_exception_context:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Server core transactional failure exception: {str(error_exception_context)}'}), 500

@app.route('/login', methods=['POST'])
def credentials_login_pipeline():
    data = request.get_json() or {}
    identity = data.get('identity')
    password = data.get('password')
    remember_me = data.get('remember_me', False)

    if not identity or not password:
        return jsonify({'success': False, 'message': 'Parameter requirements validation check fault.'}), 400

    profile_record = UserProfileRegistry.query.filter(
        (UserProfileRegistry.username == identity) | (UserProfileRegistry.email == identity)
    ).first()

    if not profile_record:
        emit_audit_log(identity, "Authentication failed: Profile record identifier could not be matched.")
        return jsonify({'success': False, 'message': 'Invalid structural parsing parameters presented.'}), 401

    # Check temporal locks
    if profile_record.account_locked_until and profile_record.account_locked_until > datetime.datetime.utcnow():
        return jsonify({'success': False, 'message': 'Security locks active: Account restricted due to repeated brute authorization attempts.'}), 423

    # Authenticate credentials payload securely
    if not check_password_hash(profile_record.password_hash, password):
        profile_record.failed_attempts += 1
        if profile_record.failed_attempts >= app.config['ACCOUNT_MAX_ATTEMPTS']:
            profile_record.account_locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
            emit_audit_log(profile_record.username, "Account entry vector locked out: Exceeded threshold constraints.")
        db.session.commit()
        return jsonify({'success': False, 'message': 'Invalid structural parsing parameters presented.'}), 401

    # Reset security counters on confirmation of correct credentials
    profile_record.failed_attempts = 0
    profile_record.account_locked_until = None
    profile_record.last_login_timestamp = datetime.datetime.utcnow()
    db.session.commit()

    # Establish isolated persistent system token states
    session.clear()
    session['uid'] = profile_record.id
    session['username'] = profile_record.username
    session['business_name'] = profile_record.business_name
    
    if remember_me:
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(days=14)

    emit_audit_log(profile_record.username, "Standard user authorization validated via system encryption comparison.")
    return jsonify({'success': True, 'message': 'Authorization signature cleared.'})

@app.route('/face-login', methods=['POST'])
def biometric_login_pipeline():
    global BIOMETRIC_PROFILE_TRAINED
    data = request.get_json() or {}
    base64_payload_string = data.get('image')

    if not base64_payload_string:
        return jsonify({'success': False, 'message': 'Data channel corruption: Missing vector mapping array buffer data.'}), 400

    try:
        # If biometric arrays are uncalibrated, force initial structural synchronization run execution passes
        if not BIOMETRIC_PROFILE_TRAINED:
            calibrate_admin_biometrics()
            if not BIOMETRIC_PROFILE_TRAINED:
                return jsonify({'success': False, 'message': 'Biometric verification offline: Reference matrices require calibration.'}), 422

        # Strip standard payload headers from incoming base64 streams
        encoded_data_block = base64_payload_string.split(',')[1] if ',' in base64_payload_string else base64_payload_string
        binary_image_buffer = base64.b64decode(encoded_data_block)
        
        np_array_matrix = np.frombuffer(binary_image_buffer, dtype=np.uint8)
        decoded_cv2_frame = cv2.imdecode(np_array_matrix, cv2.IMREAD_COLOR)
        gray_frame_matrix = cv2.cvtColor(decoded_cv2_frame, cv2.COLOR_BGR2GRAY)

        detected_faces = face_cascade_classifier.detectMultiScale(gray_frame_matrix, 1.2, 5)
        if len(detected_faces) == 0:
            return jsonify({'success': False, 'message': 'Biometric scanner exception: Target parameters unresolvable.'}), 422

        for (x, y, w, h) in detected_faces:
            face_region_of_interest = gray_frame_matrix[y:y+h, x:x+w]
            predicted_label_index, calculated_distance_metric = lbph_biometric_recognizer.predict(face_region_of_interest)
            
            # LBPH distance confidence assessment thresholding metric parameter values: lower score indicates exact vector map similarity
            if predicted_label_index == 1001 and calculated_distance_metric < 65.0:
                # Resolve primary administrator records
                admin_account_record = UserProfileRegistry.query.filter_with_key(is_admin_flag=True).first() or \
                                       UserProfileRegistry.query.filter_by(username='dr_kabuthi').first()
                
                if admin_account_record:
                    session.clear()
                    session['uid'] = admin_account_record.id
                    session['username'] = admin_account_record.username
                    session['business_name'] = admin_account_record.business_name
                    
                    emit_audit_log(admin_account_record.username, f"Biometric verification approved. Confidence Distance Metrics: {calculated_distance_metric}")
                    return jsonify({'success': True, 'message': 'Biometric verification passed.'})

        emit_audit_log('UNKNOWN_BIOMETRIC_ATTEMPT', "Biometric parameters invalid: Feature tracking signature variation error.")
        return jsonify({'success': False, 'message': 'Biometric parameters invalid: Secure signature match failed.'}), 401

    except Exception as biometric_fault_context:
        return jsonify({'success': False, 'message': f'Biometric hardware interface layer error: {str(biometric_fault_context)}'}), 500

@app.route('/forgot-password', methods=['POST'])
def recover_access_pipeline():
    data = request.get_json() or {}
    email = data.get('email')
    
    # Preventing record profiling vectors by systematically returning identical payload responses across parsed search runs
    profile_record = UserProfileRegistry.query.filter_by(email=email).first()
    if profile_record:
        emit_audit_log(profile_record.username, "Recovery transactional request token generated.")
        
    return jsonify({'success': True, 'message': 'If the corresponding identifier matches a database record, an activation key has been forwarded to the associated channel location.'})

@app.route('/logout', methods=['GET', 'POST'])
def terminate_session_pipeline():
    actor_identity = session.get('username', 'GUEST_CONTEXT')
    session.clear()
    emit_audit_log(actor_identity, "Session invalidated successfully. Security token destroyed.")
    return jsonify({'success': True, 'message': 'Session cleared safely.'})

# Fallback development setup interface
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        calibrate_admin_biometrics()
    app.run(host='0.0.0.0', port=5000, debug=True)
    import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

# THIS IS THE CRITICAL MISSING LINK FOR RENDER
@app.route('/')
def serve_login():
    return send_from_directory('.', 'login.html')

# Keep your other API routes (like /api/billing, etc.) below this...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
from flask import Flask, request, render_template, redirect, url_for, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

# Simple in-memory profile directory for newly registered users
# (In the future, this can map to your db.create_all() SQLite framework setup)
USER_REGISTRY = {
    # 'username': 'password'
}

# 1. Base Security Gate
@app.route('/')
def home_gate():
    # Render login directly through flask context to handle message injection
    return send_from_directory('.', 'login.html')

# 2. Native Login Action Processing Engine
@app.route('/login-action', methods=['POST'])
def handle_login_action():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()

    # CRITICAL: Hardcoded Admin Exemption Route
    if username == 'admin' and password == 'admin':
        return redirect('/index.html')

    # Regular Registered User Profile Verification Match Link
    elif username in USER_REGISTRY and USER_REGISTRY[username] == password:
        # Prevent regular users from logging in as the root user string
        if username == 'admin':
            return render_template('login.html', error="System Conflict: Reserved Credentials.")
        return redirect('/index.html')

    else:
        # Re-render form with a clear text indicator injection overlay
        return render_template('login.html', error="Invalid Secure Key Identification Details.")

# 3. Native Registration Logic Processing Engine
@app.route('/register-action', methods=['POST'])
def handle_register_action():
    new_username = request.form.get('new_username').strip().lower()
    new_password = request.form.get('new_password').strip()

    # Guardrail: Prevent registering user accounts targeting admin identity fields
    if new_username == 'admin':
        return render_template('login.html', error="Registration Blocked: Identity Reserved.")

    if new_username in USER_REGISTRY:
        return render_template('login.html', error="Profile Conflict: Identity already active.")

    # Commit entry save to backend structure dictionary list record
    USER_REGISTRY[new_username] = new_password
    
    # Return to landing gate with successful profile verification indicator
    return render_template('login.html', error="Registration Successful! Please login below.")

# Standard Dashboard Layout Page Direct Routing Hooks...
@app.route('/index.html')
def dashboard_home():
    return send_from_directory('.', 'index.html')
    from flask import Flask, request, render_template, redirect, send_from_directory

# Tell Flask that BOTH static files and template files live directly in the root folder '.'
app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')

USER_REGISTRY = {}

# 1. Base Security Gate (Now safely searches the root folder for login.html)
@app.route('/')
def home_gate():
    return render_template('login.html', error=None)

# 2. Native Login Processing Engine
@app.route('/login-action', methods=['POST'])
def handle_login_action():
    username = request.form.get('username').strip().lower()
    password = request.form.get('password').strip()

    # Admin Bypass (Matches lowercase 'admin' perfectly)
    if username == 'admin' and password == 'admin':
        return redirect('/index.html')

    # Regular User Check
    elif username in USER_REGISTRY and USER_REGISTRY[username] == password:
        return redirect('/index.html')

    else:
        # Re-renders login.html from the root folder with the error text injection
        return render_template('login.html', error="Invalid Secure Key Identification Details.")

# 3. Native Registration Processing Engine
@app.route('/register-action', methods=['POST'])
def handle_register_action():
    new_username = request.form.get('new_username').strip().lower()
    new_password = request.form.get('new_password').strip()

    if new_username == 'admin':
        return render_template('login.html', error="Registration Blocked: Identity Reserved.")

    if new_username in USER_REGISTRY:
        return render_template('login.html', error="Profile Conflict: Identity already active.")

    USER_REGISTRY[new_username] = new_password
    return render_template('login.html', error="Registration Successful! Please login below.")

# 4. Standard Dashboard Page Routing Tracker
@app.route('/index.html')
@app.route('/index')
def dashboard_home():
    return send_from_directory('.', 'index.html')
    import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.config['SECRET_KEY'] = 'jbs_secure_matrix_secret_key_2026'

# --- MYSQL DATABASE CONNECTION SETUP ---
# Update with your live Kinsta, Aiven, or local MySQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:your_password@localhost/jbs_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==============================================================================
# DATABASE RELATIONSHIP SCHEMAS
# ==============================================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_image = db.Column(db.String(255), default='default-avatar.png')
    business_name = db.Column(db.String(100))
    business_category = db.Column(db.String(50), default='General')
    badge = db.Column(db.String(30), default='Member') # Admin, Moderator, Verified Business, Member
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), default='General Discussions')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User')

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id])

# ==============================================================================
# FORUM LAYOUT DIRECT RESTRAINTS
# ==============================================================================

@app.route('/community-hub-forum.html')
@app.route('/forum')
def serve_forum_view():
    # Enforce basic fallback route protection
    if 'user_id' not in session and session.get('username') != 'admin':
        return redirect('/')
    return send_from_directory('.', 'community-hub-forum.html')

# ==============================================================================
# REST API CONTROLLERS
# ==============================================================================

@app.route('/get-posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    posts_data = []
    for p in posts:
        posts_data.append({
            "id": p.id,
            "content": p.content,
            "image_url": p.image_url,
            "category": p.category,
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "likes_count": len(p.likes),
            "comments_count": len(p.comments),
            "user": {
                "username": p.author.username,
                "full_name": p.author.full_name,
                "profile_image": p.author.profile_image,
                "business_name": p.author.business_name,
                "badge": p.author.badge
            }
        })
    return jsonify({"posts": posts_data})

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No data stream payload"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty reference tracking identifier"}), 400
        
    # Standard security storage target mapping rule inside flat root folder
    filename = f"upload_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file.save(os.path.join('.', filename))
    return jsonify({"image_url": f"/{filename}"})

@app.route('/notifications', methods=['GET'])
def fetch_notifications():
    uid = session.get('user_id', 1) # Default fallback to base user for sandbox testing
    notes = Notification.query.filter_by(recipient_id=uid).order_by(Notification.created_at.desc()).all()
    return jsonify([{
        "id": n.id,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at.strftime('%H:%M'),
        "sender": n.sender.username
    } for n in notes])

@app.route('/mark-notification-read', methods=['POST'])
def mark_read():
    nid = request.json.get('id')
    note = Notification.query.get(nid)
    if note:
        note.is_read = True
        db.session.commit()
    return jsonify({"status": "success"})

# ==============================================================================
# REAL-TIME FLASK-SOCKETIO SIGNAL HANDLERS
# ==============================================================================

@socketio.on('create-post')
def handle_realtime_post(data):
    uid = session.get('user_id', 1) 
    user = User.query.get(uid)
    
    new_post = Post(
        user_id=uid,
        content=data.get('content'),
        image_url=data.get('image_url'),
        category=data.get('category', 'General Discussions')
    )
    db.session.add(new_post)
    db.session.commit()

    # Broad emission structure containing full payload context definitions
    feed_payload = {
        "id": new_post.id,
        "content": new_post.content,
        "image_url": new_post.image_url,
        "category": new_post.category,
        "created_at": new_post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "likes_count": 0,
        "comments_count": 0,
        "user": {
            "username": user.username if user else "admin",
            "full_name": user.full_name if user else "System Administrator",
            "profile_image": user.profile_image if user else "default-avatar.png",
            "business_name": user.business_name if user else "JBS Core HQ",
            "badge": user.badge if user else "Admin"
        }
    }
    # Broadcast instantly to every user currently online across the platform
    emit('new-post-broadcast', feed_payload, broadcast=True)
    
    # Broadcast across system to slide out immediate dashboard push updates
    emit('global-system-alert', {
        "title": "New Community Post",
        "message": f"{feed_payload['user']['full_name']} posted in {new_post.category}"
    }, broadcast=True, include_self=False)

@socketio.on('like-post')
def handle_realtime_like(data):
    uid = session.get('user_id', 1)
    pid = data.get('post_id')
    
    existing_like = Like.query.filter_by(post_id=pid, user_id=uid).first()
    post = Post.query.get(pid)
    
    if existing_like:
        db.session.delete(existing_like)
        action = "unliked"
    else:
        new_like = Like(post_id=pid, user_id=uid)
        db.session.add(new_like)
        action = "liked"
        
        # Trigger real-time tracking notification alert rule to post owner
        if post.user_id != uid:
            liker = User.query.get(uid)
            note = Notification(
                recipient_id=post.user_id,
                sender_id=uid,
                message=f"{liker.full_name if liker else 'Admin'} liked your business post."
            )
            db.session.add(note)
            
    db.session.commit()
    
    # Broadcast updated like metrics metrics to all live client visualizers
    total_likes = Like.query.filter_by(post_id=pid).count()
    emit('like-update-broadcast', {"post_id": pid, "total_likes": total_likes}, broadcast=True)

@socketio.on('comment-post')
def handle_realtime_comment(data):
    uid = session.get('user_id', 1)
    pid = data.get('post_id')
    text = data.get('comment')
    
    user = User.query.get(uid)
    new_comment = Comment(post_id=pid, user_id=uid, comment=text)
    db.session.add(new_comment)
    
    post = Post.query.get(pid)
    if post.user_id != uid:
        note = Notification(
            recipient_id=post.user_id,
            sender_id=uid,
            message=f"{user.full_name if user else 'Admin'} commented: '{text[:30]}...'"
        )
        db.session.add(note)
        
    db.session.commit()

    comment_payload = {
        "post_id": pid,
        "comment": text,
        "username": user.username if user else "admin",
        "full_name": user.full_name if user else "System Administrator",
        "created_at": new_comment.created_at.strftime('%H:%M')
    }
    emit('comment-update-broadcast', comment_payload, broadcast=True)

# ==============================================================================
# BOOT EXECUTION LAYER MAPPING OVERRIDES
# ==============================================================================

if __name__ == '__main__':
    with app.app_context():
        # Auto-compile table structures inside your MySQL database schema instance
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    # CRITICAL: Replace app.run with socketio.run to enable WebSocket event loops
    socketio.run(app, host='0.0.0.0', port=port)