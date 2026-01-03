import React from 'react'
import type { DocumentEditorProps } from './types'
import { DEFAULT_DOCUMENT_CONFIG } from './types'
import { detectFormat } from './utils/formatDetector'
import { MarkdownRenderer } from './renderers/MarkdownRenderer'
import { TextRenderer } from './renderers/TextRenderer'
import './DocumentEditorStyles.css'

export const DocumentEditor: React.FC<DocumentEditorProps> = ({
  content,
  format = 'auto',
  originalFileName,
  config = {},
  markers = [],
  markerConfig,
  onMarkerClick,
  className = ''
}) => {
  const mergedConfig = { ...DEFAULT_DOCUMENT_CONFIG, ...config }
  const detectedFormat = format === 'auto' ? detectFormat(content, originalFileName) : format
  
  const containerStyle: React.CSSProperties = {
    backgroundColor: mergedConfig.showWordMargins ? mergedConfig.marginColor : mergedConfig.paperColor,
    padding: mergedConfig.showWordMargins ? '30px' : '0'
  }
  
  const paperStyle: React.CSSProperties = {
    maxWidth: `${mergedConfig.maxWidth}px`,
    minHeight: `${mergedConfig.minHeight}px`,
    padding: `${mergedConfig.padding}px`,
    backgroundColor: mergedConfig.paperColor,
    fontFamily: mergedConfig.fontFamily,
    fontSize: `${mergedConfig.fontSize}px`,
    lineHeight: mergedConfig.lineHeight,
    boxShadow: mergedConfig.paperShadow ? '0 2px 10px rgba(0, 0, 0, 0.1)' : 'none'
  }

  const renderContent = () => {
    const rendererProps = {
      content,
      markers: mergedConfig.enableHighlighting ? markers : [],
      markerConfig,
      onMarkerClick
    }

    switch (detectedFormat) {
      case 'markdown':
        return <MarkdownRenderer {...rendererProps} />
      case 'word':
      case 'pdf':
      case 'text':
      default:
        return <TextRenderer {...rendererProps} />
    }
  }

  return (
    <div className={`document-editor-container ${className}`} style={containerStyle}>
      <div className="document-editor-paper" style={paperStyle}>
        {renderContent()}
      </div>
    </div>
  )
}

export default DocumentEditor
