import React, { memo } from 'react';
import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  type EdgeProps,
} from '@xyflow/react';
import { cn } from '@/lib/utils';

export interface MindmapEdgeData {
  relationshipType?: string;
  label?: string | null;
}

export const MindmapEdge = memo(({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  selected,
  data,
}: EdgeProps): React.JSX.Element => {
  const edgeData = data as unknown as MindmapEdgeData;

  // Calculate smooth horizontal Bezier S-curve
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    curvature: 0.25,
  });

  return (
    <>
      {/* Invisible wider stroke for easier click/hover interaction */}
      <path
        d={edgePath}
        fill="none"
        strokeOpacity={0}
        strokeWidth={16}
        className="react-flow__edge-interaction cursor-pointer"
      />

      {/* Visible Smooth Bezier Edge */}
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: selected ? 2.5 : 2,
          stroke: selected ? '#3978D5' : '#94A3B8',
          transition: 'stroke 0.2s ease, stroke-width 0.2s ease',
        }}
      />

      {/* Optional HTML Relationship Label Badge */}
      {edgeData?.label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="nodrag nopan"
          >
            <span
              className={cn(
                'px-2 py-0.5 rounded-full text-[10px] font-medium tracking-tight shadow-subtle border transition-colors',
                selected
                  ? 'bg-brand-blue text-white border-brand-blue'
                  : 'bg-white text-slate-600 border-border hover:border-slate-400'
              )}
            >
              {edgeData.label}
            </span>
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
});

MindmapEdge.displayName = 'MindmapEdge';
