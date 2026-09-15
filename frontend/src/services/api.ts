import type { Session, Message, ModelConfig, Artifact } from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

export async function fetchHealth() {
  const res = await fetch('http://localhost:8000/health');
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error('Failed to fetch sessions');
  return res.json();
}

export async function createSession(title?: string): Promise<Session> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: title || 'New Growth Conversation' }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function deleteSession(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete session');
}

export async function fetchSessionMessages(sessionId: string): Promise<Message[]> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
  if (!res.ok) throw new Error('Failed to fetch messages');
  return res.json();
}

export async function sendChatMessage(
  sessionId: string,
  prompt: string,
  forceArtifact?: 'essay' | 'html' | 'markdown'
): Promise<Message> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, prompt, force_artifact: forceArtifact }),
  });
  if (!res.ok) throw new Error('Failed to send chat message');
  return res.json();
}

export async function fetchModelConfig(): Promise<ModelConfig> {
  const res = await fetch(`${API_BASE}/config/model`);
  if (!res.ok) throw new Error('Failed to fetch model config');
  return res.json();
}

export async function updateModelConfig(provider: string, modelName?: string): Promise<ModelConfig> {
  const res = await fetch(`${API_BASE}/config/model`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, model_name: modelName }),
  });
  if (!res.ok) throw new Error('Failed to update model config');
  return res.json();
}

export async function fetchArtifact(artifact_id: string): Promise<Artifact> {
  const res = await fetch(`${API_BASE}/artifacts/${artifact_id}`);
  if (!res.ok) throw new Error('Failed to fetch artifact');
  return res.json();
}

export async function fetchSessionArtifacts(sessionId: string): Promise<Artifact[]> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/artifacts`);
  if (!res.ok) throw new Error('Failed to fetch session artifacts');
  return res.json();
}

export async function generateArtifact(
  sessionId: string,
  messageId: string,
  artifactType: 'essay' | 'html',
  topic: string
): Promise<Artifact> {
  const res = await fetch(`${API_BASE}/artifacts/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message_id: messageId,
      artifact_type: artifactType,
      topic,
    }),
  });
  if (!res.ok) throw new Error('Failed to generate artifact');
  return res.json();
}
