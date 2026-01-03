import React, { useState } from "react";
import SkillSelector from "../components/SkillSelector";

// Direct connection to career service (bypass API gateway)
const CAREER_API = "http://localhost:5004";

export default function CareerPath() {
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Detail view state
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetail, setJobDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (selectedSkills.length === 0) {
      setError("Please select at least one skill");
      return;
    }

    setLoading(true);
    setError(null);
    setRecommendations(null);

    try {
      const resp = await fetch(`${CAREER_API}/recommend_careers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_skill_ids: selectedSkills,
          top_n: 5,
        }),
      });

      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || body.message || "API error");
      }

      const data = await resp.json();
      setRecommendations(data);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleViewJob = async (rec) => {
    setSelectedJob(rec);
    setDetailLoading(true);
    setJobDetail(null);

    try {
      const resp = await fetch(`${CAREER_API}/explain_career`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role_id: rec.role_id,
          role_title: rec.role_title,
          domain: rec.domain,
          match_score: rec.match_score,
          user_skill_ids: selectedSkills,
          matched_skills: rec.skill_gap?.matched_skills || [],
          missing_skills: rec.skill_gap?.missing_skills || [],
          readiness_score: rec.skill_gap?.readiness_score || 0,
          next_role: rec.next_role,
          next_role_title: rec.next_role_title,
        }),
      });

      if (!resp.ok) {
        throw new Error("Failed to get explanation");
      }

      const data = await resp.json();
      setJobDetail(data);
    } catch (err) {
      console.error(err);
      // Show basic detail without AI explanation
      setJobDetail({
        ...rec,
        matched_skills: (rec.skill_gap?.matched_skills || []).map((s) => ({
          id: s,
          name: s,
        })),
        missing_skills: (rec.skill_gap?.missing_skills || []).map((s) => ({
          id: s,
          name: s,
        })),
        readiness_score: rec.skill_gap?.readiness_score || 0,
        explanation: null,
      });
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedJob(null);
    setJobDetail(null);
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <h2>🎯 Career Path Recommender</h2>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Select your skills below and we'll recommend the best matching career
        roles using AI-powered cosine similarity analysis.
      </p>

      <form onSubmit={handlePredict} style={{ display: "grid", gap: "1rem" }}>
        <label>
          <strong>Your Skills</strong>
          <div style={{ marginTop: 8 }}>
            <SkillSelector
              selected={selectedSkills}
              onChange={setSelectedSkills}
            />
          </div>
        </label>

        <div style={{ marginTop: 8 }}>
          <button
            type="submit"
            disabled={loading || selectedSkills.length === 0}
            style={{
              padding: "0.75rem 1.5rem",
              background: selectedSkills.length === 0 ? "#ccc" : "#4a90d9",
              color: "white",
              border: "none",
              borderRadius: 6,
              cursor: selectedSkills.length === 0 ? "not-allowed" : "pointer",
              fontSize: 16,
            }}
          >
            {loading ? "Analyzing..." : "Find My Best Career Matches"}
          </button>
        </div>
      </form>

      {error && (
        <div
          style={{
            marginTop: "1rem",
            color: "crimson",
            padding: "1rem",
            background: "#fff0f0",
            borderRadius: 6,
          }}
        >
          {error}
        </div>
      )}

      {recommendations && (
        <div style={{ marginTop: "2rem" }}>
          {/* Summary */}
          <div
            style={{
              background: "#f8fafc",
              padding: "1rem",
              borderRadius: 8,
              marginBottom: "1.5rem",
              borderLeft: "4px solid #4a90d9",
            }}
          >
            <p style={{ margin: 0, color: "#666" }}>
              Analyzed <strong>{recommendations.skills_analyzed.length}</strong>{" "}
              skills across{" "}
              <strong>{recommendations.total_roles_compared}</strong> career
              roles
            </p>
          </div>

          {/* Recommendations */}
          <h3 style={{ marginBottom: "1rem" }}>
            🏆 Top Career Recommendations
          </h3>

          {recommendations.recommendations.map((rec, index) => (
            <div
              key={rec.role_id}
              style={{
                background:
                  index === 0
                    ? "linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%)"
                    : "#fff",
                border: index === 0 ? "2px solid #4a90d9" : "1px solid #e5e7eb",
                padding: "1.5rem",
                borderRadius: 12,
                marginBottom: "1rem",
                position: "relative",
              }}
            >
              {index === 0 && (
                <span
                  style={{
                    position: "absolute",
                    top: -10,
                    right: 16,
                    background: "#4a90d9",
                    color: "white",
                    padding: "4px 12px",
                    borderRadius: 12,
                    fontSize: 12,
                    fontWeight: "bold",
                  }}
                >
                  BEST MATCH
                </span>
              )}

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  marginBottom: "1rem",
                }}
              >
                <div>
                  <h4
                    style={{
                      margin: "0 0 4px 0",
                      fontSize: 20,
                      color: "#1e40af",
                    }}
                  >
                    {index + 1}. {rec.role_title || rec.role_id}
                  </h4>
                  {rec.domain && (
                    <span
                      style={{
                        background: "#e0e7ff",
                        color: "#4338ca",
                        padding: "2px 8px",
                        borderRadius: 4,
                        fontSize: 12,
                      }}
                    >
                      {rec.domain.replace(/_/g, " ")}
                    </span>
                  )}
                </div>
                <div style={{ textAlign: "right" }}>
                  <div
                    style={{
                      fontSize: 28,
                      fontWeight: "bold",
                      color:
                        rec.match_score >= 0.7
                          ? "#16a34a"
                          : rec.match_score >= 0.4
                          ? "#ca8a04"
                          : "#dc2626",
                    }}
                  >
                    {(rec.match_score * 100).toFixed(0)}%
                  </div>
                  <div style={{ fontSize: 12, color: "#666" }}>Match Score</div>
                </div>
              </div>

              {/* Progress bar */}
              <div
                style={{
                  background: "#e5e7eb",
                  borderRadius: 8,
                  height: 8,
                  marginBottom: "1rem",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${rec.match_score * 100}%`,
                    height: "100%",
                    background:
                      rec.match_score >= 0.7
                        ? "#16a34a"
                        : rec.match_score >= 0.4
                        ? "#ca8a04"
                        : "#dc2626",
                    borderRadius: 8,
                    transition: "width 0.5s ease",
                  }}
                />
              </div>

              {/* Next Career Step */}
              {rec.next_role && (
                <div
                  style={{
                    background: "#f0fdf4",
                    padding: "0.75rem",
                    borderRadius: 6,
                    marginBottom: "1rem",
                  }}
                >
                  <span style={{ color: "#16a34a", fontWeight: 500 }}>
                    🚀 Next Step:
                  </span>{" "}
                  <span style={{ color: "#166534" }}>
                    {rec.next_role_title || rec.next_role}
                  </span>
                </div>
              )}

              {/* Skill Gap */}
              {rec.skill_gap && (
                <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                  {/* Readiness */}
                  <div style={{ flex: "1 1 120px" }}>
                    <div
                      style={{ fontSize: 12, color: "#666", marginBottom: 4 }}
                    >
                      Readiness
                    </div>
                    <div style={{ fontWeight: "bold", color: "#1e40af" }}>
                      {(rec.skill_gap.readiness_score * 100).toFixed(0)}%
                    </div>
                  </div>

                  {/* Matched Skills */}
                  {rec.skill_gap.matched_skills?.length > 0 && (
                    <div style={{ flex: "2 1 200px" }}>
                      <div
                        style={{
                          fontSize: 12,
                          color: "#059669",
                          marginBottom: 4,
                        }}
                      >
                        ✅ Skills You Have (
                        {rec.skill_gap.matched_skills.length})
                      </div>
                      <div
                        style={{ display: "flex", flexWrap: "wrap", gap: 4 }}
                      >
                        {rec.skill_gap.matched_skills
                          .slice(0, 5)
                          .map((skill) => (
                            <span
                              key={skill}
                              style={{
                                background: "#d1fae5",
                                padding: "2px 8px",
                                borderRadius: 12,
                                fontSize: 11,
                                color: "#065f46",
                              }}
                            >
                              {skill}
                            </span>
                          ))}
                        {rec.skill_gap.matched_skills.length > 5 && (
                          <span style={{ fontSize: 11, color: "#666" }}>
                            +{rec.skill_gap.matched_skills.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Missing Skills */}
                  {rec.skill_gap.missing_skills?.length > 0 && (
                    <div style={{ flex: "2 1 200px" }}>
                      <div
                        style={{
                          fontSize: 12,
                          color: "#ca8a04",
                          marginBottom: 4,
                        }}
                      >
                        📚 Skills to Learn (
                        {rec.skill_gap.missing_skills.length})
                      </div>
                      <div
                        style={{ display: "flex", flexWrap: "wrap", gap: 4 }}
                      >
                        {rec.skill_gap.missing_skills
                          .slice(0, 5)
                          .map((skill) => (
                            <span
                              key={skill}
                              style={{
                                background: "#fef3c7",
                                padding: "2px 8px",
                                borderRadius: 12,
                                fontSize: 11,
                                color: "#92400e",
                              }}
                            >
                              {skill}
                            </span>
                          ))}
                        {rec.skill_gap.missing_skills.length > 5 && (
                          <span style={{ fontSize: 11, color: "#666" }}>
                            +{rec.skill_gap.missing_skills.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* View Details Button */}
              <button
                onClick={() => handleViewJob(rec)}
                style={{
                  marginTop: "1rem",
                  padding: "0.5rem 1rem",
                  background: "#7c3aed",
                  color: "white",
                  border: "none",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontSize: 14,
                  fontWeight: 500,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                🔍 View Details & AI Explanation
              </button>
            </div>
          ))}

          {/* How it works */}
          <div
            style={{
              background: "#faf5ff",
              padding: "1.5rem",
              borderRadius: 8,
              marginTop: "1.5rem",
            }}
          >
            <h3 style={{ margin: "0 0 1rem 0", color: "#7c3aed" }}>
              💡 How This Works
            </h3>
            <p style={{ color: "#666", lineHeight: 1.6, margin: 0 }}>
              Our AI uses <strong>Cosine Similarity</strong> to compare your
              skill profile against real job market data. Each role has an
              importance-weighted skill profile built from actual job postings.
              The match score indicates how well your skills align with each
              role's requirements. Higher scores mean better fit!
            </p>
          </div>
        </div>
      )}

      {/* Job Detail Modal */}
      {selectedJob && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "1rem",
          }}
          onClick={closeDetail}
        >
          <div
            style={{
              background: "white",
              borderRadius: 16,
              maxWidth: 700,
              width: "100%",
              maxHeight: "90vh",
              overflow: "auto",
              padding: "2rem",
              position: "relative",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={closeDetail}
              style={{
                position: "absolute",
                top: 16,
                right: 16,
                background: "#f3f4f6",
                border: "none",
                borderRadius: "50%",
                width: 32,
                height: 32,
                cursor: "pointer",
                fontSize: 18,
              }}
            >
              ✕
            </button>

            {detailLoading ? (
              <div style={{ textAlign: "center", padding: "3rem" }}>
                <div style={{ fontSize: 48, marginBottom: "1rem" }}>🤖</div>
                <div style={{ color: "#666" }}>
                  AI is analyzing this career path...
                </div>
              </div>
            ) : jobDetail ? (
              <>
                {/* Header */}
                <div style={{ marginBottom: "1.5rem" }}>
                  <h2 style={{ margin: "0 0 8px 0", color: "#1e40af" }}>
                    {jobDetail.role_title || jobDetail.role_id}
                  </h2>
                  {jobDetail.domain && (
                    <span
                      style={{
                        background: "#e0e7ff",
                        color: "#4338ca",
                        padding: "4px 12px",
                        borderRadius: 6,
                        fontSize: 14,
                      }}
                    >
                      {jobDetail.domain.replace(/_/g, " ")}
                    </span>
                  )}
                </div>

                {/* Match & Readiness Scores */}
                <div
                  style={{
                    display: "flex",
                    gap: "1rem",
                    marginBottom: "1.5rem",
                  }}
                >
                  <div
                    style={{
                      flex: 1,
                      background: "#f0f7ff",
                      padding: "1rem",
                      borderRadius: 8,
                      textAlign: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 32,
                        fontWeight: "bold",
                        color: "#2563eb",
                      }}
                    >
                      {(jobDetail.match_score * 100).toFixed(0)}%
                    </div>
                    <div style={{ fontSize: 12, color: "#666" }}>
                      Match Score
                    </div>
                  </div>
                  <div
                    style={{
                      flex: 1,
                      background: "#f0fdf4",
                      padding: "1rem",
                      borderRadius: 8,
                      textAlign: "center",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 32,
                        fontWeight: "bold",
                        color: "#16a34a",
                      }}
                    >
                      {(jobDetail.readiness_score * 100).toFixed(0)}%
                    </div>
                    <div style={{ fontSize: 12, color: "#666" }}>Readiness</div>
                  </div>
                </div>

                {/* Next Career Step */}
                {jobDetail.next_role && (
                  <div
                    style={{
                      background: "#faf5ff",
                      padding: "1rem",
                      borderRadius: 8,
                      marginBottom: "1.5rem",
                    }}
                  >
                    <div
                      style={{
                        fontWeight: 500,
                        color: "#7c3aed",
                        marginBottom: 4,
                      }}
                    >
                      🚀 Next Career Step
                    </div>
                    <div style={{ fontSize: 18, color: "#5b21b6" }}>
                      {jobDetail.next_role_title || jobDetail.next_role}
                    </div>
                  </div>
                )}

                {/* Skills You Have */}
                {jobDetail.matched_skills?.length > 0 && (
                  <div style={{ marginBottom: "1.5rem" }}>
                    <h3
                      style={{
                        margin: "0 0 0.75rem 0",
                        color: "#059669",
                        fontSize: 16,
                      }}
                    >
                      ✅ Skills You Already Have (
                      {jobDetail.matched_skills.length})
                    </h3>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {jobDetail.matched_skills.map((skill) => (
                        <span
                          key={skill.id || skill}
                          style={{
                            background: "#d1fae5",
                            padding: "6px 12px",
                            borderRadius: 16,
                            fontSize: 13,
                            color: "#065f46",
                          }}
                        >
                          {skill.name || skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Skills to Develop */}
                {jobDetail.missing_skills?.length > 0 && (
                  <div style={{ marginBottom: "1.5rem" }}>
                    <h3
                      style={{
                        margin: "0 0 0.75rem 0",
                        color: "#ca8a04",
                        fontSize: 16,
                      }}
                    >
                      📚 Skills to Develop ({jobDetail.missing_skills.length})
                    </h3>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {jobDetail.missing_skills.map((skill) => (
                        <span
                          key={skill.id || skill}
                          style={{
                            background: "#fef3c7",
                            padding: "6px 12px",
                            borderRadius: 16,
                            fontSize: 13,
                            color: "#92400e",
                          }}
                        >
                          {skill.name || skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Explanation */}
                {jobDetail.explanation && (
                  <div
                    style={{
                      background:
                        "linear-gradient(135deg, #fdf4ff 0%, #f5f3ff 100%)",
                      padding: "1.5rem",
                      borderRadius: 12,
                      border: "1px solid #e9d5ff",
                    }}
                  >
                    <h3
                      style={{
                        margin: "0 0 1rem 0",
                        color: "#7c3aed",
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                      }}
                    >
                      🤖 AI Career Analysis
                    </h3>
                    <div
                      style={{
                        color: "#4c1d95",
                        lineHeight: 1.7,
                        whiteSpace: "pre-wrap",
                      }}
                      dangerouslySetInnerHTML={{
                        __html: jobDetail.explanation
                          .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                          .replace(/\*(.*?)\*/g, "<em>$1</em>")
                          .replace(/^- /gm, "• ")
                          .replace(/^(\d+)\. /gm, "<strong>$1.</strong> ")
                          .replace(/\n/g, "<br/>"),
                      }}
                    />
                  </div>
                )}
              </>
            ) : (
              <div
                style={{ textAlign: "center", padding: "2rem", color: "#666" }}
              >
                Failed to load details. Please try again.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
