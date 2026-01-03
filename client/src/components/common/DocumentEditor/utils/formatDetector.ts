import type { DocumentFormat } from '../types'

export function detectFormat(content: string, filename?: string): DocumentFormat {
  if (filename) {
    const ext = filename.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'md':
      case 'markdown':
        return 'markdown'
      case 'docx':
      case 'doc':
        return 'word'
      case 'pdf':
        return 'pdf'
      case 'txt':
        return 'text'
    }
  }
  
  if (isMarkdownContent(content)) {
    return 'markdown'
  }
  
  return 'text'
}

function isMarkdownContent(content: string): boolean {
  const markdownPatterns = [
    /^#{1,6}\s+.+$/m,
    /\*\*[^*]+\*\*/,
    /\*[^*]+\*/,
    /^\s*[-*+]\s+.+$/m,
    /^\s*\d+\.\s+.+$/m,
    /\[.+\]\(.+\)/,
    /__[^_]+__/,
    /`[^`]+`/,
  ]
  
  let matchCount = 0
  for (const pattern of markdownPatterns) {
    if (pattern.test(content)) {
      matchCount++
    }
  }
  
  if (matchCount >= 1 && /\*\*[^*]+\*\*/.test(content)) {
    return true
  }
  
  return matchCount >= 2
}

export default detectFormat
