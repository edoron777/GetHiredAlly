/**
 * Document Styling Constants for DocStyler
 * Used by all generators (PDF, WORD, MD)
 */

// Brand Colors
export const COLORS = {
  primary: '#1E5A85',      // Dark blue - headings, accents
  secondary: '#3b82f6',    // Light blue - links
  text: '#1f2937',         // Dark gray - body text
  textLight: '#6b7280',    // Light gray - metadata
  background: '#f3f4f6',   // Light gray - metadata box
  border: '#e5e7eb',       // Border color
  white: '#ffffff',
};

// Typography
export const FONTS = {
  heading: 'Arial, Helvetica, sans-serif',
  body: 'Arial, Helvetica, sans-serif',
  sizes: {
    h1: 24,
    h2: 20,
    h3: 16,
    body: 11,
    small: 9,
    footer: 10,
  },
};

// Spacing (in points for PDF/WORD)
export const SPACING = {
  margin: {
    top: 72,    // 1 inch
    bottom: 72,
    left: 72,
    right: 72,
  },
  lineHeight: 1.5,
  paragraphSpacing: 12,
  sectionSpacing: 24,
};

// Company Information
export const COMPANY = {
  name: 'GetHiredAlly',
  website: 'https://gethiredally.com',
  app: 'https://app.gethiredally.com',
  tagline: 'Your AI-Powered Job Search Ally',
};

// Footer Template
export const FOOTER = {
  links: [
    { text: 'GetHiredAlly App', url: 'https://app.gethiredally.com' },
    { text: 'GetHiredAlly Blog', url: 'https://gethiredally.com/blog' },
  ],
  separator: ' | ',
};

// Service Names (for metadata)
export const SERVICES = {
  'cv-optimizer': 'Perfect Your CV',
  'cv-tailor': 'Tailor for This Job',
  'xray-analyzer': 'Decode the Job Post',
  'interview-questions': 'Predict the Questions',
  'interview-answers': 'Craft Your Answers',
};

// Document Templates
export const TEMPLATES = {
  header: {
    showLogo: false,  // Set to true when logo is available
    showDate: true,
    showService: true,
  },
  footer: {
    showPageNumbers: true,
    showLinks: true,
    pageFormat: 'Page {current} of {total}',
  },
  metadata: {
    showBox: true,
    backgroundColor: COLORS.background,
  },
};

/**
 * Format current date for documents
 * @returns {string} Formatted date
 */
export const formatDate = () => {
  const now = new Date();
  return now.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Format date and time for documents
 * @returns {string} Formatted date and time
 */
export const formatDateTime = () => {
  const now = new Date();
  return now.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};
