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
    
    elements.push(
      <span
        key={`marker-${pos.marker.id}-${index}`}
        id={`marker-${pos.marker.id}`}
        className={`text-marker ${styleClass}`}
        style={colorStyle}
        onClick={handleClick}
        data-tag={pos.marker.tag}
        data-marker-id={pos.marker.id}
      >
        {config.icon && config.icon.position === 'before' && (
          <span className={`marker-icon marker-icon-before ${config.icon.className || ''}`}>
            {config.icon.icon}
          </span>
        )}
        
        {content.substring(pos.start, pos.end)}
        
        {config.icon && config.icon.position === 'after' && (
          <span className={`marker-icon marker-icon-after ${config.icon.className || ''}`}>
            {config.icon.icon}
          </span>
        )}
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
