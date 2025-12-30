import React from 'react';
import ActionBarButton from './ActionBarButton';
import { 
  copyToClipboard, 
  sendEmail, 
  shareToWhatsApp, 
  stripMarkdown,
  formatContent 
} from './utils';

/**
 * ActionBar - Reusable toolbar for share/export actions
 * 
 * @param {Object} props
 * @param {string} props.content - Content to act on (text/markdown)
 * @param {string} props.fileName - Default filename for downloads
 * @param {string} props.emailSubject - Email subject line
 * @param {Array} props.hiddenButtons - Buttons to hide: ['copy', 'email', 'whatsapp', 'pdf', 'word', 'md']
 * @param {Array} props.disabledButtons - Buttons to disable
 * @param {Function} props.onCopy - Optional custom copy handler
 * @param {Function} props.onEmail - Optional custom email handler
 * @param {Function} props.onWhatsApp - Optional custom WhatsApp handler
 * @param {Function} props.onPDF - Optional custom PDF handler
 * @param {Function} props.onWord - Optional custom Word handler
 * @param {Function} props.onMarkdown - Optional custom Markdown handler
 */
const ActionBar = ({
  content = '',
  fileName = 'document',
  emailSubject = 'Shared from GetHiredAlly',
  hiddenButtons = [],
  disabledButtons = [],
  onCopy,
  onEmail,
  onWhatsApp,
  onPDF,
  onWord,
  onMarkdown,
}) => {
  
  // Check if button should be shown
  const isVisible = (button) => !hiddenButtons.includes(button);
  const isDisabled = (button) => disabledButtons.includes(button);

  // COPY handler
  const handleCopy = async () => {
    if (onCopy) {
      return onCopy(content);
    }
    const plainText = stripMarkdown(content);
    return await copyToClipboard(plainText);
  };

  // EMAIL handler
  const handleEmail = () => {
    if (onEmail) {
      return onEmail(content);
    }
    const plainText = stripMarkdown(content);
    sendEmail({
      subject: emailSubject,
      body: plainText,
    });
  };

  // WHATSAPP handler
  const handleWhatsApp = () => {
    if (onWhatsApp) {
      return onWhatsApp(content);
    }
    const plainText = stripMarkdown(content);
    shareToWhatsApp(plainText);
  };

  // PDF handler (placeholder - will show coming soon)
  const handlePDF = () => {
    if (onPDF) {
      return onPDF(content);
    }
    alert('PDF export coming soon!');
  };

  // WORD handler (placeholder - will show coming soon)
  const handleWord = () => {
    if (onWord) {
      return onWord(content);
    }
    alert('Word export coming soon!');
  };

  // MARKDOWN handler
  const handleMarkdown = () => {
    if (onMarkdown) {
      return onMarkdown(content);
    }
    // Create and download .md file
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${fileName}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Container style
  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: '4px',
    padding: '8px 16px',
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    flexWrap: 'wrap',
  };

  // Separator style
  const separatorStyle = {
    width: '1px',
    height: '24px',
    backgroundColor: '#d1d5db',
    margin: '0 8px',
  };

  return (
    <div style={containerStyle}>
      
      {/* GROUP 1: Quick Actions */}
      {isVisible('copy') && (
        <ActionBarButton
          label="Copy"
          icon="📋"
          tooltip="Copy content to clipboard"
          color="#6b7280"
          hoverBg="#f3f4f6"
          onClick={handleCopy}
          disabled={isDisabled('copy')}
          successLabel="Copied!"
        />
      )}

      {/* Separator */}
      {isVisible('copy') && (isVisible('email') || isVisible('whatsapp')) && (
        <div style={separatorStyle} />
      )}

      {/* GROUP 2: Share */}
      {isVisible('email') && (
        <ActionBarButton
          label="Email"
          icon="✉️"
          tooltip="Send via email"
          color="#3b82f6"
          hoverBg="#eff6ff"
          onClick={handleEmail}
          disabled={isDisabled('email')}
        />
      )}

      {isVisible('whatsapp') && (
        <ActionBarButton
          label="WhatsApp"
          icon="💬"
          tooltip="Share on WhatsApp"
          color="#25D366"
          hoverBg="#f0fdf4"
          onClick={handleWhatsApp}
          disabled={isDisabled('whatsapp')}
        />
      )}

      {/* Separator */}
      {(isVisible('email') || isVisible('whatsapp')) && 
       (isVisible('pdf') || isVisible('word') || isVisible('md')) && (
        <div style={separatorStyle} />
      )}

      {/* GROUP 3: Export */}
      {isVisible('pdf') && (
        <ActionBarButton
          label="PDF"
          icon="📄"
          tooltip="Download as PDF"
          color="#ef4444"
          hoverBg="#fef2f2"
          onClick={handlePDF}
          disabled={isDisabled('pdf')}
        />
      )}

      {isVisible('word') && (
        <ActionBarButton
          label="WORD"
          icon="📝"
          tooltip="Download as Word document"
          color="#2563eb"
          hoverBg="#eff6ff"
          onClick={handleWord}
          disabled={isDisabled('word')}
        />
      )}

      {isVisible('md') && (
        <ActionBarButton
          label="MD"
          icon="📋"
          tooltip="Download as Markdown"
          color="#6b7280"
          hoverBg="#f3f4f6"
          onClick={handleMarkdown}
          disabled={isDisabled('md')}
        />
      )}
    </div>
  );
};

export default ActionBar;
