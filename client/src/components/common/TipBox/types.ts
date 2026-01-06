import React from 'react'
import { SEVERITY_COLORS } from '@/constants/severityColors'

export type SectionType = 
  | 'header'
  | 'text'
  | 'category'
  | 'example-wrong'
  | 'example-correct'
  | 'input'
  | 'instructions'
  | 'custom'
  | 'warning'
  | 'requirements'

export type TipBoxMode = 'issue' | 'guide' | 'info'

export type SectionStatus = 'found' | 'missing' | 'optional'

export interface RequirementItem {
  text: string
  priority: 'mandatory' | 'recommended' | 'optional'
}

export interface TipBoxSection {
  type: SectionType
  label?: string
  content?: string
  placeholder?: string
  defaultValue?: string
  component?: React.ReactNode
  id?: string
  requirements?: RequirementItem[]
}

export interface TipBoxButton {
  id: string
  label: string
  variant: 'primary' | 'secondary' | 'danger' | 'success'
  onClick: () => void
  disabled?: boolean
  icon?: React.ReactNode
}

export interface TipBoxColor {
  primary: string
  light: string
  text: string
}

export const TIPBOX_COLORS: Record<string, TipBoxColor> = {
  critical: {
    primary: SEVERITY_COLORS.critical.primary,
    light: SEVERITY_COLORS.critical.background,
    text: '#ffffff'
  },
  important: {
    primary: SEVERITY_COLORS.important.primary,
    light: SEVERITY_COLORS.important.background,
    text: '#ffffff'
  },
  consider: {
    primary: SEVERITY_COLORS.consider.primary,
    light: SEVERITY_COLORS.consider.background,
    text: '#ffffff'
  },
  polish: {
    primary: SEVERITY_COLORS.polish.primary,
    light: SEVERITY_COLORS.polish.background,
    text: '#ffffff'
  },
  info: {
    primary: '#337ea9',
    light: '#eff6ff',
    text: '#ffffff'
  }
}

export const GUIDE_MODE_COLORS: Record<SectionStatus, { accent: string; background: string }> = {
  found: {
    accent: '#22C55E',
    background: '#F0FDF4'
  },
  missing: {
    accent: '#EAB308',
    background: '#FEFCE8'
  },
  optional: {
    accent: '#6366F1',
    background: '#EEF2FF'
  }
}

export type ImpactType = 
  | 'ats_high'
  | 'ats_medium'
  | 'human_high'
  | 'human_medium'
  | 'human_low'
  | 'best_practice'

export interface ImpactDisplayConfig {
  icon: string
  label: string
  bgColor: string
  textColor: string
  borderColor: string
}

export const IMPACT_DISPLAY: Record<ImpactType, ImpactDisplayConfig> = {
  ats_high: { 
    icon: '🤖', 
    label: 'ATS Critical', 
    bgColor: '#FEE2E2', 
    textColor: '#991B1B',
    borderColor: '#FECACA'
  },
  ats_medium: { 
    icon: '🤖', 
    label: 'ATS Impact', 
    bgColor: '#FFEDD5', 
    textColor: '#9A3412',
    borderColor: '#FED7AA'
  },
  human_high: { 
    icon: '👤', 
    label: 'Human Critical', 
    bgColor: '#FEE2E2', 
    textColor: '#991B1B',
    borderColor: '#FECACA'
  },
  human_medium: { 
    icon: '👤', 
    label: 'Human Impact', 
    bgColor: '#FEF3C7', 
    textColor: '#92400E',
    borderColor: '#FDE68A'
  },
  human_low: { 
    icon: '👤', 
    label: 'Minor Impact', 
    bgColor: '#F3F4F6', 
    textColor: '#4B5563',
    borderColor: '#E5E7EB'
  },
  best_practice: { 
    icon: '📋', 
    label: 'Best Practice', 
    bgColor: '#DBEAFE', 
    textColor: '#1E40AF',
    borderColor: '#BFDBFE'
  }
}

export interface TipBoxProps {
  isOpen: boolean
  onClose: () => void
  title: string
  category?: string
  severity?: 'critical' | 'important' | 'consider' | 'polish' | 'info'
  color?: TipBoxColor
  sections: TipBoxSection[]
  buttons?: TipBoxButton[]
  onInputChange?: (id: string, value: string) => void
  width?: string
  className?: string
  bulkAutoFixUsed?: boolean
  isAutoFixable?: boolean
  isPending?: boolean
  isFixed?: boolean
  mode?: TipBoxMode
  sectionStatus?: SectionStatus
  sectionKey?: string
  impactTypes?: string[]
}
