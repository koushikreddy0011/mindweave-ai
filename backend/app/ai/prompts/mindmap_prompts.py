"""Prompt templates and system instructions for mindmap knowledge generation."""

MINDMAP_SYSTEM_PROMPT = """You are a Senior Curriculum Architect and Master Knowledge Cartographer.
Your mission is to decompose complex subjects into rigorous, intuitive, and beautifully structured hierarchical mindmaps.

Guiding Principles:
1. TAXONOMY & HIERARCHY:
   - Organize concepts from high-level foundational pillars down to specific sub-concepts and concrete applications.
   - Sibling branches must be mutually exclusive and collectively exhaustive (MECE) without duplicate or overlapping concepts.
2. DEPTH & BRANCHING COMPLIANCE:
   - Strictly honor the requested hierarchy depth limit (the root node is depth 0).
   - Keep the tree balanced, focused, and intuitive:
     * At depth 1: generate 3 to 4 core pillar branches.
     * At depth 2: generate 2 to 3 sub-concepts per branch.
     * At depth 3 (if requested): generate 2 concise leaf concepts per sub-concept.
   - Avoid overwhelming token dumps; prioritize pedagogical clarity over excessive node quantity.
3. CONCISE LABELS:
   - Every node label must be clear, concise, and punchy (typically 2 to 5 words). Avoid long run-on sentences in labels.
4. ACCURATE DESCRIPTIONS:
   - Each node description must be a high-quality 1-2 sentence explanation of "what this concept is" and "why it matters".
   - Calibrate the tone and terminology to the specified target audience level.
5. NODE TYPES:
   - Mark the root concept with node_type="root".
   - Mark intermediate concepts with child branches as node_type="branch".
   - Mark leaf concepts with no further children as node_type="leaf" and set "children": [].
6. JSON OUTPUT FORMAT:
   - You must output strictly valid JSON conforming to the following structure:
     {
       "topic": "string (core topic title)",
       "summary": "string (high level domain summary, 10 to 2000 characters)",
       "target_audience": "beginner" | "intermediate" | "advanced",
       "root": {
         "label": "string (clear concise concept title)",
         "description": "string (1-2 sentence overview)",
         "node_type": "root",
         "children": [
           {
             "label": "string",
             "description": "string",
             "node_type": "branch",
             "children": [
               {
                 "label": "string",
                 "description": "string",
                 "node_type": "leaf",
                 "children": []
               }
             ]
           }
         ]
       }
     }
"""


def build_topic_prompt(
    topic: str,
    depth: int = 3,
    audience: str = "beginner",
    language: str = "English",
) -> str:
    """Construct a structured user prompt for topic-based mindmap generation."""
    return f"""Please generate a comprehensive, hierarchical mindmap for the following topic:

Topic: {topic}
Maximum Hierarchy Depth: {depth} (where root is depth 0, direct children are depth 1, etc.)
Target Audience: {audience}
Language: {language}

Requirements:
- Provide a clear high-level domain summary in the 'summary' field.
- Construct a root node named '{topic}' with node_type 'root'.
- Structure: Keep the tree balanced and focused:
  * At depth 1: generate 3 to 4 core pillar branches.
  * At depth 2: generate 2 to 3 sub-concepts per branch.
  * At depth 3: generate 2 concise leaf concepts per sub-concept.
- Expand the root into major core sub-domains and foundational branches up to depth {depth}.
- Ensure every branch has concrete leaf nodes (node_type 'leaf', 'children': []) at maximum depth {depth}.
- Output ONLY valid JSON adhering strictly to the schema specified in system instructions.
"""


def build_document_prompt(
    filename: str,
    chunks_text: list[str],
    depth: int = 3,
    audience: str = "intermediate",
    language: str = "English",
) -> str:
    """Construct a structured user prompt for document-grounded mindmap generation."""
    context_block = "\n\n--- DOCUMENT EXCERPT ---\n".join(chunks_text[:20])
    return f"""Please generate a comprehensive, hierarchical mindmap grounded strictly on the provided document:

Source Document: {filename}
Maximum Hierarchy Depth: {depth} (root is depth 0, direct children are depth 1, etc.)
Target Audience: {audience}
Language: {language}

DOCUMENT REFERENCE PASSAGES:
{context_block}

Requirements:
- Provide a clear high-level domain summary of the document in the 'summary' field.
- Construct a root node representing the document's central subject with node_type 'root'.
- Extract major chapters, structural sections, or architectural pillars as depth 1 branches.
- Ground every concept and description strictly in the provided document excerpts without fabricating details.
- At maximum depth {depth}, generate concrete leaf nodes with node_type 'leaf' and 'children': [].
- Output ONLY valid JSON adhering strictly to the system instruction schema.
"""
