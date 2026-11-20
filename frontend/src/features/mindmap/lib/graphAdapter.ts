import { type Node, type Edge } from '@xyflow/react';
import type { GraphData, MindmapNode, MindmapEdge } from '@/types';
import type { MindmapNodeData } from '../components/MindmapNode';
import type { MindmapEdgeData } from '../components/MindmapEdge';

export interface AdaptedGraph {
  nodes: Node[];
  edges: Edge[];
}

/**
 * Transforms backend GraphData (FastAPI / PostgreSQL) into React Flow Node[] and Edge[].
 * Calculates childCount per node and attaches custom node/edge types.
 */
export function adaptGraphToReactFlow(graphData: GraphData): AdaptedGraph {
  // Pass 1: Count children per node using parent_id
  const childCountMap = new Map<string, number>();
  for (const node of graphData.nodes) {
    if (node.parent_id) {
      childCountMap.set(
        node.parent_id,
        (childCountMap.get(node.parent_id) || 0) + 1
      );
    }
  }

  // Pass 2: Transform MindmapNode -> React Flow Node
  const nodes: Node[] = graphData.nodes.map((node: MindmapNode) => {
    const nodeData: MindmapNodeData = {
      label: node.label,
      description: node.description,
      nodeType: node.node_type,
      depth: node.depth,
      generationStatus: node.generation_status,
      childCount: childCountMap.get(node.id) || 0,
    };

    return {
      id: node.id,
      type: 'mindmapNode',
      position: {
        x: node.position_x,
        y: node.position_y,
      },
      data: nodeData as unknown as Record<string, unknown>,
    };
  });

  // Pass 3: Transform MindmapEdge -> React Flow Edge
  const edges: Edge[] = graphData.edges.map((edge: MindmapEdge) => {
    const edgeData: MindmapEdgeData = {
      relationshipType: edge.relationship_type,
      label: edge.label,
    };

    return {
      id: edge.id,
      source: edge.source_node_id,
      target: edge.target_node_id,
      type: 'mindmapEdge',
      data: edgeData as unknown as Record<string, unknown>,
    };
  });

  return { nodes, edges };
}

/**
 * Machine Learning Foundations Demo Dataset
 */
export const SAMPLE_GRAPH_DATA: GraphData = {
  mindmap: {
    id: 'mm-ml-demo-1',
    workspace_id: 'ws-personal-demo',
    title: 'Machine Learning Foundations',
    description: 'Foundations, learning paradigms, and practical applications',
    input_type: 'topic',
    input_prompt: 'Machine Learning foundations and applications',
    status: 'completed',
    root_node_id: 'n-root',
    created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    updated_at: new Date().toISOString(),
  },
  nodes: [
    {
      id: 'n-root',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: null,
      label: 'Machine Learning',
      description: 'Foundations & paradigms of statistical learning',
      node_type: 'root',
      depth: 0,
      position_x: 60,
      position_y: 240,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-sup',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-root',
      label: 'Supervised Learning',
      description: 'Training with ground truth labels',
      node_type: 'category',
      depth: 1,
      position_x: 400,
      position_y: 80,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-unsup',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-root',
      label: 'Unsupervised Learning',
      description: 'Discovering latent patterns in unlabeled data',
      node_type: 'category',
      depth: 1,
      position_x: 400,
      position_y: 240,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-rl',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-root',
      label: 'Reinforcement Learning',
      description: 'Agent optimization via environment feedback',
      node_type: 'category',
      depth: 1,
      position_x: 400,
      position_y: 400,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-cls',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-sup',
      label: 'Classification',
      description: 'Discrete class prediction',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 40,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-reg',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-sup',
      label: 'Regression',
      description: 'Continuous value estimation',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 120,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-clust',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-unsup',
      label: 'Clustering',
      description: 'Grouping similar instances',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 240,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-qlearn',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-rl',
      label: 'Q-Learning & Policy Search',
      description: 'Value iteration and policy gradients',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 360,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-actor',
      mindmap_id: 'mm-ml-demo-1',
      parent_id: 'n-rl',
      label: 'Actor-Critic Models',
      description: 'Hybrid policy-value architectures',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 440,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  edges: [
    {
      id: 'e-1',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-root',
      target_node_id: 'n-sup',
      relationship_type: 'paradigm',
      label: 'labeled',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'e-2',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-root',
      target_node_id: 'n-unsup',
      relationship_type: 'paradigm',
      label: 'unlabeled',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'e-3',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-root',
      target_node_id: 'n-rl',
      relationship_type: 'paradigm',
      label: 'rewards',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'e-4',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-sup',
      target_node_id: 'n-cls',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'e-5',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-sup',
      target_node_id: 'n-reg',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'e-6',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-unsup',
      target_node_id: 'n-clust',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'e-7',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-rl',
      target_node_id: 'n-qlearn',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'e-8',
      mindmap_id: 'mm-ml-demo-1',
      source_node_id: 'n-rl',
      target_node_id: 'n-actor',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
};

/**
 * Distributed Systems Demo Dataset
 */
export const DISTRIBUTED_SYSTEMS_GRAPH_DATA: GraphData = {
  mindmap: {
    id: 'mm-dist-demo-2',
    workspace_id: 'ws-personal-demo',
    title: 'Distributed Systems & Consensus',
    description: 'Raft, Paxos, Byzantine Fault Tolerance, and CAP theorem',
    input_type: 'topic',
    input_prompt: 'Distributed consensus algorithms and consistency models',
    status: 'completed',
    root_node_id: 'n-dist-root',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date().toISOString(),
  },
  nodes: [
    {
      id: 'n-dist-root',
      mindmap_id: 'mm-dist-demo-2',
      parent_id: null,
      label: 'Distributed Systems',
      description: 'Networked computers coordinating via message passing',
      node_type: 'root',
      depth: 0,
      position_x: 60,
      position_y: 200,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-consensus',
      mindmap_id: 'mm-dist-demo-2',
      parent_id: 'n-dist-root',
      label: 'Consensus Protocols',
      description: 'Agreeing on state across unreliable nodes',
      node_type: 'category',
      depth: 1,
      position_x: 400,
      position_y: 80,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-theorems',
      mindmap_id: 'mm-dist-demo-2',
      parent_id: 'n-dist-root',
      label: 'Theoretical Guarantees',
      description: 'Fundamental limits of distributed computing',
      node_type: 'category',
      depth: 1,
      position_x: 400,
      position_y: 320,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-raft',
      mindmap_id: 'mm-dist-demo-2',
      parent_id: 'n-consensus',
      label: 'Raft Protocol',
      description: 'Leader election, log replication, safety',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 40,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-paxos',
      mindmap_id: 'mm-dist-demo-2',
      parent_id: 'n-consensus',
      label: 'Paxos Consensus',
      description: 'Proposers, Acceptors, Learners',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 120,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-cap',
      mindmap_id: 'mm-dist-demo-2',
      parent_id: 'n-theorems',
      label: 'CAP Theorem',
      description: 'Consistency, Availability, Partition Tolerance',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 280,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'n-pacelc',
      mindmap_id: 'mm-dist-demo-2',
      parent_id: 'n-theorems',
      label: 'PACELC Theorem',
      description: 'Partition trade-offs vs normal latency trade-offs',
      node_type: 'concept',
      depth: 2,
      position_x: 720,
      position_y: 360,
      generation_status: 'completed',
      node_metadata: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
  edges: [
    {
      id: 'ed-1',
      mindmap_id: 'mm-dist-demo-2',
      source_node_id: 'n-dist-root',
      target_node_id: 'n-consensus',
      relationship_type: 'domain',
      label: 'coordination',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'ed-2',
      mindmap_id: 'mm-dist-demo-2',
      source_node_id: 'n-dist-root',
      target_node_id: 'n-theorems',
      relationship_type: 'domain',
      label: 'limits',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'ed-3',
      mindmap_id: 'mm-dist-demo-2',
      source_node_id: 'n-consensus',
      target_node_id: 'n-raft',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'ed-4',
      mindmap_id: 'mm-dist-demo-2',
      source_node_id: 'n-consensus',
      target_node_id: 'n-paxos',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'ed-5',
      mindmap_id: 'mm-dist-demo-2',
      source_node_id: 'n-theorems',
      target_node_id: 'n-cap',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'ed-6',
      mindmap_id: 'mm-dist-demo-2',
      source_node_id: 'n-theorems',
      target_node_id: 'n-pacelc',
      relationship_type: 'subtopic',
      label: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
};

/**
 * Resolves a demo dataset based on the mindmap ID.
 * Returns null if the ID is unrecognized so the caller can trigger 404 error handling.
 */
export function getDemoGraph(id?: string): GraphData | null {
  if (!id) return null;
  if (id === 'mm-dist-demo-2') {
    return DISTRIBUTED_SYSTEMS_GRAPH_DATA;
  }
  if (
    id === 'sample-id' ||
    id === 'mm-ml-demo-1' ||
    id === 'mm-ml-foundations-1'
  ) {
    return SAMPLE_GRAPH_DATA;
  }
  return null;
}
