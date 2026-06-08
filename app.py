import io
import os
from flask import Flask, request, send_file, Response, redirect, url_for

# Automatically map the absolute directory path to prevent Render deployment 404 errors
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

@app.route('/')
def home():
    """Serves the application homepage ledger interface dynamically from the workspace."""
    try:
        html_path = os.path.join(BASE_DIR, 'home.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/html')
    except FileNotFoundError:
        return f"System Maintenance Error: 'home.html' was not found at expected workspace path: {html_path}", 404

@app.route('/dashboard')
def serve_dashboard():
    """Fallback route redirecting users safely to the main workspace anchor."""
    return redirect(url_for('home'))

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """
    Receives billing JSON arrays, dynamically loops through invoice items,
    injects calculations into a clean HTML template, and compiles an A4 PDF stream.
    """
    data = request.get_json() or {}
    
    # Retrieve structural metadata with robust fallbacks
    client_name = data.get('client_name', 'Valued Client')
    client_pin = data.get('client_pin', 'N/A')
    invoice_no = data.get('invoice_no', 'JBS-TEMP')
    due_date = data.get('due_date', 'N/A')
    
    subtotal = 0
    table_rows_html = ""
    
    # Construct rows dynamically from frontend data input array
    for item in data.get('items', []):
        desc = item.get('desc', 'Service Rendered')
        qty = int(item.get('qty', 1) or 1)
        price = float(item.get('price', 0) or 0)
        total_row_price = qty * price
        subtotal += total_row_price
        
        table_rows_html += f"""
        <tr>
            <td><strong>{desc}</strong></td>
            <td style="text-align: center;">{qty}</td>
            <td style="text-align: right;">{total_row_price:,.2f}</td>
        </tr>
        """
        
    # Calculate complete compliant balance details
    vat = subtotal * 0.16
    grand_total = subtotal + vat

    # Professional layout styles and markup template string
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
            .grand-total-row {{ background-color: #0F2C59; color: #ffffff; }}
            .grand-total-row td {{ padding: 10px 12px; font-weight: 700; }}
            .totals-value {{ font-size: 12pt; font-weight: 800; text-align: right; }}
            .footer-signoff {{ display: table; width: 100%; margin-top: 35px; border-top: 1px solid #E2E8F0; padding-top: 15px; }}
            .terms-cell {{ display: table-cell; width: 75%; font-size: 8.5pt; color: #718096; line-height: 1.5; }}
            .qr-cell {{ display: table-cell; width: 25%; text-align: right; vertical-align: middle; }}
            .qr-box {{ display: inline-block; width: 65px; height: 65px; border: 2px dashed #CBD5E0; padding: 4px; border-radius: 4px; }}
            .qr-graphic {{ width: 100%; height: 100%; background-color: #2D3748; background-image: linear-gradient(45deg, #fff 25%, transparent 25%), linear-gradient(-45deg, #fff 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #fff 75%), linear-gradient(-45deg, transparent 75%, #fff 75%); background-size: 6px 6px; }}
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
                <div class="client-details">PIN: {client_pin}</div>
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
                    <div style="margin-top: 3px;"><strong>Account No:</strong> {invoice_no}</div>
                </div>
            </div>
            <div class="totals-cell">
                <table class="totals-table">
                    <tr><td style="text-align:right;">Subtotal:</td><td style="text-align:right; font-weight:600;">{subtotal:,.2f}</td></tr>
                    <tr><td style="text-align:right;">VAT (16%):</td><td style="text-align:right; font-weight:600;">{vat:,.2f}</td></tr>
                    <tr class="grand-total-row"><td style="text-align:right;">Total Due:</td><td class="totals-value">{grand_total:,.2f}</td></tr>
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
    
    # Import locally to keep memory allocation minimal during application startup
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