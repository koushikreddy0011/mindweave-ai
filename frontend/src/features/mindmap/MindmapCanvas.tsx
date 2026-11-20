import React, { useCallback, useEffect } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type NodeMouseHandler,
  type OnNodeDrag,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { MindmapNode } from './components/MindmapNode';
import { MindmapEdge } from './components/MindmapEdge';

// Static nodeTypes mapping declared OUTSIDE component to prevent remount flickering
const nodeTypes = {
  mindmapNode: MindmapNode,
  root: MindmapNode,
  category: MindmapNode,
  concept: MindmapNode,
  detail: MindmapNode,
};

// Static edgeTypes mapping declared OUTSIDE component
const edgeTypes = {
  mindmapEdge: MindmapEdge,
};

export interface MindmapCanvasProps {
  initialNodes: Node[];
  initialEdges: Edge[];
  onNodeClick?: (nodeId: string) => void;
  onNodeDragStop?: (nodeId: string, position: { x: number; y: number }) => void;
  selectedNodeId?: string | null;
  focusedNodeId?: string | null;
}

// Inner canvas controller utilizing useReactFlow hooks
function CanvasInner({
  initialNodes,
  initialEdges,
  onNodeClick,
  onNodeDragStop,
  focusedNodeId,
}: MindmapCanvasProps): React.JSX.Element {
  const [nodes, setNodes, onNodesChange]: [
    Node[],
    React.Dispatch<React.SetStateAction<Node[]>>,
    OnNodesChange<Node>
  ] = useNodesState(initialNodes);
  const [edges, , onEdgesChange]: [Edge[], unknown, OnEdgesChange<Edge>] =
    useEdgesState(initialEdges);

  const { setCenter, getNode } = useReactFlow();

  // Keep nodes in sync if initialNodes change (e.g. Reset Layout)
  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  // Smoothly center the camera when focused from outline
  useEffect(() => {
    if (focusedNodeId) {
      const node = getNode(focusedNodeId);
      if (node) {
        setCenter(node.position.x + 90, node.position.y + 35, {
          zoom: 1.15,
          duration: 600,
        });
      }
    }
  }, [focusedNodeId, setCenter, getNode]);

  const handleNodeClick: NodeMouseHandler = useCallback(
    (_, node) => {
      if (onNodeClick) {
        onNodeClick(node.id);
      }
    },
    [onNodeClick]
  );

  // Capture position when user stops dragging
  const handleNodeDragStop: OnNodeDrag = useCallback(
    (_, node) => {
      if (onNodeDragStop) {
        onNodeDragStop(node.id, {
          x: Math.round(node.position.x),
          y: Math.round(node.position.y),
        });
      }
    },
    [onNodeDragStop]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={handleNodeClick}
      onNodeDragStop={handleNodeDragStop}
      fitView
      fitViewOptions={{ padding: 0.25 }}
      minZoom={0.2}
      maxZoom={2}
      defaultEdgeOptions={{
        type: 'mindmapEdge',
      }}
      proOptions={{ hideAttribution: true }}
    >
      {/* Subtle Dots Background */}
      <Background
        variant={BackgroundVariant.Dots}
        gap={24}
        size={1.5}
        color="#CBD5E1"
      />

      {/* Viewport Zoom & Pan Controls */}
      <Controls
        className="bg-white border border-border shadow-subtle rounded-lg overflow-hidden m-4"
        showInteractive={false}
      />

      {/* MiniMap Radar */}
      <MiniMap
        className="bg-white/90 backdrop-blur-sm border border-border shadow-subtle rounded-xl overflow-hidden m-4 hidden sm:block"
        nodeColor={(n) => {
          const depth = Number(n.data?.depth ?? 0);
          if (depth === 0) return '#172B4D'; // Navy root
          if (depth === 1) return '#3978D5'; // Blue category
          return '#805AD5'; // Purple concept
        }}
        maskColor="rgba(244, 246, 250, 0.7)"
        nodeStrokeWidth={3}
        zoomable
        pannable
      />
    </ReactFlow>
  );
}

// Export canvas wrapped in ReactFlowProvider
export function MindmapCanvas(props: MindmapCanvasProps): React.JSX.Element {
  return (
    <div className="w-full h-full relative select-none bg-brand-canvas">
      <ReactFlowProvider>
        <CanvasInner {...props} />
      </ReactFlowProvider>
    </div>
  );
}
