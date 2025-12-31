import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import IssuesSummaryBox from '../components/cv-optimizer/IssuesSummaryBox';
import PathCard from '../components/cv-optimizer/PathCard';
import { getAuthToken } from '../lib/auth';

interface ReportData {
  score: number;
  totalIssues: number;
  breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  estimatedMinutes: number;
}

const CVCrossroadsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        setLoading(true);
        const token = getAuthToken();
        const response = await fetch(`/api/cv-optimizer/report/${id}/summary?token=${token}`);
        if (!response.ok) {
          throw new Error('Failed to fetch report data');
        }
        const data = await response.json();
        
        // Calculate estimated time: quick=2min, medium=5min, extensive=10min
        const estimatedMinutes = 
          (data.breakdown?.critical || 0) * 10 +
          (data.breakdown?.high || 0) * 5 +
          (data.breakdown?.medium || 0) * 3 +
          (data.breakdown?.low || 0) * 2;
        
        setReportData({
          score: data.score || 0,
          totalIssues: data.total_issues || 0,
          breakdown: {
            critical: data.breakdown?.critical || 0,
            high: data.breakdown?.high || 0,
            medium: data.breakdown?.medium || 0,
            low: data.breakdown?.low || 0,
          },
          estimatedMinutes: estimatedMinutes || 60,
        });
      } catch (err) {
        setError('Failed to load report data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchReportData();
    }
  }, [id]);

  const handleBluePill = () => {
    // Navigate to fix process
    navigate(`/service/cv-optimizer/fix/${id}`);
  };

  const handleRedPill = () => {
    // Navigate to detailed issues view
    navigate(`/service/cv-optimizer/report/${id}/details`);
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  // Score color based on value
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreRingColor = (score: number) => {
    if (score >= 70) return 'border-green-500';
    if (score >= 50) return 'border-yellow-500';
    return 'border-red-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your results...</p>
        </div>
      </div>
    );
  }

  if (error || !reportData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600">{error || 'Something went wrong'}</p>
          <button 
            onClick={handleBackToDashboard}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={handleBackToDashboard}
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <span className="mr-2">←</span> Back to Dashboard
        </button>

        {/* Score Section */}
        <div className="bg-white rounded-xl shadow-sm p-8 mb-6">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
            📊 Your CV Score
          </h2>
          
          <div className="flex justify-center mb-4">
            <div className={`w-32 h-32 rounded-full border-8 ${getScoreRingColor(reportData.score)} flex items-center justify-center bg-white`}>
              <span className={`text-4xl font-bold ${getScoreColor(reportData.score)}`}>
                {reportData.score}%
              </span>
            </div>
          </div>
          
          <p className="text-center text-gray-600">
            {reportData.score >= 70 
              ? 'Good foundation! Some improvements will help you stand out.'
              : reportData.score >= 50
              ? 'Your CV needs improvement to compete effectively.'
              : 'Significant improvements needed to attract recruiters.'}
          </p>
        </div>

        {/* Issues Summary */}
        <IssuesSummaryBox
          totalIssues={reportData.totalIssues}
          breakdown={reportData.breakdown}
          estimatedMinutes={reportData.estimatedMinutes}
        />

        {/* Choose Your Path */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Choose Your Path</h2>
          <p className="text-gray-600 mt-2">How would you like to improve your CV?</p>
        </div>

        {/* Path Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <PathCard
            variant="blue"
            title="The Easy Way"
            description="Fix all"
            issueCount={reportData.totalIssues}
            features={[
              '⚡ Done in ~30 seconds',
              '🤖 AI does the work',
              '🎯 ~85% auto-fixed',
              '📥 Download improved CV'
            ]}
            buttonText="🚀 Fix My CV Now"
            onClick={handleBluePill}
            badge="✨ Most users choose this option"
          />
          
          <PathCard
            variant="red"
            title="The Deep Dive"
            description="Review all"
            issueCount={reportData.totalIssues}
            features={[
              `⏱️ ~${Math.floor(reportData.estimatedMinutes / 60)}h ${reportData.estimatedMinutes % 60}m manual work`,
              '✋ You\'re in full control',
              '🎯 Fix what you choose',
              '📚 Learn as you go'
            ]}
            buttonText="🔍 View All Issues"
            onClick={handleRedPill}
            badge="For those who want full control"
          />
        </div>

        {/* Tip */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <p className="text-blue-800">
            💡 <strong>Tip:</strong> You can always switch paths. Start with auto-fix, 
            then review any remaining issues that need your input.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CVCrossroadsPage;
