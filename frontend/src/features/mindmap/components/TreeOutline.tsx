import React, { useState, useMemo, useEffect, useRef } from 'react';
import { 
  ChevronRight, 
  ChevronDown, 
  Search, 
  Layers, 
  Network, 
  X,
  Target
} from 'lucide-react';
import { type Node } from '@xyflow/react';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import type { MindmapNodeData } from './MindmapNode';

interface TreeOutlineProps {
  nodes: Node[];
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
  onFocusNode: (nodeId: string) => void;
  onClose?: () => void;
}

export function TreeOutline({
  nodes,
  selectedNodeId,
  onSelectNode,
  onFocusNode,
  onClose,
}: TreeOutlineProps): React.JSX.Element {
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedBranches, setCollapsedBranches] = useState<Record<string, boolean>>({});
  const activeItemRef = useRef<HTMLDivElement>(null);

  // Auto-scroll selected item into view in outline
  useEffect(() => {
    if (activeItemRef.current) {
      activeItemRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [selectedNodeId]);

  const toggleBranch = (nodeId: string, e: React.MouseEvent): void => {
    e.stopPropagation();
    setCollapsedBranches((prev) => ({
      ...prev,
      [nodeId]: !prev[nodeId],
    }));
  };

  // Filter nodes based on search query
  const filteredNodes = useMemo(() => {
    if (!searchQuery.trim()) return nodes;
    const query = searchQuery.toLowerCase();
    return nodes.filter((n) => {
      const data = n.data as unknown as MindmapNodeData;
      return (
        data.label.toLowerCase().includes(query) ||
        data.description?.toLowerCase().includes(query)
      );
    });
  }, [nodes, searchQuery]);

  return (
    <div className="h-full flex flex-col bg-white border-r border-border select-none overflow-hidden">
      
      {/* Outline Header */}
      <div className="p-3.5 border-b border-border flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2 text-slate-700">
          <Layers size={16} className="text-brand-blue" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-brand-navy">
            Outline ({nodes.length})
          </h3>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-100 transition-colors"
            title="Collapse Outline"
          >
            <X size={15} />
          </button>
        )}
      </div>

      {/* Search Filter */}
      <div className="p-2.5 border-b border-border/80 flex-shrink-0">
        <div className="relative">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Filter outline..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-8 pl-8 text-xs bg-slate-50 border-slate-200"
          />
        </div>
      </div>

      {/* Hierarchical Nodes List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {filteredNodes.map((node) => {
          const data = node.data as unknown as MindmapNodeData;
          const isSelected = selectedNodeId === node.id;
          const isCollapsed = !!collapsedBranches[node.id];
          const hasChildren = (data.childCount || 0) > 0;
          const depth = data.depth || 0;

          return (
            <div
              key={node.id}
              ref={isSelected ? activeItemRef : null}
              onClick={() => onSelectNode(node.id)}
              className={cn(
                'group flex items-center justify-between px-2 py-1.5 rounded-lg text-xs cursor-pointer transition-all',
                isSelected
                  ? 'bg-brand-blue/10 text-brand-blue font-semibold shadow-subtle'
                  : 'text-slate-700 hover:bg-slate-100/80 hover:text-slate-900'
              )}
              style={{ paddingLeft: `${depth * 14 + 8}px` }}
            >
              <div className="flex items-center gap-1.5 overflow-hidden flex-1">
                {/* Branch fold toggle or bullet */}
                {hasChildren ? (
                  <button
                    onClick={(e) => toggleBranch(node.id, e)}
                    className="p-0.5 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-200/60 transition-colors flex-shrink-0"
                  >
                    {isCollapsed ? <ChevronRight size={13} /> : <ChevronDown size={13} />}
                  </button>
                ) : (
                  <span className="w-3.5 h-3.5 flex items-center justify-center flex-shrink-0 text-slate-300">
                    •
                  </span>
                )}

                {/* Node Label */}
                <span className="truncate">{data.label}</span>
              </div>

              {/* Action & Metadata Badges */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onFocusNode(node.id);
                  }}
                  className="p-1 rounded text-slate-400 hover:text-brand-blue hover:bg-blue-50 transition-colors"
                  title="Center on Canvas"
                >
                  <Target size={12} />
                </button>
              </div>

              {/* Static Depth Badges */}
              {depth === 0 && (
                <Badge variant="navy" className="text-[9px] px-1 py-0 ml-1">Root</Badge>
              )}
            </div>
          );
        })}

        {filteredNodes.length === 0 && (
          <div className="p-4 text-center text-xs text-slate-400">
            No concepts match &ldquo;{searchQuery}&rdquo;
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-2.5 border-t border-border bg-slate-50/50 text-[11px] text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-1">
          <Network size={12} className="text-brand-blue" />
          Synchronized
        </span>
        <span>Click Target to center</span>
      </div>

    </div>
  );
}
