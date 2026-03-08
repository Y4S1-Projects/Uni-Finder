import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import CareerLadderTimeline from "../components/CareerLadder/CareerLadderTimeline";
import CareerLadderNetwork from "../components/CareerLadder/CareerLadderNetwork";
import CareerPathComparator from "../components/CareerLadder/CareerPathComparator";
import DomainSelector from "../components/CareerLadder/DomainSelector";
import ViewModeSelector from "../components/CareerLadder/ViewModeSelector";
import {
  analyzeCareerProgression,
  compareCareerPaths,
  getAllDomains,
} from "../api/careerLadderApi";
import { FaProjectDiagram, FaGlobe, FaChevronRight } from "react-icons/fa";

export default function CareerLadderPage() {
  const location = useLocation();
  const { userSkills, recommendations } = location.state || {};

  const [selectedDomain, setSelectedDomain] = useState("SOFTWARE_ENGINEERING");
  const [viewMode, setViewMode] = useState("network"); // comparison, network
  const [progressionData, setProgressionData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [availableDomains, setAvailableDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [allProgressionsData, setAllProgressionsData] = useState(null);

  // Load data immediately on mount
  useEffect(() => {
    window.scrollTo(0, 0);
    const init = async () => {
      setLoading(true);
      const domains = await loadDomains();
      if (viewMode === "network") {
        await loadAllProgressions(domains);
      }
      setLoading(false);
    };
    init();
  }, [userSkills]); // userSkills is the primary dependency for personalization

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
      return data.domains;
    } catch (error) {
      console.error("Error loading domains:", error);
      return [];
    }
  };

  const loadProgressionData = async () => {
    setLoading(true);
    try {
      const data = await analyzeCareerProgression({
        user_skill_ids: userSkills,
        target_domain: selectedDomain,
        current_role_id: recommendations?.[0]?.role_id,
      });
      setProgressionData(data);
    } catch (error) {
      console.error("Error loading progression:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadAllProgressions = async (domains) => {
    try {
      const domainsToLoad = domains || availableDomains;
      const promises = domainsToLoad.map((d) =>
        analyzeCareerProgression({
          user_skill_ids: userSkills,
          target_domain: d.domain_id,
          current_role_id: recommendations?.[0]?.role_id,
          show_all_levels: true, // Show ALL levels in network/ecosystem view
        }),
      );
      const results = await Promise.all(promises);
      setAllProgressionsData(results);
    } catch (error) {
      console.error("Error loading all progressions:", error);
    }
  };

  const loadComparisonData = async (domains) => {
    setLoading(true);
    try {
      const data = await compareCareerPaths({
        user_skill_ids: userSkills,
        domains: domains,
      });
      setComparisonData(data);
    } catch (error) {
      console.error("Error loading comparison:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDomainChange = (domain) => {
    setSelectedDomain(domain);
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);

    if (mode === "comparison" && !comparisonData) {
      // Load comparison for top 3 domains
      const topDomains = availableDomains.slice(0, 3).map((d) => d.domain_id);
      loadComparisonData(topDomains);
    } else if (mode === "network" && !allProgressionsData) {
      loadAllProgressions();
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen pt-0 bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 text-slate-900 overflow-x-hidden">
      <div className="relative z-10 m-0 p-0">
        {/* 🚀 AI-Powered Ecosystem Header */}
        <header className="sticky top-[64px] z-40 bg-white/80 backdrop-blur-2xl border-b border-slate-200 shadow-sm mt-[64px]">
          <div className="max-w-[2000px] mx-auto px-8 py-3 flex flex-col lg:flex-row items-center justify-between gap-4 w-full">
            <div className="flex flex-col justify-center items-center lg:items-start text-center lg:text-left gap-1 group">
              <div className="flex items-center gap-3">
                <div
                  className="p-2.5 rounded-xl shadow-lg relative transform transition-transform group-hover:rotate-12"
                  style={{
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  }}
                >
                  <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full" />
                  <FaProjectDiagram className="relative text-white text-2xl" />
                </div>

                <h1
                  className="text-3xl md:text-4xl font-bold tracking-tight"
                  style={{
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    backgroundClip: "text",
                  }}
                >
                  Career Ladder
                </h1>
              </div>

              <p className="text-gray-600 text-base flex items-center gap-2 font-medium">
                <FaGlobe className="text-blue-500/70 hidden sm:inline-block" />
                Explore career pathways and discover the skills you need to
                advance in your journey
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-4 w-full lg:w-auto">
              <div className="bg-white p-1.5 rounded-2xl border border-slate-200 shadow-sm flex items-center w-full sm:w-auto">
                <ViewModeSelector
                  mode={viewMode}
                  onChange={handleViewModeChange}
                />
              </div>
            </div>
          </div>
        </header>

        {/* 🔮 Dynamic Full-Screen Canvas Area */}
        <main className="relative">
          <div
            className={`${viewMode === "network" ? "h-[calc(100vh-192px)] w-full" : "max-w-7xl mx-auto py-16 px-6"}`}
          >
            {viewMode === "network" && allProgressionsData && (
              <div className="w-full h-full relative animate-in fade-in duration-1000">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(59,130,246,0.08),transparent_50%)] pointer-events-none" />
                <CareerLadderNetwork
                  allProgressions={allProgressionsData}
                  userSkills={userSkills}
                />
              </div>
            )}

            {viewMode === "comparison" && comparisonData && (
              <div className="bg-white rounded-[3rem] border border-slate-200 p-12 shadow-xl border-t-white">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
                  <div className="space-y-2">
                    <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight">
                      Market Benchmarking
                    </h2>
                    <p className="text-slate-600 text-lg max-w-2xl">
                      Visualizing your competitive index across parallel domain
                      architectures.
                    </p>
                  </div>
                  <div className="h-0.5 flex-grow mx-12 border-t border-slate-200 hidden lg:block" />
                </div>
                <CareerPathComparator
                  comparisonData={comparisonData}
                  userSkills={userSkills}
                />
              </div>
            )}
          </div>
        </main>
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
