/**
 * DocStyler - Main orchestrator for document generation
 * 
 * Usage:
 * DocStyler.generate({
 *   content: markdownContent,
 *   format: 'pdf' | 'word' | 'md',
 *   options: { title, service, fileName, metadata }
 * });
 */

import { generatePDF } from './generators/generatePDF';
import { generateWord } from './generators/generateWord';
import { downloadMD } from './generators/generateMD';

const DocStyler = {
  /**
   * Generate and download document
   * @param {Object} params - Generation parameters
   * @param {string} params.content - Content to format (markdown)
   * @param {string} params.format - Output format: 'pdf', 'word', 'md'
   * @param {Object} params.options - Document options
   */
  generate: async ({ content, format, options = {} }) => {
    if (!content) {
      console.error('DocStyler: No content provided');
      return false;
    }
    
    const validFormats = ['pdf', 'word', 'md'];
    if (!validFormats.includes(format)) {
      console.error(`DocStyler: Invalid format "${format}". Use: ${validFormats.join(', ')}`);
      return false;
    }
    
    try {
      switch (format) {
        case 'pdf':
          await generatePDF(content, options);
          break;
        case 'word':
          await generateWord(content, options);
          break;
        case 'md':
          downloadMD(content, options);
          break;
        default:
          throw new Error(`Unknown format: ${format}`);
      }
      
      console.log(`DocStyler: ${format.toUpperCase()} generated successfully`);
      return true;
    } catch (error) {
      console.error(`DocStyler: Error generating ${format}:`, error);
      throw error;
    }
  },
  
  /**
   * Generate PDF document
   */
  pdf: async (content, options) => {
    return DocStyler.generate({ content, format: 'pdf', options });
  },
  
  /**
   * Generate Word document
   */
  word: async (content, options) => {
    return DocStyler.generate({ content, format: 'word', options });
  },
  
  /**
   * Generate Markdown document
   */
  md: (content, options) => {
    return DocStyler.generate({ content, format: 'md', options });
  },
};

export default DocStyler;
