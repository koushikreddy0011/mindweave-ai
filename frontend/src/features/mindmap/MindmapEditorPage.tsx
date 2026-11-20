import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Download, 
  Network, 
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  RotateCcw,
  CheckCircle2,
  Loader2,
  AlertCircle,
  BookOpen,
  FileText,
  FileCode
} from 'lucide-react';
import { type Node as FlowNode, type Edge } from '@xyflow/react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MindmapCanvas } from './MindmapCanvas';
import { TreeOutline } from './components/TreeOutline';
import { KnowledgePanel } from './components/KnowledgePanel';
import { adaptGraphToReactFlow, getDemoGraph } from './lib/graphAdapter';
import { mindmapApi, type PositionUpdateItem } from '@/lib/api/mindmaps';
import type { GraphData } from '@/types';

type SaveStatus = 'saved' | 'saving' | 'unsaved' | 'error';

export function MindmapEditorPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();

  // Main Graph Lifecycle State
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Panel collapse states
  const [isLeftPanelOpen, setIsLeftPanelOpen] = useState(true);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);

  // Selection & Focus states
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [focusedNodeId, setFocusedNodeId] = useState<string | null>(null);

  // Canvas elements state
  const [currentNodes, setCurrentNodes] = useState<FlowNode[]>([]);
  const [currentEdges, setCurrentEdges] = useState<Edge[]>([]);

  // Export dropdown state
  const [isExportMenuOpen, setIsExportMenuOpen] = useState(false);
  const exportMenuRef = useRef<HTMLDivElement>(null);

  // Auto-Save Status
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('saved');
  const pendingUpdatesRef = useRef<Map<string, PositionUpdateItem>>(new Map());
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Close export menu on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent): void {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target as globalThis.Node)) {
        setIsExportMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch or resolve mindmap graph data dynamically based on :id
  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setErrorMessage(null);

    const loadGraph = async (): Promise<void> => {
      const token = localStorage.getItem('access_token');

      // Demo Mode or Sample-ID preview
      if (id === 'sample-id' || token === 'demo-session-token' || !token) {
        const demoData = getDemoGraph(id);
        if (demoData) {
          if (isMounted) {
            setGraphData(demoData);
            const { nodes, edges } = adaptGraphToReactFlow(demoData);
            setCurrentNodes(nodes);
            setCurrentEdges(edges);
            setSelectedNodeId(demoData.mindmap.root_node_id || nodes[0]?.id || null);
            setIsLoading(false);
          }
        } else {
          if (isMounted) {
            setErrorMessage(`Mindmap "${id}" does not exist in your workspace.`);
            setIsLoading(false);
          }
        }
        return;
      }

      // Live Backend API call
      try {
        const liveData = await mindmapApi.getMindmapGraph(id as string);
        if (isMounted) {
          setGraphData(liveData);
          const { nodes, edges } = adaptGraphToReactFlow(liveData);
          setCurrentNodes(nodes);
          setCurrentEdges(edges);
          setSelectedNodeId(liveData.mindmap.root_node_id || nodes[0]?.id || null);
          setIsLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setErrorMessage(err instanceof Error ? err.message : 'Mindmap not found');
          setIsLoading(false);
        }
      }
    };

    loadGraph();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const selectedNode = currentNodes.find((n) => n.id === selectedNodeId) || null;

  // Dispatch debounced batch update
  const flushUpdates = useCallback(async (): Promise<void> => {
    if (pendingUpdatesRef.current.size === 0 || !graphData) return;

    const updates = Array.from(pendingUpdatesRef.current.values());
    pendingUpdatesRef.current.clear();
    setSaveStatus('saving');

    const token = localStorage.getItem('access_token');

    // Demo Mode mock save
    if (token === 'demo-session-token' || !token) {
      await new Promise((resolve) => setTimeout(resolve, 400));
      setSaveStatus('saved');
      return;
    }

    try {
      await mindmapApi.updateNodePositions(graphData.mindmap.id, updates);
      setSaveStatus('saved');
    } catch {
      setSaveStatus('error');
    }
  }, [graphData]);

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  // Handle node drag stop
  const handleNodeDragStop = useCallback(
    (nodeId: string, position: { x: number; y: number }): void => {
      setSaveStatus('unsaved');

      setCurrentNodes((prev) =>
        prev.map((n) => (n.id === nodeId ? { ...n, position } : n))
      );

      pendingUpdatesRef.current.set(nodeId, {
        node_id: nodeId,
        position_x: position.x,
        position_y: position.y,
      });

      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      debounceTimerRef.current = setTimeout(() => {
        flushUpdates();
      }, 600);
    },
    [flushUpdates]
  );

  // Focus node handler
  const handleFocusNode = (nodeId: string): void => {
    setSelectedNodeId(nodeId);
    setFocusedNodeId(nodeId);
    setTimeout(() => setFocusedNodeId(null), 50);
  };

  // Reset to original tree layout
  const handleResetLayout = (): void => {
    if (!graphData) return;
    const { nodes } = adaptGraphToReactFlow(graphData);
    setCurrentNodes(nodes);
    pendingUpdatesRef.current.clear();
    setSaveStatus('saved');
  };

  // Semantic search from related concept tags
  const handleSelectRelatedNode = (nodeLabel: string): void => {
    const target = currentNodes.find((n) => {
      const label = String(n.data?.label || '').toLowerCase();
      return (
        label.includes(nodeLabel.toLowerCase()) ||
        nodeLabel.toLowerCase().includes(label)
      );
    });
    if (target) {
      handleFocusNode(target.id);
    }
  };

  // Export as Markdown Outline
  const handleExportMarkdown = (): void => {
    if (!graphData) return;

    let md = `# ${graphData.mindmap.title}\n`;
    if (graphData.mindmap.description) {
      md += `> ${graphData.mindmap.description}\n\n`;
    }

    // Build indented tree representation
    const sortedNodes = [...graphData.nodes].sort((a, b) => a.depth - b.depth);
    for (const node of sortedNodes) {
      const indent = '  '.repeat(node.depth);
      md += `${indent}- **${node.label}**`;
      if (node.description) {
        md += `: ${node.description}`;
      }
      md += '\n';
    }

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${graphData.mindmap.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_outline.md`;
    link.click();
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  // Export as raw JSON
  const handleExportJSON = (): void => {
    if (!graphData) return;
    const jsonStr = JSON.stringify(graphData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${graphData.mindmap.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_graph.json`;
    link.click();
    URL.revokeObjectURL(url);
    setIsExportMenuOpen(false);
  };

  // Loading Screen
  if (isLoading) {
    return (
      <div className="h-screen w-screen bg-brand-canvas flex flex-col items-center justify-center p-6 text-center select-none">
        <div className="w-14 h-14 rounded-2xl bg-white border border-border shadow-subtle flex items-center justify-center text-brand-blue mb-4">
          <Network size={26} className="animate-pulse" />
        </div>
        <h3 className="text-base font-bold text-brand-navy">Loading Knowledge Map</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-xs leading-relaxed">
          Retrieving graph topology and 2D coordinates from database...
        </p>
        <Loader2 size={20} className="animate-spin text-brand-blue mt-4" />
      </div>
    );
  }

  // Error Screen
  if (errorMessage || !graphData) {
    return (
      <div className="h-screen w-screen bg-brand-canvas flex flex-col items-center justify-center p-6 text-center select-none">
        <div className="w-14 h-14 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center text-red-600 mb-4 shadow-subtle">
          <AlertCircle size={28} />
        </div>
        <h3 className="text-base font-bold text-slate-900">Mindmap Not Found</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-sm leading-relaxed">
          {errorMessage || 'The requested mindmap could not be located in your active workspace.'}
        </p>
        <div className="mt-6">
          <Link to="/dashboard">
            <Button variant="default" size="sm">
              <ArrowLeft size={14} className="mr-1.5" />
              Return to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-brand-canvas overflow-hidden">
      
      {/* Editor Top Toolbar */}
      <header className="h-14 bg-white border-b border-border px-4 flex items-center justify-between flex-shrink-0 z-10 shadow-subtle">
        
        {/* Left: Back & Title & Panels Toggle */}
        <div className="flex items-center gap-3">
          <Link to="/dashboard">
            <Button variant="ghost" size="sm" className="h-8 px-2 text-slate-600">
              <ArrowLeft size={16} className="mr-1" />
              Dashboard
            </Button>
          </Link>
          
          <div className="h-4 w-px bg-border" />

          {/* Left Outline Toggle */}
          <button
            onClick={() => setIsLeftPanelOpen(!isLeftPanelOpen)}
            className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            title={isLeftPanelOpen ? 'Collapse Outline' : 'Open Outline'}
          >
            {isLeftPanelOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
          </button>

          <div className="flex items-center gap-2">
            <Network size={18} className="text-brand-blue" />
            <h1 className="text-sm font-semibold text-brand-navy truncate max-w-xs sm:max-w-md">
              {graphData.mindmap.title}
            </h1>
            <Badge variant="blue" className="text-[10px]">
              {currentNodes.length} Nodes
            </Badge>

            {/* Ambient Auto-Save Indicator Pill */}
            <div className="flex items-center ml-2">
              {saveStatus === 'saved' && (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  <CheckCircle2 size={12} />
                  Saved
                </span>
              )}
              {saveStatus === 'saving' && (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-brand-blue bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                  <Loader2 size={12} className="animate-spin" />
                  Saving...
                </span>
              )}
              {saveStatus === 'unsaved' && (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                  Unsaved
                </span>
              )}
              {saveStatus === 'error' && (
                <button
                  onClick={flushUpdates}
                  className="inline-flex items-center gap-1 text-[11px] font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full border border-red-200 hover:bg-red-100 transition-colors"
                >
                  <AlertCircle size={12} />
                  Save Error (Retry)
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right: Actions & Export Menu */}
        <div className="flex items-center gap-2">
          {/* Reset Layout */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleResetLayout}
            className="h-8 text-xs text-slate-600"
            title="Reset positions to default calculated tree layout"
          >
            <RotateCcw size={13} className="mr-1.5" />
            Reset Layout
          </Button>

          {/* Export Dropdown */}
          <div className="relative" ref={exportMenuRef}>
            <Button
              variant="default"
              size="sm"
              onClick={() => setIsExportMenuOpen(!isExportMenuOpen)}
              className="h-8 bg-brand-blue hover:bg-brand-blue/90 text-white"
            >
              <Download size={13} className="mr-1.5" />
              Export
            </Button>

            {isExportMenuOpen && (
              <div className="absolute right-0 mt-1.5 w-48 bg-white rounded-xl shadow-elevated border border-border py-1 z-50 animate-in fade-in zoom-in-95 duration-100">
                <button
                  onClick={handleExportMarkdown}
                  className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left transition-colors"
                >
                  <FileText size={14} className="text-brand-blue" />
                  <div>
                    <div className="font-semibold">Markdown Outline</div>
                    <div className="text-[10px] text-slate-400">For Obsidian & Notion (.md)</div>
                  </div>
                </button>
                <button
                  onClick={handleExportJSON}
                  className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left transition-colors"
                >
                  <FileCode size={14} className="text-brand-purple" />
                  <div>
                    <div className="font-semibold">JSON Graph</div>
                    <div className="text-[10px] text-slate-400">Full schema nodes & edges (.json)</div>
                  </div>
                </button>
              </div>
            )}
          </div>

          <div className="h-4 w-px bg-border ml-1" />

          {/* Right Knowledge Panel Toggle */}
          <button
            onClick={() => setIsRightPanelOpen(!isRightPanelOpen)}
            className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            title={isRightPanelOpen ? 'Collapse Knowledge Panel' : 'Open Knowledge Panel'}
          >
            {isRightPanelOpen ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
          </button>
        </div>

      </header>

      {/* Three-Panel Canvas Layout */}
      <div className="flex-1 flex min-h-0 overflow-hidden relative">
        
        {/* Left Panel: Tree Outline */}
        <aside
          className={`h-full flex-shrink-0 transition-all duration-300 ease-in-out z-20 ${
            isLeftPanelOpen ? 'w-64' : 'w-0'
          }`}
        >
          {isLeftPanelOpen && (
            <TreeOutline
              nodes={currentNodes}
              selectedNodeId={selectedNodeId}
              onSelectNode={(nodeId) => setSelectedNodeId(nodeId)}
              onFocusNode={handleFocusNode}
              onClose={() => setIsLeftPanelOpen(false)}
            />
          )}
        </aside>

        {/* Floating Restore Pill for Left Panel */}
        {!isLeftPanelOpen && (
          <button
            onClick={() => setIsLeftPanelOpen(true)}
            className="absolute left-3 top-3 z-30 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white border border-border shadow-card text-xs text-slate-700 hover:bg-slate-50 transition-all"
            title="Open Outline"
          >
            <PanelLeftOpen size={14} className="text-brand-blue" />
            <span className="font-medium">Outline</span>
          </button>
        )}

        {/* Center Panel: Interactive React Flow Canvas */}
        <main className="flex-1 relative bg-brand-canvas h-full overflow-hidden">
          <MindmapCanvas
            initialNodes={currentNodes}
            initialEdges={currentEdges}
            onNodeClick={(nodeId) => setSelectedNodeId(nodeId)}
            onNodeDragStop={handleNodeDragStop}
            selectedNodeId={selectedNodeId}
            focusedNodeId={focusedNodeId}
          />
        </main>

        {/* Floating Restore Pill for Right Panel */}
        {!isRightPanelOpen && (
          <button
            onClick={() => setIsRightPanelOpen(true)}
            className="absolute right-3 top-3 z-30 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-white border border-border shadow-card text-xs text-slate-700 hover:bg-slate-50 transition-all"
            title="Open Knowledge Panel"
          >
            <BookOpen size={14} className="text-brand-purple" />
            <span className="font-medium">Knowledge</span>
          </button>
        )}

        {/* Right Panel: Knowledge Explanation */}
        <aside
          className={`h-full bg-white border-l border-border flex-shrink-0 transition-all duration-300 ease-in-out z-20 overflow-hidden ${
            isRightPanelOpen ? 'w-80' : 'w-0 border-l-0'
          }`}
        >
          {isRightPanelOpen && (
            <KnowledgePanel
              selectedNode={selectedNode}
              onClose={() => setIsRightPanelOpen(false)}
              onSelectRelatedNode={handleSelectRelatedNode}
            />
          )}
        </aside>

      </div>
    </div>
  );
}
