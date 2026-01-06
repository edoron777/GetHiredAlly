import React from 'react'
import type { TextMarkerProps } from './types'
import { 
  findMarkerPositions, 
  getMarkerStyleClass,
  getMarkerColorStyle 
} from './MarkerService'
import './MarkerStyles.css'

export const TextMarker: React.FC<TextMarkerProps> = ({
  content,
  markers,
  config
}) => {
  const positions = findMarkerPositions(content, markers)
  
  if (positions.length === 0) {
    return (
      <div className={`text-marker-container ${config.className || ''}`}>
        {content}
      </div>
    )
  }
  
  const elements: React.ReactNode[] = []
  let lastEnd = 0
  
  positions.forEach((pos, index) => {
    if (pos.start > lastEnd) {
      elements.push(
        <span key={`text-${index}`}>
          {content.substring(lastEnd, pos.start)}
        </span>
      )
    }
    
    const tagColor = config.tagColors[pos.marker.tag]
    const color = tagColor?.color || '#787774'
    
    const styleClass = getMarkerStyleClass(config.style)
    const colorStyle = getMarkerColorStyle(config.style, color)
    
    const handleClick = () => {
      config.onClick?.(pos.marker.id, pos.marker.tag)
    }
    
    const renderIcon = () => {
      if (!config.icon) return null
      return (
        <span 
          className={`marker-icon-gutter ${config.icon.className || ''}`}
          style={{ color }}
          onClick={handleClick}
          data-tag={pos.marker.tag}
          data-marker-id={pos.marker.id}
        >
          {config.icon.icon}
        </span>
      )
    }
    
    elements.push(
      <span
        key={`marker-${pos.marker.id}-${index}`}
        className="marker-wrapper"
      >
        {renderIcon()}
        <span
          id={`marker-${pos.marker.id}`}
          className={`text-marker ${styleClass}`}
          style={colorStyle}
          onClick={handleClick}
          data-tag={pos.marker.tag}
          data-marker-id={pos.marker.id}
        >
          {content.substring(pos.start, pos.end)}
        </span>
      </span>
    )
    
    lastEnd = pos.end
  })
  
  if (lastEnd < content.length) {
    elements.push(
      <span key="text-end">
        {content.substring(lastEnd)}
      </span>
    )
  }
  
  return (
    <div className={`text-marker-container ${config.className || ''}`}>
      {elements}
    </div>
  )
}

export default TextMarker
