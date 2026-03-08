import React from 'react';

export default function CareerPathComparator({ comparisonData, userSkills }) {
  const { comparisons } = comparisonData;
  
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-extrabold text-[#1e1b4b] mb-2 tracking-tight">
          Sector Comparison Overview
        </h2>
        <p className="text-[#4f46e5] font-medium tracking-wide text-sm bg-[#eef2ff] inline-block px-4 py-1.5 rounded-full shadow-sm">
          See how your skills map to roles across different tech domains
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {comparisons.slice(0, 3).map((comp, index) => (
          <ComparisonCard
            key={comp.domain}
            comparison={comp}
            rank={index + 1}
            isBest={index === 0}
          />
        ))}
      </div>
    </div>
  );
}

function ComparisonCard({ comparison, rank, isBest }) {
  return (
    <div 
      className={`p-6 rounded-2xl border-2 transition-all hover:shadow-xl hover:scale-105 ${
        isBest 
          ? 'border-purple-400 bg-gradient-to-br from-purple-50 to-blue-50'
          : ''
      }`}
      style={
        !isBest 
          ? {
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
              borderColor: 'rgba(102, 126, 234, 0.3)'
            }
          : {}
      }
    >
      {isBest && (
        <div className="text-center mb-4">
          <span className="inline-block px-4 py-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full text-sm font-bold">
            🏆 BEST MATCH
          </span>
        </div>
      )}
      
      <h3 className="text-xl font-bold text-gray-800 mb-2">
        {comparison.domain_name}
      </h3>
      
      <div className="text-5xl font-bold mb-4" style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        {Math.round(comparison.match_score * 100)}%
      </div>
      
      <div className="space-y-3 text-sm">
        <div className="flex justify-between items-start gap-4">
          <span className="text-gray-500 shrink-0">Best Fit Level:</span>
          <span className="font-bold text-gray-800 text-right">
            Level {comparison.best_fit_level}
          </span>
        </div>
        <div className="flex justify-between items-start gap-4">
          <span className="text-gray-500 shrink-0">Role:</span>
          <span className="font-bold text-gray-800 text-right">
            {comparison.best_fit_role}
          </span>
        </div>
        <div className="flex justify-between items-start gap-4">
          <span className="text-gray-500 shrink-0">Jobs Available:</span>
          <span className="font-bold text-gray-800 text-right">
            {comparison.jobs_available}
          </span>
        </div>
      </div>
    </div>
  );
}
