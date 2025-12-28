import { Link, useLocation } from 'react-router-dom';

interface NavItem {
  id: string;
  label: string;
  shortLabel: string;
  route: string;
  isComingSoon: boolean;
}

const NAV_ITEMS: NavItem[] = [
  {
    id: 'cv-optimizer',
    label: 'Perfect Your CV',
    shortLabel: 'Perfect CV',
    route: '/service/cv-optimizer',
    isComingSoon: false
  },
  {
    id: 'ats-optimizer',
    label: 'Tailor for This Job',
    shortLabel: 'Tailor',
    route: '/service/ats-optimizer',
    isComingSoon: true
  },
  {
    id: 'xray-analyzer',
    label: 'Decode the Job Post',
    shortLabel: 'Decode',
    route: '/service/understand-job',
    isComingSoon: false
  },
  {
    id: 'interview-questions',
    label: 'Predict the Questions',
    shortLabel: 'Predict',
    route: '/service/predict-questions',
    isComingSoon: false
  },
  {
    id: 'answer-builder',
    label: 'Craft Your Answers',
    shortLabel: 'Craft',
    route: '/service/answer-builder',
    isComingSoon: true
  }
];

export function SecondaryNav() {
  const location = useLocation();
  
  const isActive = (route: string) => {
    return location.pathname.startsWith(route);
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky z-40" style={{ top: '64px' }}>
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex items-center justify-center gap-2 px-4 py-2 min-w-max">
          {NAV_ITEMS.map((item) => (
            item.isComingSoon ? (
              <span
                key={item.id}
                className="px-4 py-2 text-sm text-gray-400 cursor-not-allowed whitespace-nowrap"
                title="Coming Soon"
              >
                <span className="hidden sm:inline">{item.label}</span>
                <span className="sm:hidden">{item.shortLabel}</span>
              </span>
            ) : (
              <Link
                key={item.id}
                to={item.route}
                className={`
                  px-4 py-2 text-sm font-medium rounded-full whitespace-nowrap transition-all
                  ${isActive(item.route)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <span className="hidden sm:inline">{item.label}</span>
                <span className="sm:hidden">{item.shortLabel}</span>
              </Link>
            )
          ))}
        </div>
      </div>
    </nav>
  );
}
