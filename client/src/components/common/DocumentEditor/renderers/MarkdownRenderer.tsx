import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { RendererProps } from '../types'
import { TextMarker, CV_OPTIMIZER_COLORS } from '../../TextMarker'

export const MarkdownRenderer: React.FC<RendererProps> = ({
  content,
  markers = [],
  markerConfig,
  onMarkerClick
}) => {
  if (markers.length === 0) {
    return (
      <div className="markdown-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
    )
  }
  
  return (
    <div className="markdown-content markdown-with-markers">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => {
            const text = extractText(children)
            const relevantMarkers = markers.filter(m => text.includes(m.matchText))
            
            if (relevantMarkers.length === 0) {
              return <p>{children}</p>
            }
            
            return (
              <p>
                <TextMarker
                  content={text}
                  markers={relevantMarkers}
                  config={{
                    style: 'rectangle',
                    tagColors: CV_OPTIMIZER_COLORS,
                    icon: { icon: 'ⓘ', position: 'after' },
                    onClick: onMarkerClick,
                    ...markerConfig
                  }}
                />
              </p>
            )
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

function extractText(children: React.ReactNode): string {
  if (typeof children === 'string') return children
  if (Array.isArray(children)) {
    return children.map(child => extractText(child)).join('')
  }
  if (React.isValidElement(children)) {
    const props = children.props as { children?: React.ReactNode }
    if (props.children) {
      return extractText(props.children)
    }
  }
  return String(children || '')
}

export default MarkdownRenderer
