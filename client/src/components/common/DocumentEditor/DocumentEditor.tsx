import React, { useMemo } from 'react'
import type { DocumentEditorProps } from './types'
import { DEFAULT_DOCUMENT_CONFIG } from './types'
import { detectFormat } from './utils/formatDetector'
import { MarkdownRenderer } from './renderers/MarkdownRenderer'
import { WordRenderer } from './renderers/WordRenderer'
import { TextRenderer } from './renderers/TextRenderer'
import './DocumentEditorStyles.css'

export const DocumentEditor: React.FC<DocumentEditorProps> = ({
  content,
  format = 'auto',
  originalFileUrl,
  originalFileName,
  config = {},
  markers = [],
  markerConfig,
  onMarkerClick,
  className = ''
}) => {
  const mergedConfig = { ...DEFAULT_DOCUMENT_CONFIG, ...config }
  
  const detectedFormat = useMemo(() => {
    if (format !== 'auto') return format
    return detectFormat(content, originalFileName)
  }, [format, content, originalFileName])
  
  const cssVariables = {
    '--doc-max-width': `${mergedConfig.maxWidth}px`,
    '--doc-min-height': `${mergedConfig.minHeight}px`,
    '--doc-padding': `${mergedConfig.padding}px`,
    '--doc-font-family': mergedConfig.fontFamily,
    '--doc-font-size': `${mergedConfig.fontSize}px`,
    '--doc-line-height': String(mergedConfig.lineHeight),
    '--doc-margin-color': mergedConfig.marginColor,
    '--doc-paper-color': mergedConfig.paperColor,
  } as React.CSSProperties
  
  const renderContent = () => {
    const rendererProps = {
      content,
      originalFileUrl,
      markers: mergedConfig.enableHighlighting ? markers : [],
      markerConfig,
      onMarkerClick
    }
    
    switch (detectedFormat) {
      case 'markdown':
        return <MarkdownRenderer {...rendererProps} />
      case 'word':
        return <WordRenderer {...rendererProps} />
      case 'pdf':
      case 'text':
      default:
        return <TextRenderer {...rendererProps} />
    }
  }
  
  return (
    <div 
      className={`document-editor-container ${className}`}
      style={cssVariables}
    >
      <div className={`document-editor-paper ${mergedConfig.paperShadow ? 'with-shadow' : ''}`}>
        <div className="document-editor-content">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}

export default DocumentEditor
