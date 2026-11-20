import React, { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { 
  Network, 
  Loader2, 
  AlertCircle, 
  Layers
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MindmapNodeData {
  label: string;
  description?: string | null;
  nodeType: 'root' | 'category' | 'concept' | 'detail';
  depth: number;
  generationStatus?: 'pending' | 'completed' | 'failed';
  childCount?: number;
}

export const MindmapNode = memo(({ data, selected }: NodeProps): React.JSX.Element => {
  const nodeData = data as unknown as MindmapNodeData;
  const { 
    label, 
    description, 
    nodeType = 'concept', 
    depth = 0, 
    generationStatus = 'completed',
    childCount = 0 
  } = nodeData;

  const isRoot = depth === 0 || nodeType === 'root';
  const isCategory = depth === 1 || nodeType === 'category';
  const isConcept = depth === 2 || nodeType === 'concept';
  const isDetail = depth >= 3 || nodeType === 'detail';

  const isGenerating = generationStatus === 'pending';
  const isFailed = generationStatus === 'failed';

  return (
    <div
      className={cn(
        // Base node styling
        'relative rounded-xl transition-all duration-200 select-none group',
        
        // Depth-specific visual identity
        isRoot && 'bg-brand-navy text-white border-2 border-slate-900 shadow-elevated min-w-[200px] max-w-[240px] p-4',
        isCategory && 'bg-white text-slate-900 border-2 border-brand-blue shadow-card hover:border-brand-blue/90 min-w-[190px] max-w-[220px] p-3.5',
        isConcept && 'bg-white text-slate-800 border-2 border-brand-purple/70 shadow-subtle hover:border-brand-purple min-w-[170px] max-w-[200px] p-3',
        isDetail && 'bg-white text-slate-700 border border-slate-300 shadow-subtle hover:border-slate-400 min-w-[150px] max-w-[180px] p-2.5',

        // Selection ring
        selected && 'ring-2 ring-brand-blue ring-offset-2 ring-offset-white shadow-elevated',

        // Status overrides
        isGenerating && 'border-amber-400 bg-amber-50/40 animate-pulse',
        isFailed && 'border-red-400 bg-red-50/50'
      )}
    >
      {/* Target Handle: Connects from parent (Root has no parent, so no left handle) */}
      {!isRoot && (
        <Handle
          type="target"
          position={Position.Left}
          className={cn(
            '!w-2.5 !h-2.5 !border-2 !border-white transition-colors',
            isCategory && '!bg-brand-blue',
            isConcept && '!bg-brand-purple',
            isDetail && '!bg-slate-500'
          )}
        />
      )}

      {/* Header: Node Type Tag or Status Indicator */}
      <div className="flex items-center justify-between gap-1.5 mb-1.5">
        <div className="flex items-center gap-1">
          {isRoot && (
            <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-blue-300">
              <Network size={12} className="text-brand-blue" />
              Root Concept
            </span>
          )}
          {isCategory && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-brand-blue border border-blue-200">
              Category
            </span>
          )}
          {isConcept && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-50 text-brand-purple border border-purple-200">
              Concept
            </span>
          )}
          {isDetail && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
              Detail
            </span>
          )}
        </div>

        {/* Dynamic Status Badges */}
        {isGenerating && (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-600 bg-amber-100/80 px-1.5 py-0.5 rounded">
            <Loader2 size={10} className="animate-spin" />
            AI Generating
          </span>
        )}
        {isFailed && (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-red-600 bg-red-100/80 px-1.5 py-0.5 rounded">
            <AlertCircle size={10} />
            Failed
          </span>
        )}
        {!isGenerating && !isFailed && childCount > 0 && (
          <span
            className={cn(
              'inline-flex items-center gap-0.5 text-[10px] font-mono px-1.5 py-0.5 rounded',
              isRoot ? 'bg-white/15 text-white' : 'bg-slate-100 text-slate-500'
            )}
          >
            <Layers size={9} />
            {childCount}
          </span>
        )}
      </div>

      {/* Main Node Label */}
      <h4
        className={cn(
          'leading-tight tracking-tight line-clamp-2',
          isRoot ? 'text-sm sm:text-base font-bold text-white' : 'text-xs sm:text-sm font-semibold text-slate-900',
          isDetail && 'font-medium text-xs'
        )}
      >
        {label}
      </h4>

      {/* Optional Short Description (Root and Categories) */}
      {description && (
        <p
          className={cn(
            'text-[11px] mt-1 line-clamp-1 leading-normal',
            isRoot ? 'text-slate-300' : 'text-slate-500'
          )}
        >
          {description}
        </p>
      )}

      {/* Source Handle: Connects to children on the right */}
      <Handle
        type="source"
        position={Position.Right}
        className={cn(
          '!w-2.5 !h-2.5 !border-2 !border-white transition-colors',
          isRoot && '!bg-brand-blue',
          isCategory && '!bg-brand-blue',
          isConcept && '!bg-brand-purple',
          isDetail && '!bg-slate-500'
        )}
      />
    </div>
  );
});

MindmapNode.displayName = 'MindmapNode';
