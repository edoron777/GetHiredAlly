/**
 * Markdown Converter Utility for DocStyler
 * Converts markdown to plain text or structured data
 */

/**
 * Convert markdown to plain text
 * @param {string} markdown - Markdown content
 * @returns {string} Plain text
 */
export const markdownToPlainText = (markdown) => {
  if (!markdown) return '';
  
  return markdown
    // Remove headers but keep text
    .replace(/^#{1,6}\s+(.+)$/gm, '$1\n')
    // Remove bold/italic markers
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/__(.+?)__/g, '$1')
    .replace(/_(.+?)_/g, '$1')
    // Remove links, keep text
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    // Convert bullet points
    .replace(/^[\s]*[-*+]\s+/gm, '• ')
    // Remove code blocks
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`([^`]+)`/g, '$1')
    // Remove horizontal rules
    .replace(/^[-*_]{3,}$/gm, '───────────────────')
    // Clean up whitespace
    .replace(/\n{3,}/g, '\n\n')
    .trim();
};

/**
 * Parse markdown into structured sections
 * @param {string} markdown - Markdown content
 * @returns {Array} Array of sections with type and content
 */
export const parseMarkdownSections = (markdown) => {
  if (!markdown) return [];
  
  const lines = markdown.split('\n');
  const sections = [];
  let currentSection = null;
  let currentContent = [];
  
  lines.forEach((line) => {
    // Check for headers
    const h1Match = line.match(/^#\s+(.+)$/);
    const h2Match = line.match(/^##\s+(.+)$/);
    const h3Match = line.match(/^###\s+(.+)$/);
    
    if (h1Match || h2Match || h3Match) {
      // Save previous section
      if (currentSection) {
        sections.push({
          ...currentSection,
          content: currentContent.join('\n').trim(),
        });
      }
      
      // Start new section
      currentSection = {
        type: h1Match ? 'h1' : h2Match ? 'h2' : 'h3',
        title: (h1Match || h2Match || h3Match)[1],
      };
      currentContent = [];
    } else {
      currentContent.push(line);
    }
  });
  
  // Save last section
  if (currentSection) {
    sections.push({
      ...currentSection,
      content: currentContent.join('\n').trim(),
    });
  } else if (currentContent.length > 0) {
    // Content without headers
    sections.push({
      type: 'body',
      title: null,
      content: currentContent.join('\n').trim(),
    });
  }
  
  return sections;
};

/**
 * Extract bullet points from content
 * @param {string} content - Content with bullet points
 * @returns {Array} Array of bullet point strings
 */
export const extractBulletPoints = (content) => {
  if (!content) return [];
  
  const bullets = [];
  const lines = content.split('\n');
  
  lines.forEach((line) => {
    const bulletMatch = line.match(/^[\s]*[-*+]\s+(.+)$/);
    if (bulletMatch) {
      bullets.push(bulletMatch[1].trim());
    }
  });
  
  return bullets;
};

/**
 * Convert markdown bold/italic to styled spans (for HTML)
 * @param {string} text - Text with markdown formatting
 * @returns {string} HTML with styled spans
 */
export const convertInlineFormatting = (text) => {
  if (!text) return '';
  
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
};
