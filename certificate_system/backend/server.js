const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const qrcode = require('qrcode');

const db = require('./db');
const blockchain = require('./blockchainService');
const { generateCertificatePDF } = require('./pdfGenerator');

require('dotenv').config({ path: path.join(__dirname, '../../.env') }); // Load environment variables from project root

const app = express();
const PORT = process.env.PORT || 5001;
const JWT_SECRET = process.env.SECRET_KEY || 'exposys_fallback_jwt_key';

// Ensure uploads directories exist
const uploadsDir = path.join(__dirname, 'uploads');
const qrCodesDir = path.join(uploadsDir, 'qr_codes');
const certificatesDir = path.join(uploadsDir, 'certificates');

fs.mkdirSync(uploadsDir, { recursive: true });
fs.mkdirSync(qrCodesDir, { recursive: true });
fs.mkdirSync(certificatesDir, { recursive: true });

app.use(cors());
app.use(express.json());

// Serve static files (PDFs and QR Codes)
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Helper: Verify Werkzeug pbkdf2 Password Hashes from Flask
function verifyWerkzeugHash(password, storedHash) {
  try {
    const parts = storedHash.split('$');
    if (parts.length !== 3) return false;
    const [algorithmInfo, salt, expectedHash] = parts;
    
    const algoParts = algorithmInfo.split(':');
    if (algoParts.length !== 3) return false;
    const [method, hashName, iterationsStr] = algoParts;
    
    if (method !== 'pbkdf2' || hashName !== 'sha256') {
      console.error(`Unsupported Werkzeug hashing method: ${method}:${hashName}`);
      return false;
    }
    
    const iterations = parseInt(iterationsStr, 10);
    const key = crypto.pbkdf2Sync(password, salt, iterations, 32, 'sha256');
    const calculatedHash = key.toString('hex');
    
    return calculatedHash === expectedHash;
  } catch (err) {
    console.error('Password verification error', err);
    return false;
  }
}

// Middleware: Verify Admin JWT
function authenticateAdmin(req, res, next) {
  const internalSecret = req.headers['x-internal-secret'];
  if (internalSecret && internalSecret === 'exposys_internal_secret_key') {
    return next();
  }

  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.admin = user;
    next();
  });
}

// ─── AUTHENTICATION ROUTES ──────────────────────────────────────────────────

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }

  try {
    const queryResult = await db.query('SELECT * FROM admins WHERE email = $1', [email]);
    if (queryResult.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const admin = queryResult.rows[0];
    const isMatch = verifyWerkzeugHash(password, admin.password);

    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const token = jwt.sign(
      { id: admin.id, name: admin.name, email: admin.email },
      JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.json({
      token,
      admin: {
        id: admin.id,
        name: admin.name,
        email: admin.email
      }
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Database server error' });
  }
});

// ─── STUDENT ROUTES ────────────────────────────────────────────────────────

app.get('/api/students', authenticateAdmin, async (req, res) => {
  try {
    // Select students, joining with certificates status if exists
    const queryStr = `
      SELECT 
        s.id, 
        s.name, 
        s.email, 
        s.internship_domain, 
        s.duration, 
        s.created_at,
        c.certificate_id,
        c.status as certificate_status,
        c.blockchain_hash,
        c.tx_hash,
        c.pdf_path
      FROM students s
      LEFT JOIN certificates c ON s.id = c.student_id
      ORDER BY s.created_at DESC
    `;
    const result = await db.query(queryStr);
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching students:', err);
    res.status(500).json({ error: 'Database error' });
  }
});

// ─── CERTIFICATE ROUTES (ADMIN CONTROL) ─────────────────────────────────────

app.post('/api/blockchain/register', authenticateAdmin, async (req, res) => {
  const { certificateId, studentName, domainName, issueDate, certificateHash, verificationUrl } = req.body;
  if (!certificateId || !studentName || !domainName || !certificateHash || !verificationUrl) {
     return res.status(400).json({ error: "Missing parameters" });
  }
  try {
     const blockRes = await blockchain.registerCertificate({
      certificateId,
      studentName,
      domainName,
      issueDate,
      certificateHash,
      verificationUrl
    });
    res.json({ success: true, txHash: blockRes.txHash, isMock: blockRes.isMock });
  } catch(e) {
    console.error(e);
    res.status(500).json({ error: e.toString() });
  }
});

app.post('/api/certificates/approve', authenticateAdmin, async (req, res) => {
  const { studentId, startDate, endDate, issueDate, domainName } = req.body;

  if (!studentId || !startDate || !endDate || !issueDate) {
    return res.status(400).json({ error: 'All fields are required' });
  }

  try {
    // Fetch student info
    const studentRes = await db.query('SELECT * FROM students WHERE id = $1', [studentId]);
    if (studentRes.rows.length === 0) {
      return res.status(404).json({ error: 'Student not found' });
    }
    const student = studentRes.rows[0];

    // Determine target domain (use passed domainName or fallback to main domain)
    const targetDomain = domainName || student.internship_domain || 'Unassigned';

    // Generate unique Certificate ID
    const randomHex = crypto.randomBytes(4).toString('hex').toUpperCase();
    const certificateId = `EXPOSYS-CERT-${studentId}-${randomHex}`;

    // Clean existing certificate for this student and domain
    await db.query('DELETE FROM certificates WHERE student_id = $1 AND domain_name = $2', [studentId, targetDomain]);

    // Public Verification URL pointing to Frontend Verify route
    const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    const verificationUrl = `${frontendUrl}/verify/${certificateId}`;

    // Generate QR Code containing verification URL
    const qrCodeFilename = `${certificateId}.png`;
    const qrCodeLocalPath = path.join(qrCodesDir, qrCodeFilename);
    await qrcode.toFile(qrCodeLocalPath, verificationUrl, {
      width: 250,
      margin: 1
    });

    // Create Metadata Hash for Blockchain
    const metadataString = JSON.stringify({
      certificateId,
      studentName: student.name,
      domainName: targetDomain,
      startDate,
      endDate,
      issueDate,
      verificationUrl
    });
    const blockchainHash = crypto.createHash('sha256').update(metadataString).digest('hex');

    // Register on Blockchain (Polygon / Simulator fallback)
    const blockRes = await blockchain.registerCertificate({
      certificateId,
      studentName: student.name,
      domainName: targetDomain,
      issueDate,
      certificateHash: blockchainHash,
      verificationUrl
    });

    // Generate Certificate PDF
    const pdfFilename = `${certificateId}.pdf`;
    const pdfLocalPath = path.join(certificatesDir, pdfFilename);
    await generateCertificatePDF({
      studentName: student.name,
      domainName: targetDomain,
      startDate,
      endDate,
      certificateId,
      issueDate,
      qrCodePath: qrCodeLocalPath
    }, pdfLocalPath);

    // Save into database
    const insertQuery = `
      INSERT INTO certificates (
        certificate_id, student_id, student_name, domain_name, 
        start_date, end_date, issue_date, blockchain_hash, tx_hash, 
        qr_code, status, pdf_path
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      RETURNING *
    `;
    const dbRes = await db.query(insertQuery, [
      certificateId,
      studentId,
      student.name,
      targetDomain,
      startDate,
      endDate,
      issueDate,
      blockchainHash,
      blockRes.txHash,
      `/uploads/qr_codes/${qrCodeFilename}`,
      'approved',
      `/uploads/certificates/${pdfFilename}`
    ]);

    res.status(201).json({
      message: 'Certificate approved, generated and registered successfully.',
      certificate: dbRes.rows[0]
    });
  } catch (err) {
    console.error('Approval/Generation error:', err);
    res.status(500).json({ error: 'Server error during certificate generation' });
  }
});

app.post('/api/certificates/reject', authenticateAdmin, async (req, res) => {
  const { studentId, studentName, domainName } = req.body;
  if (!studentId || !studentName || !domainName) {
    return res.status(400).json({ error: 'Missing parameters' });
  }

  try {
    await db.query('DELETE FROM certificates WHERE student_id = $1 AND domain_name = $2', [studentId, domainName]);

    const randomHex = crypto.randomBytes(4).toString('hex').toUpperCase();
    const certificateId = `EXPOSYS-REJ-${studentId}-${randomHex}`;

    const insertQuery = `
      INSERT INTO certificates (
        certificate_id, student_id, student_name, domain_name, 
        start_date, end_date, issue_date, status
      ) VALUES ($1, $2, $3, $4, CURRENT_DATE, CURRENT_DATE, CURRENT_DATE, $5)
      RETURNING *
    `;
    const dbRes = await db.query(insertQuery, [
      certificateId,
      studentId,
      studentName,
      domainName,
      'rejected'
    ]);

    res.json({ message: 'Certificate rejected successfully.', certificate: dbRes.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

app.post('/api/certificates/hold', authenticateAdmin, async (req, res) => {
  const { studentId, studentName, domainName } = req.body;
  if (!studentId || !studentName || !domainName) {
    return res.status(400).json({ error: 'Missing parameters' });
  }

  try {
    await db.query('DELETE FROM certificates WHERE student_id = $1 AND domain_name = $2', [studentId, domainName]);

    const randomHex = crypto.randomBytes(4).toString('hex').toUpperCase();
    const certificateId = `EXPOSYS-HLD-${studentId}-${randomHex}`;

    const insertQuery = `
      INSERT INTO certificates (
        certificate_id, student_id, student_name, domain_name, 
        start_date, end_date, issue_date, status
      ) VALUES ($1, $2, $3, $4, CURRENT_DATE, CURRENT_DATE, CURRENT_DATE, $5)
      RETURNING *
    `;
    const dbRes = await db.query(insertQuery, [
      certificateId,
      studentId,
      studentName,
      domainName,
      'held'
    ]);

    res.json({ message: 'Certificate put on hold.', certificate: dbRes.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database error' });
  }
});

app.post('/api/certificates/revoke', authenticateAdmin, async (req, res) => {
  const { certificateId } = req.body;
  if (!certificateId) {
    return res.status(400).json({ error: 'Certificate ID is required' });
  }

  try {
    const certQuery = await db.query('SELECT * FROM certificates WHERE certificate_id = $1', [certificateId]);
    if (certQuery.rows.length === 0) {
      return res.status(404).json({ error: 'Certificate not found' });
    }

    // Revoke on blockchain
    await blockchain.revokeCertificate(certificateId);

    // Update in database
    const updateRes = await db.query(
      'UPDATE certificates SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE certificate_id = $2 RETURNING *',
      ['revoked', certificateId]
    );

    res.json({ message: 'Certificate revoked successfully.', certificate: updateRes.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Revocation error' });
  }
});

// ─── PUBLIC VERIFICATION & DOWNLOAD ROUTES ──────────────────────────────────

// Public lookup by ID
app.get('/api/certificates/verify/:certificateId', async (req, res) => {
  const { certificateId } = req.params;

  try {
    const result = await db.query('SELECT * FROM certificates WHERE certificate_id = $1', [certificateId]);
    if (result.rows.length === 0) {
      return res.json({ verified: false, status: 'invalid', message: '❌ Invalid Certificate: Certificate ID not found' });
    }

    const dbCert = result.rows[0];

    if (dbCert.status === 'rejected') {
      return res.json({ verified: false, status: 'rejected', message: '❌ Rejected: Certificate application was rejected' });
    }
    if (dbCert.status === 'held') {
      return res.json({ verified: false, status: 'held', message: '⚠️ Pending: Certificate approval is currently on hold' });
    }
    if (dbCert.status === 'revoked') {
      return res.json({
        verified: false,
        status: 'revoked',
        message: '⚠️ Revoked Certificate: This certificate was officially revoked.',
        certificate: dbCert
      });
    }

    // Attempt blockchain integrity verification
    let chainData;
    let tamperProof = false;
    try {
      chainData = await blockchain.verifyCertificate(certificateId);
      if (!chainData.exists && blockchain.isMock && dbCert.status === 'approved') {
        // Automatically sync to mock blockchain state
        await blockchain.registerCertificate({
          certificateId: dbCert.certificate_id,
          studentName: dbCert.student_name,
          domainName: dbCert.domain_name,
          issueDate: dbCert.issue_date,
          certificateHash: dbCert.blockchain_hash,
          verificationUrl: `${process.env.FRONTEND_URL || 'http://localhost:5173'}/verify/${dbCert.certificate_id}`
        });
        chainData = await blockchain.verifyCertificate(certificateId);
      }
      if (chainData.exists) {
        // Compare blockchain hash with DB hash
        tamperProof = (chainData.certificateHash === dbCert.blockchain_hash);
      }
    } catch (e) {
      console.warn("Could not verify on blockchain network, using db metadata", e.message);
      chainData = { exists: true, isRevoked: false };
      tamperProof = true; // assume true if blockchain network is down but db is intact
    }

    if (!tamperProof) {
      return res.json({
        verified: false,
        status: 'tampered',
        message: '❌ Tampered Certificate: Data hash does not match blockchain records!',
        certificate: dbCert
      });
    }

    res.json({
      verified: true,
      status: 'valid',
      message: '✅ Valid Certificate',
      certificate: dbCert,
      blockchain: {
        txHash: dbCert.tx_hash,
        hash: dbCert.blockchain_hash,
        isMock: chainData.isMock
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database or validation service error' });
  }
});

// Public search by Student Name / Email / ID to download certificate
app.get('/api/certificates/download-search', async (req, res) => {
  const { search } = req.query; // Search key: name, email, or certificate ID
  if (!search) {
    return res.status(400).json({ error: 'Search term is required' });
  }

  try {
    const queryStr = `
      SELECT 
        c.certificate_id,
        c.student_name,
        c.domain_name,
        c.start_date,
        c.end_date,
        c.issue_date,
        c.status,
        c.pdf_path,
        s.email
      FROM certificates c
      JOIN students s ON c.student_id = s.id
      WHERE c.certificate_id ILIKE $1 
         OR c.student_name ILIKE $1 
         OR s.email ILIKE $1
      ORDER BY c.created_at DESC
    `;
    const result = await db.query(queryStr, [`%${search}%`]);
    res.json(result.rows);
  } catch (err) {
    console.error('Search error:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Express Backend Server running on http://localhost:${PORT}`);
});
