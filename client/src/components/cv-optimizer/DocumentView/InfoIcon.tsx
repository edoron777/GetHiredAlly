interface InfoIconProps {
  severity: 'critical' | 'important' | 'consider' | 'polish';
  issueId: string;
  onClick: (issueId: string) => void;
}

export default function InfoIcon({ severity, issueId, onClick }: InfoIconProps) {
  return (
    <span 
      className={`info-icon ${severity}`}
      onClick={(e) => {
        e.stopPropagation();
        onClick(issueId);
      }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick(issueId)}
      title="Click for tips"
    >
      i
    </span>
  );
}
