import { SEVERITY_COLORS } from '@/constants/severityColors';

interface ScoreWidgetProps {
  score: number;
  originalScore?: number;
  issuesCounts: {
    critical: number;
    important: number;
    consider: number;
    polish: number;
  };
}

function getScoreColor(score: number): string {
  if (score < 50) return '#dc2626';
  if (score <= 70) return '#ca8a04';
  return '#16a34a';
}

export default function ScoreWidget({ score, originalScore, issuesCounts }: ScoreWidgetProps) {
  const scoreColor = getScoreColor(score);
  const scoreImprovement = originalScore && score > originalScore ? score - originalScore : 0;

  return (
    <div className="score-widget">
      <div 
        className="score-circle"
        style={{ borderColor: scoreColor }}
      >
        <span className="score-number" style={{ color: scoreColor }}>
          {score}
        </span>
        <span className="score-label">CV Score</span>
        {scoreImprovement > 0 && (
          <span className="score-improvement">+{scoreImprovement}</span>
        )}
      </div>

      <div className="issue-counts">
        <div className="issue-count-item">
          <span style={{ color: SEVERITY_COLORS.critical.primary }}>●</span>
          <span>{issuesCounts.critical}</span>
        </div>
        <div className="issue-count-item">
          <span style={{ color: SEVERITY_COLORS.important.primary }}>●</span>
          <span>{issuesCounts.important}</span>
        </div>
        <div className="issue-count-item">
          <span style={{ color: SEVERITY_COLORS.consider.primary }}>●</span>
          <span>{issuesCounts.consider}</span>
        </div>
        <div className="issue-count-item">
          <span style={{ color: SEVERITY_COLORS.polish.primary }}>●</span>
          <span>{issuesCounts.polish}</span>
        </div>
      </div>
    </div>
  );
}
