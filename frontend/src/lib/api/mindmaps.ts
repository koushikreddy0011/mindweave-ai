import { apiClient } from './client';
import type { Mindmap, GraphData, NodeExplanation } from '@/types';

export interface TopicGenerationPayload {
  topic: string;
  workspace_id: string;
  max_depth?: number;
  explanation_level?: 'beginner' | 'intermediate' | 'advanced';
  include_examples?: boolean;
}

export interface UploadedDocument {
  id: string;
  workspace_id: string;
  filename: string;
  file_size_bytes: number;
  total_pages: number;
  status: string;
  chunks_count: number;
  created_at: string;
}

export interface DocumentGenerationPayload {
  document_id: string;
  workspace_id: string;
  max_depth?: number;
  explanation_level?: 'beginner' | 'intermediate' | 'advanced';
  include_examples?: boolean;
}

export interface PositionUpdateItem {
  node_id: string;
  position_x: number;
  position_y: number;
}

export interface BatchPositionPayload {
  positions: PositionUpdateItem[];
}

export const mindmapApi = {
  async getMindmaps(workspaceId?: string): Promise<Mindmap[]> {
    const params = workspaceId ? { workspace_id: workspaceId } : undefined;
    const response = await apiClient.get<Mindmap[]>('/mindmaps', { params });
    return response.data;
  },

  async getMindmapGraph(id: string): Promise<GraphData> {
    const response = await apiClient.get<GraphData>(`/mindmaps/${id}/graph`);
    return response.data;
  },

  async generateTopicMindmap(payload: TopicGenerationPayload): Promise<{ mindmap_id: string; status: string }> {
    const response = await apiClient.post<{ mindmap_id: string; status: string }>(
      '/generations/topic?async_mode=true',
      payload
    );
    return response.data;
  },

  async uploadDocument(workspaceId: string, file: File): Promise<UploadedDocument> {
    const formData = new FormData();
    formData.append('workspace_id', workspaceId);
    formData.append('file', file);

    const response = await apiClient.post<UploadedDocument>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    });
    return response.data;
  },

  async generateDocumentMindmap(
    payload: DocumentGenerationPayload
  ): Promise<{ mindmap_id: string; status: string }> {
    const response = await apiClient.post<{ mindmap_id: string; status: string }>(
      '/generations/document?async_mode=true',
      payload
    );
    return response.data;
  },

  /**
   * Polls mindmap record until generation is completed or failed
   */
  async pollMindmapStatus(
    mindmapId: string,
    maxAttempts = 45,
    intervalMs = 2000
  ): Promise<Mindmap> {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const response = await apiClient.get<Mindmap>(`/mindmaps/${mindmapId}`);
      const map = response.data;

      if (map.status === 'completed') {
        return map;
      }

      if (map.status === 'failed') {
        throw new Error('Mindmap generation failed. Please try again with a different topic.');
      }

      // Wait before next poll attempt
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }

    throw new Error('Generation took longer than expected. Please check your dashboard in a few moments.');
  },

  async getNodeExplanation(nodeId: string): Promise<NodeExplanation> {
    const response = await apiClient.post<NodeExplanation>(
      `/nodes/${nodeId}/explain`,
      null,
      { timeout: 180000 }
    );
    return response.data;
  },

  /**
   * Persist updated node coordinates following canvas drag adjustments
   */
  async updateNodePositions(
    mindmapId: string,
    positions: PositionUpdateItem[]
  ): Promise<{ updated: number }> {
    const response = await apiClient.patch<{ updated: number }>(
      `/mindmaps/${mindmapId}/positions`,
      { positions }
    );
    return response.data;
  },
};
