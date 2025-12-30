/**
 * Word Generator for DocStyler
 * Generates styled DOCX using docx library
 */

import { 
  Document, 
  Paragraph, 
  TextRun, 
  HeadingLevel, 
  AlignmentType,
  PageNumber,
  Footer,
  ExternalHyperlink,
  Packer
} from 'docx';
import { saveAs } from 'file-saver';
import { COLORS, COMPANY, FOOTER, SERVICES, formatDateTime } from '../styles/documentStyles';
import { markdownToPlainText, parseMarkdownSections } from '../utils/markdownConverter';

/**
 * Generate and download Word document
 * @param {string} content - Main content (markdown)
 * @param {Object} options - Document options
 */
export const generateWord = async (content, options = {}) => {
  const {
    title = 'Document',
    service = '',
    fileName = 'document',
    metadata = {},
  } = options;
  
  try {
    const serviceName = SERVICES[service] || service || 'GetHiredAlly';
    const sections = [];
    
    // === HEADER SECTION ===
    const headerParagraphs = [
      // Title
      new Paragraph({
        children: [
          new TextRun({
            text: title,
            bold: true,
            size: 48, // 24pt
            color: COLORS.primary.replace('#', ''),
          }),
        ],
        spacing: { after: 200 },
      }),
      
      // Service
      new Paragraph({
        children: [
          new TextRun({
            text: `Service: ${serviceName}`,
            size: 20,
            color: COLORS.textLight.replace('#', ''),
          }),
        ],
        spacing: { after: 100 },
      }),
      
      // Date
      new Paragraph({
        children: [
          new TextRun({
            text: `Generated: ${formatDateTime()}`,
            size: 20,
            color: COLORS.textLight.replace('#', ''),
          }),
        ],
        spacing: { after: 100 },
      }),
    ];
    
    // Score (if available)
    if (metadata?.score !== undefined) {
      headerParagraphs.push(
        new Paragraph({
          children: [
            new TextRun({
              text: `Score: ${metadata.score}/100 (${metadata.grade || 'N/A'})`,
              bold: true,
              size: 22,
              color: COLORS.primary.replace('#', ''),
            }),
          ],
          spacing: { after: 200 },
        })
      );
    }
    
    // Divider
    headerParagraphs.push(
      new Paragraph({
        children: [
          new TextRun({
            text: '─'.repeat(60),
            color: COLORS.border.replace('#', ''),
          }),
        ],
        spacing: { after: 400 },
      })
    );
    
    // === CONTENT ===
    const plainText = markdownToPlainText(content);
    const lines = plainText.split('\n');
    
    const contentParagraphs = lines.map((line) => {
      if (!line.trim()) {
        return new Paragraph({ spacing: { after: 200 } });
      }
      
      const isBullet = line.startsWith('• ');
      
      return new Paragraph({
        children: [
          new TextRun({
            text: line,
            size: 22, // 11pt
          }),
        ],
        bullet: isBullet ? { level: 0 } : undefined,
        spacing: { after: 120 },
      });
    });
    
    // === CREATE DOCUMENT ===
    const doc = new Document({
      sections: [{
        properties: {},
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                children: [
                  new TextRun({
                    text: 'Page ',
                    size: 16,
                    color: COLORS.textLight.replace('#', ''),
                  }),
                  new TextRun({
                    children: [PageNumber.CURRENT],
                    size: 16,
                    color: COLORS.textLight.replace('#', ''),
                  }),
                  new TextRun({
                    text: ' of ',
                    size: 16,
                    color: COLORS.textLight.replace('#', ''),
                  }),
                  new TextRun({
                    children: [PageNumber.TOTAL_PAGES],
                    size: 16,
                    color: COLORS.textLight.replace('#', ''),
                  }),
                  new TextRun({
                    text: '     |     ',
                    size: 16,
                    color: COLORS.textLight.replace('#', ''),
                  }),
                  new ExternalHyperlink({
                    children: [
                      new TextRun({
                        text: 'GetHiredAlly App',
                        size: 16,
                        color: COLORS.secondary.replace('#', ''),
                      }),
                    ],
                    link: COMPANY.app,
                  }),
                  new TextRun({
                    text: ' | ',
                    size: 16,
                    color: COLORS.textLight.replace('#', ''),
                  }),
                  new ExternalHyperlink({
                    children: [
                      new TextRun({
                        text: 'GetHiredAlly Blog',
                        size: 16,
                        color: COLORS.secondary.replace('#', ''),
                      }),
                    ],
                    link: COMPANY.website + '/blog',
                  }),
                ],
                alignment: AlignmentType.CENTER,
              }),
            ],
          }),
        },
        children: [
          ...headerParagraphs,
          ...contentParagraphs,
        ],
      }],
    });
    
    // === DOWNLOAD ===
    const blob = await Packer.toBlob(doc);
    saveAs(blob, `${fileName}.docx`);
    
    return true;
  } catch (error) {
    console.error('Word generation error:', error);
    throw error;
  }
};

export default { generateWord };
