document.addEventListener("DOMContentLoaded", () => {
    // Check local storage for persistent theme choice
    const savedTheme = localStorage.getItem("jbs-theme");
    const toggleButton = document.getElementById("theme-toggle");

    if (savedTheme === "light") {
        document.documentElement.setAttribute("data-theme", "light");
        if (toggleButton) toggleButton.innerHTML = `<i class="fa-solid fa-sun"></i>`;
    }

    if (toggleButton) {
        toggleButton.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            if (currentTheme === "light") {
                document.documentElement.removeAttribute("data-theme");
                localStorage.setItem("jbs-theme", "dark");
                toggleButton.innerHTML = `<i class="fa-solid fa-moon"></i>`;
            } else {
                document.documentElement.setAttribute("data-theme", "light");
                localStorage.setItem("jbs-theme", "light");
                toggleButton.innerHTML = `<i class="fa-solid fa-sun"></i>`;
            }
        });
    }
});
const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware configurations
app.use(cors());
app.use(express.json());

// Serve static assets out of the 'public' folder (CSS, Client JS, Images)
app.use(express.static(path.join(__dirname, 'public')));

/* ==========================================================================
   1. MOCK DATA REGISTRIES (Simulating Database Entities)
   ========================================================================== */
let inventoryStock = [
    { code: "JBS-SKU-401", name: "Amoxicillin 500mg Matrix Pack", category: "Medical / Pharmacy", qty: 820, value: 120000, status: "Optimal Vault Reserves" },
    { code: "JBS-SKU-902", name: "Portland Cement Type I 50KG Bags", category: "Hardware Supply", qty: 8, value: 6800, status: "Depleted Alert Stage" },
    { code: "JBS-SKU-114", name: "High-Nitrogen Growth Liquid 1L", category: "Agrovet Solutions", qty: 142, value: 213000, status: "Reorder Schedule Armed" }
];

let mpesaTransactions = [
    { token: "RFI84910DX", date: "2026-06-09 10:42", account: "Kamau Supermarket Systems", phone: "0722000111", amount: 45000, status: "API Reconciled" },
    { token: "RFI84911AF", date: "2026-06-09 11:15", account: "Wamae Agrovet Outlet", phone: "0711999888", amount: 12300, status: "API Reconciled" }
];

/* ==========================================================================
   2. RESTFUL API ROUTING GATEWAYS
   ========================================================================== */

// Get current inventory datasets
app.get('/api/inventory', (req, res) => {
    res.json(inventoryStock);
});

// Get payment gateway verification streams
app.get('/api/mpesa/ledger', (req, res) => {
    res.json(mpesaTransactions);
});

// Inbound STK Push Callback Webhook simulation entry point
app.post('/api/mpesa/callback', (req, res) => {
    const { account, phone, amount } = req.body;
    
    if (!account || !amount) {
        return res.status(400).json({ error: "Missing payload payment data parameters" });
    }

    const newTransaction = {
        token: "RFI" + Math.floor(100000 + Math.random() * 900000) + "TX",
        date: new Date().toISOString().replace('T', ' ').substring(0, 16),
        account,
        phone: phone || "07XXXXXXXX",
        amount: parseFloat(amount),
        status: "API Reconciled"
    };

    mpesaTransactions.unshift(newTransaction); // Add to the top of ledger
    res.status(201).json({ message: "Callback settlement committed successfully", transaction: newTransaction });
});

/* ==========================================================================
   3. CLEAN EXPLICIT CLIENT PAGE ROUTING LAYER
   ========================================================================== */
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));
app.get('/dashboard', (req, res) => res.sendFile(path.join(__dirname, 'public', 'dashboard.html')));
app.get('/billing', (req, res) => res.sendFile(path.join(__dirname, 'public', 'billing.html')));
app.get('/mpesa', (req, res) => res.sendFile(path.join(__dirname, 'public', 'mpesa.html')));
app.get('/inventory', (req, res) => res.sendFile(path.join(__dirname, 'public', 'inventory.html')));
app.get('/scanner', (req, res) => res.sendFile(path.join(__dirname, 'public', 'scanner.html')));
app.get('/forum', (req, res) => res.sendFile(path.join(__dirname, 'public', 'forum.html')));
app.get('/about', (req, res) => res.sendFile(path.join(__dirname, 'public', 'about.html')));

// Fallback Wildcard 404 handler
app.use((req, res) => {
    res.status(404).send('<h1>Error 404: JBS Platform Resource Not Found</h1>');
});

/* ==========================================================================
   4. SYSTEM INITIALIZATION LISTENERS
   ========================================================================== */
app.listen(PORT, () => {
    console.log(`================================================================`);
    console.log(` JBS PLATFORM BACKEND ENGINE ONLINE`);
    console.log(` Running locally on connection channel: http://localhost:${PORT}`);
    console.log(`================================================================`);
});
// Fetch and render products on load
async function loadInventory() {
    const response = await fetch('/api/inventory');
    const items = await response.json();
    const tableBody = document.querySelector('.data-table tbody');
    if (!tableBody) return;

    tableBody.innerHTML = items.map(item => `
        <tr>
            <td><code>${item.code}</code></td>
            <td>${item.name}</td>
            <td>${item.category}</td>
            <td>${item.qty} units</td>
            <td>Ksh ${item.value.toLocaleString()}</td>
            <td><span class="status-pill ${item.qty > 10 ? 'status-success' : 'status-danger'}">${item.status}</span></td>
        </tr>
    `).join('');
}

// Handle adding a new product manually
async function addProduct(event) {
    event.preventDefault();
    const payload = {
        code: document.getElementById('prod-code').value,
        name: document.getElementById('prod-name').value,
        category: document.getElementById('prod-category').value,
        qty: parseInt(document.getElementById('prod-qty').value),
        value: parseFloat(document.getElementById('prod-value').value)
    };

    const response = await fetch('/api/inventory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (response.ok) {
        loadInventory();
        event.target.reset();
    }
}

// Simulated Barcode Scanner Reader Engine
function simulateBarcodeScan(scannedCode) {
    console.log(`Processing scanned hardware asset label: ${scannedCode}`);
    // Auto-fill form fields if a match is detected
    document.getElementById('prod-code').value = scannedCode;
}

document.addEventListener('DOMContentLoaded', loadInventory);
// Dynamic Message Fetcher Engine
async function loadFeed() {
    try {
        const res = await fetch('/api/forum/messages');
        const data = await res.json();
        const forumBox = document.getElementById('forum-box');
        if (!forumBox) return;

        // Render rows dynamically into the UI window
        forumBox.innerHTML = data.map(m => `
            <div style="margin-bottom:1rem; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:0.5rem; animation: fadeIn 0.3s ease;">
                <span style="color:var(--accent-gold); font-weight:bold;">@${m.user}</span> 
                <span style="font-size:0.75rem; color:var(--text-muted); margin-left:8px;">${m.time}</span>
                <p style="margin:5px 0 0 0; color:#fff; font-size:0.95rem;">${m.text}</p>
            </div>
        `).join('');
    } catch(err) {
        console.error("Failed to sync community message updates.", err);
    }
}

// Intercept click submit events safely
document.getElementById('forum-form').addEventListener('submit', async (e) => {
    e.preventDefault(); // Stop page from refreshing or redirecting!
    
    const userField = document.getElementById('user-handle');
    const textField = document.getElementById('msg-text');

    if (!textField.value.trim()) return;

    try {
        const response = await fetch('/api/forum/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user: userField.value,
                text: textField.value
            })
        });

        if (response.ok) {
            textField.value = ""; // Clear out input field instantly on success
            await loadFeed();     // Force an immediate refresh of the message board
            
            // Automatically scroll the chat container window to the bottom row
            const forumBox = document.getElementById('forum-box');
            forumBox.scrollTop = forumBox.scrollHeight;
        } else {
            const errData = await response.json();
            alert(`Broadcast Refused: ${errData.message}`);
        }
    } catch (err) {
        alert("Network transaction failed. Verify Node.js backend is active.");
    }
});

// Run loop schedules
setInterval(loadFeed, 3000); // Check for incoming messages every 3 seconds
document.addEventListener('DOMContentLoaded', loadFeed); // Run instantly when page first loads