import React, { useState, useEffect } from 'react'
import mammoth from 'mammoth'
import DOMPurify from 'dompurify'
import type { RendererProps } from '../types'
import { TextRenderer } from './TextRenderer'

export const WordRenderer: React.FC<RendererProps> = ({
  content,
  originalFileUrl,
  markers = [],
  markerConfig,
  onMarkerClick
}) => {
  const [html, setHtml] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    if (!originalFileUrl) {
      return
    }
    
    const loadDocument = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const response = await fetch(originalFileUrl)
        if (!response.ok) throw new Error('Failed to fetch document')
        
        const arrayBuffer = await response.arrayBuffer()
        const result = await mammoth.convertToHtml({ arrayBuffer })
        
        const safeHtml = DOMPurify.sanitize(result.value, {
          ALLOWED_TAGS: ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                         'strong', 'em', 'u', 'ul', 'ol', 'li', 
                         'a', 'br', 'table', 'tr', 'td', 'th'],
          ALLOWED_ATTR: ['href', 'target']
        })
        
        setHtml(safeHtml)
      } catch (err) {
        console.error('Error loading Word document:', err)
        setError('Could not load formatted document')
      } finally {
        setLoading(false)
      }
    }
    
    loadDocument()
  }, [originalFileUrl])
  
  if (loading) {
    return (
      <div className="word-content word-loading">
        <div className="loading-spinner">Loading formatted document...</div>
      </div>
    )
  }
  
  if (error || !html) {
    return (
      <TextRenderer
        content={content}
        markers={markers}
        markerConfig={markerConfig}
        onMarkerClick={onMarkerClick}
      />
    )
  }
  
  return (
    <div 
      className="word-content"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

export default WordRenderer
