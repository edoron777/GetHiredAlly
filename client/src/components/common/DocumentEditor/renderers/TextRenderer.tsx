import React from 'react'
import type { RendererProps } from '../types'
import { TextMarker, CV_OPTIMIZER_COLORS } from '../../TextMarker'

export const TextRenderer: React.FC<RendererProps> = ({
  content,
  htmlContent,
  markers = [],
  markerConfig,
  onMarkerClick
}) => {
  if (htmlContent && markers.length === 0) {
    return (
      <div 
        className="text-content cv-html-content"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    )
  }
  
  if (markers.length === 0) {
    return (
      <div className="text-content">
        <div className="text-preformatted">{content}</div>
      </div>
    )
  }
  
  return (
    <div className="text-content">
      <TextMarker
        content={content}
        markers={markers}
        config={{
          style: 'rectangle',
          tagColors: CV_OPTIMIZER_COLORS,
          icon: { icon: 'ⓘ', position: 'after' },
          onClick: onMarkerClick,
          ...markerConfig
        }}
      />
    </div>
  )
}

export default TextRenderer
