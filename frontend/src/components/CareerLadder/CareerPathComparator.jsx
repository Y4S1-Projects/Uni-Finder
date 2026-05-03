import React from 'react';

export default function CareerPathComparator({ comparisonData, userSkills }) {
  const { comparisons } = comparisonData;
  
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-extrabold text-[#1e1b4b] mb-2 tracking-tight">
          Sector Comparison Overview
        </h2>
        <p className="text-indigo-600 font-medium tracking-wide text-sm bg-indigo-50 inline-block px-4 py-1.5 rounded-full border border-indigo-100 shadow-sm">
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
      className={`relative p-6 rounded-2xl border transition-all duration-300 hover:shadow-lg hover:-translate-y-1 bg-white flex flex-col justify-between h-full gap-4 ${
        isBest 
          ? 'border-indigo-500 ring-4 ring-indigo-500/5 shadow-md'
          : 'border-gray-200 shadow-sm'
      }`}
    >
      {isBest && (
        <div className="absolute -top-3 right-4 z-10">
          <span className="px-3 py-1 bg-indigo-600 text-white rounded-full text-[10px] font-black shadow-md uppercase tracking-wider">
            🏆 BEST MATCH
          </span>
        </div>
      )}
      
      <div className="flex-1 space-y-4">
        <h3 className="text-xl font-bold text-gray-900 leading-tight">
          {comparison.domain_name}
        </h3>
        
        <div className="text-5xl font-extrabold text-indigo-600 tracking-tight">
          {Math.round((comparison.match_score || 0) * 100)}%
        </div>
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
          <span className="font-bold text-gray-900 text-right">
            {comparison.best_fit_role}
          </span>
        </div>
        <div className="flex justify-between items-start gap-4">
          <span className="text-gray-500 shrink-0">Jobs Available:</span>
          <span className="font-bold text-gray-900 text-right">
            {comparison.jobs_available}
          </span>
        </div>
      </div>
    </div>
  );
}
