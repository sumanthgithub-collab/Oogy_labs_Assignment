import React from 'react';
import type { Session, ModelConfig } from '../types';
import { Plus, MessageSquare, Trash2, Sparkles } from 'lucide-react';
import { ModelSelector } from './ModelSelector';

interface Props {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  modelConfig: ModelConfig | null;
  onUpdateModelConfig: (provider: string, modelName?: string) => Promise<void>;
}

export const Sidebar: React.FC<Props> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  modelConfig,
  onUpdateModelConfig,
}) => {
  return (
    <div className="w-80 h-full bg-slate-900/95 border-r border-slate-800 flex flex-col justify-between p-4 z-10">
      <div className="flex flex-col h-full min-h-0">
        {/* Logo / Header */}
        <div className="flex items-center gap-3 pb-4 mb-3 border-b border-slate-800">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-600 text-slate-950 shadow-lg shadow-amber-500/20">
            <Sparkles className="w-5 h-5 font-bold" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight">Lenny Growth Assistant</h1>
            <p className="text-[11px] text-amber-400/90 font-medium">Grounded PM & Growth RAG</p>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          onClick={onNewSession}
          className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-amber-500/10 mb-4"
        >
          <Plus className="w-4 h-4" /> New Conversation
        </button>

        {/* Sessions List */}
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-1 mb-2">
          Recent Sessions ({sessions.length})
        </div>

        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 custom-scrollbar">
          {sessions.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500">No conversations yet</div>
          ) : (
            sessions.map((s) => {
              const isActive = s.id === activeSessionId;
              return (
                <div
                  key={s.id}
                  onClick={() => onSelectSession(s.id)}
                  className={`group relative flex items-center justify-between p-2.5 rounded-xl cursor-pointer transition-all border ${
                    isActive
                      ? 'bg-slate-800 border-amber-500/40 text-slate-100 shadow-md'
                      : 'border-transparent hover:bg-slate-800/50 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 pr-6">
                    <MessageSquare className={`w-4 h-4 shrink-0 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
                    <span className="text-xs font-medium truncate">{s.title}</span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(s.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-all absolute right-2"
                    title="Delete session"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Model Selector at Bottom */}
      <div className="pt-3 border-t border-slate-800">
        <ModelSelector config={modelConfig} onUpdateConfig={onUpdateModelConfig} />
      </div>
    </div>
  );
};
