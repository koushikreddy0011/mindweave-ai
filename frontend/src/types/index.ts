/**
 * MindWeave AI - Shared Domain Types
 * Synchronized with FastAPI Pydantic v2 schemas
 */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Workspace {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export type MindmapStatus = 'draft' | 'processing' | 'completed' | 'failed';
export type InputType = 'topic' | 'document';

export interface Mindmap {
  id: string;
  workspace_id: string;
  title: string;
  description: string | null;
  input_type: InputType;
  input_prompt: string | null;
  status: MindmapStatus;
  root_node_id: string | null;
  created_at: string;
  updated_at: string;
}

export type NodeType = 'root' | 'category' | 'concept' | 'detail';

export interface MindmapNode {
  id: string;
  mindmap_id: string;
  parent_id: string | null;
  label: string;
  description: string | null;
  node_type: NodeType;
  depth: number;
  position_x: number;
  position_y: number;
  generation_status: 'pending' | 'completed' | 'failed';
  node_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface MindmapEdge {
  id: string;
  mindmap_id: string;
  source_node_id: string;
  target_node_id: string;
  relationship_type: string;
  label: string | null;
  created_at: string;
  updated_at: string;
}

export interface NodeExplanation {
  id: string;
  node_id: string;
  overview: string;
  detailed_explanation: string;
  how_it_works: string[];
  examples: string[];
  applications: string[];
  key_concepts: string[];
  related_concepts: string[];
  created_at: string;
  updated_at: string;
}

export interface GraphData {
  mindmap: Mindmap;
  nodes: MindmapNode[];
  edges: MindmapEdge[];
}

export interface NodePositionUpdate {
  node_id: string;
  position_x: number;
  position_y: number;
}
