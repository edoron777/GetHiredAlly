import React from 'react'
import type { TextMarkerProps } from './types'
import { 
  findMarkerPositions, 
  getMarkerStyleClass,
  getMarkerColorStyle 
} from './MarkerService'
import './MarkerStyles.css'

const URL_PATTERN = /(\b(?:https?:\/\/)?(?:www\.)?(?:linkedin\.com\/in\/[\w-]+|github\.com\/[\w-]+|[\w-]+\.(?:com|org|net|io|dev|co|me|info)(?:\/[\w\-._~:/?#[\]@!$&'()*+,;=%]*)?))/gi

function linkifySegment(text: string, keyPrefix: string): React.ReactNode[] {
  const parts: React.ReactNode[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null
  const regex = new RegExp(URL_PATTERN.source, 'gi')
  
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index))
    }
    const url = match[0]
    const href = url.startsWith('http') ? url : `https://${url}`
    parts.push(
      <a
        key={`${keyPrefix}-link-${match.index}`}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 hover:underline"
        onClick={(e) => e.stopPropagation()}
      >
        {url}
      </a>
    )
    lastIndex = regex.lastIndex
  }
  
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex))
  }
  
  return parts.length > 0 ? parts : [text]
}

export const TextMarker: React.FC<TextMarkerProps> = ({
  content,
  markers,
  config
}) => {
  const positions = findMarkerPositions(content, markers)
  
  if (positions.length === 0) {
    return (
      <div className={`text-marker-container ${config.className || ''}`}>
        {linkifySegment(content, 'full')}
      </div>
    )
  }
  
  const elements: React.ReactNode[] = []
  let lastEnd = 0
  
  positions.forEach((pos, index) => {
    if (pos.start > lastEnd) {
      elements.push(
        <span key={`text-${index}`}>
          {linkifySegment(content.substring(lastEnd, pos.start), `seg-${index}`)}
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
        {linkifySegment(content.substring(lastEnd), 'end')}
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
