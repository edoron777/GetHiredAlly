import type { MarkerItem } from './types'

interface MarkerPosition {
  start: number
  end: number
  marker: MarkerItem
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function needsWordBoundary(text: string): boolean {
  return /^[a-zA-Z]/.test(text) && /[a-zA-Z]$/.test(text) && text.length <= 10
}

export function findMarkerPositions(
  content: string,
  markers: MarkerItem[]
): MarkerPosition[] {
  const positions: MarkerPosition[] = []
  
  const normalizedContent = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
  
  markers.forEach(marker => {
    if (!marker.matchText || marker.matchText.length === 0) return
    
    const matchText = marker.matchText
    let index = -1
    
    const normalizedMatchText = matchText.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
    
    if (needsWordBoundary(normalizedMatchText)) {
      const pattern = new RegExp(`\\b${escapeRegex(normalizedMatchText)}\\b`, 'i')
      const match = pattern.exec(normalizedContent)
      if (match) {
        index = match.index
      }
    } else {
      index = normalizedContent.toLowerCase().indexOf(normalizedMatchText.toLowerCase())
    }
    
    if (index !== -1) {
      positions.push({
        start: index,
        end: index + matchText.length,
        marker
      })
    }
  })
  
  return resolveOverlaps(positions.sort((a, b) => a.start - b.start))
}

function resolveOverlaps(positions: MarkerPosition[]): MarkerPosition[] {
  const result: MarkerPosition[] = []
  let lastEnd = -1
  
  positions.forEach(pos => {
    if (pos.start >= lastEnd) {
      result.push(pos)
      lastEnd = pos.end
    }
  })
  
  return result
}

export function getMarkerStyleClass(style: 'underline' | 'rectangle'): string {
  return style === 'underline' ? 'marker-underline' : 'marker-rectangle'
}

export function getMarkerColorStyle(
  style: 'underline' | 'rectangle',
  color: string
): React.CSSProperties {
  if (style === 'underline') {
    return {
      background: `linear-gradient(to bottom, transparent 60%, ${color}40 60%)`,
      borderBottom: `2px solid ${color}`
    }
  } else {
    return {
      backgroundColor: `${color}30`,
      color: color,
      borderRadius: '3px',
      padding: '1px 3px'
    }
  }
}
