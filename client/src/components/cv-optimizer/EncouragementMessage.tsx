interface EncouragementMessageProps {
  type: 'intro' | 'effort' | 'completion';
  quickWinsCount?: number;
}

export default function EncouragementMessage({ 
  type, 
  quickWinsCount = 0 
}: EncouragementMessageProps) {
  const messages = {
    intro: {
      icon: '🚀',
      title: 'Your Improvement Roadmap',
      message: 'Making these improvements could increase your interview callback rate by up to 40%. Let\'s start with the changes that have the biggest impact.'
    },
    effort: {
      icon: '⚡',
      title: 'Quick Wins Available',
      message: `Start with ${quickWinsCount} quick fixes below - they take just minutes and have big impact!`
    },
    completion: {
      icon: '🎉',
      title: 'Great Job!',
      message: 'You\'ve taken an important step by reviewing your CV. Every improvement increases your chances of landing interviews. You\'ve got this!'
    }
  };

  const { icon, title, message } = messages[type];

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h4 className="font-semibold text-blue-800 mb-1">{title}</h4>
          <p className="text-blue-700 text-sm">{message}</p>
        </div>
      </div>
    </div>
  );
}
