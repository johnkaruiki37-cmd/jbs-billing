from flask import Flask, request, send_file, render_template, redirect, url_for, session, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import sqlite3
import os

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)
bcrypt = Bcrypt(app)
app.secret_key = 'jbs_secure_super_secret_key_2026'#Add this line!

# SECURITY: Load from environment variable, not hardcoded
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_change_in_production')

# --- DATABASE INITIALIZATION ---

def init_db():
    """Initialize SQLite database with users table"""
    conn = sqlite3.connect('jbs_billing.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin if DB is empty
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        hashed_pw = bcrypt.generate_password_hash('bmd2026').decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ('admin', hashed_pw)
        )
        conn.commit()
        print("Database initialized with default admin user")
    
    conn.close()

init_db()

# --- AUTHENTICATION HELPERS ---

def verify_login(username, password):
    """Verify username and password against database"""
    if not username or not password:
        return False
    
    conn = sqlite3.connect('jbs_billing.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return bcrypt.check_password_hash(row[0], password)
    return False

def login_required(f):
    """Decorator to protect routes"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

# --- NAVIGATION ROUTES ---

@app.route('/')
def home():
    """Landing page - redirect to dashboard if logged in"""
    if 'logged_in' in session:
        return redirect(url_for('home.html'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Handle login form"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if verify_login(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main billing dashboard"""
    return render_template('dashboard.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/support')
def support():
    """Support/FAQ page"""
    return render_template('support.html')

# --- PDF GENERATION ---

@app.route('/generate-pdf', methods=['POST'])
@login_required
def generate_pdf():
    """Generate KRA-compliant invoice PDF"""
    try:
        data = request.get_json()
        
        customer_name = (data.get('customer') or 'Valued Customer').strip()
        invoice_no = (data.get('invoice') or 'N/A').strip()
        raw_total = (data.get('total') or '0').replace('ksh', '').strip()
        served_by = (data.get('servedBy') or 'Admin').strip()
        current_date = (data.get('date') or '').strip()
        current_time = (data.get('time') or '').strip()
        
        # Validate and convert total
        try:
            grand_total = float(raw_total)
            if grand_total < 0:
                return jsonify({"error": "Total cannot be negative"}), 400
        except ValueError:
            return jsonify({"error": "Invalid total amount"}), 400
        
        # KRA Tax Calculation: Total = Base + 16% VAT
        base_amount = grand_total / 1.16
        vat_amount = grand_total - base_amount
        
        pdf_path = f"invoice_{invoice_no}.pdf"
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        story = []
        
        # Styles
        title_style = ParagraphStyle(
            'DocTitle',
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=colors.HexColor("#1A365D")
        )
        company_style = ParagraphStyle(
            'CompInfo',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#4A5568")
        )
        meta_style = ParagraphStyle('MetaText', fontSize=10, leading=14)
        table_header = ParagraphStyle(
            'TH',
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=colors.white
        )
        table_cell = ParagraphStyle('TC', fontSize=10)
        
        # Header
        header_data = [
            [
                Paragraph("<b>JOHN BILLING SYSTEM</b>", title_style),
                Paragraph(
                    f"<b>INVOICE RECEIPT</b><br/>No: #{invoice_no}",
                    ParagraphStyle('R', alignment=2, fontSize=11)
                )
            ],
            [
                Paragraph(
                    "Nairobi, Kenya<br/>Contact: +254 798 770325<br/>Email: johnkaruiki37@gmail.com",
                    company_style
                ),
                Paragraph(
                    f"<b>Date:</b> {current_date}<br/><b>Time:</b> {current_time}<br/><b>Status:</b> PAID",
                    ParagraphStyle('R2', alignment=2, fontSize=9, leading=13)
                )
            ]
        ]
        t1 = Table(header_data, colWidths=[270, 260])
        t1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(t1)
        story.append(Spacer(1, 15))
        
        # Accent line
        line = Table([[""]], colWidths=[530], rowHeights=[2])
        line.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#1A365D"))]))
        story.append(line)
        story.append(Spacer(1, 15))
        
        # Metadata
        meta_data = [
            [
                Paragraph(f"<b>BILLED TO:</b><br/>{customer_name}", meta_style),
                Paragraph(
                    f"<b>TRANSACTION DETAILS:</b><br/>Served By: {served_by}<br/>Payment System: Cash/M-Pesa",
                    meta_style
                )
            ]
        ]
        t2 = Table(meta_data, colWidths=[265, 265])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ('PADDING', (0, 0), (-1, -1), 8)
        ]))
        story.append(t2)
        story.append(Spacer(1, 20))
        
        # Items table
        items_data = [
            [
                Paragraph("Description", table_header),
                Paragraph("Qty", table_header),
                Paragraph("Unit Price", table_header),
                Paragraph("Amount", table_header)
            ],
            [
                Paragraph("General Ledger Goods / Services Rendered", table_cell),
                Paragraph("1", table_cell),
                Paragraph(f"Ksh {base_amount:,.2f}", table_cell),
                Paragraph(f"Ksh {base_amount:,.2f}", table_cell)
            ],
            ["", "", Paragraph("Subtotal (Excl. VAT):", table_cell), Paragraph(f"Ksh {base_amount:,.2f}", table_cell)],
            ["", "", Paragraph("KRA VAT (16.00%):", table_cell), Paragraph(f"Ksh {vat_amount:,.2f}", table_cell)],
            ["", "", Paragraph("<b>Grand Total:</b>", table_cell), Paragraph(f"<b>Ksh {grand_total:,.2f}</b>", table_cell)]
        ]
        
        t3 = Table(items_data, colWidths=[240, 40, 120, 130])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ('ALIGN', (2, 2), (2, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.HexColor("#E2E8F0")),
            ('LINEABOVE', (2, 4), (3, 4), 1, colors.HexColor("#1A365D"))
        ]))
        story.append(t3)
        
        doc.build(story)
        return send_file(pdf_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    from flask import send_from_directory


import os
from flask import send_from_directory

@app.route('/script.js')
def serve_script():
    # Dynamically find the absolute path of your root folder
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, 'script.js')

@app.route('/style.css')
def serve_css():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, 'style.css')

    