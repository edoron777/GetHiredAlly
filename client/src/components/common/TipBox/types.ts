import React from 'react'

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
    primary: '#990033',
    light: '#fff0f5',
    text: '#ffffff'
  },
  important: {
    primary: '#990099',
    light: '#fdf0fd',
    text: '#ffffff'
  },
  consider: {
    primary: '#008080',
    light: '#f0ffff',
    text: '#ffffff'
  },
  polish: {
    primary: '#1E5A85',
    light: '#f0f7ff',
    text: '#ffffff'
  },
  info: {
    primary: '#337ea9',
    light: '#eff6ff',
    text: '#ffffff'
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
}
