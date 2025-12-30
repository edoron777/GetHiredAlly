/**
 * WhatsApp utility for ActionBar
 */

// WhatsApp message limit
const WHATSAPP_MAX_LENGTH = 4096;

/**
 * Share content via WhatsApp
 * @param {string} text - Text to share
 * @returns {void}
 */
export const shareToWhatsApp = (text) => {
  if (!text) return;
  
  // Truncate if too long
  let content = text;
  if (content.length > WHATSAPP_MAX_LENGTH) {
    content = content.substring(0, WHATSAPP_MAX_LENGTH - 20) + '...\n\n[Truncated]';
  }
  
  const encoded = encodeURIComponent(content);
  const url = `https://wa.me/?text=${encoded}`;
  
  // Open in new tab
  window.open(url, '_blank', 'noopener,noreferrer');
};
