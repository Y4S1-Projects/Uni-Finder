import React, { useState, useEffect } from 'react';
import { FaTimes, FaCheckCircle, FaTimesCircle, FaBook, FaClock, FaFire } from 'react-icons/fa';
import { getSkillDetails } from '../../api/careerLadderApi';

export default function LevelDetailModal({ level, userSkills, onClose }) {
  const [skillDetails, setSkillDetails] = useState({});
  const [activeTab, setActiveTab] = useState('overview'); // overview, skills, roadmap
  
  useEffect(() => {
    // Load details for all skills
    const loadSkillDetails = async () => {
      const allSkills = [...(level.matched_skills || []), ...(level.missing_skills || [])];
      const details = {};
      
      for (const skillId of allSkills) {
        try {
          const data = await getSkillDetails(skillId);
          details[skillId] = data;
        } catch (error) {
          console.error(`Error loading skill ${skillId}:`, error);
        }
      }
      
      setSkillDetails(details);
    };
    
    loadSkillDetails();
  }, [level]);
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div 
          className="p-8 text-white relative"
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}
        >
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:bg-white/20 rounded-full p-2 transition-colors"
          >
            <FaTimes size={24} />
          </button>
          
          <div className="flex items-start justify-between">
            <div>
              <span className="inline-block px-4 py-1 bg-white/20 rounded-full text-sm font-bold mb-3">
                Level {level.level}
              </span>
              <h2 className="text-3xl font-bold mb-2">{level.role_title}</h2>
              <p className="text-white/90">{level.experience_range}</p>
            </div>
            
            <div className="text-right">
              <div className="text-5xl font-bold mb-1">
                {Math.round((level.readiness_score || 0) * 100)}%
              </div>
              <p className="text-sm text-white/80">Readiness Score</p>
            </div>
          </div>
          
          {/* Tabs */}
          <div className="flex gap-4 mt-6">
            {['overview', 'skills', 'roadmap'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2 rounded-lg font-semibold transition-all ${
                  activeTab === tab
                    ? 'bg-white text-purple-700'
                    : 'bg-white/20 text-white hover:bg-white/30'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
        
        {/* Content */}
        <div className="p-8 overflow-y-auto max-h-[60vh]">
          {activeTab === 'overview' && (
            <OverviewTab level={level} />
          )}
          
          {activeTab === 'skills' && (
            <SkillsTab 
              matchedSkills={level.matched_skills || []}
              missingSkills={level.missing_skills || []}
              skillDetails={skillDetails}
            />
          )}
          
          {activeTab === 'roadmap' && (
            <RoadmapTab level={level} skillDetails={skillDetails} />
          )}
        </div>
        
        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-between">
          <button
            onClick={onClose}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
          
          <button
            className="px-8 py-3 text-white rounded-xl font-semibold transition-all hover:shadow-lg"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            Set as My Target Goal
          </button>
        </div>
      </div>
    </div>
  );
}

function OverviewTab({ level }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-3 text-gray-800">Role Overview</h3>
        <p className="text-gray-600 leading-relaxed">
          {level.role_description || `As a ${level.role_title}, you'll be responsible for advancing your technical expertise and taking on more complex challenges in your domain.`}
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          icon={<FaClock className="text-blue-500" />}
          label="Experience Required"
          value={level.experience_range}
        />
        <StatCard
          icon={<FaFire className="text-orange-500" />}
          label="Difficulty"
          value={level.difficulty || 'Medium'}
        />
        <StatCard
          icon={<FaClock className="text-purple-500" />}
          label="Time to Achieve"
          value={level.estimated_time || '12-18 months'}
        />
      </div>
      
      {level.key_responsibilities && (
        <div>
          <h3 className="text-xl font-bold mb-3 text-gray-800">Key Responsibilities</h3>
          <ul className="space-y-2">
            {level.key_responsibilities.map((resp, index) => (
              <li key={index} className="flex items-start gap-3">
                <FaCheckCircle className="text-green-500 mt-1 flex-shrink-0" />
                <span className="text-gray-700">{resp}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function SkillsTab({ matchedSkills, missingSkills, skillDetails }) {
  return (
    <div className="space-y-8">
      {/* Matched Skills */}
      <div>
        <h3 className="text-xl font-bold mb-4 text-gray-800 flex items-center gap-2">
          <FaCheckCircle className="text-green-500" />
          Skills You Have ({matchedSkills.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {matchedSkills.map((skillId) => (
            <SkillBadge
              key={skillId}
              skillId={skillId}
              skillName={skillDetails[skillId]?.name || skillId}
              variant="matched"
            />
          ))}
        </div>
      </div>
      
      {/* Missing Skills */}
      <div>
        <h3 className="text-xl font-bold mb-4 text-gray-800 flex items-center gap-2">
          <FaTimesCircle className="text-red-500" />
          Skills to Develop ({missingSkills.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {missingSkills.map((skillId) => (
            <SkillBadge
              key={skillId}
              skillId={skillId}
              skillName={skillDetails[skillId]?.name || skillId}
              variant="missing"
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function RoadmapTab({ level, skillDetails }) {
  const missingSkills = level.missing_skills || [];
  
  // Prioritize skills
  const prioritizedSkills = missingSkills.slice(0, 5);
  
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold mb-3 text-gray-800">Your Learning Roadmap</h3>
        <p className="text-gray-600 mb-6">
          Focus on developing these skills to reach this career level
        </p>
      </div>
      
      <div className="space-y-4">
        {prioritizedSkills.map((skillId, index) => (
          <div key={skillId} className="p-5 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border-2 border-purple-200">
            <div className="flex items-start gap-4">
              <div 
                className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-white"
                style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }}
              >
                {index + 1}
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-gray-800 mb-2">
                  {skillDetails[skillId]?.name || skillId}
                </h4>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <FaClock />
                    2-3 months
                  </span>
                  <span className="flex items-center gap-1">
                    <FaBook />
                    Online courses available
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-8 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200">
        <h4 className="font-bold text-gray-800 mb-2">Estimated Timeline</h4>
        <p className="text-gray-600">
          With consistent effort, you can be ready for this role in approximately{' '}
          <span className="font-bold text-purple-700">{level.estimated_time || '12-18 months'}</span>
        </p>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <div className="p-4 bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl border-2 border-gray-200">
      <div className="flex items-center gap-3 mb-2">
        <div className="text-2xl">{icon}</div>
        <div className="text-sm text-gray-600">{label}</div>
      </div>
      <div className="text-xl font-bold text-gray-800">{value}</div>
    </div>
  );
}

function SkillBadge({ skillId, skillName, variant }) {
  const styles = variant === 'matched'
    ? 'bg-green-100 border-green-300 text-green-800'
    : 'bg-red-100 border-red-300 text-red-800';
  
  const icon = variant === 'matched'
    ? <FaCheckCircle className="text-green-600" />
    : <FaTimesCircle className="text-red-600" />;
  
  return (
    <div className={`px-4 py-3 rounded-lg border-2 ${styles} flex items-center gap-2 font-semibold`}>
      {icon}
      <span>{skillName}</span>
    </div>
  );
}
