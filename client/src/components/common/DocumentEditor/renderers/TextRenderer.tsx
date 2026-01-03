import React from 'react'
import type { RendererProps } from '../types'
import { TextMarker, CV_OPTIMIZER_COLORS } from '../../TextMarker'

export const TextRenderer: React.FC<RendererProps> = ({
  content,
  markers = [],
  markerConfig,
  onMarkerClick,
  className = ''
}) => {
  if (markers.length === 0) {
    return (
      <div className={`document-editor-content ${className}`}>
        {content}
      </div>
    )
  }

  return (
    <TextMarker
      content={content}
      markers={markers}
      config={{
        style: 'rectangle',
        tagColors: CV_OPTIMIZER_COLORS,
        icon: { icon: 'ⓘ', position: 'after' },
        onClick: onMarkerClick,
        className: `document-editor-content ${className}`,
        ...markerConfig
      }}
    />
  )
}

export default TextRenderer
