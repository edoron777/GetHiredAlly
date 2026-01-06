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
}
