import { ExternalLink } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-100 border-t border-gray-200 mt-auto">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-gray-600 text-sm">
            © {currentYear} GetHiredAlly. All rights reserved.
          </div>
          
          <div className="flex items-center gap-6 text-sm">
            <a 
              href="https://gethiredally.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-blue-600 transition-colors flex items-center gap-1"
            >
              Blog
              <ExternalLink size={12} />
            </a>
            
            <a 
              href="mailto:contact@gethiredally.com"
              className="text-gray-600 hover:text-blue-600 transition-colors"
            >
              Contact Us
            </a>
            
            <a 
              href="mailto:bugs@gethiredally.com?subject=Bug Report"
              className="text-gray-600 hover:text-blue-600 transition-colors"
            >
              Report Bug
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
