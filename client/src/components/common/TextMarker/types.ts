export interface MarkerItem {
  id: string
  matchText: string
  tag: string
}

export interface TagColorMap {
  [tagName: string]: {
    color: string
    hoverColor?: string
  }
}

export type MarkerStyle = 'underline' | 'rectangle'

export interface MarkerIcon {
  icon: React.ReactNode
  position: 'before' | 'after'
  className?: string
}

export interface MarkerConfig {
  style: MarkerStyle
  tagColors: TagColorMap
  icon?: MarkerIcon
  onClick?: (id: string, tag: string) => void
  className?: string
}

export interface TextMarkerProps {
  content: string
  markers: MarkerItem[]
  config: MarkerConfig
}
