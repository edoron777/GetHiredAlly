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
    primary: '#e03e3e',
    light: '#fef2f2',
    text: '#ffffff'
  },
  important: {
    primary: '#d9730d',
    light: '#fff7ed',
    text: '#ffffff'
  },
  consider: {
    primary: '#cb932f',
    light: '#fefce8',
    text: '#ffffff'
  },
  polish: {
    primary: '#448361',
    light: '#f0fdf4',
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
  severity?: 'critical' | 'important' | 'consider' | 'polish' | 'info'
  color?: TipBoxColor
  sections: TipBoxSection[]
  buttons?: TipBoxButton[]
  onInputChange?: (id: string, value: string) => void
  width?: string
  className?: string
}
