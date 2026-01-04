import React from 'react'
import type { TipBoxProps, TipBoxColor } from './types'
import { TIPBOX_COLORS } from './types'
import { TipBoxSection } from './TipBoxSection'
import './TipBoxStyles.css'

export const TipBox: React.FC<TipBoxProps> = ({
  isOpen,
  onClose,
  title,
  category,
  severity = 'info',
  color,
  sections,
  buttons = [],
  onInputChange,
  width = '500px',
  className = '',
  bulkAutoFixUsed = false,
  isAutoFixable = false,
  isPending = false,
  isFixed = false
}) => {
  const colorScheme: TipBoxColor = color || TIPBOX_COLORS[severity]

  if (!isOpen) return null

  const showAutoFixButton = 
    isAutoFixable && 
    !bulkAutoFixUsed && 
    !isFixed &&
    !isPending

  const filteredButtons = buttons.filter(button => {
    if (button.id === 'auto-fix') {
      return showAutoFixButton
    }
    return true
  })

  const getButtonStyle = (variant: string) => {
    switch (variant) {
      case 'primary':
        return { backgroundColor: colorScheme.primary, color: colorScheme.text }
      case 'success':
        return { backgroundColor: '#448361', color: '#ffffff' }
      case 'danger':
        return { backgroundColor: '#e03e3e', color: '#ffffff' }
      case 'secondary':
      default:
        return { backgroundColor: '#f3f4f6', color: '#374151' }
    }
  }

  return (
    <div className="tipbox-overlay" onClick={onClose}>
      <div 
        className={`tipbox-modal ${className}`}
        style={{ width }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="tipbox-header" style={{ backgroundColor: colorScheme.primary }}>
          <div className="tipbox-header-content">
            <h3 className="tipbox-title" style={{ color: colorScheme.text }}>
              {title}
            </h3>
            <div className="tipbox-tags">
              <span 
                className="tipbox-severity-badge"
                style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: colorScheme.text }}
              >
                {severity.toUpperCase()}
              </span>
              {category && (
                <span 
                  className="tipbox-category-badge-header"
                  style={{ backgroundColor: 'rgba(255,255,255,0.15)', color: colorScheme.text }}
                >
                  {category}
                </span>
              )}
            </div>
          </div>
          <button className="tipbox-close-btn" onClick={onClose} style={{ color: colorScheme.text }}>
            ✕
          </button>
        </div>

        <div className="tipbox-body">
          {sections.map((section, index) => (
            <TipBoxSection
              key={`section-${index}`}
              section={section}
              color={colorScheme}
              onInputChange={onInputChange}
            />
          ))}
        </div>

        {!showAutoFixButton && !isFixed && !isPending && isAutoFixable && (
          <p className="tipbox-info">
            ℹ️ This issue requires your personal input
          </p>
        )}

        {filteredButtons.length > 0 && (
          <div className="tipbox-footer">
            {filteredButtons.map((button) => (
              <button
                key={button.id}
                className={`tipbox-btn tipbox-btn-${button.variant}`}
                style={getButtonStyle(button.variant)}
                onClick={button.onClick}
                disabled={button.disabled}
              >
                {button.icon && <span className="tipbox-btn-icon">{button.icon}</span>}
                {button.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default TipBox
