import React from 'react';

/**
 * ScoreDashboard - Displays CV score breakdown by category
 * Shows users WHY they received their score
 */

const CATEGORY_CONFIG = {
  content_quality: { label: "Content Quality", max: 40, order: 1 },
  language_clarity: { label: "Language & Clarity", max: 18, order: 2 },
  formatting: { label: "Formatting & Structure", max: 18, order: 3 },
  completeness: { label: "Completeness", max: 12, order: 4 },
  professional: { label: "Professional Presentation", max: 8, order: 5 },
  red_flags: { label: "Red Flag Avoidance", max: 4, order: 6 }
};

const getBarColor = (score, max) => {
  const percentage = (score / max) * 100;
  if (percentage >= 70) return '#22c55e'; // green
  if (percentage >= 40) return '#eab308'; // yellow
  return '#ef4444'; // red
};

const getStatusIcon = (score, max) => {
  const percentage = (score / max) * 100;
  if (percentage >= 70) return '✓';
  if (percentage >= 40) return '⚠️';
  return '✗';
};

export default function ScoreDashboard({ breakdown, totalScore, grade, message }) {
  if (!breakdown) return null;

  // Sort categories by order
  const sortedCategories = Object.entries(breakdown)
    .filter(([key]) => CATEGORY_CONFIG[key])
    .sort((a, b) => CATEGORY_CONFIG[a[0]].order - CATEGORY_CONFIG[b[0]].order);

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      marginBottom: '24px'
    }}>
      {/* Header with total score */}
      <div style={{
        textAlign: 'center',
        marginBottom: '24px',
        paddingBottom: '20px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div style={{
          fontSize: '48px',
          fontWeight: 'bold',
          color: '#1f2937'
        }}>
          {totalScore}<span style={{ fontSize: '24px', color: '#6b7280' }}>/100</span>
        </div>
        <div style={{
          fontSize: '20px',
          fontWeight: '600',
          color: totalScore >= 68 ? '#22c55e' : totalScore >= 52 ? '#eab308' : '#ef4444',
          marginTop: '8px'
        }}>
          {grade}
        </div>
        {message && (
          <div style={{
            fontSize: '14px',
            color: '#6b7280',
            marginTop: '8px'
          }}>
            {message}
          </div>
        )}
      </div>

      {/* Title */}
      <div style={{
        fontSize: '16px',
        fontWeight: '600',
        color: '#374151',
        marginBottom: '16px'
      }}>
        Score Breakdown
      </div>

      {/* Category bars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {sortedCategories.map(([category, score]) => {
          const config = CATEGORY_CONFIG[category];
          const percentage = (score / config.max) * 100;
          
          return (
            <div key={category}>
              {/* Label row */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '4px'
              }}>
                <span style={{ fontSize: '14px', color: '#374151' }}>
                  {config.label}
                </span>
                <span style={{ 
                  fontSize: '14px', 
                  fontWeight: '500',
                  color: '#6b7280'
                }}>
                  {Math.round(score)}/{config.max} {getStatusIcon(score, config.max)}
                </span>
              </div>
              
              {/* Progress bar */}
              <div style={{
                height: '8px',
                backgroundColor: '#e5e7eb',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${percentage}%`,
                  backgroundColor: getBarColor(score, config.max),
                  borderRadius: '4px',
                  transition: 'width 0.3s ease'
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
