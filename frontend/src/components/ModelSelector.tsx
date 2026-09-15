import React, { useState } from 'react';
import type { ModelConfig } from '../types';
import { ChevronDown, Check, Zap, Server, Shield, Sparkles } from 'lucide-react';

interface Props {
  config: ModelConfig | null;
  onUpdateConfig: (provider: string, modelName?: string) => Promise<void>;
}

export const ModelSelector: React.FC<Props> = ({ config, onUpdateConfig }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!config) return null;

  const providers = [
    { id: 'ollama', name: 'Ollama (Local)', desc: 'Local hardware LLM instance', icon: Server, badge: 'Local Demo' },
    { id: 'anthropic', name: 'Anthropic Claude', desc: 'Claude 3.5 Sonnet cloud LLM', icon: Sparkles, badge: 'Cloud' },
    { id: 'openai', name: 'OpenAI GPT', desc: 'GPT-4o / GPT-4o-mini cloud LLM', icon: Zap, badge: 'Cloud' },
    { id: 'mock', name: 'Mock Fallback', desc: 'Deterministic mock provider', icon: Shield, badge: 'Test Mode' },
  ];

  const currentProvider = providers.find((p) => p.id === config.provider) || providers[0];
  const IconComp = currentProvider.icon;

  const handleSelect = async (providerId: string) => {
    setIsOpen(false);
    await onUpdateConfig(providerId, undefined);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 transition-all text-left group"
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 group-hover:bg-amber-500/20 transition-colors">
            <IconComp className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-slate-200 truncate flex items-center gap-1.5">
              {currentProvider.name}
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-700 text-amber-400 font-medium">
                {currentProvider.badge}
              </span>
            </div>
            <div className="text-[11px] text-slate-400 truncate">{config.model_name}</div>
          </div>
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute left-0 right-0 bottom-full mb-2 bg-slate-900 border border-slate-700/90 rounded-xl shadow-2xl p-2 z-50 animate-in fade-in slide-in-from-bottom-2">
          <div className="text-[11px] font-semibold text-slate-400 px-2 py-1 uppercase tracking-wider">
            Switch LLM Provider
          </div>

          <div className="space-y-1 mt-1">
            {providers.map((p) => {
              const PIcon = p.icon;
              const isSelected = p.id === config.provider;
              return (
                <button
                  key={p.id}
                  onClick={() => handleSelect(p.id)}
                  className={`w-full text-left p-2 rounded-lg flex items-center justify-between transition-colors ${
                    isSelected ? 'bg-amber-500/10 border border-amber-500/30' : 'hover:bg-slate-800/80'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <PIcon className={`w-4 h-4 ${isSelected ? 'text-amber-400' : 'text-slate-400'}`} />
                    <div>
                      <div className="text-xs font-medium text-slate-200">{p.name}</div>
                      <div className="text-[10px] text-slate-400">{p.desc}</div>
                    </div>
                  </div>
                  {isSelected && <Check className="w-3.5 h-3.5 text-amber-400" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
