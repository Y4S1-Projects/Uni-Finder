import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import CareerLadderTimeline from '../components/CareerLadder/CareerLadderTimeline';
import CareerLadderNetwork from '../components/CareerLadder/CareerLadderNetwork';
import CareerPathComparator from '../components/CareerLadder/CareerPathComparator';
import DomainSelector from '../components/CareerLadder/DomainSelector';
import ViewModeSelector from '../components/CareerLadder/ViewModeSelector';
import { analyzeCareerProgression, compareCareerPaths, getAllDomains } from '../api/careerLadderApi';

export default function CareerLadderPage() {
  const location = useLocation();
  const { userSkills, recommendations } = location.state || {};
  
  const [selectedDomain, setSelectedDomain] = useState('SOFTWARE_ENGINEERING');
  const [viewMode, setViewMode] = useState('timeline'); // timeline, comparison, network
  const [progressionData, setProgressionData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [availableDomains, setAvailableDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [allProgressionsData, setAllProgressionsData] = useState(null);
  
  // Load available domains on mount
  useEffect(() => {
    loadDomains();
  }, []);
  
  // Load progression data when domain changes
  useEffect(() => {
    if (selectedDomain && userSkills) {
      loadProgressionData();
    }
  }, [selectedDomain, userSkills]);
  
  const loadDomains = async () => {
    try {
      const data = await getAllDomains();
      setAvailableDomains(data.domains);
      setLoading(false);
    } catch (error) {
      console.error('Error loading domains:', error);
      setLoading(false);
    }
  };
  
  const loadProgressionData = async () => {
    setLoading(true);
    try {
      const data = await analyzeCareerProgression({
        user_skill_ids: userSkills,
        target_domain: selectedDomain,
        current_role_id: recommendations?.[0]?.role_id
      });
      setProgressionData(data);
    } catch (error) {
      console.error('Error loading progression:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAllProgressions = async () => {
    setLoading(true);
    try {
      let domainsToLoad = availableDomains;
      if (domainsToLoad.length === 0) {
        const data = await getAllDomains();
        domainsToLoad = data.domains;
        setAvailableDomains(domainsToLoad);
      }
      
      const promises = domainsToLoad.map(d => analyzeCareerProgression({
        user_skill_ids: userSkills,
        target_domain: d.domain_id,
        current_role_id: recommendations?.[0]?.role_id
      }));
      const results = await Promise.all(promises);
      setAllProgressionsData(results);
    } catch (error) {
      console.error('Error loading all progressions:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const loadComparisonData = async (domains) => {
    setLoading(true);
    try {
      const data = await compareCareerPaths({
        user_skill_ids: userSkills,
        domains: domains
      });
      setComparisonData(data);
    } catch (error) {
      console.error('Error loading comparison:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDomainChange = (domain) => {
    setSelectedDomain(domain);
  };
  
  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    
    if (mode === 'comparison' && !comparisonData) {
      // Load comparison for top 3 domains
      const topDomains = availableDomains.slice(0, 3).map(d => d.domain_id);
      loadComparisonData(topDomains);
    } else if (mode === 'network' && !allProgressionsData) {
      loadAllProgressions();
    }
  };
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4"
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
            Your Career Ladder
          </h1>
          <p className="text-gray-600 text-lg">
            Explore your career progression path and plan your next steps
          </p>
        </div>
        
        {/* Controls */}
        <div className="flex flex-col md:flex-row gap-6 mb-8">
          <div className="flex-1">
            {viewMode !== 'network' && (
              <DomainSelector
                domains={availableDomains}
                selected={selectedDomain}
                onChange={handleDomainChange}
              />
            )}
          </div>
          <div className="flex-1">
            <ViewModeSelector
              mode={viewMode}
              onChange={handleViewModeChange}
            />
          </div>
        </div>
        
        {/* Main Content */}
        <div className="bg-white rounded-3xl shadow-2xl p-8">
          {viewMode === 'timeline' && progressionData && (
            <CareerLadderTimeline
              progressionData={progressionData}
              userSkills={userSkills}
              domain={selectedDomain}
            />
          )}

          {viewMode === 'network' && allProgressionsData && (
            <CareerLadderNetwork
              allProgressions={allProgressionsData}
              userSkills={userSkills}
            />
          )}
          
          {viewMode === 'comparison' && comparisonData && (
            <CareerPathComparator
              comparisonData={comparisonData}
              userSkills={userSkills}
            />
          )}
        </div>
      </div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Loading career ladder...</p>
      </div>
    </div>
  );
}
