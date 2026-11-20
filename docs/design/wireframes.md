Screen A — Dashboard







Layout specification
- Left sidebar: Logo, Dashboard, My Mindmaps, Documents, Settings.
- Main header: Welcome message, search, profile.
- Primary action: Create New Mindmap.
- Recent projects: Cards with title, topic, last modified date and node count.
- Empty state: Illustration and create-first-mindmap action.
Screen B — Create a mindmap










Layout specification
- Page heading: Create your knowledge map.
- Two input modes: Topic and Documents.
- Topic mode: Large text area with an example prompt.
- Document mode: PDF upload area and document list.
- Generation settings:
  - Explanation level: Beginner / Intermediate / Advanced.
  - Map depth: 2 / 3 / 4 levels.
  - Include examples: On / Off.
- Generate Mindmap button.
Screen C — Mindmap editor
Most important screen










This screen is the heart of MindWeave.

Three-panel layout
Panel	Approximate width	Contents
Left	230 px	Workspace navigation and node outline
Center	Flexible	Interactive graph
Right	360 px	Knowledge and explanation panel

The center canvas should occupy most of the screen.

Example node design
Machine Learning
Root node
Supervised Learning
Classification

Regression



Unsupervised Learning
Clustering

Dimensionality Reduction



Reinforcement Learning
Rewards

Policy Learning




Illustrative hierarchy for the editor's node styling.
Right panel contents

When a user selects a node, display:
1. Concept overview.
2. Detailed explanation.
3. How it works.
4. Examples.
5. Applications.
6. Related concepts.
7. Sources and citations.
8. Ask AI about this concept.
The panel should have separate loading, empty, error and completed states.
Screen D — Document workspace










Features:
- Upload and manage PDFs.
- View extraction status.
- See which mindmaps use a particular document.
- Delete documents.
- View source references and page numbers.
Screen E — Settings










Features:
- Account profile.
- Explanation preferences.
- Default generation depth.
- AI usage and token consumption.
- Account security.

4. User experience flows
These are the workflows that should drive the frontend and backend implementation.
Flow 1: Generate from a topic
Dashboard
   |
   v
Create Mindmap
   |
   v
Enter "Machine Learning"
   |
   v
Choose depth and explanation level
   |
   v
Click Generate
   |
   v
AI generates hierarchy
   |
   v
Mindmap editor opens
   |
   v
Explanations load progressively
   |
   v
User selects a node
   |
   v
Knowledge panel displays explanation
   |
   v
Save Mindmap


Flow 2: Generate from a PDF
Dashboard
   |
   v
Create Mindmap
   |
   v
Select Documents
   |
   v
Upload PDF
   |
   v
Extract and process text
   |
   v
Generate document-based hierarchy
   |
   v
Attach source references
   |
   v
Open mindmap editor


Flow 3: Explore a concept
Select a node
      |
      v
Check saved explanation
      |
      +------ Available ------> Display explanation
      |
      +------ Not available --> Generate explanation
                                      |
                                      v
                                Save explanation
                                      |
                                      v
                                Display panel
                                      |
                                      v
                              Explore related nodes