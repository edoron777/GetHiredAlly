export { DocumentEditor, default } from './DocumentEditor'
export { detectFormat } from './utils/formatDetector'
export { TextRenderer } from './renderers/TextRenderer'
export { MarkdownRenderer } from './renderers/MarkdownRenderer'
export { WordRenderer } from './renderers/WordRenderer'

export type {
  DocumentFormat,
  DocumentEditorConfig,
  DocumentEditorProps,
  RendererProps,
  ProcessedDocument,
  TextPositionMap
} from './types'

export { DEFAULT_DOCUMENT_CONFIG } from './types'
