// ===========================================
// COMMON REUSABLE COMPONENTS
// ===========================================
//
// This file exports all reusable components.
// Import from here instead of individual files.
//
// Usage: import { StandardToolbar, VideoModal, ServiceCard } from '../components/common'
//
// RULES:
// 1. ALWAYS use components from this folder when available
// 2. NEVER duplicate component code in individual pages
// 3. If changes needed, modify the component here - updates everywhere automatically
//
// ===========================================

export { StandardToolbar } from './StandardToolbar';
export { VideoModal } from './VideoModal';
export { ServiceCard } from './ServiceCard';
export { SectionSeparator } from './SectionSeparator';
export { SecondaryNav } from './SecondaryNav';
export { Footer } from './Footer';
export { GoogleSignInButton } from './GoogleSignInButton';
export { OrDivider } from './OrDivider';
export { GHAScanner, playStartSound, playCompleteSound, playErrorSound, STATUS_MESSAGES, SCANNER_STYLES, SCANNER_COLORS } from './GHAScanner';
export { UserSessionKeep, useServiceSession, SERVICE_CONFIGS } from './UserSessionKeep';
export type { ServiceSessionData, ServiceConfig } from './UserSessionKeep';
export { TextMarker, CV_OPTIMIZER_COLORS, NOTION_COLORS } from './TextMarker';
export type { MarkerItem, TagColorMap, MarkerStyle, MarkerIcon, MarkerConfig, TextMarkerProps } from './TextMarker';
export { TipBox, TIPBOX_COLORS } from './TipBox';
export type { TipBoxProps, TipBoxButton, TipBoxColor, SectionType } from './TipBox';
