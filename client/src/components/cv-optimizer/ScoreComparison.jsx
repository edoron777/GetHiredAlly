import React from 'react';

/**
 * ScoreComparison - Shows before/after optimization results
 * Gives users transparency and feeling of success
 */

const CATEGORY_LABELS = {
  quantification: "Achievements & Metrics",
  experience: "Experience Quality",
  language: "Action Verbs",
  grammar: "Grammar & Spelling",
  skills: "Skills Presentation",
  formatting: "Formatting",
  contact: "Contact Information",
  length: "CV Length"
};

export default function ScoreComparison({ 
  beforeScore, 
  afterScore, 
  improvement,
  message,
  categoryImprovements 
}) {
  if (!beforeScore || !afterScore) return null;

  const hasImprovements = categoryImprovements && Object.keys(categoryImprovements).length > 0;
  
  // Separate improved vs unchanged categories
  const improved = [];
  const unchanged = [];
  
  if (hasImprovements) {
    Object.entries(categoryImprovements).forEach(([category, data]) => {
      if (data.improvement > 0) {
        improved.push({ category, ...data });
      } else {
        unchanged.push({ category, ...data });
      }
    });
  }

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      marginBottom: '24px'
    }}>
      {/* Header */}
      <div style={{
        textAlign: 'center',
        marginBottom: '24px',
        paddingBottom: '20px',
        borderBottom: '1px solid #e5e7eb'
      }}>
        <div style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#22c55e',
          marginBottom: '16px'
        }}>
          🎉 Optimization Complete!
        </div>
        
        {/* Before → After */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '24px'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>Before</div>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#6b7280' }}>
              {beforeScore}
            </div>
          </div>
          
          <div style={{ fontSize: '24px', color: '#9ca3af' }}>→</div>
          
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>After</div>
            <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#22c55e' }}>
              {afterScore}
            </div>
          </div>
          
          <div style={{
            backgroundColor: '#dcfce7',
            color: '#16a34a',
            padding: '8px 16px',
            borderRadius: '20px',
            fontWeight: '600',
            fontSize: '16px'
          }}>
            +{improvement} points
          </div>
        </div>
        
        {message && (
          <div style={{
            fontSize: '14px',
            color: '#374151',
            marginTop: '16px'
          }}>
            {message}
          </div>
        )}
      </div>

      {/* What Improved */}
      {improved.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#16a34a',
            marginBottom: '12px'
          }}>
            ✓ What Improved
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {improved.map(({ category, before, after, improvement: catImprovement, max_possible }) => (
              <div 
                key={category}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 12px',
                  backgroundColor: '#f0fdf4',
                  borderRadius: '8px'
                }}
              >
                <span style={{ fontSize: '14px', color: '#374151' }}>
                  {CATEGORY_LABELS[category] || category}
                </span>
                <span style={{ fontSize: '14px', color: '#16a34a', fontWeight: '500' }}>
                  {before} → {after}/{max_possible} (+{catImprovement})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Needs Your Input */}
      {unchanged.length > 0 && (
        <div>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#d97706',
            marginBottom: '12px'
          }}>
            ⚠️ Needs Your Input
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {unchanged.map(({ category, before, max_possible }) => (
              <div 
                key={category}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 12px',
                  backgroundColor: '#fffbeb',
                  borderRadius: '8px'
                }}
              >
                <span style={{ fontSize: '14px', color: '#374151' }}>
                  {CATEGORY_LABELS[category] || category}
                </span>
                <span style={{ fontSize: '14px', color: '#d97706' }}>
                  {before}/{max_possible} (no change)
                </span>
              </div>
            ))}
          </div>
          
          <div style={{
            fontSize: '13px',
            color: '#6b7280',
            marginTop: '12px',
            padding: '12px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px'
          }}>
            💡 To improve further: Fill in the placeholders in your CV with real numbers and achievements, then re-upload.
          </div>
        </div>
      )}
    </div>
  );
}
