import React from 'react';
import { Sparkles } from 'lucide-react';

interface Props {
  onSelectPrompt: (prompt: string) => void;
}

export const SuggestionChips: React.FC<Props> = ({ onSelectPrompt }) => {
  const suggestions = [
    { title: 'LNO Framework', prompt: "What is Shreyas Doshi's LNO framework for time management?" },
    { title: 'Product-Led Growth', prompt: 'How does Elena Verna define Product-Led Growth loops?' },
    { title: 'DHM Model', prompt: "What is Gibson Biddle's DHM framework for Netflix product strategy?" },
    { title: 'Four Growth Fits', prompt: "Explain Brian Balfour's Four Growth Fits model." },
    { title: 'Growth Loops', prompt: 'Why does Casey Winters prefer growth loops over acquisition funnels?' },
    { title: 'Empowered Teams', prompt: 'How does Marty Cagan distinguish empowered product teams from feature factories?' },
  ];

  return (
    <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-2xl mb-4">
      <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 mb-2.5">
        <Sparkles className="w-3.5 h-3.5" />
        <span>Grounded PM & Growth Queries</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {suggestions.map((s, i) => (
          <button
            key={i}
            onClick={() => onSelectPrompt(s.prompt)}
            className="text-left p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-amber-500/40 transition-all text-xs text-slate-300 hover:text-white group"
          >
            <div className="font-semibold text-amber-400/90 group-hover:text-amber-400 mb-0.5">{s.title}</div>
            <div className="text-[11px] text-slate-400 line-clamp-1">{s.prompt}</div>
          </button>
        ))}
      </div>
    </div>
  );
};
