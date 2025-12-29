interface CVScoreCircleProps {
  score: number;
  size?: 'small' | 'medium' | 'large';
  label?: string;
  showMessage?: boolean;
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#22C55E';
  if (score >= 70) return '#EAB308';
  if (score >= 60) return '#EAB308';
  if (score >= 50) return '#F97316';
  return '#EF4444';
}

function getScoreMessage(score: number): string {
  if (score >= 90) return 'Excellent!';
  if (score >= 80) return 'Great CV!';
  if (score >= 70) return 'Good - Minor improvements';
  if (score >= 60) return 'Fair - Room to improve';
  if (score >= 50) return 'Needs work';
  return 'Significant improvements needed';
}

export default function CVScoreCircle({ 
  score, 
  size = 'large', 
  label = 'CV Score',
  showMessage = true
}: CVScoreCircleProps) {
  const sizeConfig = {
    small: { width: 100, stroke: 8, fontSize: 24, labelSize: 12 },
    medium: { width: 140, stroke: 10, fontSize: 32, labelSize: 14 },
    large: { width: 180, stroke: 12, fontSize: 48, labelSize: 16 }
  };

  const config = sizeConfig[size];
  const radius = (config.width - config.stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.max(0, Math.min(100, score));
  const offset = circumference - (progress / 100) * circumference;
  const color = getScoreColor(score);
  const message = getScoreMessage(score);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: config.width, height: config.width }}>
        <svg
          width={config.width}
          height={config.width}
          className="transform -rotate-90"
        >
          <circle
            cx={config.width / 2}
            cy={config.width / 2}
            r={radius}
            fill="none"
            stroke="#E5E7EB"
            strokeWidth={config.stroke}
          />
          <circle
            cx={config.width / 2}
            cy={config.width / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={config.stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 0.5s ease-in-out' }}
          />
        </svg>
        <div 
          className="absolute inset-0 flex items-center justify-center"
          style={{ fontSize: config.fontSize }}
        >
          <span className="font-bold text-gray-900">{score}%</span>
        </div>
      </div>
      <p 
        className="mt-2 font-medium text-gray-700"
        style={{ fontSize: config.labelSize }}
      >
        {label}
      </p>
      {showMessage && (
        <p 
          className="text-sm mt-1"
          style={{ color }}
        >
          {message}
        </p>
      )}
    </div>
  );
}
