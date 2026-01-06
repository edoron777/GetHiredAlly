import React from 'react'

const URL_PATTERN = /(\b(?:https?:\/\/)?(?:www\.)?(?:linkedin\.com\/in\/[\w-]+|github\.com\/[\w-]+|[\w-]+\.(?:com|org|net|io|dev|co|me|info)(?:\/[\w\-._~:/?#[\]@!$&'()*+,;=%]*)?))/gi

export function linkifyText(text: string): React.ReactNode[] {
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
        key={`link-${match.index}`}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 hover:underline"
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

export function linkifyContent(content: string): React.ReactNode {
  const lines = content.split('\n')
  
  return lines.map((line, index) => (
    <React.Fragment key={index}>
      {linkifyText(line)}
      {index < lines.length - 1 && '\n'}
    </React.Fragment>
  ))
}
