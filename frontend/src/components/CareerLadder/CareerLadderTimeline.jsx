import React, { useState } from 'react';
import { FaCheckCircle, FaLock, FaArrowUp, FaStar, FaTrophy } from 'react-icons/fa';
import LevelDetailModal from './LevelDetailModal';

export default function CareerLadderTimeline({ progressionData, userSkills, domain }) {
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [showModal, setShowModal] = useState(false);
  
  const { current_position, progression_path, total_levels } = progressionData;
  
  // Combine current position with progression path
  const allLevels = [
    {
      ...current_position,
      is_current: true,
      readiness_score: 1.0
    },
    ...progression_path
  ];
  
  const handleLevelClick = (level) => {
    setSelectedLevel(level);
    setShowModal(true);
  };
  
  return (
    <div className="relative">
      {/* Timeline Container */}
      <div className="relative">
        {/* Vertical Line */}
        <div className="absolute left-8 top-0 bottom-0 w-1 bg-gradient-to-b from-purple-600 via-blue-500 to-gray-300"></div>
        
        {/* Level Cards */}
        <div className="space-y-12">
          {allLevels.map((level, index) => {
            const isAchievable = level.readiness_score >= 0.4;
            const isCurrent = level.is_current;
            const isLocked = level.readiness_score < 0.2 && !isCurrent;
            
            return (
              <LevelCard
                key={level.level}
                level={level}
                index={index}
                isCurrent={isCurrent}
                isAchievable={isAchievable}
                isLocked={isLocked}
                onClick={() => handleLevelClick(level)}
              />
            );
          })}
        </div>
      </div>
      
      {/* Detail Modal */}
      {showModal && selectedLevel && (
        <LevelDetailModal
          level={selectedLevel}
          userSkills={userSkills}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}

function LevelCard({ level, index, isCurrent, isAchievable, isLocked, onClick }) {
  const getCardStyle = () => {
    if (isCurrent) {
      return {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        border: '3px solid #5a67d8',
        transform: 'scale(1.05)'
      };
    } else if (isAchievable) {
      return {
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%)',
        border: '2px solid rgba(59, 130, 246, 0.3)'
      };
    } else if (isLocked) {
      return {
        background: 'linear-gradient(135deg, rgba(156, 163, 175, 0.1) 0%, rgba(209, 213, 219, 0.1) 100%)',
        border: '2px solid rgba(156, 163, 175, 0.3)',
        opacity: 0.6
      };
    } else {
      return {
        background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)',
        border: '2px solid rgba(168, 85, 247, 0.3)'
      };
    }
  };
  
  const getIcon = () => {
    if (isCurrent) return <FaStar className="text-yellow-400 text-2xl" />;
    if (isAchievable) return <FaArrowUp className="text-blue-500 text-2xl" />;
    if (isLocked) return <FaLock className="text-gray-400 text-2xl" />;
    return <FaTrophy className="text-purple-500 text-2xl" />;
  };
  
  const textColor = isCurrent ? 'text-white' : 'text-gray-800';
  
  return (
    <div className="relative flex items-start gap-8 ml-4">
      {/* Timeline Node */}
      <div className="relative z-10 flex-shrink-0">
        <div 
          className="w-16 h-16 rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-110"
          style={getCardStyle()}
        >
          {getIcon()}
        </div>
        
        {isCurrent && (
          <div className="absolute -top-2 -right-2">
            <span className="flex h-6 w-6">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-6 w-6 bg-yellow-500 items-center justify-center">
                <FaCheckCircle className="text-white text-sm" />
              </span>
            </span>
          </div>
        )}
      </div>
      
      {/* Card Content */}
      <div 
        className={`flex-1 p-6 rounded-2xl shadow-xl transition-all duration-300 cursor-pointer hover:shadow-2xl hover:scale-[1.02] ${isLocked ? 'cursor-not-allowed' : ''}`}
        style={getCardStyle()}
        onClick={!isLocked ? onClick : undefined}
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className={`text-sm font-bold px-3 py-1 rounded-full ${isCurrent ? 'bg-white/20 text-white' : 'bg-purple-100 text-purple-700'}`}>
                Level {level.level}
              </span>
              {isCurrent && (
                <span className="text-sm font-bold px-3 py-1 rounded-full bg-yellow-400 text-gray-900 animate-pulse">
                  YOU ARE HERE
                </span>
              )}
            </div>
            <h3 className={`text-2xl font-bold ${textColor} mb-1`}>
              {level.role_title}
            </h3>
            <p className={`text-sm ${isCurrent ? 'text-white/80' : 'text-gray-600'}`}>
              {level.experience_range}
            </p>
          </div>
          
          {!isCurrent && (
            <div className="text-right">
              <div className="text-3xl font-bold mb-1" style={{
                background: isAchievable ? 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)' : 'linear-gradient(135deg, #9ca3af 0%, #6b7280 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                {Math.round(level.readiness_score * 100)}%
              </div>
              <p className="text-xs text-gray-600">Ready</p>
            </div>
          )}
        </div>
        
        {/* Progress Bar */}
        {!isCurrent && (
          <div className="mb-4">
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full transition-all duration-500 rounded-full"
                style={{
                  width: `${level.readiness_score * 100}%`,
                  background: isAchievable 
                    ? 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)'
                    : 'linear-gradient(90deg, #9ca3af 0%, #6b7280 100%)'
                }}
              />
            </div>
          </div>
        )}
        
        {/* Skills Summary */}
        {!isCurrent && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className={isCurrent ? 'text-white/90' : 'text-gray-700'}>
              <span className="font-semibold">Skills Matched:</span>
              <span className="ml-2 font-bold text-green-600">
                {level.matched_skills?.length || 0}
              </span>
            </div>
            <div className={isCurrent ? 'text-white/90' : 'text-gray-700'}>
              <span className="font-semibold">Skills Needed:</span>
              <span className="ml-2 font-bold text-red-600">
                {level.missing_skills?.length || 0}
              </span>
            </div>
          </div>
        )}
        
        {/* Time Estimate */}
        {!isCurrent && level.estimated_time && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className={`text-sm ${isCurrent ? 'text-white/80' : 'text-gray-600'}`}>
              <span className="font-semibold">Estimated Time:</span>
              <span className="ml-2">{level.estimated_time}</span>
            </p>
          </div>
        )}
        
        {/* CTA */}
        {!isLocked && !isCurrent && (
          <button className="mt-4 w-full py-2 px-4 bg-white text-purple-700 rounded-lg font-semibold hover:bg-purple-50 transition-colors">
            View Details & Learning Path →
          </button>
        )}
      </div>
    </div>
  );
}
