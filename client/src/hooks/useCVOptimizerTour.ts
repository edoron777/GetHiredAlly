import { driver } from "driver.js";
import "driver.js/dist/driver.css";

export const useCVOptimizerTour = () => {
  
  const startUploadTour = () => {
    const driverObj = driver({
      showProgress: true,
      animate: true,
      smoothScroll: true,
      stagePadding: 10,
      popoverClass: 'cv-tour-popover',
      steps: [
        {
          element: '[data-tour="upload-area"]',
          popover: {
            title: 'Step 1: Upload Your CV',
            description: 'Drag and drop your CV file here, or click "Browse Files" to select from your computer. Supports PDF, DOCX, DOC, and TXT files.',
            side: 'bottom' as const,
            align: 'center' as const
          }
        },
        {
          element: '[data-tour="scan-button"]',
          popover: {
            title: 'Step 2: Start Analysis',
            description: 'Click this button to start the AI-powered analysis. It takes just a few seconds to scan your CV for issues.',
            side: 'top' as const,
            align: 'center' as const
          }
        }
      ],
      onDestroyStarted: () => {
        driverObj.destroy();
      }
    });
    
    driverObj.drive();
  };

  const startResultsTour = () => {
    const driverObj = driver({
      showProgress: true,
      animate: true,
      smoothScroll: true,
      stagePadding: 10,
      popoverClass: 'cv-tour-popover',
      steps: [
        {
          element: '[data-tour="cv-score"]',
          popover: {
            title: 'Your CV Score',
            description: 'This is your overall CV score out of 100. Below you can see the breakdown by severity: Critical (red), Important (orange), and Consider (blue).',
            side: 'right' as const,
            align: 'start' as const
          }
        },
        {
          element: '[data-tour="issues-summary"]',
          popover: {
            title: 'Found Issues',
            description: 'Here you can see how many issues were found, split between document-specific issues and general improvements.',
            side: 'right' as const,
            align: 'start' as const
          }
        },
        {
          element: '[data-tour="view-toggle"]',
          popover: {
            title: 'View Options',
            description: 'Switch between Document View (see your CV with highlights), List View (see all issues in a list), or Side by Side comparison.',
            side: 'bottom' as const,
            align: 'start' as const
          }
        },
        {
          element: '[data-tour="auto-fix-button"]',
          popover: {
            title: 'Quick Auto-Fix',
            description: 'Click here to automatically fix issues that can be corrected by AI. This is the fastest way to improve your CV!',
            side: 'bottom' as const,
            align: 'center' as const
          }
        },
        {
          element: '[data-tour="document-view"]',
          popover: {
            title: 'Your CV Document',
            description: 'Colored highlights show where issues are in your CV. Click on any highlight to see details and fix suggestions.',
            side: 'left' as const,
            align: 'start' as const
          }
        },
        {
          element: '[data-tour="export-buttons"]',
          popover: {
            title: 'Export Your CV',
            description: 'Once you\'re happy with the fixes, export your optimized CV as PDF, Word, or Markdown.',
            side: 'bottom' as const,
            align: 'end' as const
          }
        }
      ],
      onDestroyStarted: () => {
        driverObj.destroy();
      }
    });
    
    driverObj.drive();
  };

  return { startUploadTour, startResultsTour };
};
