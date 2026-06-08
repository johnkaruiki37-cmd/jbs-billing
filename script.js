/**
 * John's Billing System - Client Logic Controller
 */

function calculateTotals() {
    const rows = document.querySelectorAll('.invoice-row');
    let subtotal = 0;

    rows.forEach(row => {
        const qtyInput = row.querySelector('.item-qty');
        const priceInput = row.querySelector('.item-price');
        const totalContainer = row.querySelector('.item-total');

        const qty = parseInt(qtyInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const rowTotal = qty * price;
        subtotal += rowTotal;

        // Render formatted local row calculations
        totalContainer.textContent = rowTotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    });

    // Compute aggregate tax objects
    const vat = subtotal * 0.16;
    const grandTotal = subtotal + vat;

    // Inject state data parameters cleanly back to UI containers
    document.getElementById('summary-subtotal').textContent = `KES ${subtotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('summary-vat').textContent = `KES ${vat.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('summary-grand-total').textContent = `KES ${grandTotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function addRecordLine() {
    console.log("Adding a new record line item...");
    const tbody = document.getElementById('invoice-table-body');
    
    if (!tbody) {
        console.error("Could not find the target element with ID 'invoice-table-body' on this page!");
        return;
    }

    const row = document.createElement('tr');
    row.className = 'invoice-row';
    row.innerHTML = `
        <td><input type="text" class="form-input item-desc" placeholder="Enter service description or product details..."></td>
        <td><input type="number" class="form-input item-qty" value="1" style="text-align:center;" oninput="calculateTotals()"></td>
        <td><input type="number" class="form-input item-price" value="0" style="text-align:right;" oninput="calculateTotals()"></td>
        <td class="item-total" style="text-align: right; font-weight: 600;">0.00</td>
    `;
    
    tbody.appendChild(row);
    calculateTotals();
}

async function compileAndDownloadPDF() {
    console.log("Downloading compliant KRA PDF...");
    
    const payload = {
        client_name: document.getElementById('client-name').value,
        client_pin: document.getElementById('client-pin').value,
        invoice_no: document.getElementById('invoice-no').value,
        due_date: document.getElementById('due-date').value,
        items: []
    };

    const rows = document.querySelectorAll('.invoice-row');
    rows.forEach(row => {
        payload.items.push({
            desc: row.querySelector('.item-desc').value,
            qty: row.querySelector('.item-qty').value,
            price: row.querySelector('.item-price').value
        });
    });

    try {
        const response = await fetch('/download-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server returned error status code: ${response.status}`);
        }

        // Process file payload stream down to disk download anchor
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${payload.invoice_no}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
    } catch (error) {
        console.error("PDF engine failure:", error);
        alert("Transmission dropped. Check that the python app backend console is running cleanly.");
    }
}

// Initial calculation call on load
calculateTotals();