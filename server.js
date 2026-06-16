const express = require('express');
const path = require('path');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(__dirname));

/* ==========================================================================
   CENTRAL PLATFORM SYSTEM LEDGERS (Thread-Safe Database Store Matrix)
   ========================================================================== */
let inventoryStock = {
    "JBS-SKU-401": { product_id: "PRD-001", name: "Amoxicillin 500mg Matrix Pack", barcode: "JBS-SKU-401", serial_number: "SN-AMX-9941A", qty: 820, date_added: "2026-01-10 10:00", last_scanned: "2026-06-15 09:12", supplier: "Biomed Africa", category: "Medical / Pharmacy", unit_value: 120 }
};

// Enterprise Social Model Registries 
let masterForumPosts = [
    {
        id: "PST-1002",
        category: "Tax & Compliance",
        content: "Be careful when preparing your returns on #KRAEfiling2026 this week. Ensure all ledger match calculations are balanced inside your inventory reporting matrices before clicking submit.",
        image_url: "",
        likes: 12,
        created_at: "2026-06-15 11:20",
        author: {
            id: "USR-001",
            user: "Admin_Kabuthi",
            full_name: "Dr. John Kabuthi",
            business_name: "JBS Main Hub Node",
            badge: "Admin",
            avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80"
        }
    }
];

let connectedOperatorsMap = new Map();

const sanitizeInput = (str) => str ? String(str).trim().replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";

/* ==========================================================================
   SOCKET.IO REAL-TIME COMMUNICATION ENGINE CHANNELS
   ========================================================================== */
io.on('connection', (socket) => {
    console.log(`[SOCKET PIPELINE CONNECTED] Active socket session ID: ${socket.id}`);

    // Handle initial network presence announcements
    socket.on('operator_handshake_join', (profilePayload) => {
        connectedOperatorsMap.set(socket.id, profilePayload);
        // Multicast updated active operator matrices back to all active UI grids
        io.emit('online_operators_matrix', Array.from(connectedOperatorsMap.values()));
    });

    socket.on('disconnect', () => {
        connectedOperatorsMap.delete(socket.id);
        io.emit('online_operators_matrix', Array.from(connectedOperatorsMap.values()));
        console.log(`[SOCKET DISCONNECTED] Dropped stream tracking link ID: ${socket.id}`);
    });
});

/* ==========================================================================
   ADVANCED COMMUNITY HUBS SOCIAL PLATFORM ROUTING ENDPOINTS
   ========================================================================== */

// 1. Fetch all community posts
app.get('/api/forum/posts', (req, res) => {
    res.json(masterForumPosts);
});

// 2. Transmit and broadcast new community posts instantly
app.post('/api/forum/create-post', (req, res) => {
    const { author, category, content, image_url } = req.body;
    
    if(!content || !content.trim()) {
        return res.status(400).json({ success: false, message: "Content input cannot be blank." });
    }

    const timestampStr = new Date().toISOString().replace('T', ' ').substring(0, 16);
    const generatedPostRow = {
        id: `PST-${Date.now()}`,
        category: sanitizeInput(category || "General Discussions"),
        content: sanitizeInput(content),
        image_url: image_url ? String(image_url).trim() : "",
        likes: 0,
        created_at: timestampStr,
        author: {
            id: sanitizeInput(author.id),
            user: sanitizeInput(author.user),
            full_name: sanitizeInput(author.full_name),
            business_name: sanitizeInput(author.business_name),
            badge: sanitizeInput(author.badge || "Member"),
            avatar: author.avatar || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80"
        }
    };

    masterForumPosts.unshift(generatedPostRow);

    // Dynamic real-time socket propagation to all online dashboard pipelines
    io.emit('incoming_forum_post', generatedPostRow);

    res.status(201).json({ success: true, post: generatedPostRow });
});

// 3. Like a post instantly via socket updates
app.post('/api/forum/like/:id', (req, res) => {
    const targetPost = masterForumPosts.find(p => p.id === req.params.id);
    if (!targetPost) return res.status(404).json({ success: false, message: "Target element missing." });

    targetPost.likes += 1;
    
    // Broadcast live update across all online user interfaces
    io.emit('post_reaction_updated', { postId: targetPost.id, count: targetPost.likes });
    
    res.json({ success: true, total_likes: targetPost.likes });
});

/* ==========================================================================
   LEGACY ADAPTER CHANNELS AND FILE INTERACTION ROUTERS
   ========================================================================== */
app.get('/api/inventory', (req, res) => res.json(Object.values(inventoryStock)));
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));
app.get('/scanner', (req, res) => res.sendFile(path.join(__dirname, 'scanner.html')));
app.get('/forum', (req, res) => res.sendFile(path.join(__dirname, 'community-hub-forum.html')));
app.get('/inventory', (req, res) => res.sendFile(path.join(__dirname, 'inventory.html')));

app.use((req, res) => {
    res.status(404).send('<body style="background:#0f172a;color:#ef4444;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;"><h1>Error 404: Resource Missing</h1></body>');
});

// CRITICAL: Listen using the custom HTTP framework object container rather than the bare Express app instance 
server.listen(PORT, () => {
    console.log(`================================================================`);
    console.log(` JBS COHESIVE REAL-TIME NETWORKING ONLINE ON PORT: ${PORT}`);
    console.log(`================================================================`);
});
const express = require('express');
const path = require('path');
const cors = require('cors');
const http = require('http');

const app = express();
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(__dirname));

/* ==========================================================================
   CENTRAL SYSTEM REGISTRY STORAGE (Cohesive Memory Datastore)
   ========================================================================== */
let inventoryStock = {
    "JBS-SKU-401": { product_id: "PRD-001", name: "Amoxicillin 500mg Matrix Pack", barcode: "JBS-SKU-401", serial_number: "SN-AMX-9941A", qty: 820, supplier: "Biomed Africa", category: "Medical / Pharmacy", unit_value: 120 },
    "JBS-SKU-902": { product_id: "PRD-002", name: "Portland Cement Type I 50KG Bags", barcode: "JBS-SKU-902", serial_number: "SN-CMT-1102X", qty: 15, supplier: "Bamburi Structural", category: "Hardware Supply", unit_value: 850 }
};

let mpesaTransactions = [];
let billingInvoicesLedger = [];

const sanitizeInput = (str) => str ? String(str).trim().replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";

/* ==========================================================================
   INTELLIGENT RECONCILIATION BILLING API CHANNELS
   ========================================================================== */

// 1. /api/billing/create-invoice -> Atomic Transaction Processing Loop
app.post('/api/billing/create-invoice', (req, res) => {
    const { invoice_id, due_date, salesperson, customer, items, payment } = req.body;

    if (!invoice_id || !items || !items.length) {
        return res.status(400).json({ success: false, message: "Malformed configuration arrays parameters received." });
    }

    // Step A: Perform comprehensive storage security crosscheck validations
    for (const line of items) {
        const storedAsset = inventoryStock[line.barcode];
        if (!storedAsset) {
            return res.status(404).json({ success: false, message: `Catalog key '${line.barcode}' missing from storage ledgers.` });
        }
        if (storedAsset.qty < line.qty) {
            return res.status(400).json({ success: false, message: `Storage Shortage: Count of asset '${storedAsset.name}' is insufficient to balance requests.` });
        }
    }

    // Step B: Commit mutations securely across product fields
    let invoiceSubtotalGross = 0;
    let totalDiscountDeductions = 0;

    for (const line of items) {
        const storedAsset = inventoryStock[line.barcode];
        storedAsset.qty -= line.qty; // Decrement stock volume automatically

        const lineGross = line.qty * line.price;
        const lineDiscount = lineGross * (line.discount / 100);
        
        invoiceSubtotalGross += lineGross;
        totalDiscountDeductions += lineDiscount;
    }

    const netTaxVatAmount = (invoiceSubtotalGross - totalDiscountDeductions) * 0.16;
    const finalGrandTotalCalculated = (invoiceSubtotalGross - totalDiscountDeductions) + netTaxVatAmount;

    // Step C: Compile formal system order tracking row model instance
    const cleanInvoiceRow = {
        invoice_id: sanitizeInput(invoice_id),
        date_created: new Date().toISOString().substring(0, 10),
        due_date: sanitizeInput(due_date),
        salesperson: sanitizeInput(salesperson),
        customer: {
            name: sanitizeInput(customer.name),
            phone: sanitizeInput(customer.phone)
        },
        items: items,
        financials: {
            subtotal: invoiceSubtotalGross,
            discount: totalDiscountDeductions,
            vat: netTaxVatAmount,
            grand_total: finalGrandTotalCalculated
        },
        payment: {
            method: sanitizeInput(payment.method),
            status: sanitizeInput(payment.status),
            amount_paid: parseFloat(payment.amount_paid) || 0
        }
    };

    billingInvoicesLedger.unshift(cleanInvoiceRow);

    // Step D: Cross-link automation interface streams to mpesa.html if channel checks match
    if (payment.method === "M-Pesa" || payment.amount_paid > 0) {
        const generatedMpesaToken = "JBS" + Math.random().toString(36).substring(2, 11).toUpperCase();
        mpesaTransactions.unshift({
            token: generatedMpesaToken,
            date: new Date().toISOString().replace('T', ' ').substring(0, 16),
            account: `Inv Ref: ${invoice_id} &bull; ${customer.name}`,
            phone: customer.phone,
            amount: payment.amount_paid,
            status: "API Reconciled"
        });
    }

    res.status(201).json({ success: true, invoice: cleanInvoiceRow });
});

// 2. /api/billing/summary -> Computes dynamic real-time reporting variables
app.get('/api/billing/summary', (req, res) => {
    let total_sales_value = 0;
    let outstanding_credit = 0;

    billingInvoicesLedger.forEach(inv => {
        total_sales_value += inv.payment.amount_paid;
        const remainingBalance = inv.financials.grand_total - inv.payment.amount_paid;
        if (remainingBalance > 0) {
            outstanding_credit += remainingBalance;
        }
    });

    res.json({
        total_sales_value,
        invoice_count: billingInvoicesLedger.length,
        outstanding_credit
    });
});

// 3. /api/billing/history -> Serving complete chronological order listings
app.get('/api/billing/history', (req, res) => {
    res.json(billingInvoicesLedger);
});

// Secondary catalog data bridge endpoints adapters
app.get('/api/inventory', (req, res) => res.json(Object.values(inventoryStock)));
app.get('/api/mpesa/ledger', (req, res) => res.json(mpesaTransactions));

/* ==========================================================================
   FRONTEND ROUTER INTERFACE ASSIGNMENTS
   ========================================================================== */
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));
app.get('/billing', (req, res) => res.sendFile(path.join(__dirname, 'billing.html')));
app.get('/inventory', (req, res) => res.sendFile(path.join(__dirname, 'inventory.html')));

app.use((req, res) => {
    res.status(404).send('<body style="background:#0f172a;color:#ef4444;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;"><h1>Error 404: Layout Segment Missing</h1></body>');
});

server.listen(PORT, () => {
    console.log(`================================================================`);
    console.log(` JBS CORE INVOICE ENG DESIGN ONLINE RUNNING ON PORT: ${PORT}`);
    console.log(`================================================================`);
});
const express = require('express');
const path = require('path');
const cors = require('cors');
const http = require('http');

const app = express();
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(__dirname));

/* ==========================================================================
   CENTRAL PLATFORM PERSISTENCE MEMORY LEDGER (Unified App State)
   ========================================================================== */
let inventoryStock = {
    "JBS-SKU-401": { product_id: "PRD-001", name: "Amoxicillin 500mg Matrix Pack", barcode: "JBS-SKU-401", serial_number: "SN-AMX-9941A", qty: 820, supplier: "Biomed Africa", category: "Medical / Pharmacy", unit_value: 120 },
    "JBS-SKU-902": { product_id: "PRD-002", name: "Portland Cement Type I 50KG Bags", barcode: "JBS-SKU-902", serial_number: "SN-CMT-1102X", qty: 15, supplier: "Bamburi Structural", category: "Hardware Supply", unit_value: 850 }
};

// Interconnected Ledger Database Matrix tables matches 
let billingInvoicesLedger = [];

const sanitizeInput = (str) => str ? String(str).trim().replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";

/* ==========================================================================
   AUTOMATED INTERLINKED DATA PROPAGATION API CHANNELS
   ========================================================================== */

// 1. Core transactional ledger insertion pipeline endpoint (Invoked by billing.html submissions)
app.post('/api/billing/create-invoice', (req, res) => {
    const { invoice_id, due_date, salesperson, customer, items, payment } = req.body;

    if (!invoice_id || !items || !items.length) {
        return res.status(400).json({ success: false, message: "Missing or malformed payload options." });
    }

    // Storage level protection crosscheck loops
    for (const line of items) {
        const storedAsset = inventoryStock[line.barcode];
        if (!storedAsset || storedAsset.qty < line.qty) {
            return res.status(400).json({ success: false, message: `Shortage validation lockout structural exception for: ${line.barcode}` });
        }
    }

    let subtotalGross = 0;
    let totalDiscounts = 0;

    // Mutate and adjust physical stock logs levels
    for (const line of items) {
        const storedAsset = inventoryStock[line.barcode];
        storedAsset.qty -= line.qty; 

        const lineGross = line.qty * line.price;
        const lineDiscount = lineGross * (line.discount / 100);
        subtotalGross += lineGross;
        totalDiscounts += lineDiscount;
    }

    const calculatedTaxVat = (subtotalGross - totalDiscounts) * 0.16;
    const computedGrandTotalValue = (subtotalGross - totalDiscounts) + calculatedTaxVat;

    const comprehensiveInvoiceRecord = {
        invoice_id: sanitizeInput(invoice_id),
        date_created: new Date().toISOString().substring(0, 10),
        due_date: sanitizeInput(due_date),
        salesperson: sanitizeInput(salesperson),
        customer: {
            name: sanitizeInput(customer.name),
            phone: sanitizeInput(customer.phone)
        },
        items: items,
        financials: {
            subtotal: subtotalGross,
            discount: totalDiscounts,
            vat: calculatedTaxVat,
            grand_total: computedGrandTotalValue
        },
        payment: {
            method: sanitizeInput(payment.method),
            status: sanitizeInput(payment.status),
            amount_paid: parseFloat(payment.amount_paid) || 0
        }
    };

    billingInvoicesLedger.unshift(comprehensiveInvoiceRecord);
    res.status(201).json({ success: true, invoice: comprehensiveInvoiceRecord });
});

// 2. Extended M-Pesa Matrix Extractor endpoint -> Deconstructs invoice objects parameters straight into structured row logs
app.get('/api/mpesa/transactions-extended', (req, res) => {
    const trackingMatrixRows = billingInvoicesLedger.map((inv, idx) => {
        // Generate verifiable predictable pseudo tracking codes safely deterministic across index allocations
        const shortHashSeed = (parseInt(inv.invoice_id.replace(/\D/g, '')) || 519) + idx;
        const pseudoMpesaCode = "MK" + (shortHashSeed * 7 + 10437).toString().substring(0, 8);
        
        const balanceRemainingDue = inv.financials.grand_total - inv.payment.amount_paid;

        return {
            mpesa_code: pseudoMpesaCode,
            invoice_number: inv.invoice_id,
            customer_name: inv.customer.name,
            phone_number: inv.customer.phone,
            amount_due: inv.financials.grand_total,
            amount_paid: inv.payment.amount_paid,
            balance: balanceRemainingDue >= 0 ? balanceRemainingDue : 0,
            payment_method: inv.payment.method,
            payment_status: inv.payment.status,
            transaction_date: inv.date_created + " 16:00" // Normalizes timing parameters bounds
        };
    });

    res.json(trackingMatrixRows);
});

// 3. Simple stats aggregator route logic
app.get('/api/billing/summary', (req, res) => {
    let total_sales_value = 0;
    let outstanding_credit = 0;

    billingInvoicesLedger.forEach(inv => {
        total_sales_value += inv.payment.amount_paid;
        const balance = inv.financials.grand_total - inv.payment.amount_paid;
        if(balance > 0) outstanding_credit += balance;
    });

    res.json({ total_sales_value, invoice_count: billingInvoicesLedger.length, outstanding_credit });
});

app.get('/api/inventory', (req, res) => res.json(Object.values(inventoryStock)));
app.get('/api/billing/history', (req, res) => res.json(billingInvoicesLedger));

/* ==========================================================================
   VIEW ENGINE TEMPLATE PATH MAPS
   ========================================================================== */
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));
app.get('/billing', (req, res) => res.sendFile(path.join(__dirname, 'billing.html')));
app.get('/mpesa', (req, res) => res.sendFile(path.join(__dirname, 'mpesa.html')));
app.get('/inventory', (req, res) => res.sendFile(path.join(__dirname, 'inventory.html')));

app.use((req, res) => {
    res.status(404).send('<body style="background:#0f172a;color:#ef4444;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;"><h1>Error 404: Layout Segment Missing</h1></body>');
});

server.listen(PORT, () => {
    console.log(`================================================================`);
    console.log(` JBS NETWORK AUTO-LINK ENGINE RUNNING ON PORT: ${PORT}`);
    console.log(`================================================================`);
});
const express = require('express');
const path = require('path');
const cors = require('cors');
const http = require('http');

const app = express();
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(__dirname));

/* ==========================================================================
   CENTRAL SYSTEM UNIFIED LIFECYCLE DATASTORE REGISTRIES
   ========================================================================== */
let inventoryStockTable = {
    "JBS-SKU-401": { product_id: "PRD-001", name: "Amoxicillin 500mg Matrix Pack", barcode: "JBS-SKU-401", serial_number: "SN-AMX-9941A", category: "Medical / Pharmacy", supplier: "Biomed Africa", qty: 24, cost_price: 90, selling_price: 120 },
    "JBS-SKU-902": { product_id: "PRD-002", name: "Portland Cement Type I 50KG Bags", barcode: "JBS-SKU-902", serial_number: "SN-CMT-1102X", category: "Hardware Supply", supplier: "Bamburi Structural", qty: 3, cost_price: 720, selling_price: 850 }
};

let billingInvoicesLedger = [];
let registeredSseResponseClientsList = []; // Array maintaining open event pipelines listeners

const sanitizeHtmlString = (str) => str ? String(str).trim().replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";

/* ==========================================================================
   SERVER-SENT EVENTS (SSE) LIGHTWEIGHT STREAM CHANNELS ENGINE
   ========================================================================== */
app.get('/api/inventory/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    // Enqueue client connection thread onto central active channel array list
    registeredSseResponseClientsList.push(res);

    req.on('close', () => {
        registeredSseResponseClientsList = registeredSseResponseClientsList.filter(client => client !== res);
    });
});

// Broadcaster pipeline helper mechanism wrapping downstream delivery vectors
function broadcastTelemetryEventAlert(type, message, voiceCue, operatorHandle) {
    const trackingPayloadBlock = {
        type: type,
        message: message,
        voice_cue: voiceCue,
        operator: operatorHandle || "System_Engine",
        timestamp: new Date().toLocaleTimeString()
    };

    const formattedSseString = `data: ${JSON.stringify({ type: "TELEMETRY_ALERT", payload: trackingPayloadBlock })}\n\n`;
    
    registeredSseResponseClientsList.forEach(clientConnection => {
        try { clientConnection.write(formattedSseString); } catch(e) {}
    });
}

/* ==========================================================================
   PRODUCTION WAREHOUSE OPERATIONS DATA CORE REST ENDPOINTS
   ========================================================================== */

app.get('/api/inventory/records-extended', (req, res) => {
    res.json(Object.values(inventoryStockTable));
});

// 1. Hardware Scanner Hookups Input Node (/api/inventory/scanner-update)
app.post('/api/inventory/scanner-update', (req, res) => {
    const { barcode, qty_scanned, operator } = req.body;
    const cleanBarcode = sanitizeHtmlString(barcode);
    const cleanOperator = sanitizeHtmlString(operator) || "Scanner_Hardware_Node";

    if(!cleanBarcode) return res.status(400).json({ success: false, message: "No barcode identified." });

    const matchedAsset = inventoryStockTable[cleanBarcode];
    if(matchedAsset) {
        const initialHoldingLevel = matchedAsset.qty;
        matchedAsset.qty += (parseInt(qty_scanned) || 1);
        
        broadcastTelemetryEventAlert(
            "STOCK_MUTATION_SCAN",
            `Inbound scanner increment for ${matchedAsset.name}. Holdings rose from ${initialHoldingLevel} to ${matchedAsset.qty}.`,
            "Inventory updated.",
            cleanOperator
        );
        return res.json({ success: true, message: "Asset stock successfully incremented via hardware scan.", asset: matchedAsset });
    } else {
        // Fallback: Scaffold unknown items into safe cache memory profiles 
        const freshScaffoldAsset = {
            product_id: "PRD-" + Math.floor(1000 + Math.random() * 9000),
            name: "Unregistered Scanned SKU Item Placeholder",
            barcode: cleanBarcode,
            serial_number: "SN-SCAN-" + Math.floor(10000 + Math.random() * 90000),
            category: "General Intake Sorting",
            supplier: "Awaiting Identification Logs",
            qty: parseInt(qty_scanned) || 1,
            cost_price: 0,
            selling_price: 0
        };
        inventoryStockTable[cleanBarcode] = freshScaffoldAsset;

        broadcastTelemetryEventAlert(
            "NEW_ASSET_DISCOVERED",
            `Unknown hardware barcode tag parsed: '${cleanBarcode}'. New baseline matrix trace appended.`,
            "New product successfully added.",
            cleanOperator
        );
        return res.status(201).json({ success: true, message: "Scaffolded entry successfully generated.", asset: freshScaffoldAsset });
    }
});

// 2. /api/inventory/add-product -> Core profile creator interface
app.post('/api/inventory/add-product', (req, res) => {
    const { barcode, name, serial_number, category, supplier, qty, cost_price, selling_price, operator } = req.body;
    const cleanBarcode = sanitizeHtmlString(barcode);

    if (inventoryStockTable[cleanBarcode]) {
        return res.status(400).json({ success: false, message: "Asset key entry already recorded in central datastores." });
    }

    const freshProductProfile = {
        product_id: "PRD-" + Math.floor(1000 + Math.random() * 9000),
        name: sanitizeHtmlString(name),
        barcode: cleanBarcode,
        serial_number: sanitizeHtmlString(serial_number),
        category: sanitizeHtmlString(category),
        supplier: sanitizeHtmlString(supplier),
        qty: parseInt(qty) || 0,
        cost_price: parseFloat(cost_price) || 0,
        selling_price: parseFloat(selling_price) || 0
    };

    inventoryStockTable[cleanBarcode] = freshProductProfile;

    broadcastTelemetryEventAlert(
        "MANUAL_INTAKE_CREATION",
        `New profile logged: ${freshProductProfile.name} added to warehouse inventories matrix.`,
        "New product successfully added.",
        sanitizeHtmlString(operator)
    );

    res.status(201).json({ success: true, asset: freshProductProfile });
});

// 3. /api/inventory/update-product -> Core layout modification loop interface 
app.post('/api/inventory/update-product', (req, res) => {
    const { barcode, name, serial_number, category, supplier, qty, cost_price, selling_price, operator } = req.body;
    const match = inventoryStockTable[sanitizeHtmlString(barcode)];

    if(!match) return res.status(404).json({ success: false, message: "Target asset layout mapping context not discovered." });

    match.name = sanitizeHtmlString(name);
    match.serial_number = sanitizeHtmlString(serial_number);
    match.category = sanitizeHtmlString(category);
    match.supplier = sanitizeHtmlString(supplier);
    match.qty = parseInt(qty) || 0;
    match.cost_price = parseFloat(cost_price) || 0;
    match.selling_price = parseFloat(selling_price) || 0;

    let verbalCueFeedbackMessage = "Inventory updated.";
    let notificationClassificationTag = "MANUAL_PROFILE_MUTATION";

    if(match.qty === 0) {
        verbalCueFeedbackMessage = "Product out of stock.";
        notificationClassificationTag = "CRITICAL_DEPLETED_WARNING";
    } else if(match.qty <= 15) {
        verbalCueFeedbackMessage = "Low stock detected.";
        notificationClassificationTag = "LOW_STOCK_THRESHOLD_ALERT";
    }

    broadcastTelemetryEventAlert(
        notificationClassificationTag,
        `Profile record parameters for ${match.name} edited. Internal levels tracked at: ${match.qty} units.`,
        verbalCueFeedbackMessage,
        sanitizeHtmlString(operator)
    );

    res.json({ success: true, asset: match });
});

// 4. /api/inventory/delete-product -> Drops an asset from memory mapping frames
app.post('/api/inventory/delete-product', (req, res) => {
    const { barcode, operator } = req.body;
    const match = inventoryStockTable[sanitizeHtmlString(barcode)];

    if(match) {
        const deletedProductNameStringLabel = match.name;
        delete inventoryStockTable[sanitizeHtmlString(barcode)];

        broadcastTelemetryEventAlert(
            "ASSET_RECORD_PURGED",
            `Product vector '${deletedProductNameStringLabel}' permanently removed from system registries database mappings.`,
            "Warning: Record dropped.",
            sanitizeHtmlString(operator)
        );
        return res.json({ success: true });
    }
    res.status(404).json({ success: false, message: "Target record matrix drop vector not found." });
});

/* ==========================================================================
   CROSS-MODULE TRANSACTION STREAMS INTERFACES LOGISTICS
   ========================================================================== */
app.post('/api/billing/create-invoice', (req, res) => {
    const { invoice_id, due_date, salesperson, customer, items, payment } = req.body;

    if (!invoice_id || !items || !items.length) {
        return res.status(400).json({ success: false, message: "Malformed invoice structures received." });
    }

    // Protection loops to secure inventory constraints
    for (const line of items) {
        const storedAsset = inventoryStockTable[line.barcode];
        if (!storedAsset || storedAsset.qty < line.qty) {
            return res.status(400).json({ success: false, message: `Shortage validation exception for: ${line.barcode}` });
        }
    }

    let subtotalGross = 0;
    let totalDiscounts = 0;

    // Deduct stock levels and broadcast system alerts automatically
    for (const line of items) {
        const storedAsset = inventoryStockTable[line.barcode];
        const previousQty = storedAsset.qty;
        storedAsset.qty -= line.qty; 

        subtotalGross += (line.qty * line.price);
        totalDiscounts += ((line.qty * line.price) * (line.discount / 100));

        let localizedVocalCueMessage = "Inventory updated.";
        let alertContextLevelTag = "TRANSACTION_DEDUCTION_MUTATION";

        if (storedAsset.qty === 0) {
            localizedVocalCueMessage = "Product out of stock.";
            alertContextLevelTag = "CRITICAL_DEPLETED_WARNING";
        } else if (storedAsset.qty <= 15) {
            localizedVocalCueMessage = "Low stock detected.";
            alertContextLevelTag = "LOW_STOCK_THRESHOLD_ALERT";
        }

        broadcastTelemetryEventAlert(
            alertContextLevelTag,
            `Invoice deduction transaction for ${storedAsset.name}. Qty dropped from ${previousQty} to ${storedAsset.qty}.`,
            localizedVocalCueMessage,
            sanitizeHtmlString(salesperson)
        );
    }

    const calculatedTaxVat = (subtotalGross - totalDiscounts) * 0.16;
    const computedGrandTotalValue = (subtotalGross - totalDiscounts) + calculatedTaxVat;

    const invoiceRecordBlock = {
        invoice_id: sanitizeHtmlString(invoice_id),
        date_created: new Date().toISOString().substring(0, 10),
        due_date: sanitizeHtmlString(due_date),
        salesperson: sanitizeHtmlString(salesperson),
        customer: { name: sanitizeHtmlString(customer.name), phone: sanitizeHtmlString(customer.phone) },
        items,
        financials: { subtotal: subtotalGross, discount: totalDiscounts, vat: calculatedTaxVat, grand_total: computedGrandTotalValue },
        payment: { method: sanitizeHtmlString(payment.method), status: sanitizeHtmlString(payment.status), amount_paid: parseFloat(payment.amount_paid) || 0 }
    };

    billingInvoicesLedger.unshift(invoiceRecordBlock);
    res.status(201).json({ success: true, invoice: invoiceRecordBlock });
});

// Additional structural extraction bridge configurations endpoint interfaces
app.get('/api/mpesa/transactions-extended', (req, res) => {
    const generatedMpesaMatrixRows = billingInvoicesLedger.map((inv, idx) => {
        const seedHash = (parseInt(inv.invoice_id.replace(/\D/g, '')) || 519) + idx;
        const generatedPseudoMpesaCode = "MK" + (seedHash * 7 + 10437).toString().substring(0, 8);
        const outstandingBalanceValue = inv.financials.grand_total - inv.payment.amount_paid;

        return {
            mpesa_code: generatedPseudoMpesaCode,
            invoice_number: inv.invoice_id,
            customer_name: inv.customer.name,
            phone_number: inv.customer.phone,
            amount_due: inv.financials.grand_total,
            amount_paid: inv.payment.amount_paid,
            balance: outstandingBalanceValue >= 0 ? outstandingBalanceValue : 0,
            payment_method: inv.payment.method,
            payment_status: inv.payment.status,
            transaction_date: inv.date_created + " 16:00"
        };
    });
    res.json(generatedMpesaMatrixRows);
});

app.get('/api/billing/summary', (req, res) => {
    let total_sales_value = 0;
    let outstanding_credit = 0;
    billingInvoicesLedger.forEach(inv => {
        total_sales_value += inv.payment.amount_paid;
        const balance = inv.financials.grand_total - inv.payment.amount_paid;
        if(balance > 0) outstanding_credit += balance;
    });
    res.json({ total_sales_value, invoice_count: billingInvoicesLedger.length, outstanding_credit });
});

app.get('/api/billing/history', (req, res) => res.json(billingInvoicesLedger));
app.get('/api/inventory', (req, res) => res.json(Object.values(inventoryStockTable)));

/* ==========================================================================
   VIEW ENGINE STATICS ROUTER MAPS ASSIGNMENTS
   ========================================================================== */
app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));
app.get('/billing', (req, res) => res.sendFile(path.join(__dirname, 'billing.html')));
app.get('/mpesa', (req, res) => res.sendFile(path.join(__dirname, 'mpesa.html')));
app.get('/inventory', (req, res) => res.sendFile(path.join(__dirname, 'inventory.html')));

app.use((req, res) => {
    res.status(404).send('<body style="background:#0f172a;color:#ef4444;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;"><h1>Error 404: Layout Segment Missing</h1></body>');
});

server.listen(PORT, () => {
    console.log(`================================================================`);
    console.log(` JBS REALTIME SYSTEM ENGINE ONLINE RUNNING ON PORT: ${PORT}`);
    console.log(`================================================================`);
});
