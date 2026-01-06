import React from 'react'
import type { TipBoxProps, TipBoxColor, ImpactType } from './types'
import { TIPBOX_COLORS, GUIDE_MODE_COLORS, IMPACT_DISPLAY } from './types'
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
  isFixed = false,
  mode = 'issue',
  sectionStatus,
  sectionKey,
  impactTypes = []
}) => {
  const getColorScheme = (): TipBoxColor => {
    if (mode === 'guide' && sectionStatus) {
      const guideColors = GUIDE_MODE_COLORS[sectionStatus]
      return {
        primary: guideColors.accent,
        light: guideColors.background,
        text: '#ffffff'
      }
    }
    return color || TIPBOX_COLORS[severity]
  }

  const colorScheme: TipBoxColor = getColorScheme()

  const renderImpactBadges = () => {
    if (!impactTypes || impactTypes.length === 0) return null
    
    return (
      <div className="tipbox-impact-badges">
        {impactTypes.map((type) => {
          const config = IMPACT_DISPLAY[type as ImpactType]
          if (!config) return null
          return (
            <span 
              key={type}
              className="tipbox-impact-badge"
              style={{ 
                backgroundColor: config.bgColor, 
                color: config.textColor,
                borderColor: config.borderColor
              }}
            >
              {config.icon} {config.label}
            </span>
          )
        })}
      </div>
    )
  }

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

  const renderHeader = () => {
    if (mode === 'guide') {
      return (
        <div className="tipbox-header tipbox-header--guide" style={{ backgroundColor: colorScheme.primary }}>
          <div className="tipbox-header-content">
            <div className="tipbox-header__title-row">
              <span className="tipbox-header__icon">💡</span>
              <h3 className="tipbox-title" style={{ color: colorScheme.text }}>
                {title}
              </h3>
            </div>
            {sectionStatus && (
              <span className={`tipbox-status-badge tipbox-status-badge--${sectionStatus}`}>
                {sectionStatus === 'found' && '✅ Found in your CV'}
                {sectionStatus === 'missing' && '⚠️ Missing from your CV'}
                {sectionStatus === 'optional' && 'ℹ️ Optional Section'}
              </span>
            )}
          </div>
          <button className="tipbox-close-btn" onClick={onClose} style={{ color: colorScheme.text }}>
            ✕
          </button>
        </div>
      )
    }

    return (
      <div className="tipbox-header" style={{ backgroundColor: colorScheme.primary }}>
        <div className="tipbox-header-content">
          <div className="tipbox-header-title-row">
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
          {renderImpactBadges()}
        </div>
        <button className="tipbox-close-btn" onClick={onClose} style={{ color: colorScheme.text }}>
          ✕
        </button>
      </div>
    )
  }

  const renderFooter = () => {
    if (mode === 'guide') {
      return (
        <div className="tipbox-footer tipbox-footer--guide">
          <button 
            className="tipbox-btn tipbox-btn-primary"
            style={{ backgroundColor: colorScheme.primary, color: colorScheme.text }}
            onClick={onClose}
          >
            Got It
          </button>
        </div>
      )
    }

    if (filteredButtons.length === 0) return null

    return (
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
    )
  }

  return (
    <div className="tipbox-overlay" onClick={onClose}>
      <div 
        className={`tipbox-modal ${mode === 'guide' ? 'tipbox-modal--guide' : ''} ${className}`}
        style={{ width }}
        onClick={(e) => e.stopPropagation()}
      >
        {renderHeader()}

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

        {mode !== 'guide' && !showAutoFixButton && !isFixed && !isPending && isAutoFixable && (
          <p className="tipbox-info">
            ℹ️ This issue requires your personal input
          </p>
        )}

        {renderFooter()}
      </div>
    </div>
  )
}

export default TipBox
