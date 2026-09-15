import React, { useState } from 'react';
import type { Artifact } from '../types';
import { FileText, Code, Eye, X, Copy, Check, Download, Shield, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Props {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<Props> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code' | 'metadata'>('preview');
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: artifact.artifact_type === 'html' ? 'text/html' : 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full lg:w-1/2 h-full bg-slate-900 border-l border-slate-800 flex flex-col shadow-2xl z-20 animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
            {artifact.artifact_type === 'html' ? (
              <Code className="w-5 h-5" />
            ) : artifact.artifact_type === 'essay' ? (
              <Sparkles className="w-5 h-5" />
            ) : (
              <FileText className="w-5 h-5" />
            )}
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-bold text-slate-100 truncate">{artifact.title}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 font-semibold uppercase tracking-wider">
                {artifact.artifact_type}
              </span>
              {artifact.artifact_type === 'html' && (
                <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-mono">
                  <Shield className="w-3 h-3" /> Sandboxed Iframe
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Header Actions */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleCopy}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            title="Copy Content"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
          <button
            onClick={handleDownload}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            title="Download Artifact"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 px-4 pt-3 border-b border-slate-800 bg-slate-900">
        <button
          onClick={() => setActiveTab('preview')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-t-lg transition-colors border-b-2 ${
            activeTab === 'preview'
              ? 'border-amber-500 text-amber-400 bg-slate-800/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Eye className="w-3.5 h-3.5" /> Preview
        </button>
        <button
          onClick={() => setActiveTab('code')}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-t-lg transition-colors border-b-2 ${
            activeTab === 'code'
              ? 'border-amber-500 text-amber-400 bg-slate-800/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Code className="w-3.5 h-3.5" /> Source Code
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden p-4 bg-slate-950">
        {activeTab === 'preview' && (
          <div className="w-full h-full rounded-xl overflow-hidden border border-slate-800 bg-slate-900">
            {artifact.artifact_type === 'html' ? (
              <iframe
                title={artifact.title}
                srcDoc={artifact.content}
                sandbox="allow-scripts"
                className="w-full h-full border-0 bg-slate-950"
              />
            ) : (
              <div className="w-full h-full p-6 overflow-y-auto prose prose-invert prose-amber max-w-none text-slate-200">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
              </div>
            )}
          </div>
        )}

        {activeTab === 'code' && (
          <pre className="w-full h-full p-4 bg-slate-900 border border-slate-800 rounded-xl overflow-auto font-mono text-xs text-slate-300">
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
};
