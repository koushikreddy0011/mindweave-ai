import { create } from 'zustand';
import { workspaceApi, type CreateWorkspacePayload } from '@/lib/api/workspaces';
import { mindmapApi } from '@/lib/api/mindmaps';
import type { Workspace, Mindmap } from '@/types';

// Realistic demo data for offline/demo preview mode
const DEMO_WORKSPACES: Workspace[] = [
  {
    id: 'ws-personal-demo',
    user_id: 'demo-user-12345',
    name: 'Personal Workspace',
    description: 'Default personal workspace',
    created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'ws-research-demo',
    user_id: 'demo-user-12345',
    name: 'AI Research Lab',
    description: 'Literature reviews and deep learning architectures',
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    updated_at: new Date().toISOString(),
  },
];

const DEMO_MINDMAPS: Record<string, Mindmap[]> = {
  'ws-personal-demo': [
    {
      id: 'mm-ml-demo-1',
      workspace_id: 'ws-personal-demo',
      title: 'Machine Learning Foundations',
      description: 'Comprehensive taxonomy of supervised, unsupervised, and reinforcement learning',
      input_type: 'topic',
      input_prompt: 'Machine Learning foundations, key paradigms, and practical applications',
      status: 'completed',
      root_node_id: 'node-root-ml',
      created_at: new Date(Date.now() - 3600000 * 4).toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'mm-dist-demo-2',
      workspace_id: 'ws-personal-demo',
      title: 'Distributed Systems & Consensus',
      description: 'Raft, Paxos, Byzantine Fault Tolerance, and CAP theorem',
      input_type: 'topic',
      input_prompt: 'Distributed consensus algorithms and consistency models',
      status: 'completed',
      root_node_id: 'node-root-dist',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  'ws-research-demo': [
    {
      id: 'mm-transformer-demo-3',
      workspace_id: 'ws-research-demo',
      title: 'Transformer Architecture & Attention',
      description: 'Self-attention, Multi-head attention, and positional encodings',
      input_type: 'topic',
      input_prompt: 'Attention is All You Need and modern transformer variants',
      status: 'completed',
      root_node_id: 'node-root-tf',
      created_at: new Date(Date.now() - 3600000 * 12).toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
};

interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  mindmaps: Mindmap[];
  isLoadingWorkspaces: boolean;
  isLoadingMindmaps: boolean;
  error: string | null;

  // Actions
  fetchWorkspaces: () => Promise<void>;
  setActiveWorkspace: (workspace: Workspace) => void;
  createWorkspace: (payload: CreateWorkspacePayload) => Promise<Workspace>;
  fetchMindmaps: (workspaceId?: string) => Promise<void>;
}

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  workspaces: [],
  activeWorkspace: null,
  mindmaps: [],
  isLoadingWorkspaces: false,
  isLoadingMindmaps: false,
  error: null,

  fetchWorkspaces: async () => {
    set({ isLoadingWorkspaces: true, error: null });
    const token = localStorage.getItem('access_token');

    // Use demo data if in demo mode
    if (token === 'demo-session-token') {
      const active = get().activeWorkspace || DEMO_WORKSPACES[0];
      set({
        workspaces: DEMO_WORKSPACES,
        activeWorkspace: active,
        isLoadingWorkspaces: false,
      });
      get().fetchMindmaps(active.id);
      return;
    }

    try {
      const workspaces = await workspaceApi.getWorkspaces();
      const currentActive = get().activeWorkspace;
      const nextActive = workspaces.find((w) => w.id === currentActive?.id) || workspaces[0] || null;

      set({
        workspaces,
        activeWorkspace: nextActive,
        isLoadingWorkspaces: false,
      });

      if (nextActive) {
        get().fetchMindmaps(nextActive.id);
      }
    } catch {
      // Graceful fallback to demo data if offline
      const active = get().activeWorkspace || DEMO_WORKSPACES[0];
      set({
        workspaces: DEMO_WORKSPACES,
        activeWorkspace: active,
        isLoadingWorkspaces: false,
      });
      get().fetchMindmaps(active.id);
    }
  },

  setActiveWorkspace: (workspace: Workspace) => {
    set({ activeWorkspace: workspace });
    get().fetchMindmaps(workspace.id);
  },

  createWorkspace: async (payload: CreateWorkspacePayload): Promise<Workspace> => {
    const token = localStorage.getItem('access_token');

    if (token === 'demo-session-token') {
      const newWs: Workspace = {
        id: `ws-${Date.now()}`,
        user_id: 'demo-user-12345',
        name: payload.name,
        description: payload.description || null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      const updated = [...get().workspaces, newWs];
      set({ workspaces: updated, activeWorkspace: newWs });
      get().fetchMindmaps(newWs.id);
      return newWs;
    }

    try {
      const created = await workspaceApi.createWorkspace(payload);
      const updated = [...get().workspaces, created];
      set({ workspaces: updated, activeWorkspace: created });
      get().fetchMindmaps(created.id);
      return created;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create workspace';
      set({ error: message });
      throw err;
    }
  },

  fetchMindmaps: async (workspaceId?: string) => {
    const targetWsId = workspaceId || get().activeWorkspace?.id;
    if (!targetWsId) return;

    set({ isLoadingMindmaps: true, error: null });
    const token = localStorage.getItem('access_token');

    if (token === 'demo-session-token') {
      const maps = DEMO_MINDMAPS[targetWsId] || [];
      set({ mindmaps: maps, isLoadingMindmaps: false });
      return;
    }

    try {
      const mindmaps = await mindmapApi.getMindmaps(targetWsId);
      set({ mindmaps, isLoadingMindmaps: false });
    } catch {
      const maps = DEMO_MINDMAPS[targetWsId] || [];
      set({ mindmaps: maps, isLoadingMindmaps: false });
    }
  },
}));
