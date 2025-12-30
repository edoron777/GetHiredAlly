import React, { useState } from 'react';

/**
 * ActionBarButton - Individual button for ActionBar
 * 
 * @param {Object} props
 * @param {string} props.label - Button label text
 * @param {string} props.icon - Icon character or emoji
 * @param {string} props.tooltip - Tooltip text
 * @param {string} props.color - Text/icon color (hex)
 * @param {string} props.hoverBg - Hover background color (hex)
 * @param {Function} props.onClick - Click handler
 * @param {boolean} props.disabled - Disabled state
 * @param {boolean} props.loading - Loading state
 * @param {string} props.successLabel - Label to show on success
 */
const ActionBarButton = ({
  label,
  icon,
  tooltip,
  color = '#6b7280',
  hoverBg = '#f3f4f6',
  onClick,
  disabled = false,
  loading = false,
  successLabel = null,
}) => {
  const [showSuccess, setShowSuccess] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleClick = async (e) => {
    if (disabled || loading) return;
    
    try {
      await onClick?.(e);
      
      // Show success state if successLabel is provided
      if (successLabel) {
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 2000);
      }
    } catch (err) {
      console.error('ActionBarButton error:', err);
    }
  };

  const buttonStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '8px 12px',
    border: 'none',
    borderRadius: '6px',
    background: isHovered && !disabled ? hoverBg : 'transparent',
    color: disabled ? '#9ca3af' : color,
    fontSize: '14px',
    fontWeight: '600',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'background-color 0.2s, opacity 0.2s',
    opacity: disabled || loading ? 0.5 : 1,
    position: 'relative',
    whiteSpace: 'nowrap',
  };

  const tooltipStyle = {
    position: 'absolute',
    bottom: '100%',
    left: '50%',
    transform: 'translateX(-50%)',
    padding: '6px 12px',
    backgroundColor: '#1f2937',
    color: '#ffffff',
    fontSize: '12px',
    borderRadius: '4px',
    whiteSpace: 'nowrap',
    opacity: isHovered && tooltip ? 1 : 0,
    visibility: isHovered && tooltip ? 'visible' : 'hidden',
    transition: 'opacity 0.2s',
    pointerEvents: 'none',
    marginBottom: '8px',
    zIndex: 10,
  };

  const displayLabel = showSuccess && successLabel ? successLabel : label;
  const displayIcon = showSuccess && successLabel ? '✓' : icon;

  return (
    <button
      type="button"
      style={buttonStyle}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      disabled={disabled || loading}
      aria-label={tooltip || label}
      title={tooltip || label}
    >
      {/* Tooltip */}
      {tooltip && (
        <span style={tooltipStyle}>
          {tooltip}
        </span>
      )}
      
      {/* Icon */}
      {displayIcon && (
        <span aria-hidden="true">{displayIcon}</span>
      )}
      
      {/* Label */}
      {displayLabel && (
        <span>{loading ? 'Loading...' : displayLabel}</span>
      )}
    </button>
  );
};

export default ActionBarButton;
