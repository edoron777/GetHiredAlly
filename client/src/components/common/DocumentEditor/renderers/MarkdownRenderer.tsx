import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { RendererProps } from '../types'
import { TextMarker, CV_OPTIMIZER_COLORS } from '../../TextMarker'

export const MarkdownRenderer: React.FC<RendererProps> = ({
  content,
  markers = [],
  markerConfig,
  onMarkerClick,
  className = ''
}) => {
  if (markers.length > 0) {
    return (
      <TextMarker
        content={content}
        markers={markers}
        config={{
          style: 'rectangle',
          tagColors: CV_OPTIMIZER_COLORS,
          icon: { icon: 'ⓘ', position: 'after' },
          onClick: onMarkerClick,
          className: `markdown-content ${className}`,
          ...markerConfig
        }}
      />
    )
  }

  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default MarkdownRenderer
