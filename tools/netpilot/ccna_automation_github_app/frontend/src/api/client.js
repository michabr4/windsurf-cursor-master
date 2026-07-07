const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function asJson(response) {
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchStudyPlan(profile) {
  const res = await fetch(`${API_BASE}/api/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  });
  return asJson(res);
}

export async function fetchFlashcards(domain) {
  const query = domain ? `?domain=${encodeURIComponent(domain)}` : '';
  const res = await fetch(`${API_BASE}/api/flashcards${query}`);
  return asJson(res);
}

export async function fetchWeakAreas(results) {
  const res = await fetch(`${API_BASE}/api/weak-areas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(results),
  });
  return asJson(res);
}

export async function fetchPracticeQuestions(domain) {
  const query = domain ? `?domain=${encodeURIComponent(domain)}` : '';
  const res = await fetch(`${API_BASE}/api/practice-questions${query}`);
  return asJson(res);
}

export async function fetchSourcePackage() {
  const res = await fetch(`${API_BASE}/api/source-package`);
  return asJson(res);
}
