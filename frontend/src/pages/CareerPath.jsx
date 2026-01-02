import React, { useState } from "react";
import SkillSelector from "../components/SkillSelector";

// Direct connection to career service (bypass API gateway)
const CAREER_API = "http://localhost:5004";

export default function CareerPath() {
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (selectedSkills.length === 0) {
      setError("Please select at least one skill");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const resp = await fetch(`${CAREER_API}/predict_role`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_skill_ids: selectedSkills,
        }),
      });

      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || body.message || "API error");
      }

      const data = await resp.json();
      setResult(data);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 900, margin: "0 auto" }}>
      <h2>Career Path Predictor</h2>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Select your skills below and we'll predict your current role, show your
        next career step, and identify skills you need to develop.
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
            {loading ? "Analyzing..." : "Predict My Career Path"}
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

      {result && (
        <div style={{ marginTop: "2rem" }}>
          {/* Predicted Role */}
          <div
            style={{
              background: "#f0f7ff",
              padding: "1.5rem",
              borderRadius: 8,
              marginBottom: "1rem",
            }}
          >
            <h3 style={{ margin: "0 0 0.5rem 0", color: "#2563eb" }}>
              📊 Your Predicted Role
            </h3>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1e40af" }}>
              {result.predicted_role_title || result.predicted_role}
            </div>
            {result.confidence && (
              <div style={{ marginTop: 8, color: "#666" }}>
                Confidence: {(result.confidence * 100).toFixed(1)}%
              </div>
            )}
            {result.domain && (
              <div style={{ marginTop: 4, color: "#666" }}>
                Domain: {result.domain.replace(/_/g, " ")}
              </div>
            )}
          </div>

          {/* Next Career Step */}
          {result.next_role && (
            <div
              style={{
                background: "#f0fdf4",
                padding: "1.5rem",
                borderRadius: 8,
                marginBottom: "1rem",
              }}
            >
              <h3 style={{ margin: "0 0 0.5rem 0", color: "#16a34a" }}>
                🚀 Next Career Step
              </h3>
              <div
                style={{ fontSize: 20, fontWeight: "bold", color: "#166534" }}
              >
                {result.next_role_title || result.next_role}
              </div>
              {result.skill_gap && (
                <div style={{ marginTop: 8, color: "#666" }}>
                  Readiness Score:{" "}
                  <strong>
                    {(result.skill_gap.readiness_score * 100).toFixed(0)}%
                  </strong>
                </div>
              )}
            </div>
          )}

          {/* Missing Skills */}
          {result.skill_gap &&
            result.skill_gap.missing_skills &&
            result.skill_gap.missing_skills.length > 0 && (
              <div
                style={{
                  background: "#fffbeb",
                  padding: "1.5rem",
                  borderRadius: 8,
                  marginBottom: "1rem",
                }}
              >
                <h3 style={{ margin: "0 0 1rem 0", color: "#ca8a04" }}>
                  📚 Skills to Develop
                </h3>
                <p style={{ color: "#666", marginBottom: "1rem" }}>
                  To advance to{" "}
                  <strong>{result.next_role_title || result.next_role}</strong>,
                  consider learning these skills:
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {result.skill_gap.missing_skills.map((skill) => (
                    <span
                      key={skill}
                      style={{
                        background: "#fef3c7",
                        padding: "6px 12px",
                        borderRadius: 16,
                        fontSize: 13,
                        color: "#92400e",
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

          {/* Matched Skills */}
          {result.skill_gap &&
            result.skill_gap.matched_skills &&
            result.skill_gap.matched_skills.length > 0 && (
              <div
                style={{
                  background: "#ecfdf5",
                  padding: "1.5rem",
                  borderRadius: 8,
                  marginBottom: "1rem",
                }}
              >
                <h3 style={{ margin: "0 0 1rem 0", color: "#059669" }}>
                  ✅ Skills You Already Have
                </h3>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {result.skill_gap.matched_skills.map((skill) => (
                    <span
                      key={skill}
                      style={{
                        background: "#d1fae5",
                        padding: "6px 12px",
                        borderRadius: 16,
                        fontSize: 13,
                        color: "#065f46",
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

          {/* Explanation */}
          <div
            style={{
              background: "#faf5ff",
              padding: "1.5rem",
              borderRadius: 8,
            }}
          >
            <h3 style={{ margin: "0 0 1rem 0", color: "#7c3aed" }}>
              💡 How This Works
            </h3>
            <p style={{ color: "#666", lineHeight: 1.6 }}>
              Our AI model analyzed your selected skills using a{" "}
              <strong>Decision Tree Classifier</strong> trained on real job
              postings. Based on the skill patterns, it predicted your most
              likely current role in the job market.
            </p>
            {result.next_role && result.skill_gap && (
              <p
                style={{ color: "#666", lineHeight: 1.6, marginTop: "0.75rem" }}
              >
                Your readiness score of{" "}
                <strong>
                  {(result.skill_gap.readiness_score * 100).toFixed(0)}%
                </strong>{" "}
                indicates how well your current skills match the requirements
                for{" "}
                <strong>{result.next_role_title || result.next_role}</strong>.
                {result.skill_gap.readiness_score >= 0.7
                  ? " You're well-prepared for this next step!"
                  : result.skill_gap.readiness_score >= 0.4
                  ? " You have a solid foundation but should focus on developing the missing skills."
                  : " Focus on building the skills listed above to progress in your career."}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
