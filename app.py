import io

from flask import Flask, request, send_file, render_template, redirect, url_for, session, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import sqlite3
import os
import io
import os
from flask import send_from_directory
from flask import send_file
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
    try:
        # Pass session variables directly to protect the template evaluation
        return render_template(
            'home.html', 
            logged_in=session.get('logged_in', False),
            username=session.get('username', None)
        )
    except Exception as e:
        return f"Template Render Error: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Check credentials
        if verify_login(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            # If login fails, stay on login.html and show an error
            return render_template('login.html', error="Invalid credentials")
            
    # If it's a GET request, just show the login page
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/document')
def document_page():
    # Since everything sits independently in the root folder, 
    # we render it directly from your flat workspace structure.
    return render_template('document.html')

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



@app.route('/script.js')
def serve_script():
    # Dynamically find the absolute path of your root folder
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, 'script.js')

@app.route('/style.css')
def serve_css():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root_dir, 'style.css')

    import io
from flask import send_file

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    # ... your calculation logic here ...
    
    # Create an in-memory file stream instead of saving a file to Render's slow disk
    pdf_buffer = io.BytesIO()
    
    # Tell your PDF library (like ReportLab or FPDF) to write directly into the buffer
    # example: pdf.output(pdf_buffer) or canvas.save()
    
    pdf_buffer.seek(0)
    
    # Send it instantly down the pipeline
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='KRA_Compliant_Invoice.pdf'
    )
    import io
from flask import Flask, request, send_file, Response

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/dashboard')
def serve_dashboard():
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    # 1. Capture payload data sent from the dashboard
    data = request.get_json() or {}
    
    client_name = data.get('client_name', 'Valued Client')
    client_pin = data.get('client_pin', 'N/A')
    invoice_no = data.get('invoice_no', 'JBS-TEMP')
    due_date = data.get('due_date', 'N/A')
    
    # 2. Re-calculate financial sums cleanly on the server backend
    subtotal = 0
    table_rows_html = ""
    
    for item in data.get('items', []):
        desc = item.get('desc', 'Service Rendered')
        qty = int(item.get('qty', 1) or 1)
        price = float(item.get('price', 0) or 0)
        total_row_price = qty * price
        subtotal += total_row_price
        
        # Build individual tabular rows dynamically
        table_rows_html += f"""
        <tr>
            <td><strong>{desc}</strong></td>
            <td style="text-align: center;">{qty}</td>
            <td style="text-align: right;">{total_row_price:,.2f}</td>
        </tr>
        """
        
    vat = subtotal * 0.16
    grand_total = subtotal + vat

    # 3. Inject the dynamic fields directly into your layout template string
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4; margin: 16mm 14mm 20mm 14mm;
                @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font-family: Arial; font-size: 8pt; color: #888888; }}
                @bottom-left {{ content: "John's Billing System (JBS) • KRA Compliant Ledger"; font-family: Arial; font-size: 8pt; color: #888888; font-style: italic; }}
            }}
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #2D3748; margin: 0; padding: 0; font-size: 10pt; }}
            .header-container {{ display: table; width: 100%; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 2px solid #E2E8F0; }}
            .header-left {{ display: table-cell; width: 60%; vertical-align: top; }}
            .header-right {{ display: table-cell; width: 40%; vertical-align: top; text-align: right; }}
            .logo {{ font-size: 24pt; font-weight: 800; color: #0F2C59; margin: 0; }}
            .logo span {{ color: #3182CE; }}
            .company-details {{ font-size: 9pt; color: #4A5568; margin-top: 5px; }}
            .invoice-title {{ font-size: 26pt; font-weight: 800; color: #0F2C59; text-transform: uppercase; margin: 0; }}
            .status-badge {{ display: inline-block; background-color: #C6F6D5; color: #22543D; font-weight: 700; font-size: 9pt; padding: 4px 12px; border-radius: 12px; margin-top: 8px; border: 1px solid #9AE6B4; }}
            .meta-container {{ display: table; width: 100%; margin-bottom: 30px; }}
            .meta-left {{ display: table-cell; width: 55%; background-color: #F8FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #0F2C59; }}
            .meta-right {{ display: table-cell; width: 45%; padding-left: 25px; vertical-align: top; }}
            .section-heading {{ font-size: 9pt; font-weight: 700; color: #718096; text-transform: uppercase; margin: 0 0 8px 0; }}
            .client-name {{ font-size: 12pt; font-weight: 700; color: #0F2C59; }}
            .info-table {{ width: 100%; border-collapse: collapse; }}
            .info-table td {{ padding: 4px 0; font-size: 9.5pt; }}
            .info-label {{ color: #718096; }}
            .info-value {{ font-weight: 700; text-align: right; color: #2D3748; }}
            .items-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 25px; }}
            .items-table th {{ background-color: #0F2C59; color: #ffffff; padding: 10px 12px; font-weight: 700; text-transform: uppercase; font-size: 9pt; }}
            .items-table th:first-child {{ border-top-left-radius: 6px; }}
            .items-table th:last-child {{ border-top-right-radius: 6px; text-align: right; }}
            .items-table td {{ padding: 11px 12px; border-bottom: 1px solid #E2E8F0; font-size: 9.5pt; }}
            .items-table td:last-child {{ text-align: right; font-weight: 600; }}
            .items-table tr:nth-child(even) td {{ background-color: #F8FAFC; }}
            .summary-container {{ display: table; width: 100%; margin-top: 15px; }}
            .payment-cell {{ display: table-cell; width: 55%; vertical-align: top; padding-right: 20px; }}
            .totals-cell {{ display: table-cell; width: 45%; vertical-align: top; }}
            .payment-panel {{ background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; }}
            .mpesa-header {{ color: #48BB78; font-weight: 800; font-size: 10pt; text-transform: uppercase; margin-bottom: 8px; }}
            .totals-table {{ width: 100%; border-collapse: collapse; }}
            .totals-table td {{ padding: 6px 8px; font-size: 9.5pt; }}
            .grand-total-row td {{ background-color: #0F2C59; color: #ffffff; padding: 10px 12px; border-radius: 6px; }}
            .grand-total-row .totals-value {{ font-size: 13pt; font-weight: 800; text-align: right; }}
            .footer-signoff {{ display: table; width: 100%; margin-top: 35px; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
            .terms-cell {{ display: table-cell; width: 75%; font-size: 8.5pt; color: #718096; line-height: 1.5; }}
            .qr-cell {{ display: table-cell; width: 25%; text-align: right; vertical-align: middle; }}
            .qr-box {{ display: inline-block; width: 70px; height: 70px; border: 2px dashed #CBD5E0; padding: 4px; border-radius: 4px; }}
            .qr-graphic {{ width: 100%; height: 100%; background-color: #2D3748; background-image: linear-gradient(45deg, #fff 25%, transparent 25%), linear-gradient(-45deg, #fff 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #fff 75%), linear-gradient(-45deg, transparent 75%, #fff 75%); background-size: 8px 8px; }}
        </style>
    </head>
    <body>
        <div class="header-container">
            <div class="header-left">
                <h1 class="logo">JBS<span>.</span></h1>
                <div class="company-details">
                    <strong>John's Billing System Ltd.</strong><br>
                    Eldoret-Malaba Road, Polyview Heights<br>
                    PIN: P051234567Z • Email: billing@jbs.co.ke
                </div>
            </div>
            <div class="header-right">
                <h2 class="invoice-title">Invoice</h2>
                <div class="status-badge">Paid</div>
            </div>
        </div>

        <div class="meta-container">
            <div class="meta-left">
                <h3 class="section-heading">Billed To:</h3>
                <div class="client-name">{client_name}</div>
                <div class="client-details">
                    PIN: {client_pin}
                </div>
            </div>
            <div class="meta-right">
                <h3 class="section-heading">Invoice Details:</h3>
                <table class="info-table">
                    <tr><td class="info-label">Invoice No:</td><td class="info-value">{invoice_no}</td></tr>
                    <tr><td class="info-label">Due Date:</td><td class="info-value">{due_date}</td></tr>
                </table>
            </div>
        </div>

        <table class="items-table">
            <thead>
                <tr>
                    <th style="text-align: left; width: 50%;">Item / Service Description</th>
                    <th style="text-align: center; width: 15%;">Qty</th>
                    <th style="text-align: right; width: 35%;">Amount (KES)</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>

        <div class="summary-container">
            <div class="payment-cell">
                <h3 class="section-heading">Payment Channels:</h3>
                <div class="payment-panel">
                    <div class="mpesa-header">Lipa Na M-Pesa</div>
                    <div><strong>Business Till No:</strong> 5928103</div>
                    <div style="margin-top: 3px;"><strong>Account No:</strong> JBS-0089</div>
                </div>
            </div>
            <div class="totals-cell">
                <table class="totals-table">
                    <tr><td style="text-align:right;">Subtotal:</td><td style="text-align:right; font-weight:600;">{subtotal:,.2f}</td></tr>
                    <tr><td style="text-align:right;">VAT (16%):</td><td style="text-align:right; font-weight:600;">{vat:,.2f}</td></tr>
                    <tr class="grand-total-row"><td style="color:#fff; text-align:right; font-weight:700;">Total Due:</td><td class="totals-value">{grand_total:,.2f}</td></tr>
                </table>
            </div>
        </div>

        <div class="footer-signoff">
            <div class="terms-cell">
                <strong>Terms & Conditions:</strong><br>
                All balances are tracked natively in KES. Payments must clear via authorized M-Pesa channels. Accounts overdue by 14 days incur standard tracking fines.
            </div>
            <div class="qr-cell">
                <div class="qr-box"><div class="qr-graphic"></div></div>
                <div style="font-size: 7pt; color: #A0AEC0; font-weight: bold; margin-top: 3px;">KRA TIMS VAL</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 4. Stream via WeasyPrint directly from server RAM buffers
    from weasyprint import HTML
    pdf_buffer = io.BytesIO()
    HTML(string=html_template).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{invoice_no}.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)