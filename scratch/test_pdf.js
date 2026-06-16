const { generateCertificatePDF } = require('../certificate_system/backend/pdfGenerator.js');
const path = require('path');

const data = {
  studentName: "sriram kumar",
  domainName: "Backend Developer",
  startDate: "2026-04-12",
  endDate: "2026-06-12",
  issueDate: "2026-06-12",
  certificateId: "EXPOSYS-CERT-7-E546FB35",
  qrCodePath: path.join(__dirname, '../certificate_system/backend/uploads/sample_qr.png') // assuming some file, or leave blank if it crashes without
};

generateCertificatePDF(data, path.join(__dirname, 'test_out.pdf'))
  .then(() => console.log('PDF Generated Successfully at test_out.pdf'))
  .catch(err => console.error(err));
