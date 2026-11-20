import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Sparkles, 
  CheckCircle2, 
  Code2, 
  Briefcase, 
  Layers, 
  Tag, 
  Loader2, 
  AlertCircle, 
  X,
  RotateCcw
} from 'lucide-react';
import { type Node } from '@xyflow/react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { mindmapApi } from '@/lib/api/mindmaps';
import { DEMO_EXPLANATIONS } from '../lib/demoExplanations';
import type { NodeExplanation } from '@/types';
import type { MindmapNodeData } from './MindmapNode';

interface KnowledgePanelProps {
  selectedNode: Node | null;
  onClose: () => void;
  onSelectRelatedNode?: (nodeLabel: string) => void;
}

export function KnowledgePanel({
  selectedNode,
  onClose,
  onSelectRelatedNode,
}: KnowledgePanelProps): React.JSX.Element {
  const [explanation, setExplanation] = useState<NodeExplanation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryTrigger, setRetryTrigger] = useState(0);

  // In-memory client cache to prevent redundant network fetches
  const [cache, setCache] = useState<Record<string, NodeExplanation>>(DEMO_EXPLANATIONS);

  const nodeData = selectedNode?.data as unknown as MindmapNodeData | undefined;

  useEffect(() => {
    if (!selectedNode) {
      setExplanation(null);
      setError(null);
      return;
    }

    const nodeId = selectedNode.id;

    // Check in-memory cache first
    if (cache[nodeId]) {
      setExplanation(cache[nodeId]);
      setIsLoading(false);
      setError(null);
      return;
    }

    // Otherwise fetch or generate via API
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    const fetchExplanation = async (): Promise<void> => {
      try {
        const token = localStorage.getItem('access_token');

        // Offline / Demo fallback
        if (token === 'demo-session-token' || !token) {
          // Fallback template for nodes not in DEMO_EXPLANATIONS
          const fallback: NodeExplanation = {
            id: `exp-${nodeId}`,
            node_id: nodeId,
            overview: `${nodeData?.label || 'This concept'} represents a fundamental topic in this knowledge tree.`,
            detailed_explanation: `Detailed exploration of ${nodeData?.label || 'this concept'} highlighting theoretical architecture, mathematical formulation, and system design patterns.`,
            how_it_works: [
              `Input formulation and state initialization for ${nodeData?.label || 'the concept'}.`,
              'Algorithmic execution and progressive refinement.',
              'Validation and error measurement against target criteria.',
            ],
            examples: [
              `Standard reference implementation of ${nodeData?.label || 'this concept'}.`,
              'Production enterprise deployment pattern.',
            ],
            applications: [
              'High-throughput distributed systems.',
              'Real-time automated analytics pipelines.',
            ],
            key_concepts: ['Taxonomy', 'Optimization', 'Performance', 'Architecture'],
            related_concepts: ['Machine Learning', 'Data Processing'],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };

          if (isMounted) {
            setExplanation(fallback);
            setCache((prev) => ({ ...prev, [nodeId]: fallback }));
            setIsLoading(false);
          }
          return;
        }

        // Live API fetch
        const data = await mindmapApi.getNodeExplanation(nodeId);
        if (isMounted) {
          setExplanation(data);
          setCache((prev) => ({ ...prev, [nodeId]: data }));
          setIsLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load explanation');
          setIsLoading(false);
        }
      }
    };

    fetchExplanation();

    return () => {
      isMounted = false;
    };
  }, [selectedNode, cache, nodeData?.label, retryTrigger]);

  // Handle Retry
  const handleRetry = (): void => {
    if (!selectedNode) return;
    setError(null);
    setIsLoading(true);
    setCache((prev) => {
      const next = { ...prev };
      delete next[selectedNode.id];
      return next;
    });
    setRetryTrigger((prev) => prev + 1);
  };

  // State 1: Empty State
  if (!selectedNode) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center text-slate-400 select-none">
        <div className="w-12 h-12 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400 mb-3 shadow-subtle">
          <BookOpen size={22} />
        </div>
        <h4 className="text-sm font-semibold text-slate-700">No Concept Selected</h4>
        <p className="text-xs text-slate-400 mt-1 max-w-[200px] leading-relaxed">
          Click any node on the canvas or tree outline to inspect its live AI breakdown.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden select-text">
      
      {/* Panel Header */}
      <div className="p-4 border-b border-border flex items-center justify-between flex-shrink-0 bg-white">
        <div className="flex items-center gap-2">
          <BookOpen size={17} className="text-brand-purple" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-brand-navy">
            Knowledge Panel
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="purple" className="text-[10px] px-2 py-0.5">
            <Sparkles size={10} className="mr-1 text-brand-purple" />
            AI Grounded
          </Badge>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-100 transition-colors"
            title="Close Panel"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Panel Content Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        
        {/* Node Title & Depth Tag */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="blue" className="text-[10px]">
              Depth {nodeData?.depth ?? 0} {nodeData?.nodeType || 'Concept'}
            </Badge>
          </div>
          <h2 className="text-xl font-bold text-brand-navy tracking-tight leading-snug">
            {nodeData?.label || selectedNode.id}
          </h2>
          {Boolean(nodeData?.description) && (
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              {nodeData?.description}
            </p>
          )}
        </div>

        {/* State 2: Loading Skeleton */}
        {isLoading && (
          <div className="space-y-4 animate-pulse">
            <div className="p-4 rounded-xl bg-slate-100 border border-slate-200 space-y-2">
              <div className="h-3.5 bg-slate-200 rounded w-1/3" />
              <div className="h-3 bg-slate-200 rounded w-full" />
              <div className="h-3 bg-slate-200 rounded w-4/5" />
            </div>
            <div className="space-y-2">
              <div className="h-3.5 bg-slate-200 rounded w-1/4" />
              <div className="h-3 bg-slate-200 rounded w-full" />
              <div className="h-3 bg-slate-200 rounded w-5/6" />
              <div className="h-3 bg-slate-200 rounded w-2/3" />
            </div>
            <div className="flex items-center justify-center gap-2 py-6 text-xs text-slate-400">
              <Loader2 size={16} className="animate-spin text-brand-purple" />
              <span>Retrieving knowledge breakdown...</span>
            </div>
          </div>
        )}

        {/* State 3: Error State */}
        {error && !isLoading && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-xs space-y-2.5">
            <div className="flex items-center gap-2 text-red-700 font-semibold">
              <AlertCircle size={16} />
              <span>Explanation Failed</span>
            </div>
            <p className="text-red-600 leading-relaxed">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              className="text-xs text-red-700 border-red-300 hover:bg-red-100/50"
            >
              <RotateCcw size={12} className="mr-1.5" />
              Retry Generation
            </Button>
          </div>
        )}

        {/* State 4: Completed Content Breakdown */}
        {explanation && !isLoading && (
          <div className="space-y-6 text-xs text-slate-700 leading-relaxed">
            
            {/* Section 1: Concept Overview */}
            <div className="p-4 rounded-xl bg-brand-canvas border border-border space-y-1.5">
              <div className="flex items-center gap-1.5 text-brand-navy font-semibold text-xs">
                <Sparkles size={14} className="text-brand-purple" />
                <span>Overview</span>
              </div>
              <p className="text-slate-700 leading-relaxed">{explanation.overview}</p>
            </div>

            {/* Section 2: Detailed Explanation */}
            <div className="space-y-2">
              <h4 className="font-bold text-brand-navy text-xs uppercase tracking-wider">
                Detailed Explanation
              </h4>
              <p className="text-slate-600 leading-relaxed max-w-prose">
                {explanation.detailed_explanation}
              </p>
            </div>

            {/* Section 3: How It Works */}
            {explanation.how_it_works?.length > 0 && (
              <div className="space-y-2.5">
                <h4 className="font-bold text-brand-navy text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <Layers size={13} className="text-brand-blue" />
                  <span>How It Works</span>
                </h4>
                <ol className="space-y-2 pl-1">
                  {explanation.how_it_works.map((step, idx) => (
                    <li key={idx} className="flex items-start gap-2.5">
                      <span className="w-5 h-5 rounded-full bg-blue-50 text-brand-blue border border-blue-200 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span className="text-slate-600 leading-relaxed">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Section 4: Concrete Examples */}
            {explanation.examples?.length > 0 && (
              <div className="space-y-2.5">
                <h4 className="font-bold text-brand-navy text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <Code2 size={13} className="text-emerald-600" />
                  <span>Practical Examples</span>
                </h4>
                <div className="space-y-2">
                  {explanation.examples.map((example, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 font-mono text-[11px] leading-relaxed"
                    >
                      {example}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Section 5: Applications */}
            {explanation.applications?.length > 0 && (
              <div className="space-y-2.5">
                <h4 className="font-bold text-brand-navy text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <Briefcase size={13} className="text-brand-navy" />
                  <span>Real-World Applications</span>
                </h4>
                <ul className="space-y-1.5">
                  {explanation.applications.map((app, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-slate-600">
                      <CheckCircle2 size={14} className="text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{app}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Section 6: Key Concepts & Related Topics */}
            <div className="space-y-3 pt-2 border-t border-border">
              {explanation.key_concepts?.length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                    <Tag size={12} />
                    Key Concepts
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {explanation.key_concepts.map((concept, idx) => (
                      <Badge key={idx} variant="outline" className="text-[11px]">
                        {concept}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {explanation.related_concepts?.length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                    <Sparkles size={12} className="text-brand-purple" />
                    Related Topics (Click to explore)
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {explanation.related_concepts.map((related, idx) => (
                      <button
                        key={idx}
                        onClick={() => onSelectRelatedNode?.(related)}
                        className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium bg-purple-50 text-brand-purple border border-purple-200 hover:bg-brand-purple hover:text-white transition-colors"
                      >
                        {related} &rarr;
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
