import React, { useState } from 'react';
import type { Citation } from '../types';
import { Quote, X } from 'lucide-react';

interface Props {
  citations: Citation[];
}

export const CitationBadge: React.FC<Props> = ({ citations }) => {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-800/80">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 mb-2">
        <Quote className="w-3.5 h-3.5" />
        <span>Grounded Sources ({citations.length})</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {citations.map((c, i) => (
          <button
            key={i}
            onClick={() => setSelectedCitation(c)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/90 hover:bg-slate-700/80 border border-slate-700/80 text-[11px] text-slate-300 transition-all hover:scale-105"
          >
            <span className="font-semibold text-amber-400">{c.guest_name}</span>
            <span className="text-slate-400 text-[10px]">@{c.timestamp}</span>
            <span className="px-1 py-0.5 rounded bg-amber-500/10 text-amber-400 text-[9px] font-mono">
              {(c.relevance_score * 100).toFixed(0)}%
            </span>
          </button>
        ))}
      </div>

      {selectedCitation && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700/90 rounded-2xl max-w-lg w-full p-5 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="text-sm font-bold text-amber-400">{selectedCitation.guest_name}</div>
                <div className="text-xs font-medium text-slate-200 mt-0.5">{selectedCitation.episode_title}</div>
                <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-2">
                  <span>Timestamp: {selectedCitation.timestamp}</span>
                  <span>•</span>
                  <span>Relevance: {(selectedCitation.relevance_score * 100).toFixed(1)}%</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedCitation(null)}
                className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed max-h-60 overflow-y-auto">
              "{selectedCitation.snippet}"
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setSelectedCitation(null)}
                className="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold text-xs transition-colors"
              >
                Close Citation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
