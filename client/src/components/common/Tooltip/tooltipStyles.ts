/**
 * Style Constants for GHATooltip
 * Defines variants, colors, and styling
 */

// Tooltip Variants
export const TOOLTIP_VARIANTS = {
  default: {
    background: '#E8F4FD',
    border: '#1E5A85',
    iconColor: '#1E5A85',
  },
  warning: {
    background: '#FEF3C7',
    border: '#D97706',
    iconColor: '#D97706',
  },
  info: {
    background: '#F0F9FF',
    border: '#0284C7',
    iconColor: '#0284C7',
  },
} as const;

// Typography
export const TOOLTIP_TYPOGRAPHY = {
  title: {
    size: '14px',
    weight: 600,
    color: '#1E3A5F',
  },
  text: {
    size: '13px',
    weight: 400,
    color: '#374151',
  },
  link: {
    size: '12px',
    weight: 500,
    color: '#3b82f6',
  },
};

// Layout
export const TOOLTIP_LAYOUT = {
  maxWidth: '280px',
  padding: '12px 16px',
  borderRadius: '6px',
  borderWidth: '1px',
  shadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
};

// Timing
export const TOOLTIP_TIMING = {
  delayDuration: 300,
  skipDelayDuration: 0,
  animationDuration: 150,
};

// Combined export
export const TOOLTIP_STYLES = {
  variants: TOOLTIP_VARIANTS,
  typography: TOOLTIP_TYPOGRAPHY,
  layout: TOOLTIP_LAYOUT,
  timing: TOOLTIP_TIMING,
};

export type TooltipVariant = keyof typeof TOOLTIP_VARIANTS;
