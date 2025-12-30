/**
 * PDF Generator for DocStyler
 * Generates styled PDF using pdf-lib
 */

import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import { COLORS, FONTS, SPACING, COMPANY, FOOTER, SERVICES, formatDateTime } from '../styles/documentStyles';
import { markdownToPlainText, parseMarkdownSections } from '../utils/markdownConverter';

/**
 * Convert hex color to RGB values (0-1 range)
 * @param {string} hex - Hex color code
 * @returns {Object} RGB values
 */
const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16) / 255,
    g: parseInt(result[2], 16) / 255,
    b: parseInt(result[3], 16) / 255,
  } : { r: 0, g: 0, b: 0 };
};

/**
 * Sanitize text for PDF (remove unsupported characters)
 * pdf-lib StandardFonts only support WinAnsi encoding (basic Latin)
 * @param {string} text - Text to sanitize
 * @returns {string} Sanitized text
 */
const sanitizeForPdf = (text) => {
  if (!text) return '';
  return text
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2013/g, '-')
    .replace(/\u2014/g, '--')
    .replace(/\u2026/g, '...')
    .replace(/[\u00A0]/g, ' ')
    .replace(/[^\x00-\x7F]/g, (char) => {
      const replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ñ': 'n', 'ç': 'c', '•': '-', '–': '-', '—': '-',
      };
      return replacements[char] || '';
    });
};

/**
 * Generate and download PDF document
 * @param {string} content - Main content (markdown)
 * @param {Object} options - Document options
 */
export const generatePDF = async (content, options = {}) => {
  const {
    title = 'Document',
    service = '',
    fileName = 'document',
    metadata = {},
  } = options;
  
  try {
    // Create PDF document
    const pdfDoc = await PDFDocument.create();
    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
    const fontBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
    
    // Page setup
    const pageWidth = 612;  // Letter size
    const pageHeight = 792;
    const margin = SPACING.margin.left;
    const contentWidth = pageWidth - (margin * 2);
    
    // Colors
    const primaryColor = hexToRgb(COLORS.primary);
    const textColor = hexToRgb(COLORS.text);
    const lightColor = hexToRgb(COLORS.textLight);
    
    // Create first page
    let page = pdfDoc.addPage([pageWidth, pageHeight]);
    let yPosition = pageHeight - margin;
    
    // === HEADER ===
    const serviceName = SERVICES[service] || service || 'GetHiredAlly';
    
    // Title (sanitized)
    page.drawText(sanitizeForPdf(title), {
      x: margin,
      y: yPosition,
      size: FONTS.sizes.h1,
      font: fontBold,
      color: rgb(primaryColor.r, primaryColor.g, primaryColor.b),
    });
    yPosition -= 30;
    
    // Service and date
    page.drawText(`Service: ${serviceName}`, {
      x: margin,
      y: yPosition,
      size: FONTS.sizes.small,
      font: font,
      color: rgb(lightColor.r, lightColor.g, lightColor.b),
    });
    yPosition -= 15;
    
    page.drawText(`Generated: ${formatDateTime()}`, {
      x: margin,
      y: yPosition,
      size: FONTS.sizes.small,
      font: font,
      color: rgb(lightColor.r, lightColor.g, lightColor.b),
    });
    yPosition -= 15;
    
    // Score (if available)
    if (metadata?.score !== undefined) {
      page.drawText(`Score: ${metadata.score}/100 (${metadata.grade || 'N/A'})`, {
        x: margin,
        y: yPosition,
        size: FONTS.sizes.small,
        font: fontBold,
        color: rgb(primaryColor.r, primaryColor.g, primaryColor.b),
      });
      yPosition -= 15;
    }
    
    // Divider line
    yPosition -= 10;
    page.drawLine({
      start: { x: margin, y: yPosition },
      end: { x: pageWidth - margin, y: yPosition },
      thickness: 1,
      color: rgb(lightColor.r, lightColor.g, lightColor.b),
    });
    yPosition -= 30;
    
    // === CONTENT ===
    const plainText = sanitizeForPdf(markdownToPlainText(content));
    const lines = plainText.split('\n');
    
    for (const line of lines) {
      // Check if need new page
      if (yPosition < margin + 50) {
        page = pdfDoc.addPage([pageWidth, pageHeight]);
        yPosition = pageHeight - margin;
      }
      
      // Skip empty lines but add spacing
      if (!line.trim()) {
        yPosition -= 10;
        continue;
      }
      
      // Check for bullet points
      const isBullet = line.startsWith('• ');
      const lineText = isBullet ? line : line;
      
      // Word wrap
      const words = lineText.split(' ');
      let currentLine = '';
      
      for (const word of words) {
        const testLine = currentLine ? `${currentLine} ${word}` : word;
        const textWidth = font.widthOfTextAtSize(testLine, FONTS.sizes.body);
        
        if (textWidth > contentWidth) {
          // Draw current line
          page.drawText(currentLine, {
            x: margin,
            y: yPosition,
            size: FONTS.sizes.body,
            font: font,
            color: rgb(textColor.r, textColor.g, textColor.b),
          });
          yPosition -= 16;
          currentLine = word;
          
          // Check for new page
          if (yPosition < margin + 50) {
            page = pdfDoc.addPage([pageWidth, pageHeight]);
            yPosition = pageHeight - margin;
          }
        } else {
          currentLine = testLine;
        }
      }
      
      // Draw remaining text
      if (currentLine) {
        page.drawText(currentLine, {
          x: margin,
          y: yPosition,
          size: FONTS.sizes.body,
          font: font,
          color: rgb(textColor.r, textColor.g, textColor.b),
        });
        yPosition -= 16;
      }
    }
    
    // === FOOTER (on all pages) ===
    const pages = pdfDoc.getPages();
    const totalPages = pages.length;
    
    pages.forEach((p, index) => {
      const pageNum = index + 1;
      const footerY = 30;
      
      // Page number
      const pageText = `Page ${pageNum} of ${totalPages}`;
      p.drawText(pageText, {
        x: margin,
        y: footerY,
        size: FONTS.sizes.footer,
        font: font,
        color: rgb(lightColor.r, lightColor.g, lightColor.b),
      });
      
      // Links
      const linksText = FOOTER.links.map(l => l.text).join(FOOTER.separator);
      const linksWidth = font.widthOfTextAtSize(linksText, FONTS.sizes.footer);
      p.drawText(linksText, {
        x: pageWidth - margin - linksWidth,
        y: footerY,
        size: FONTS.sizes.footer,
        font: font,
        color: rgb(primaryColor.r, primaryColor.g, primaryColor.b),
      });
    });
    
    // === DOWNLOAD ===
    const pdfBytes = await pdfDoc.save();
    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${fileName}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('PDF generation error:', error);
    throw error;
  }
};

export default { generatePDF };
