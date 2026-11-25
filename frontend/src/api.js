/**
 * API client communicating with PodResearch 2.0 Backend
 */

const API_BASE = '/api';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function generateArticle(payload) {
  const res = await fetch(`${API_BASE}/sessions/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to start generation');
  }
  return res.json();
}

export async function getSession(sessionId) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error(`Failed to fetch session ${sessionId}`);
  return res.json();
}

export async function saveHumanReview(sessionId, decisions, directArticleEdits = null) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/human-review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      decisions,
      direct_article_edits: directArticleEdits,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to save review decisions');
  }
  return res.json();
}

export async function requestRevision(sessionId, selectedFeedback, directArticleEdits, additionalInstructions = "") {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/revise`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_feedback: selectedFeedback,
      direct_article_edits: directArticleEdits,
      additional_instructions: additionalInstructions,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to trigger revision');
  }
  return res.json();
}

export async function approveArticle(sessionId, finalArticle, reviewerNotes = "") {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      final_article: finalArticle,
      editor_notes: reviewerNotes,
      reviewer_notes: reviewerNotes,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to approve article');
  }
  return res.json();
}

export async function publishToMedium(sessionId, payload) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/publish/medium`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to publish to Medium');
  }
  return res.json();
}

export async function publishToDevto(sessionId, payload) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/publish/devto`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to publish to Dev.to');
  }
  return res.json();
}
