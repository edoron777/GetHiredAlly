import React from 'react'
import type { TipBoxSection as SectionType, TipBoxColor } from './types'

interface Props {
  section: SectionType
  color: TipBoxColor
  onInputChange?: (id: string, value: string) => void
}

export const TipBoxSection: React.FC<Props> = ({ 
  section, 
  color,
  onInputChange 
}) => {
  const { type, label, content, placeholder, defaultValue, component, id } = section

  const renderLabel = () => {
    if (!label) return null
    return <div className="tipbox-section-label">{label}</div>
  }

  switch (type) {
    case 'text':
      return (
        <div className="tipbox-section tipbox-section-text">
          {renderLabel()}
          <p className="tipbox-text">{content}</p>
        </div>
      )

    case 'category':
      return (
        <div className="tipbox-section tipbox-section-category">
          {renderLabel()}
          <span 
            className="tipbox-category-badge"
            style={{ backgroundColor: color.light, color: color.primary }}
          >
            {content}
          </span>
        </div>
      )

    case 'example-wrong':
      return (
        <div className="tipbox-section tipbox-section-example">
          {renderLabel()}
          <div className="tipbox-example tipbox-example-wrong">
            <span className="tipbox-example-icon">✗</span>
            <span className="tipbox-example-text">{content}</span>
          </div>
        </div>
      )

    case 'example-correct':
      return (
        <div className="tipbox-section tipbox-section-example">
          {renderLabel()}
          <div className="tipbox-example tipbox-example-correct">
            <span className="tipbox-example-icon">✓</span>
            <span className="tipbox-example-text">{content}</span>
          </div>
        </div>
      )

    case 'input':
      return (
        <div className="tipbox-section tipbox-section-input">
          {renderLabel()}
          <textarea
            className="tipbox-input"
            placeholder={placeholder}
            defaultValue={defaultValue}
            onChange={(e) => onInputChange?.(id || 'default', e.target.value)}
            rows={3}
          />
        </div>
      )

    case 'instructions':
      return (
        <div className="tipbox-section tipbox-section-instructions">
          {renderLabel()}
          <div className="tipbox-instructions">{content}</div>
        </div>
      )

    case 'custom':
      return (
        <div className="tipbox-section tipbox-section-custom">
          {renderLabel()}
          {component}
        </div>
      )

    case 'warning':
      return (
        <div className="tipbox-section tipbox-section-warning">
          {renderLabel()}
          <div className="tipbox-warning-box">
            <span className="tipbox-warning-icon">⚠</span>
            <span className="tipbox-warning-text">{content}</span>
          </div>
        </div>
      )

    default:
      return null
  }
}

export default TipBoxSection
