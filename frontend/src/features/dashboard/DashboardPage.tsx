import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  PlusCircle, 
  Sparkles, 
  Network, 
  Search, 
  Briefcase, 
  FolderPlus 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { MindmapCard } from './MindmapCard';
import { useWorkspaceStore } from '@/store/useWorkspaceStore';
import { useAuthStore } from '@/store/useAuthStore';

export function DashboardPage(): React.JSX.Element {
  const { user } = useAuthStore();
  const { 
    activeWorkspace, 
    mindmaps, 
    isLoadingMindmaps, 
    fetchWorkspaces 
  } = useWorkspaceStore();

  const [searchQuery, setSearchQuery] = useState('');

  // Fetch workspaces and active mindmaps on mount
  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  // Client-side real-time search filter
  const filteredMindmaps = useMemo(() => {
    if (!searchQuery.trim()) return mindmaps;
    const query = searchQuery.toLowerCase();
    return mindmaps.filter(
      (m) =>
        m.title.toLowerCase().includes(query) ||
        m.input_prompt?.toLowerCase().includes(query) ||
        m.description?.toLowerCase().includes(query)
    );
  }, [mindmaps, searchQuery]);

  return (
    <div className="space-y-8">
      
      {/* Welcome Hero Banner */}
      <div className="relative overflow-hidden p-6 sm:p-8 rounded-2xl bg-brand-navy text-white shadow-elevated">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/10 text-white text-xs backdrop-blur-sm">
            <Sparkles size={13} className="text-brand-purple" />
            <span>AI Knowledge Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome back, {user?.full_name?.split(' ')[0] || 'Explorer'} 👋
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Organize complex subjects into structured hierarchical mindmaps. Every concept contains contextual explanations, how-it-works breakdowns, and related topics.
          </p>
          <div className="pt-2">
            <Link to="/create">
              <Button variant="default" className="bg-brand-blue hover:bg-brand-blue/90 text-white font-medium shadow-md">
                <PlusCircle size={16} className="mr-2" />
                Create New Mindmap
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between text-slate-500">
              <CardDescription>Active Workspace</CardDescription>
              <Briefcase size={16} className="text-brand-blue" />
            </div>
            <CardTitle className="text-xl font-bold truncate">
              {activeWorkspace?.name || 'Personal Workspace'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-slate-500">
              {activeWorkspace?.description || 'Default workspace'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between text-slate-500">
              <CardDescription>Total Mindmaps</CardDescription>
              <Network size={16} className="text-brand-purple" />
            </div>
            <CardTitle className="text-2xl font-bold">{mindmaps.length}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-slate-500">In this workspace</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between text-slate-500">
              <CardDescription>System Status</CardDescription>
              <Sparkles size={16} className="text-emerald-600" />
            </div>
            <CardTitle className="text-base font-semibold text-brand-navy">
              Knowledge Engine
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-emerald-600 font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Online & Operational
            </p>
          </CardContent>
        </Card>

      </div>

      {/* Search and Header Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-brand-navy">Your Mindmaps</h2>
            <p className="text-xs text-slate-500">Select any mindmap to explore or expand its graph</p>
          </div>

          {/* Search Input */}
          <div className="relative w-full sm:w-72">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <Input
              type="text"
              placeholder="Search mindmaps..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-9 text-xs"
            />
          </div>
        </div>

        {/* Loading Skeletons */}
        {isLoadingMindmaps && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-40 rounded-xl bg-slate-100 animate-pulse border border-border p-5 space-y-3">
                <div className="w-8 h-8 rounded-lg bg-slate-200" />
                <div className="h-4 bg-slate-200 rounded w-3/4" />
                <div className="h-3 bg-slate-200 rounded w-1/2" />
              </div>
            ))}
          </div>
        )}

        {/* Mindmaps Grid */}
        {!isLoadingMindmaps && filteredMindmaps.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredMindmaps.map((mindmap) => (
              <MindmapCard key={mindmap.id} mindmap={mindmap} />
            ))}
          </div>
        )}

        {/* Empty State: No Matches on Search */}
        {!isLoadingMindmaps && filteredMindmaps.length === 0 && searchQuery && (
          <div className="p-8 text-center bg-white rounded-xl border border-border space-y-2">
            <p className="text-sm font-semibold text-slate-700">No mindmaps matching &ldquo;{searchQuery}&rdquo;</p>
            <p className="text-xs text-slate-500">Try adjusting your search query</p>
          </div>
        )}

        {/* Empty State: Zero Mindmaps in Workspace */}
        {!isLoadingMindmaps && mindmaps.length === 0 && !searchQuery && (
          <Card className="border-dashed border-2 border-slate-300 bg-white/50 text-center p-8 sm:p-12">
            <div className="max-w-sm mx-auto space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 text-brand-blue flex items-center justify-center mx-auto shadow-subtle">
                <FolderPlus size={24} />
              </div>
              <h3 className="text-base font-semibold text-brand-navy">No Mindmaps in this Workspace</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Generate your first interactive knowledge map by entering a topic prompt or uploading a concept.
              </p>
              <div className="pt-2">
                <Link to="/create">
                  <Button variant="default" size="sm">
                    <PlusCircle size={14} className="mr-1.5" />
                    Create First Mindmap
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        )}

      </div>

    </div>
  );
}
