/**
 * Email utility for ActionBar
 */

/**
 * Open email client with pre-filled content
 * @param {Object} options - Email options
 * @param {string} options.subject - Email subject
 * @param {string} options.body - Email body content
 * @param {string} options.to - Optional recipient
 * @returns {void}
 */
export const sendEmail = ({ subject = '', body = '', to = '' }) => {
  const encodedSubject = encodeURIComponent(subject);
  const encodedBody = encodeURIComponent(body);
  const encodedTo = encodeURIComponent(to);
  
  let mailtoUrl = 'mailto:';
  
  if (to) {
    mailtoUrl += encodedTo;
  }
  
  mailtoUrl += `?subject=${encodedSubject}&body=${encodedBody}`;
  
  // Open in same window (will open email client)
  window.location.href = mailtoUrl;
};
