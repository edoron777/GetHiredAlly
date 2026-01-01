export { TextMarker, default } from './TextMarker'
export { findMarkerPositions, getMarkerStyleClass, getMarkerColorStyle } from './MarkerService'
export type { 
  MarkerItem, 
  TagColorMap, 
  MarkerStyle, 
  MarkerIcon, 
  MarkerConfig, 
  TextMarkerProps 
} from './types'

export const CV_OPTIMIZER_COLORS = {
  critical: { color: '#e03e3e' },
  important: { color: '#d9730d' },
  consider: { color: '#cb932f' },
  polish: { color: '#448361' }
}

export const NOTION_COLORS = {
  red: { color: '#e03e3e' },
  orange: { color: '#d9730d' },
  yellow: { color: '#cb932f' },
  green: { color: '#448361' },
  blue: { color: '#337ea9' },
  purple: { color: '#9065b0' },
  pink: { color: '#c14c8a' },
  gray: { color: '#787774' }
}
