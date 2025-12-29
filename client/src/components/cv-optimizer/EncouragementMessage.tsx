interface EncouragementMessageProps {
  type: 'intro' | 'effort' | 'completion' | 'filter';
  quickWinsCount?: number;
  filterType?: string;
  count?: number;
}

export default function EncouragementMessage({ 
  type, 
  quickWinsCount = 0,
  filterType = 'all',
  count = 0
}: EncouragementMessageProps) {
  const getFilterMessage = () => {
    switch (filterType) {
      case 'critical':
        return {
          icon: '⚡',
          title: 'Quick Wins',
          message: count > 0 
            ? `Start with ${count} quick fix${count !== 1 ? 'es' : ''} below - they take just minutes and have big impact!`
            : 'No quick wins found in current view.'
        }
      case 'high':
        return {
          icon: '🎯',
          title: 'Important Improvements',
          message: count > 0
            ? `${count} important improvement${count !== 1 ? 's' : ''} that will significantly strengthen your CV`
            : 'No important improvements found in current view.'
        }
      case 'medium':
        return {
          icon: '💡',
          title: 'Worth Considering',
          message: count > 0
            ? `${count} suggestion${count !== 1 ? 's' : ''} worth considering to make your CV stand out`
            : 'No suggestions found in current view.'
        }
      case 'low':
        return {
          icon: '✨',
          title: 'Polish Items',
          message: count > 0
            ? `${count} minor polish item${count !== 1 ? 's' : ''} for that extra professional touch`
            : 'No polish items found in current view.'
        }
      default:
        return {
          icon: '📋',
          title: 'All Suggestions',
          message: `You have ${count} total suggestion${count !== 1 ? 's' : ''} to review`
        }
    }
  }

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
    },
    filter: getFilterMessage()
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
