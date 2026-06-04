from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)
CORS(app)

# --- NAVIGATIONAL ROUTING SYSTEM ---

@app.route('/')
def home():
    """Renders the Corporate Landing Page with company history."""
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    """Renders the primary operational Ledger & Billing System."""
    return render_template('index.html')

@app.route('/contact')
def contact():
    """Renders the official business communications directory."""
    return render_template('contact.html')

@app.route('/support')
def support():
    """Renders the dynamic FAQ matrix and ticketing help desk."""
    return render_template('support.html')


# --- KRA TAXATION COMPLIANT RECEIPT GENERATION ROUTE ---
@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    
    customer_name = data.get('customer', 'Valued Customer')
    invoice_no = data.get('invoice', 'N/A')
    raw_total = data.get('total', '0').replace('ksh', '').strip()
    
    served_by = data.get('servedBy', 'Admin')
    current_date = data.get('date', '')
    current_time = data.get('time', '')
    
    try:
        grand_total = float(raw_total)
    except ValueError:
        grand_total = 0.0
        
    # KRA Tax Breakdown: Total = Base Price + 16% VAT (Base Price = Total / 1.16)
    base_amount = grand_total / 1.16
    vat_amount = grand_total - base_amount

    pdf_path = "invoice_receipt.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', fontName="Helvetica-Bold", fontSize=22, textColor=colors.HexColor("#1A365D"))
    company_style = ParagraphStyle('CompInfo', fontSize=10, leading=14, textColor=colors.HexColor("#4A5568"))
    meta_style = ParagraphStyle('MetaText', fontSize=10, leading=14)
    table_header = ParagraphStyle('TH', fontName="Helvetica-Bold", fontSize=10, textColor=colors.white)
    table_cell = ParagraphStyle('TC', fontSize=10)

    # 1. Header Column Array Layout
    header_data = [
        [
            Paragraph("<b>JOHN BILLING SYSTEM</b>", title_style), 
            Paragraph(f"<b>INVOICE RECEIPT</b><br/>No: #{invoice_no}", ParagraphStyle('R', alignment=2, fontSize=11))
        ],
        [
            Paragraph("Nairobi, Kenya<br/>Contact: +254 798 770325<br/>Email: johnkaruiki37@gmail.com", company_style), 
            Paragraph(f"<b>Date:</b> {current_date}<br/><b>Time:</b> {current_time}<br/><b>Status:</b> PAID", ParagraphStyle('R2', alignment=2, fontSize=9, leading=13))
        ]
    ]
    t1 = Table(header_data, colWidths=[270, 260])
    t1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # Elegant Branding Accent Ribbon
    line = Table([[""]], colWidths=[530], rowHeights=[2])
    line.setStyle(TableStyle([('BACKGROUND', (0,0), (0,0), colors.HexColor("#1A365D"))]))
    story.append(line)
    story.append(Spacer(1, 15))

    # 2. Metadata Section
    meta_data = [
        [
            Paragraph(f"<b>BILLED TO:</b><br/>{customer_name}", meta_style), 
            Paragraph(f"<b>TRANSACTION DETAILS:</b><br/>Served By: {served_by}<br/>Payment System: Cash/M-Pesa", meta_style)
        ]
    ]
    t2 = Table(meta_data, colWidths=[265, 265])
    t2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(t2)
    story.append(Spacer(1, 20))

    # 3. KRA Compliant Items & Taxation Grid
    items_data = [
        [Paragraph("Description", table_header), Paragraph("Qty", table_header), Paragraph("Unit Price", table_header), Paragraph("Amount", table_header)],
        [Paragraph("General Ledger Goods / Services Rendered", table_cell), Paragraph("1", table_cell), Paragraph(f"Ksh {base_amount:,.2f}", table_cell), Paragraph(f"Ksh {base_amount:,.2f}", table_cell)],
        ["", "", Paragraph("Subtotal (Excl. VAT):", table_cell), Paragraph(f"Ksh {base_amount:,.2f}", table_cell)],
        ["", "", Paragraph("KRA VAT (16.00%):", table_cell), Paragraph(f"Ksh {vat_amount:,.2f}", table_cell)],
        ["", "", Paragraph("<b>Grand Total:</b>", table_cell), Paragraph(f"<b>Ksh {grand_total:,.2f}</b>", table_cell)]
    ]
    
    t3 = Table(items_data, colWidths=[240, 40, 120, 130])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (2,2), (2,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('LINEBELOW', (0,1), (-1,1), 0.5, colors.HexColor("#E2E8F0")),
        ('LINEABOVE', (2,4), (3,4), 1, colors.HexColor("#1A365D"))
    ]))
    story.append(t3)
    
    doc.build(story)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, send_file, render_template, redirect, url_for, session
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

# CRITICAL: Set a secret key to keep user login sessions securely encrypted
app.secret_key = 'jbs_secure_super_secret_key_2026'

# --- SECURITY GATEKEEPER ROUTING SYSTEM ---

@app.route('/')
def home():
    # If already logged in, skip the gateway and go straight to work
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Grab input details securely from the form payload
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Secure admin credentials alignment
    if username == 'admin' and password == 'bmd2026':
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    else:
        # If wrong, reload login with an error message parameter
        return render_template('login.html', error="Invalid Secure Terminal Credentials.")

@app.route('/logout')
def logout():
    # Clear the browser session tokens cleanly
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    # PROTECTED ROUTE: If they aren't logged in, block them completely!
    if 'logged_in' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/support')
def support():
    return render_template('support.html')
@app.route('/login', methods=['GET', 'POST']) # <-- Add methods here!
def login():
    if request.method == 'POST':
        # 1. Grab data from the HTML form
        username = request.form.get('username') 
        password = request.form.get('password')
        
        # 2. Add your login verification logic here...
        #if username == 'admin' and password =='bmd2026':
        session['logged_in'] = True
        return redirect(url_for('auth.dashboard'))     
    # If it's a GET request, just display the login page
    return render_template('login.html')
import sqlite3
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Database Setup Function
def init_db():
    conn = sqlite3.connect('logistics.db')
    cursor = conn.cursor()
    
    # Create a users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # For testing: Let's create a dummy driver/admin account if the DB is empty
    cursor.execute("SELECT * FROM users WHERE username='logistics_admin'")
    if not cursor.fetchone():
        # Hash the password "secure123" before saving it
        hashed_pw = bcrypt.generate_password_hash("secure123").decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       ('logistics_admin', hashed_pw))
        conn.commit()
        print("Database initialized with dummy user 'logistics_admin'.")
        
    conn.close()

# Initialize the database immediately when the script runs
init_db()

@app.route('/api/login', methods=['POST'])
def login_backend():
    data = request.get_json()
    
    # 1. Extract data from Frontend request
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # 2. Look up the user in the SQLite Database
    conn = sqlite3.connect('logistics.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    # 3. Verify user exists and check if the password matches the hash
    if row:
        stored_password_hash = row[0]
        
        # Bcrypt compares the typed password with the encrypted hash
        if bcrypt.check_password_hash(stored_password_hash, password):
            return jsonify({
                "status": "success",
                "message": f"Welcome back, {username}!"
            }), 200

    # 4. If anything fails, return an error code
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)


    