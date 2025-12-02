// Point directly to the backend API (running on port 3000 by default).
// You can override this via REACT_APP_MATCHER_API_BASE in your env if needed.
const BASE_URL =
  process.env.REACT_APP_MATCHER_API_BASE || 'http://localhost:3000/api/scholarships';

export async function requestMatches(profile, options = {}) {
  const { topN = 5, matchType } = options;

  const response = await fetch(`${BASE_URL}/match?topN=${topN}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ...profile,
      match_type: matchType,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message = errorBody?.message || 'Failed to fetch recommendations.';
    throw new Error(message);
  }

  const payload = await response.json();
  const matches = payload.matches || [];

  if (!matchType) {
    return matches;
  }

  return matches.filter((item) => {
    if (!item?.record_type) {
      return false;
    }
    return item.record_type.toLowerCase() === matchType.toLowerCase();
  });
}


