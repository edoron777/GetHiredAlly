import type { MarkerItem, MarkerConfig } from '../TextMarker'

/**
 * Supported document formats
 */
export type DocumentFormat = 'markdown' | 'word' | 'pdf' | 'text' | 'auto'

/**
 * Configuration for DocumentEditor appearance
 */
export interface DocumentEditorConfig {
  maxWidth?: number
  minHeight?: number
  padding?: number
  
  fontFamily?: string
  fontSize?: number
  lineHeight?: number
  
  showWordMargins?: boolean
  marginColor?: string
  paperColor?: string
  paperShadow?: boolean
  
  enableHighlighting?: boolean
}

/**
 * Main props for DocumentEditor component
 */
export interface DocumentEditorProps {
  content: string
  
  format?: DocumentFormat
  
  originalFileUrl?: string
  originalFileName?: string
  
  config?: DocumentEditorConfig
  
  markers?: MarkerItem[]
  markerConfig?: Partial<MarkerConfig>
  onMarkerClick?: (id: string, tag: string) => void
  
  className?: string
}

/**
 * Default configuration values
 */
export const DEFAULT_DOCUMENT_CONFIG: DocumentEditorConfig = {
  maxWidth: 1600,
  minHeight: 800,
  padding: 60,
  fontFamily: "'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif",
  fontSize: 20,
  lineHeight: 1.7,
  showWordMargins: true,
  marginColor: '#e8eaed',
  paperColor: '#ffffff',
  paperShadow: true,
  enableHighlighting: true
}

/**
 * Props for individual renderers
 */
export interface RendererProps {
  content: string
  originalFileUrl?: string
  markers?: MarkerItem[]
  markerConfig?: Partial<MarkerConfig>
  onMarkerClick?: (id: string, tag: string) => void
  className?: string
}

/**
 * Result from Word/PDF processing
 */
export interface ProcessedDocument {
  html: string
  textMapping: TextPositionMap[]
}

/**
 * Maps original text positions to rendered positions
 * Used for TextMarker integration with formatted content
 */
export interface TextPositionMap {
  originalStart: number
  originalEnd: number
  renderedSelector: string
}
