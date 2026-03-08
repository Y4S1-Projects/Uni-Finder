const API_BASE_URL =
  process.env.REACT_APP_CAREER_SERVICE_URL || "http://127.0.0.1:5004";

export async function getAllDomains() {
  const response = await fetch(`${API_BASE_URL}/career_ladders/list`);
  if (!response.ok) throw new Error("Failed to fetch domains");
  return response.json();
}

export async function getCareerLadder(domain) {
  const response = await fetch(`${API_BASE_URL}/career_ladder/${domain}`);
  if (!response.ok) throw new Error("Failed to fetch career ladder");
  return response.json();
}

export async function analyzeCareerProgression(data) {
  const response = await fetch(`${API_BASE_URL}/analyze_career_progression`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...data,
      show_all_levels: data.show_all_levels ?? false,
    }),
  });
  if (!response.ok) throw new Error("Failed to analyze progression");
  return response.json();
}

export async function compareCareerPaths(data) {
  const response = await fetch(`${API_BASE_URL}/compare_career_paths`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to compare paths");
  return response.json();
}

export async function getSkillDetails(skillId) {
  const response = await fetch(`${API_BASE_URL}/skill_details/${skillId}`);
  if (!response.ok) throw new Error("Failed to fetch skill details");
  return response.json();
}
