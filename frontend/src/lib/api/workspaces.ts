import { apiClient } from './client';
import type { Workspace } from '@/types';

export interface CreateWorkspacePayload {
  name: string;
  description?: string;
}

export const workspaceApi = {
  async getWorkspaces(): Promise<Workspace[]> {
    const response = await apiClient.get<Workspace[]>('/workspaces');
    return response.data;
  },

  async getWorkspace(id: string): Promise<Workspace> {
    const response = await apiClient.get<Workspace>(`/workspaces/${id}`);
    return response.data;
  },

  async createWorkspace(payload: CreateWorkspacePayload): Promise<Workspace> {
    const response = await apiClient.post<Workspace>('/workspaces', payload);
    return response.data;
  },
};
