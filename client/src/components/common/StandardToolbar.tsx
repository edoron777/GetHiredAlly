// ===========================================
// STANDARD TOOLBAR COMPONENT
// ===========================================
//
// USAGE: Import and use in any page that needs toolbar functionality
//
// import { StandardToolbar } from '../components/common';
//
// <StandardToolbar
//   onExpandAll={handleExpandAll}
//   onCollapseAll={handleCollapseAll}
//   onPDF={handleExportPDF}
//   onWord={handleExportWord}
//   onMarkdown={handleExportMarkdown}
//   serviceName="CV Analysis Report"
// />
//
// FLEXIBLE OPTIONS:
// - showEmail, showWhatsApp, showPDF, showWord, showMarkdown (default: true)
// - Set to false to hide specific buttons
// - onEmail, onWhatsApp for custom handlers (optional)
//
// DO NOT copy this code into other files!
// DO NOT create alternative toolbar components!
// If you need changes, modify THIS file only.
//
// ===========================================

import { useState } from 'react'
import { Loader2, Mail, MessageCircle, FileDown } from 'lucide-react'

interface StandardToolbarProps {
  onExpandAll: () => void
  onCollapseAll: () => void
  serviceName: string
  shareUrl?: string

  onEmail?: () => void
  onWhatsApp?: () => void
  onPDF?: () => Promise<void>
  onWord?: () => Promise<void>
  onMarkdown?: () => Promise<void>

  showEmail?: boolean
  showWhatsApp?: boolean
  showPDF?: boolean
  showWord?: boolean
  showMarkdown?: boolean
}

export function StandardToolbar({
  onExpandAll,
  onCollapseAll,
  serviceName,
  shareUrl,
  onEmail,
  onWhatsApp,
  onPDF,
  onWord,
  onMarkdown,
  showEmail = true,
  showWhatsApp = true,
  showPDF = true,
  showWord = true,
  showMarkdown = true
}: StandardToolbarProps) {
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [downloadingDocx, setDownloadingDocx] = useState(false)
  const [downloadingMd, setDownloadingMd] = useState(false)

  const handlePDF = async () => {
    if (!onPDF) return
    setDownloadingPdf(true)
    try {
      await onPDF()
    } finally {
      setDownloadingPdf(false)
    }
  }

  const handleWord = async () => {
    if (!onWord) return
    setDownloadingDocx(true)
    try {
      await onWord()
    } finally {
      setDownloadingDocx(false)
    }
  }

  const handleMarkdown = async () => {
    if (!onMarkdown) return
    setDownloadingMd(true)
    try {
      await onMarkdown()
    } finally {
      setDownloadingMd(false)
    }
  }

  const defaultEmailHandler = () => {
    const subject = encodeURIComponent(`${serviceName} - GetHiredAlly`)
    const body = encodeURIComponent(
      `Check out my interview preparation from GetHiredAlly!\n\n${shareUrl || window.location.href}\n\nPrepare for your interview: https://gethiredally.com/`
    )
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank')
  }

  const defaultWhatsAppHandler = () => {
    const message = encodeURIComponent(
      `Check out my interview preparation from GetHiredAlly! ${shareUrl || window.location.href}`
    )
    window.open(`https://wa.me/?text=${message}`, '_blank')
  }

  const handleEmail = onEmail || defaultEmailHandler
  const handleWhatsApp = onWhatsApp || defaultWhatsAppHandler

  const shouldShowEmail = showEmail
  const shouldShowWhatsApp = showWhatsApp
  const shouldShowPDF = showPDF && onPDF
  const shouldShowWord = showWord && onWord
  const shouldShowMarkdown = showMarkdown && onMarkdown

  const hasShareButtons = shouldShowEmail || shouldShowWhatsApp
  const hasExportButtons = shouldShowPDF || shouldShowWord || shouldShowMarkdown

  const buttonStyle = {
    color: 'white',
    padding: '4px 8px',
    borderRadius: '4px',
    border: 'none',
    background: 'none',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 500 as const,
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    transition: 'background-color 0.2s'
  }

  const separatorStyle = {
    color: 'rgba(255,255,255,0.3)',
    fontSize: '16px',
    margin: '0 8px'
  }

  return (
    <div
      style={{
        backgroundColor: '#1E3A5F',
        borderRadius: '8px',
        padding: '8px 16px',
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <button
          type="button"
          title="Expand All"
          onClick={onExpandAll}
          style={{
            ...buttonStyle,
            fontSize: '20px',
            fontWeight: 700,
            padding: '4px 12px'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        >
          +
        </button>
        <button
          type="button"
          title="Collapse All"
          onClick={onCollapseAll}
          style={{
            ...buttonStyle,
            fontSize: '20px',
            fontWeight: 700,
            padding: '4px 12px'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        >
          −
        </button>
      </div>

      <span style={separatorStyle}>│</span>

      <div style={{ flexGrow: 1 }}></div>

      {hasShareButtons && (
        <>
          <span style={separatorStyle}>│</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {shouldShowEmail && (
              <button
                type="button"
                onClick={handleEmail}
                style={buttonStyle}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <Mail className="h-4 w-4" />
                Email
              </button>
            )}
            {shouldShowWhatsApp && (
              <button
                type="button"
                onClick={handleWhatsApp}
                style={buttonStyle}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <MessageCircle className="h-4 w-4" />
                WhatsApp
              </button>
            )}
          </div>
        </>
      )}

      {hasExportButtons && (
        <>
          <span style={separatorStyle}>│</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {shouldShowPDF && (
              <button
                type="button"
                disabled={downloadingPdf}
                onClick={handlePDF}
                style={{
                  ...buttonStyle,
                  opacity: downloadingPdf ? 0.6 : 1,
                  cursor: downloadingPdf ? 'not-allowed' : 'pointer'
                }}
                onMouseEnter={(e) => !downloadingPdf && (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)')}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                {downloadingPdf ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                PDF
              </button>
            )}
            {shouldShowWord && (
              <button
                type="button"
                disabled={downloadingDocx}
                onClick={handleWord}
                style={{
                  ...buttonStyle,
                  opacity: downloadingDocx ? 0.6 : 1,
                  cursor: downloadingDocx ? 'not-allowed' : 'pointer'
                }}
                onMouseEnter={(e) => !downloadingDocx && (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)')}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                {downloadingDocx ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                WORD
              </button>
            )}
            {shouldShowMarkdown && (
              <button
                type="button"
                title="Download as Markdown"
                disabled={downloadingMd}
                onClick={handleMarkdown}
                style={{
                  ...buttonStyle,
                  opacity: downloadingMd ? 0.6 : 1,
                  cursor: downloadingMd ? 'not-allowed' : 'pointer'
                }}
                onMouseEnter={(e) => !downloadingMd && (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)')}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                {downloadingMd ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
                MD
              </button>
            )}
          </div>
        </>
      )}
    </div>
  )
}
