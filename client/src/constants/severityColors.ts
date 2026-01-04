/**
 * CV Optimizer Severity Color Convention
 * 
 * SINGLE SOURCE OF TRUTH for severity colors.
 * All components MUST import colors from this file.
 * DO NOT define severity colors anywhere else.
 */

export const SEVERITY_COLORS = {
  critical: {
    primary: '#990033',
    background: 'rgba(153, 0, 51, 0.1)',
    text: '#990033',
    label: 'Critical',
  },
  important: {
    primary: '#990099',
    background: 'rgba(153, 0, 153, 0.1)',
    text: '#990099',
    label: 'Important',
  },
  consider: {
    primary: '#1E5A85',
    background: 'rgba(30, 90, 133, 0.1)',
    text: '#1E5A85',
    label: 'Consider',
  },
  polish: {
    primary: '#008080',
    background: 'rgba(0, 128, 128, 0.1)',
    text: '#008080',
    label: 'Polish',
  },
} as const;

export const SEVERITY_ORDER = ['critical', 'important', 'consider', 'polish'] as const;

export type SeverityLevel = keyof typeof SEVERITY_COLORS;

export function getSeverityColor(severity: SeverityLevel): string {
  return SEVERITY_COLORS[severity]?.primary || '#6B7280';
}

export function getSeverityBackground(severity: SeverityLevel): string {
  return SEVERITY_COLORS[severity]?.background || 'rgba(107, 114, 128, 0.1)';
}
