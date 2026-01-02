import React, { useState, useEffect } from "react";
import SkillSelector from "../components/SkillSelector";

const API_GATEWAY =
  process.env.REACT_APP_API_GATEWAY_URL || "http://localhost:8080";
const CAREER_API = `${API_GATEWAY}/career`;

export default function CareerPath() {
  const [domain, setDomain] = useState("SOFTWARE_ENGINEERING");
  const [currentRole, setCurrentRole] = useState("JR_SE");
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const skills = selectedSkills;

    try {
      const resp = await fetch(`${CAREER_API}/simulate_path`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain,
          current_role: currentRole,
          user_skill_ids: skills,
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

  useEffect(() => {
    console.log("selectedSkills:", selectedSkills);
  }, [selectedSkills]);

  return (
    <div style={{ padding: "2rem", maxWidth: 800, margin: "0 auto" }}>
      <h2>Career Path Simulation</h2>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "0.7rem" }}>
        <label>
          Domain
          <input
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            style={{ width: "100%" }}
          />
        </label>
        <label>
          Current Role
          <input
            value={currentRole}
            onChange={(e) => setCurrentRole(e.target.value)}
            style={{ width: "100%" }}
          />
        </label>
        <label>
          Your Skills
          <SkillSelector
            selected={selectedSkills}
            onChange={setSelectedSkills}
          />
        </label>
        <div>
          <button
            type="submit"
            disabled={loading}
            style={{ padding: "0.5rem 1rem" }}
          >
            {loading ? "Running..." : "Simulate"}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ marginTop: "1rem", color: "crimson" }}>{error}</div>
      )}

      {result && (
        <div
          style={{
            marginTop: "1rem",
            background: "#f7f7f7",
            padding: "1rem",
            borderRadius: 6,
          }}
        >
          <h3>Result</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
