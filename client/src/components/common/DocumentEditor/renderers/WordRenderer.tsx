import React from 'react'
import type { RendererProps } from '../types'
import { TextRenderer } from './TextRenderer'

export const WordRenderer: React.FC<RendererProps> = (props) => {
  return <TextRenderer {...props} />
}

export default WordRenderer
