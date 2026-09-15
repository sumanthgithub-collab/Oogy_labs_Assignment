import React, { useState, useRef, useEffect } from 'react';
import type { Message, Artifact, ModelConfig } from '../types';
import { Send, Bot, User, Sparkles, Code, FileText, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { CitationBadge } from './CitationBadge';
import { SuggestionChips } from './SuggestionChips';

interface Props {
  messages: Message[];
  onSendMessage: (prompt: string, forceArtifact?: 'essay' | 'html') => Promise<void>;
  loading: boolean;
  onSelectArtifact: (art: Artifact) => void;
  selectedArtifactId?: string;
  modelConfig: ModelConfig | null;
  onGenerateArtifact: (msgId: string, type: 'essay' | 'html', topic: string) => Promise<void>;
}

export const ChatInterface: React.FC<Props> = ({
  messages,
  onSendMessage,
  loading,
  onSelectArtifact,
  selectedArtifactId,
  modelConfig,
  onGenerateArtifact,
}) => {
  const [inputPrompt, setInputPrompt] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || loading) return;
    const p = inputPrompt;
    setInputPrompt('');
    onSendMessage(p);
  };

  return (
    <div className="flex-1 h-full flex flex-col bg-slate-950 min-w-0">
      {/* Header */}
      <div className="px-6 py-3 border-b border-slate-800/80 bg-slate-900/60 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Lenny Growth Advisor</h2>
            <p className="text-[11px] text-slate-400">Grounded in Lenny's Podcast Transcripts</p>
          </div>
        </div>

        {modelConfig && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-semibold uppercase text-amber-400 text-[10px]">{modelConfig.provider}</span>
            <span className="text-slate-400 font-mono text-[11px]">{modelConfig.model_name}</span>
          </div>
        )}
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="max-w-3xl mx-auto py-12">
            <div className="text-center mb-8">
              <div className="inline-flex p-3 rounded-2xl bg-amber-500/10 text-amber-400 mb-3">
                <Sparkles className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Welcome to The Lenny Growth Assistant</h3>
              <p className="text-sm text-slate-400 max-w-lg mx-auto">
                Ask tactical questions about Product Management, PLG, Growth Loops, and Leadership. Answers are strictly grounded in Lenny's Podcast transcripts with full citations.
              </p>
            </div>
            <SuggestionChips onSelectPrompt={(p) => onSendMessage(p)} />
          </div>
        ) : (
          messages.map((m) => {
            const isUser = m.role === 'user';
            return (
              <div key={m.id} className={`flex gap-4 max-w-4xl mx-auto ${isUser ? 'justify-end' : 'justify-start'}`}>
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div className={`space-y-3 max-w-2xl ${isUser ? 'order-1' : 'order-2'}`}>
                  <div
                    className={`p-4 rounded-2xl text-sm leading-relaxed ${
                      isUser
                        ? 'bg-amber-500 text-slate-950 font-medium rounded-tr-none shadow-lg shadow-amber-500/10'
                        : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none shadow-md'
                    }`}
                  >
                    {isUser ? (
                      <p>{m.content}</p>
                    ) : (
                      <div className="prose prose-invert prose-amber max-w-none text-slate-200 text-xs sm:text-sm">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                      </div>
                    )}

                    {!isUser && <CitationBadge citations={m.citations} />}
                  </div>

                  {/* Generated Artifact Badges / Actions */}
                  {!isUser && (
                    <div className="flex flex-wrap items-center gap-2 pt-1">
                      {m.artifacts &&
                        m.artifacts.map((art) => (
                          <button
                            key={art.id}
                            onClick={() => onSelectArtifact(art)}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                              selectedArtifactId === art.id
                                ? 'bg-amber-500/20 border-amber-500 text-amber-400'
                                : 'bg-slate-900/90 border-slate-700/80 text-slate-300 hover:border-amber-500/40 hover:text-white'
                            }`}
                          >
                            <FileText className="w-3.5 h-3.5 text-amber-400" />
                            <span>{art.title}</span>
                            <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 uppercase">
                              {art.artifact_type}
                            </span>
                          </button>
                        ))}

                      {/* Action Triggers for quick artifact creation */}
                      <button
                        onClick={() => onGenerateArtifact(m.id, 'essay', m.content.slice(0, 50))}
                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-[11px] text-slate-400 hover:text-amber-400 transition-colors"
                      >
                        <Sparkles className="w-3 h-3" /> Ship 30 Essay
                      </button>
                      <button
                        onClick={() => onGenerateArtifact(m.id, 'html', m.content.slice(0, 50))}
                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-[11px] text-slate-400 hover:text-amber-400 transition-colors"
                      >
                        <Code className="w-3 h-3" /> Visual Card
                      </button>
                    </div>
                  )}
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })
        )}

        {loading && (
          <div className="flex gap-4 max-w-4xl mx-auto">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 animate-bounce" />
            </div>
            <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
              <span>Searching transcript knowledge base and synthesizing grounded answer...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            placeholder="Ask Lenny Growth Assistant (e.g. Shreyas Doshi LNO, Elena Verna PLG loops)..."
            disabled={loading}
            className="w-full py-3.5 pl-4 pr-12 rounded-2xl bg-slate-900 border border-slate-700/80 focus:border-amber-500 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-1 focus:ring-amber-500/50 shadow-inner"
          />
          <button
            type="submit"
            disabled={!inputPrompt.trim() || loading}
            className="absolute right-2 p-2 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-bold transition-all shadow-md shadow-amber-500/10"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
