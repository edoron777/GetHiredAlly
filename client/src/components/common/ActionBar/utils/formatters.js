/**
 * Content formatting utilities for ActionBar
 */

/**
 * Strip markdown formatting from text
 * @param {string} content - Markdown content
 * @returns {string} Plain text
 */
export const stripMarkdown = (content) => {
  if (!content) return '';
  
  return content
    // Remove headers
    .replace(/^#{1,6}\s+/gm, '')
    // Remove bold/italic
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/__(.+?)__/g, '$1')
    .replace(/_(.+?)_/g, '$1')
    // Remove links, keep text
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    // Remove bullet points
    .replace(/^[\s]*[-*+]\s+/gm, '• ')
    // Remove numbered lists formatting
    .replace(/^[\s]*\d+\.\s+/gm, '')
    // Remove code blocks
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`([^`]+)`/g, '$1')
    // Remove horizontal rules
    .replace(/^[-*_]{3,}$/gm, '')
    // Clean up extra whitespace
    .replace(/\n{3,}/g, '\n\n')
    .trim();
};

/**
 * Format content for specific output type
 * @param {string} content - Raw content
 * @param {string} format - Output format: 'plain', 'html', 'markdown'
 * @returns {string} Formatted content
 */
export const formatContent = (content, format = 'plain') => {
  if (!content) return '';
  
  switch (format) {
    case 'plain':
      return stripMarkdown(content);
    case 'html':
      // Basic markdown to HTML conversion
      return content
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    case 'markdown':
    default:
      return content;
  }
};
