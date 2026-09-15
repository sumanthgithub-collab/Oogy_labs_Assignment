export interface Citation {
  guest_name: string;
  episode_title: string;
  episode_id: string;
  timestamp?: string;
  snippet: string;
  relevance_score: number;
}

export interface Artifact {
  id: string;
  session_id: string;
  message_id?: string;
  title: string;
  artifact_type: 'markdown' | 'html' | 'essay';
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations: Citation[];
  created_at: string;
  artifacts?: Artifact[];
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ModelConfig {
  provider: 'ollama' | 'anthropic' | 'openai' | 'mock';
  model_name: string;
  status: string;
  available_providers: string[];
}
