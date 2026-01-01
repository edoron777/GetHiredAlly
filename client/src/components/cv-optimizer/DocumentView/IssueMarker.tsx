interface IssueMarkerProps {
  severity: 'critical' | 'important' | 'consider' | 'polish';
  children: React.ReactNode;
  issueId: string;
  onClick?: (issueId: string) => void;
}

export default function IssueMarker({ severity, children, issueId, onClick }: IssueMarkerProps) {
  return (
    <span 
      className={`issue-marker ${severity}`}
      data-issue-id={issueId}
      onClick={() => onClick?.(issueId)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.(issueId)}
    >
      {children}
    </span>
  );
}
