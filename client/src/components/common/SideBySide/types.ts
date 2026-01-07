/**
 * SideBySide Component Types
 * Reusable side-by-side comparison component for GetHiredAlly
 */

export interface MarkerConfig {
  id: string;
  text: string;
  severity?: 'critical' | 'important' | 'consider' | 'polish';
  type?: 'issue' | 'fix' | 'change';
  tooltip?: string;
}

export interface ChangeConfig {
  originalText: string;
  newText: string;
  issueId?: string;
  category?: string;
  explanation?: string;
}

export interface PanelStats {
  label: string;
  value: string | number;
  color?: 'red' | 'green' | 'amber' | 'blue' | 'neutral';
}

export interface SideBySidePanelConfig {
  /** Panel title (e.g., "Original CV", "Fixed CV") */
  title: string;
  
  /** Content to display */
  content: string;
  
  /** Panel type - controls color scheme */
  type: 'original' | 'fixed' | 'neutral';
  
  /** Markers for TextMarker highlighting (optional) */
  markers?: MarkerConfig[];
  
  /** Changes to highlight (optional) */
  changes?: ChangeConfig[];
  
  /** Stats to display in header (optional) */
  stats?: PanelStats;
  
  /** Custom className for panel (optional) */
  className?: string;
}

export interface SideBySideProps {
  /** Left panel configuration */
  left: SideBySidePanelConfig;
  
  /** Right panel configuration */
  right: SideBySidePanelConfig;
  
  /** Enable synchronized scrolling between panels (default: true) */
  syncScroll?: boolean;
  
  /** Maximum height of the component (default: '600px') */
  maxHeight?: string;
  
  /** Callback when a marker is clicked */
  onMarkerClick?: (id: string, panel: 'left' | 'right') => void;
  
  /** Custom className for container */
  className?: string;
}
