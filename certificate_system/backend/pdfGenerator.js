const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');

/**
 * Generates an internship certificate PDF based on the simple template.
 * @param {Object} data - Certificate metadata
 */
function generateCertificatePDF(data, outputPath) {
  return new Promise((resolve, reject) => {
    try {
      const doc = new PDFDocument({
        layout: 'landscape',
        size: 'A4',
        margins: { top: 0, bottom: 0, left: 0, right: 0 }
      });

      const writeStream = fs.createWriteStream(outputPath);
      doc.pipe(writeStream);

      // 1. Draw Background Template Image (Simple Border)
      const templatePath = path.join(__dirname, 'certificate_template.png');
      if (!fs.existsSync(templatePath)) {
        return reject(new Error('Certificate template image not found at ' + templatePath));
      }
      doc.image(templatePath, 0, 0, { width: 841.89, height: 595.28 });

      // Helper function to format date
      const formatDate = (dateStr) => {
        try {
          const date = new Date(dateStr);
          if (isNaN(date.getTime())) return dateStr;
          return date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'long',
            year: 'numeric'
          }); // e.g., 12 June 2026
        } catch (e) {
          return dateStr;
        }
      };

      const startFmt = formatDate(data.startDate);
      const endFmt = formatDate(data.endDate);
      const issueFmt = formatDate(data.issueDate);

      // 2. Dynamic Text Elements

      // Whiteout Box to cover the baked-in text on the template
      doc.rect(170, 100, 500, 420).fill('#ffffff');

      // 2. Dynamic Text Elements

      // Header
      doc.font('Helvetica-Bold')
         .fontSize(36)
         .fillColor('#555555')
         .text('INTERNSHIP CERTIFICATE', 0, 130, {
           align: 'center',
           width: 841.89,
           characterSpacing: 1
         });

      // Presentation
      doc.font('Helvetica')
         .fontSize(16)
         .fillColor('#333333')
         .text('We award this certificate to', 0, 190, {
           align: 'center',
           width: 841.89
         });

      // Helper function for Title Case
      const toTitleCase = str => str.replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());

      // Student Name
      doc.font('Times-Italic')
         .fontSize(52)
         .fillColor('#555555')
         .text(toTitleCase(data.studentName), 0, 240, {
           align: 'center',
           width: 841.89
         });

      // Description
      doc.font('Helvetica')
         .fontSize(15)
         .fillColor('#333333')
         .text('In recognition of their contribution to the company as', 0, 320, {
           align: 'center',
           width: 841.89
         });

      // Highlighted Domain
      doc.font('Helvetica-Bold')
         .fontSize(20)
         .fillColor('#555555')
         .text(data.domainName, 0, 355, {
           align: 'center',
           width: 841.89
         });

      // Duration label
      doc.font('Helvetica')
         .fontSize(15)
         .fillColor('#333333')
         .text('For the period of', 0, 395, {
           align: 'center',
           width: 841.89
         });

      // Duration Dates
      doc.font('Helvetica')
         .fontSize(15)
         .fillColor('#333333')
         .text(`${startFmt} to ${endFmt}`, 0, 425, {
           align: 'center',
           width: 841.89
         });

      // Footer Area
      const footY = 480;

      // Left Column (Issue Details)
      doc.font('Helvetica-Bold').fontSize(14).fillColor('#555555')
         .text(`DATE: ${issueFmt}`, 180, footY, { width: 200, align: 'center' });
      doc.font('Helvetica').fontSize(12).fillColor('#555555')
         .text(`ID: ${data.certificateId}`, 180, footY + 20, { width: 200, align: 'center' });

      // Right Column (Signature)
      doc.font('Helvetica-Bold').fontSize(14).fillColor('#555555')
         .text('Y. Raghavendra', 460, footY, { width: 200, align: 'center' });
      doc.font('Helvetica').fontSize(12).fillColor('#555555')
         .text('Authorized Signatory', 460, footY + 20, { width: 200, align: 'center' });

      // QR Code in bottom center (replacing the badge)
      if (data.qrCodePath && fs.existsSync(data.qrCodePath)) {
        doc.image(data.qrCodePath, 385, 460, { width: 75, height: 75 });
      }

      doc.end();

      writeStream.on('finish', () => {
        resolve(outputPath);
      });

      writeStream.on('error', (err) => {
        reject(err);
      });
    } catch (error) {
      reject(error);
    }
  });
}

module.exports = { generateCertificatePDF };
