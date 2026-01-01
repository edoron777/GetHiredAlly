import type { MarkerItem } from './types'

interface MarkerPosition {
  start: number
  end: number
  marker: MarkerItem
}

export function findMarkerPositions(
  content: string,
  markers: MarkerItem[]
): MarkerPosition[] {
  const positions: MarkerPosition[] = []
  
  markers.forEach(marker => {
    if (!marker.matchText || marker.matchText.length === 0) return
    
    const index = content.indexOf(marker.matchText)
    
    if (index !== -1) {
      positions.push({
        start: index,
        end: index + marker.matchText.length,
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
      borderRadius: '3px',
      padding: '1px 3px'
    }
  }
}
