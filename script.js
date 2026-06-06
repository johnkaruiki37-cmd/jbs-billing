let subtotal = 0;

function addItem() {
    let item = document.getElementById("item").value;
    let price = parseFloat(document.getElementById("price").value);
    let quantity = parseInt(document.getElementById("quantity").value);

    if (item.trim() === "" || isNaN(price) || isNaN(quantity)) {
        alert("Please enter valid item description, price, and quantity values.");
        return;
    }

    let total = price * quantity;
    subtotal += total;

    // Run tax calculation adjustments on UI
    calculate();

    let table = document.getElementById("billTable");
    let rowHTML = `
        <tr>
            <td><b>${item}</b></td>
            <td>${quantity}</td>
            <td>Ksh ${price.toFixed(2)}</td>
            <td>Ksh ${total.toFixed(2)}</td>
        </tr>
    `;
    table.insertAdjacentHTML('beforeend', rowHTML);

    // Clear item fields for next line entry
    document.getElementById("item").value = "";
    document.getElementById("price").value = "";
    document.getElementById("quantity").value = "1";
}

function calculate() {
    // Current 2026 Kenyan KRA Statutory VAT Ratio (16%)
    let vat = subtotal * 0.16;
    let grand = subtotal + vat;

    if(document.getElementById("subtotalValue")) document.getElementById("subtotalValue").innerText = subtotal.toFixed(2);
    if(document.getElementById("vatValue")) document.getElementById("vatValue").innerText = vat.toFixed(2);
    if(document.getElementById("grandValue")) document.getElementById("grandValue").innerText = grand.toFixed(2);
}

async function downloadPDF() {
    let grandText = document.getElementById("grandValue") ? document.getElementById("grandValue").innerText : "0.00";
    
    let data = {
        customer: document.getElementById("customer").value || "Valued Client",
        invoice: document.getElementById("invoice").value || "N/A",
        total: grandText,
        servedBy: document.getElementById("cashier") ? document.getElementById("cashier").value : "System Admin",
        date: new Date().toLocaleDateString('en-GB'),
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    try {
        const response = await fetch("http://127.0.0.1:5000/generate-pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `KRA_Invoice_${data.invoice}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert("Error: Server was unable to compile the binary ReportLab target asset.");
        }
    } catch (error) {
        console.error("Transmission Error:", error);
        alert("Could not talk to the Flask backend terminal. Please double check that 'py app.py' is running!");
    }
}
function generateInvoiceLink() {
    let customerName = document.getElementById("customer").value || "Valued Client";
    let invoiceNo = document.getElementById("invoice").value || "N/A";
    let grandText = document.getElementById("grandTotalDisplay").innerText || "0";

    let payload = {
        customer: customerName,
        invoice: invoiceNo,
        total: grandText,
        servedBy: "Admin",
        date: new Date().toLocaleDateString('en-GB'),
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Send data to our single-folder Flask backend
    fetch('/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) throw new Error("Backend engine generation error");
        return response.blob();
    })
    .then(blob => {
        // Create a direct virtual object link to the file blob data
        let fileUrl = window.URL.createObjectURL(blob);
        
        // Grab our HTML link elements
        let container = document.getElementById("invoice-link-container");
        let metaText = document.getElementById("invoice-link-meta");
        let downloadBtn = document.getElementById("direct-download-btn");

        // Inject the download target and file name attributes
        downloadBtn.href = fileUrl;
        downloadBtn.download = `Invoice_${invoiceNo}.pdf`;

        // Update descriptions dynamically
        metaText.innerText = `Invoice: #${invoiceNo} | Client: ${customerName} | Total: ${grandText}`;

        // Make the link box display on screen cleanly
        container.style.display = "block";
    })
    .catch(error => {
        console.error("Link generation failure:", error);
        alert("System encountered an issue linking the generated asset.");
    });
}
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const fileNameSpan = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFileBtn');

let selectedFile = null;

// Trigger file browser when clicking the drop zone
// Locate line 139 and modify the listener assignment safely
const targetFormElement = document.getElementById('loginForm'); // or whatever ID is on line 139

if (targetFormElement) {
    targetFormElement.addEventListener('submit', function(e) {
        // Your existing form logic stays right here
    });
}
// 2. Wrap it in a safety check so it only runs if the element exists on the page
if (dropzone) {
    dropzone.addEventListener('click', function() {
        // Automatically click the hidden file input when the box is clicked
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.click();
        }
    });
}

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

// Drag and drop event listeners
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drop-zone--over');
});

['dragleave', 'dragend'].forEach(type => {
    dropZone.addEventListener(type, () => dropZone.classList.remove('drop-zone--over'));
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drop-zone--over');
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFile(e.dataTransfer.files[0]);
    }
});

function handleFile(file) {
    selectedFile = file;
    fileNameSpan.textContent = file.name;
    filePreview.style.display = 'flex';
}

removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectedFile = null;
    fileInput.value = '';
    filePreview.style.display = 'none';
});

// --- DISPATCH CHANNELS ---

// 1. WhatsApp Redirection API
document.getElementById('sendWhatsApp').addEventListener('click', () => {
    const phone = document.getElementById('whatsappNumber').value.trim();
    if (!phone || phone === "254") {
        alert("Please provide a valid WhatsApp number including your country code.");
        return;
    }
    
    // Note: Standard web links cannot attach physical files directly due to browser security.
    // We send an optimized alert text prompting immediate follow-up.
    const message = encodeURIComponent(`Hello, I am sending over the requested invoice document: *${selectedFile ? selectedFile.name : 'Invoice'}*. Please check your email or let me know if you would like me to upload it here.`);
    
    window.open(`https://api.whatsapp.com/send?phone=${phone}&text=${message}`, '_blank');
});

// 2. Gmail Redirection Link Generator
document.getElementById('sendGmail').addEventListener('click', () => {
    const email = document.getElementById('emailAddress').value.trim();
    if (!email) {
        alert("Please enter a recipient email address.");
        return;
    }

    const subject = encodeURIComponent("Logistics Invoice & Documentation");
    const body = encodeURIComponent(`Greetings,\n\nPlease find attached the relevant logistics documentation: ${selectedFile ? selectedFile.name : 'Invoice'}.\n\nBest Regards,\nLogistics Team`);
    
    // Opens user's desktop email client or web client with details filled out
    window.location.href = `mailto:${email}?subject=${subject}&body=${body}`;
});
function generateInvoiceLink() {
    console.log("Generating invoice link...");
    // Add your logic for creating an invoice link here
}

function downloadPDF() {
    console.log("Downloading compliant KRA PDF...");
    // Add your logic for compiling or downloading the PDF asset here
}
function addRecordLine() {
    console.log("Adding a new record line item...");
    // Add your logic here to insert a row into your ledger stream table
}