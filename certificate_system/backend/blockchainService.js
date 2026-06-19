const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../.env') }); // Load environment variables from project root

// Load contract ABI (compiled by Hardhat)
let contractAbi = null;
try {
  const artifactPath = path.join(__dirname, '../blockchain/artifacts/contracts/CertificateRegistry.sol/CertificateRegistry.json');
  if (fs.existsSync(artifactPath)) {
    const artifact = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));
    contractAbi = artifact.abi;
  }
} catch (e) {
  console.warn("Could not load smart contract ABI artifact. Make sure to compile in blockchain folder. Will default to mock fallback.");
}

const mockDbPath = path.join(__dirname, 'blockchain_mock_state.json');

// Simulated Blockchain Store for Fallback Mode
function saveMockCertificate(certData) {
  let mockDb = {};
  if (fs.existsSync(mockDbPath)) {
    try {
      mockDb = JSON.parse(fs.readFileSync(mockDbPath, 'utf8'));
    } catch (e) {
      mockDb = {};
    }
  }
  mockDb[certData.certificateId] = certData;
  fs.writeFileSync(mockDbPath, JSON.stringify(mockDb, null, 2), 'utf8');
}

function getMockCertificate(certificateId) {
  if (fs.existsSync(mockDbPath)) {
    try {
      const mockDb = JSON.parse(fs.readFileSync(mockDbPath, 'utf8'));
      return mockDb[certificateId] || null;
    } catch (e) {
      return null;
    }
  }
  return null;
}

class BlockchainService {
  constructor() {
    this.provider = null;
    this.signer = null;
    this.contract = null;
    this.isMock = true;

    this.rpcUrl = process.env.POLYGON_RPC_URL; // e.g. https://rpc-amoy.polygon.technology
    this.privateKey = process.env.PRIVATE_KEY; // Admin's deployer key
    this.contractAddress = process.env.CONTRACT_ADDRESS;

    this.initialize();
  }

  async initialize() {
    try {
      if (!this.rpcUrl || !this.privateKey || !this.contractAddress || !contractAbi) {
        console.log("🔗 [Blockchain] Missing RPC URL, Private Key, Contract Address, or ABI. Using Mock Simulator Mode.");
        this.isMock = true;
        return;
      }

      this.provider = new ethers.JsonRpcProvider(this.rpcUrl);
      this.signer = new ethers.Wallet(this.privateKey, this.provider);
      this.contract = new ethers.Contract(this.contractAddress, contractAbi, this.signer);
      
      // Test connection
      await this.provider.getNetwork();
      console.log(`🔗 [Blockchain] Connected to Polygon RPC at ${this.rpcUrl}. Contract address: ${this.contractAddress}`);
      this.isMock = false;
    } catch (err) {
      console.warn("⚠️ [Blockchain] Failed to connect to network. Falling back to Mock Simulator Mode.", err.message);
      this.isMock = true;
    }
  }

  /**
   * Registers a certificate hash on Polygon.
   */
  async registerCertificate(cert) {
    if (this.isMock) {
      const txHash = '0x' + Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
      const mockCert = {
        certificateId: cert.certificateId,
        studentName: cert.studentName,
        domainName: cert.domainName,
        issueDate: cert.issueDate,
        certificateHash: cert.certificateHash,
        verificationUrl: cert.verificationUrl,
        txHash: txHash,
        isRevoked: false,
        registeredAt: new Date().toISOString()
      };
      saveMockCertificate(mockCert);
      console.log(`🔒 [Blockchain Simulator] Certificate ${cert.certificateId} registered. Tx Hash: ${txHash}`);
      return {
        success: true,
        txHash: txHash,
        isMock: true
      };
    }

    try {
      // Send transaction to smart contract
      const tx = await this.contract.registerCertificate(
        cert.certificateId,
        cert.studentName,
        cert.domainName,
        cert.issueDate,
        cert.certificateHash,
        cert.verificationUrl
      );
      
      console.log(`⏳ [Blockchain] Registering certificate ${cert.certificateId}. Tx Hash sent: ${tx.hash}`);
      const receipt = await tx.wait();
      console.log(`✅ [Blockchain] Registration confirmed in block ${receipt.blockNumber}.`);
      return {
        success: true,
        txHash: tx.hash,
        isMock: false
      };
    } catch (err) {
      console.error(`❌ [Blockchain Error] Failed to register certificate ${cert.certificateId}:`, err);
      throw err;
    }
  }

  /**
   * Revokes a certificate on Polygon.
   */
  async revokeCertificate(certificateId) {
    if (this.isMock) {
      const mockCert = getMockCertificate(certificateId);
      if (mockCert) {
        mockCert.isRevoked = true;
        saveMockCertificate(mockCert);
        console.log(`🚫 [Blockchain Simulator] Certificate ${certificateId} revoked.`);
        return { success: true, isMock: true };
      }
      return { success: false, error: "Not found", isMock: true };
    }

    try {
      const tx = await this.contract.revokeCertificate(certificateId);
      console.log(`⏳ [Blockchain] Revoking certificate ${certificateId}. Tx Hash sent: ${tx.hash}`);
      await tx.wait();
      console.log(`✅ [Blockchain] Revocation confirmed.`);
      return { success: true, txHash: tx.hash, isMock: false };
    } catch (err) {
      console.error(`❌ [Blockchain Error] Failed to revoke certificate ${certificateId}:`, err);
      throw err;
    }
  }

  /**
   * Verifies a certificate directly from Polygon or local simulator.
   */
  async verifyCertificate(certificateId) {
    if (this.isMock) {
      const mockCert = getMockCertificate(certificateId);
      if (mockCert) {
        return {
          exists: true,
          isRevoked: mockCert.isRevoked,
          certificateId: mockCert.certificateId,
          studentName: mockCert.studentName,
          domainName: mockCert.domainName,
          issueDate: mockCert.issueDate,
          certificateHash: mockCert.certificateHash,
          verificationUrl: mockCert.verificationUrl,
          txHash: mockCert.txHash,
          isMock: true
        };
      }
      return { exists: false, isMock: true };
    }

    try {
      const certData = await this.contract.getCertificate(certificateId);
      // Returns list match: certificateId, studentName, domainName, issueDate, certificateHash, verificationUrl, isRevoked, exists
      if (!certData.exists) {
        return { exists: false, isMock: false };
      }

      return {
        exists: true,
        certificateId: certData.certificateId,
        studentName: certData.studentName,
        domainName: certData.domainName,
        issueDate: certData.issueDate,
        certificateHash: certData.certificateHash,
        verificationUrl: certData.verificationUrl,
        isRevoked: certData.isRevoked,
        txHash: this.contractAddress, // we reference contract as proof or standard tx log
        isMock: false
      };
    } catch (err) {
      console.warn("⚠️ [Blockchain Verification Error] Could not query smart contract. Checking simulator fallback...", err.message);
      // Fallback check simulator in case it was created in simulator
      const mockCert = getMockCertificate(certificateId);
      if (mockCert) {
        return { ...mockCert, exists: true, isMock: true };
      }
      throw err;
    }
  }
}

module.exports = new BlockchainService();
