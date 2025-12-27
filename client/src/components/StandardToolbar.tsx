import { useState } from 'react'
import { Loader2, Mail, MessageCircle, FileDown } from 'lucide-react'

interface StandardToolbarProps {
  onExpandAll: () => void
  onCollapseAll: () => void
  onPDF: () => Promise<void>
  onWord: () => Promise<void>
  onMarkdown: () => Promise<void>
  serviceName: string
  shareUrl?: string
}

export function StandardToolbar({
  onExpandAll,
  onCollapseAll,
  onPDF,
  onWord,
  onMarkdown,
  serviceName,
  shareUrl
}: StandardToolbarProps) {
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [downloadingDocx, setDownloadingDocx] = useState(false)
  const [downloadingMd, setDownloadingMd] = useState(false)

  const handlePDF = async () => {
    setDownloadingPdf(true)
    try {
      await onPDF()
    } finally {
      setDownloadingPdf(false)
    }
  }

  const handleWord = async () => {
    setDownloadingDocx(true)
    try {
      await onWord()
    } finally {
      setDownloadingDocx(false)
    }
  }

  const handleMarkdown = async () => {
    setDownloadingMd(true)
    try {
      await onMarkdown()
    } finally {
      setDownloadingMd(false)
    }
  }

  const handleEmail = () => {
    const subject = encodeURIComponent(`${serviceName} - GetHiredAlly`)
    const body = encodeURIComponent(
      `Check out my interview preparation from GetHiredAlly!\n\n${shareUrl || window.location.href}\n\nPrepare for your interview: https://gethiredally.com/`
    )
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank')
  }

  const handleWhatsApp = () => {
    const message = encodeURIComponent(
      `Check out my interview preparation from GetHiredAlly! ${shareUrl || window.location.href}`
    )
    window.open(`https://wa.me/?text=${message}`, '_blank')
  }

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
          style={buttonStyle}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        >
          +
        </button>
        <button
          type="button"
          title="Collapse All"
          onClick={onCollapseAll}
          style={buttonStyle}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
        >
          −
        </button>
      </div>

      <span style={separatorStyle}>│</span>

      <div style={{ flexGrow: 1 }}></div>

      <span style={separatorStyle}>│</span>

      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
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
      </div>

      <span style={separatorStyle}>│</span>

      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
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
      </div>
    </div>
  )
}
