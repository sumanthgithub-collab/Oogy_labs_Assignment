import { useState, useEffect } from 'react';
import type { Session, Message, Artifact, ModelConfig } from './types';
import {
  fetchSessions,
  createSession,
  deleteSession,
  fetchSessionMessages,
  sendChatMessage,
  fetchModelConfig,
  updateModelConfig,
  generateArtifact,
} from './services/api';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { ArtifactViewer } from './components/ArtifactViewer';

export function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [modelConfig, setModelConfig] = useState<ModelConfig | null>(null);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Load Sessions and Model Config on mount
  useEffect(() => {
    loadSessions();
    loadModelConfig();
  }, []);

  // Load Messages when Active Session changes
  useEffect(() => {
    if (activeSessionId) {
      loadMessages(activeSessionId);
    } else {
      setMessages([]);
    }
  }, [activeSessionId]);

  const loadSessions = async () => {
    try {
      const list = await fetchSessions();
      setSessions(list);
      if (list.length > 0 && !activeSessionId) {
        setActiveSessionId(list[0].id);
      }
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const loadModelConfig = async () => {
    try {
      const cfg = await fetchModelConfig();
      setModelConfig(cfg);
    } catch (err) {
      console.error('Failed to load model config:', err);
    }
  };

  const loadMessages = async (sessionId: string) => {
    try {
      const msgs = await fetchSessionMessages(sessionId);
      setMessages(msgs);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleNewSession = async () => {
    try {
      const newSess = await createSession('New Growth Conversation');
      setSessions([newSess, ...sessions]);
      setActiveSessionId(newSess.id);
      setActiveArtifact(null);
    } catch (err) {
      console.error('Failed to create new session:', err);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      const remaining = sessions.filter((s) => s.id !== id);
      setSessions(remaining);
      if (activeSessionId === id) {
        setActiveSessionId(remaining.length > 0 ? remaining[0].id : null);
        setActiveArtifact(null);
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleSendMessage = async (prompt: string, forceArtifact?: 'essay' | 'html') => {
    let sessId = activeSessionId;
    if (!sessId) {
      const created = await createSession(prompt.slice(0, 35) + '...');
      setSessions([created, ...sessions]);
      setActiveSessionId(created.id);
      sessId = created.id;
    }

    // Optimistic UI user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: sessId,
      role: 'user',
      content: prompt,
      citations: [],
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const responseMsg = await sendChatMessage(sessId, prompt, forceArtifact);
      setMessages((prev) => [...prev.filter((m) => !m.id.startsWith('temp-')), tempUserMsg, responseMsg]);

      // If response generated artifacts, automatically open the first artifact in viewer
      if (responseMsg.artifacts && responseMsg.artifacts.length > 0) {
        setActiveArtifact(responseMsg.artifacts[0]);
      }
      loadSessions(); // Refresh titles/message counts
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateModelConfig = async (provider: string, modelName?: string) => {
    try {
      const updated = await updateModelConfig(provider, modelName);
      setModelConfig(updated);
    } catch (err) {
      console.error('Failed to update model config:', err);
    }
  };

  const handleGenerateArtifact = async (msgId: string, type: 'essay' | 'html', topic: string) => {
    if (!activeSessionId) return;
    setLoading(true);
    try {
      const art = await generateArtifact(activeSessionId, msgId, type, topic);
      setActiveArtifact(art);
      loadMessages(activeSessionId); // Refresh messages to attach artifact
    } catch (err) {
      console.error('Failed to generate artifact:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 font-sans text-slate-100 antialiased">
      {/* Left Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        modelConfig={modelConfig}
        onUpdateModelConfig={handleUpdateModelConfig}
      />

      {/* Center Chat View */}
      <ChatInterface
        messages={messages}
        onSendMessage={handleSendMessage}
        loading={loading}
        onSelectArtifact={setActiveArtifact}
        selectedArtifactId={activeArtifact?.id}
        modelConfig={modelConfig}
        onGenerateArtifact={handleGenerateArtifact}
      />

      {/* Right Artifact Viewer Side Panel */}
      {activeArtifact && (
        <ArtifactViewer artifact={activeArtifact} onClose={() => setActiveArtifact(null)} />
      )}
    </div>
  );
}
