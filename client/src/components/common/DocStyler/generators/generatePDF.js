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
    // Use parseMarkdownSections for structured content with heading detection
    const sections = parseMarkdownSections(content);
    
    // Helper function to draw text with word wrap
    const drawWrappedText = (text, textFont, textSize, textColor, indent = 0) => {
      const sanitizedText = sanitizeForPdf(text);
      const lines = sanitizedText.split('\n');
      
      for (const line of lines) {
        if (!line.trim()) {
          yPosition -= 8;
          continue;
        }
        
        const words = line.split(' ');
        let currentLine = '';
        const effectiveWidth = contentWidth - indent;
        
        for (const word of words) {
          const testLine = currentLine ? `${currentLine} ${word}` : word;
          const textWidth = textFont.widthOfTextAtSize(testLine, textSize);
          
          if (textWidth > effectiveWidth) {
            if (yPosition < margin + 60) {
              page = pdfDoc.addPage([pageWidth, pageHeight]);
              yPosition = pageHeight - margin;
            }
            page.drawText(currentLine, {
              x: margin + indent,
              y: yPosition,
              size: textSize,
              font: textFont,
              color: textColor,
            });
            yPosition -= textSize + 4;
            currentLine = word;
          } else {
            currentLine = testLine;
          }
        }
        
        if (currentLine) {
          if (yPosition < margin + 60) {
            page = pdfDoc.addPage([pageWidth, pageHeight]);
            yPosition = pageHeight - margin;
          }
          page.drawText(currentLine, {
            x: margin + indent,
            y: yPosition,
            size: textSize,
            font: textFont,
            color: textColor,
          });
          yPosition -= textSize + 4;
        }
      }
    };
    
    // Process each section with appropriate styling
    for (const section of sections) {
      // Check if need new page before heading
      if (yPosition < margin + 80) {
        page = pdfDoc.addPage([pageWidth, pageHeight]);
        yPosition = pageHeight - margin;
      }
      
      // Draw section heading if present
      if (section.title) {
        let headingSize, headingFont;
        
        switch (section.type) {
          case 'h1':
            headingSize = FONTS.sizes.h2; // 20pt for main sections
            headingFont = fontBold;
            yPosition -= 12; // Extra spacing before h1
            break;
          case 'h2':
            headingSize = FONTS.sizes.h3; // 16pt for subsections
            headingFont = fontBold;
            yPosition -= 8;
            break;
          case 'h3':
            headingSize = 14;
            headingFont = fontBold;
            yPosition -= 6;
            break;
          default:
            headingSize = FONTS.sizes.body;
            headingFont = font;
        }
        
        // Draw heading in primary color
        page.drawText(sanitizeForPdf(section.title), {
          x: margin,
          y: yPosition,
          size: headingSize,
          font: headingFont,
          color: rgb(primaryColor.r, primaryColor.g, primaryColor.b),
        });
        yPosition -= headingSize + 8;
      }
      
      // Draw section content
      if (section.content) {
        drawWrappedText(
          section.content,
          font,
          FONTS.sizes.body,
          rgb(textColor.r, textColor.g, textColor.b)
        );
        yPosition -= 8; // Spacing after section
      }
    }
    
    // Fallback: if no sections parsed, use plain text
    if (sections.length === 0) {
      const plainText = sanitizeForPdf(markdownToPlainText(content));
      drawWrappedText(plainText, font, FONTS.sizes.body, rgb(textColor.r, textColor.g, textColor.b));
    }
    
    // === FOOTER (on all pages) ===
    const pages = pdfDoc.getPages();
    const totalPages = pages.length;
    console.log('PDF: Adding footers to', totalPages, 'pages');
    
    pages.forEach((p, index) => {
      const pageNum = index + 1;
      const footerY = 50;
      
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
