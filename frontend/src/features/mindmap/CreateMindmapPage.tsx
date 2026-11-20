import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, 
  FileText, 
  Layers, 
  GraduationCap, 
  CheckCircle2, 
  Loader2, 
  AlertCircle,
  Briefcase,
  UploadCloud,
  Trash2,
  FileCheck
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useWorkspaceStore } from '@/store/useWorkspaceStore';
import { mindmapApi, type UploadedDocument } from '@/lib/api/mindmaps';
import { cn } from '@/lib/utils';

// Inspiration prompt suggestions
const INSPIRATION_PROMPTS = [
  'Quantum Computing & Superposition',
  'Deep Learning & Neural Architectures',
  'Distributed Consensus (Raft & Paxos)',
  'Microservices Architecture & API Gateways',
  'Cellular Respiration & Photosynthesis',
];

type ExplanationLevel = 'beginner' | 'intermediate' | 'advanced';

const PROGRESS_STEPS = [
  { step: 1, label: 'Prompting Gemini 3.6 Flash engine...', duration: 700 },
  { step: 2, label: 'Validating recursive Pydantic tree schema...', duration: 600 },
  { step: 3, label: 'Calculating 2D tree layout coordinates...', duration: 600 },
  { step: 4, label: 'Persisting mindmap and nodes to PostgreSQL...', duration: 600 },
];

const DOCUMENT_PROGRESS_STEPS = [
  { step: 1, label: 'Retrieving vectorized text chunks from PostgreSQL...', duration: 700 },
  { step: 2, label: 'Prompting Gemini 3.6 Flash with grounded document passages...', duration: 700 },
  { step: 3, label: 'Synthesizing verified hierarchical taxonomy...', duration: 600 },
  { step: 4, label: 'Calculating 2D layout and persisting document mindmap...', duration: 600 },
];

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function CreateMindmapPage(): React.JSX.Element {
  const navigate = useNavigate();
  const { activeWorkspace, workspaces, fetchWorkspaces } = useWorkspaceStore();

  // Mode Selection
  const [activeTab, setActiveTab] = useState<'topic' | 'document'>('topic');

  // Shared Form State
  const [topicPrompt, setTopicPrompt] = useState('');
  const [maxDepth, setMaxDepth] = useState<number>(3);
  const [explanationLevel, setExplanationLevel] = useState<ExplanationLevel>('intermediate');
  const [includeExamples, setIncludeExamples] = useState<boolean>(true);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>(
    activeWorkspace?.id || workspaces[0]?.id || 'ws-personal-demo'
  );

  // Document Grounding State
  const [uploadedDoc, setUploadedDoc] = useState<UploadedDocument | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Generation Progress State
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Hydrate workspaces if none loaded yet
  useEffect(() => {
    if (workspaces.length === 0) {
      fetchWorkspaces();
    }
  }, [workspaces.length, fetchWorkspaces]);

  // Sync selectedWorkspaceId if activeWorkspace updates and currently empty or default
  useEffect(() => {
    if (activeWorkspace?.id && selectedWorkspaceId === 'ws-personal-demo') {
      setSelectedWorkspaceId(activeWorkspace.id);
    }
  }, [activeWorkspace, selectedWorkspaceId]);

  // Handle Topic Form Submission
  const handleGenerate = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!topicPrompt.trim()) {
      setErrorMessage('Please enter a topic or concept to generate a mindmap.');
      return;
    }

    setIsGenerating(true);
    setErrorMessage(null);
    setCurrentStepIndex(0);

    // Progress stepper animation
    const stepInterval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < PROGRESS_STEPS.length - 1 ? prev + 1 : prev));
    }, 700);

    const token = localStorage.getItem('access_token');

    // Demo Mode Simulation
    if (token === 'demo-session-token' || !token) {
      setTimeout(() => {
        clearInterval(stepInterval);
        setIsGenerating(false);
        navigate('/mindmaps/sample-id');
      }, 2600);
      return;
    }

    // Live Backend Call with Async Polling
    try {
      const initResponse = await mindmapApi.generateTopicMindmap({
        topic: topicPrompt.trim(),
        workspace_id: selectedWorkspaceId,
        max_depth: maxDepth,
        explanation_level: explanationLevel,
        include_examples: includeExamples,
      });

      // Poll until background worker finishes
      await mindmapApi.pollMindmapStatus(initResponse.mindmap_id);

      clearInterval(stepInterval);
      setIsGenerating(false);
      navigate(`/mindmaps/${initResponse.mindmap_id}`);
    } catch (err) {
      clearInterval(stepInterval);
      setIsGenerating(false);
      const rawMsg = err instanceof Error ? err.message : 'Generation failed';
      setErrorMessage(rawMsg);
    }
  };

  // Handle PDF File Ingestion
  const handleFileUpload = async (file: File): Promise<void> => {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setErrorMessage('Please upload a valid PDF document (.pdf).');
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setErrorMessage('File size exceeds 20MB limit. Please upload a smaller PDF.');
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);

    try {
      const doc = await mindmapApi.uploadDocument(selectedWorkspaceId, file);
      setUploadedDoc(doc);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to upload and vectorize PDF document.';
      setErrorMessage(msg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    setIsDragging(false);
  };

  // Handle Document Grounded Mindmap Submission
  const handleDocumentGenerate = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!uploadedDoc) {
      setErrorMessage('Please upload a PDF document before generating a mindmap.');
      return;
    }

    setIsGenerating(true);
    setErrorMessage(null);
    setCurrentStepIndex(0);

    const stepInterval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < DOCUMENT_PROGRESS_STEPS.length - 1 ? prev + 1 : prev));
    }, 700);

    const token = localStorage.getItem('access_token');
    if (token === 'demo-session-token' || !token) {
      setTimeout(() => {
        clearInterval(stepInterval);
        setIsGenerating(false);
        navigate('/mindmaps/sample-id');
      }, 2600);
      return;
    }

    try {
      const initResponse = await mindmapApi.generateDocumentMindmap({
        document_id: uploadedDoc.id,
        workspace_id: selectedWorkspaceId,
        max_depth: maxDepth,
        explanation_level: explanationLevel,
        include_examples: includeExamples,
      });

      // Poll until background worker finishes
      await mindmapApi.pollMindmapStatus(initResponse.mindmap_id);

      clearInterval(stepInterval);
      setIsGenerating(false);
      navigate(`/mindmaps/${initResponse.mindmap_id}`);
    } catch (err) {
      clearInterval(stepInterval);
      setIsGenerating(false);
      const rawMsg = err instanceof Error ? err.message : 'Document mindmap generation failed';
      setErrorMessage(rawMsg);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-brand-navy tracking-tight">
          Create Knowledge Map
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Transform any concept or subject into an interactive, explorable hierarchical mindmap.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div className="grid grid-cols-2 gap-3 max-w-md">
        <button
          type="button"
          onClick={() => {
            setActiveTab('topic');
            setErrorMessage(null);
          }}
          className={cn(
            'flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-semibold border transition-all',
            activeTab === 'topic'
              ? 'bg-brand-navy text-white border-brand-navy shadow-subtle'
              : 'bg-white text-slate-600 border-border hover:bg-slate-50'
          )}
        >
          <Sparkles size={15} className={activeTab === 'topic' ? 'text-brand-blue' : 'text-slate-400'} />
          <span>Topic Generation</span>
        </button>

        <button
          type="button"
          onClick={() => {
            setActiveTab('document');
            setErrorMessage(null);
          }}
          className={cn(
            'flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-semibold border transition-all',
            activeTab === 'document'
              ? 'bg-brand-navy text-white border-brand-navy shadow-subtle'
              : 'bg-white text-slate-600 border-border hover:bg-slate-50'
          )}
        >
          <FileText size={15} className={activeTab === 'document' ? 'text-brand-blue' : 'text-slate-400'} />
          <span>Document (PDF)</span>
          <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-emerald-300 bg-emerald-50 text-emerald-700">RAG</Badge>
        </button>
      </div>

      {/* Tab 1: Topic Generation Form */}
      {activeTab === 'topic' && (
        <Card className="shadow-elevated border-border overflow-hidden">
          
          {/* Active Generation Progress Overlay */}
          {isGenerating ? (
            <div className="p-8 sm:p-12 space-y-6 text-center animate-in fade-in duration-200">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 text-brand-blue flex items-center justify-center mx-auto shadow-subtle">
                <Sparkles size={28} className="animate-pulse text-brand-purple" />
              </div>

              <div className="space-y-1.5 max-w-md mx-auto">
                <h3 className="text-lg font-bold text-brand-navy">
                  Generating Your Knowledge Map
                </h3>
                <p className="text-xs text-slate-500">
                  Gemini 3.6 Flash is synthesizing hierarchical concepts and computing layout coordinates...
                </p>
              </div>

              {/* Progress Steps */}
              <div className="max-w-md mx-auto space-y-3 text-left pt-2">
                {PROGRESS_STEPS.map((step, idx) => {
                  const isDone = currentStepIndex > idx;
                  const isCurrent = currentStepIndex === idx;

                  return (
                    <div
                      key={step.step}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-lg border text-xs transition-all',
                        isDone && 'bg-emerald-50/70 border-emerald-200 text-emerald-800',
                        isCurrent && 'bg-blue-50/70 border-brand-blue/40 text-brand-blue font-semibold shadow-subtle',
                        !isDone && !isCurrent && 'bg-slate-50/50 border-slate-200 text-slate-400 opacity-60'
                      )}
                    >
                      {isDone && <CheckCircle2 size={16} className="text-emerald-600 flex-shrink-0" />}
                      {isCurrent && <Loader2 size={16} className="animate-spin text-brand-blue flex-shrink-0" />}
                      {!isDone && !isCurrent && <span className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[10px] text-slate-400 flex-shrink-0">{step.step}</span>}
                      <span>{step.label}</span>
                    </div>
                  );
                })}
              </div>

              {/* Animated Progress Bar */}
              <div className="max-w-md mx-auto w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-brand-blue h-1.5 transition-all duration-500 ease-out"
                  style={{
                    width: `${((currentStepIndex + 1) / PROGRESS_STEPS.length) * 100}%`,
                  }}
                />
              </div>
            </div>
          ) : (
            <form onSubmit={handleGenerate}>
              <CardContent className="p-6 sm:p-8 space-y-6">
                
                {/* Error Banner */}
                {errorMessage && (
                  <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2.5">
                    <AlertCircle size={16} className="mt-0.5 flex-shrink-0 text-red-600" />
                    <span>{errorMessage}</span>
                  </div>
                )}

                {/* Prompt Textarea */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-brand-navy uppercase tracking-wider" htmlFor="topic-prompt">
                      Topic or Concept Prompt
                    </label>
                    <span className="text-[11px] text-slate-400">
                      {topicPrompt.length}/300 characters
                    </span>
                  </div>
                  <textarea
                    id="topic-prompt"
                    rows={4}
                    maxLength={300}
                    placeholder="e.g. Quantum Computing, key physical principles (superposition, entanglement), algorithms, and hardware implementations..."
                    value={topicPrompt}
                    onChange={(e) => setTopicPrompt(e.target.value)}
                    className="w-full rounded-xl border border-border bg-white p-3.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all leading-relaxed"
                    required
                  />
                </div>

                {/* Inspiration Chips */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                    <Sparkles size={12} className="text-brand-purple" />
                    Try an example prompt:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {INSPIRATION_PROMPTS.map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        onClick={() => setTopicPrompt(prompt)}
                        className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-50 hover:bg-blue-50 text-slate-600 hover:text-brand-blue border border-border transition-colors text-left"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Parameters Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-3 border-t border-border">
                  
                  {/* Parameter 1: Map Depth */}
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-brand-navy flex items-center gap-1">
                      <Layers size={14} className="text-brand-blue" />
                      <span>Hierarchy Depth</span>
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { depth: 2, label: '2 Levels', desc: 'Overview (~6 nodes)' },
                        { depth: 3, label: '3 Levels', desc: 'Standard (~14 nodes)' },
                        { depth: 4, label: '4 Levels', desc: 'Deep (~28 nodes)' },
                      ].map((item) => (
                        <button
                          key={item.depth}
                          type="button"
                          onClick={() => setMaxDepth(item.depth)}
                          className={cn(
                            'p-2.5 rounded-lg border text-left transition-all',
                            maxDepth === item.depth
                              ? 'border-brand-blue bg-blue-50/60 text-brand-blue font-semibold ring-1 ring-brand-blue'
                              : 'border-border bg-white text-slate-700 hover:bg-slate-50'
                          )}
                        >
                          <div className="text-xs">{item.label}</div>
                          <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Parameter 2: Explanation Level */}
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-brand-navy flex items-center gap-1">
                      <GraduationCap size={14} className="text-brand-purple" />
                      <span>Explanation Difficulty</span>
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {(['beginner', 'intermediate', 'advanced'] as ExplanationLevel[]).map((level) => (
                        <button
                          key={level}
                          type="button"
                          onClick={() => setExplanationLevel(level)}
                          className={cn(
                            'py-2 px-3 rounded-lg border text-xs capitalize text-center transition-all',
                            explanationLevel === level
                              ? 'border-brand-purple bg-purple-50/60 text-brand-purple font-semibold ring-1 ring-brand-purple'
                              : 'border-border bg-white text-slate-700 hover:bg-slate-50'
                          )}
                        >
                          {level}
                        </button>
                      ))}
                    </div>
                  </div>

                </div>

                {/* Additional Settings: Workspace & Examples Toggle */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-3 border-t border-border">
                  
                  {/* Target Workspace */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700 flex items-center gap-1">
                      <Briefcase size={13} className="text-slate-500" />
                      <span>Target Workspace</span>
                    </label>
                    <select
                      value={selectedWorkspaceId}
                      onChange={(e) => setSelectedWorkspaceId(e.target.value)}
                      className="w-full h-9 rounded-lg border border-border bg-white px-3 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                    >
                      {workspaces.length > 0 ? (
                        workspaces.map((ws) => (
                          <option key={ws.id} value={ws.id}>
                            {ws.name}
                          </option>
                        ))
                      ) : (
                        <option value="ws-personal-demo">Personal Workspace</option>
                      )}
                    </select>
                  </div>

                  {/* Examples Toggle */}
                  <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <div className="space-y-0.5">
                      <span className="text-xs font-semibold text-slate-800">
                        Include Concrete Examples
                      </span>
                      <p className="text-[11px] text-slate-500">
                        Generates code and practical applications
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={includeExamples}
                      onChange={(e) => setIncludeExamples(e.target.checked)}
                      className="w-4 h-4 rounded text-brand-blue focus:ring-brand-blue cursor-pointer"
                    />
                  </div>

                </div>

                {/* Submit Action */}
                <div className="pt-4">
                  <Button
                    type="submit"
                    variant="default"
                    className="w-full h-11 text-sm font-semibold bg-brand-blue hover:bg-brand-blue/90 text-white shadow-md"
                  >
                    <Sparkles size={16} className="mr-2" />
                    Generate Mindmap with Gemini 3.6 Flash
                  </Button>
                </div>

              </CardContent>
            </form>
          )}

        </Card>
      )}

      {/* Tab 2: Document Mode (RAG Grounding) */}
      {activeTab === 'document' && (
        <Card className="shadow-elevated border-border overflow-hidden">
          
          {/* Active Generation Progress Overlay */}
          {isGenerating ? (
            <div className="p-8 sm:p-12 space-y-6 text-center animate-in fade-in duration-200">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 text-brand-blue flex items-center justify-center mx-auto shadow-subtle">
                <FileText size={28} className="animate-pulse text-brand-blue" />
              </div>

              <div className="space-y-1.5 max-w-md mx-auto">
                <h3 className="text-lg font-bold text-brand-navy">
                  Generating Grounded Document Mindmap
                </h3>
                <p className="text-xs text-slate-500">
                  Synthesizing verified concepts grounded strictly in {uploadedDoc?.filename || 'the document'}...
                </p>
              </div>

              {/* Progress Steps */}
              <div className="max-w-md mx-auto space-y-3 text-left pt-2">
                {DOCUMENT_PROGRESS_STEPS.map((step, idx) => {
                  const isDone = currentStepIndex > idx;
                  const isCurrent = currentStepIndex === idx;

                  return (
                    <div
                      key={step.step}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-lg border text-xs transition-all',
                        isDone && 'bg-emerald-50/70 border-emerald-200 text-emerald-800',
                        isCurrent && 'bg-blue-50/70 border-brand-blue/40 text-brand-blue font-semibold shadow-subtle',
                        !isDone && !isCurrent && 'bg-slate-50/50 border-slate-200 text-slate-400 opacity-60'
                      )}
                    >
                      {isDone && <CheckCircle2 size={16} className="text-emerald-600 flex-shrink-0" />}
                      {isCurrent && <Loader2 size={16} className="animate-spin text-brand-blue flex-shrink-0" />}
                      {!isDone && !isCurrent && <span className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[10px] text-slate-400 flex-shrink-0">{step.step}</span>}
                      <span>{step.label}</span>
                    </div>
                  );
                })}
              </div>

              {/* Animated Progress Bar */}
              <div className="max-w-md mx-auto w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-brand-blue h-1.5 transition-all duration-500 ease-out"
                  style={{
                    width: `${((currentStepIndex + 1) / DOCUMENT_PROGRESS_STEPS.length) * 100}%`,
                  }}
                />
              </div>
            </div>
          ) : (
            <form onSubmit={handleDocumentGenerate}>
              <CardContent className="p-6 sm:p-8 space-y-6">
                
                {/* Error Banner */}
                {errorMessage && (
                  <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2.5">
                    <AlertCircle size={16} className="mt-0.5 flex-shrink-0 text-red-600" />
                    <span>{errorMessage}</span>
                  </div>
                )}

                {/* File Upload / Selected Card Section */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-brand-navy uppercase tracking-wider">
                      Source Document (PDF)
                    </label>
                    <span className="text-[11px] text-slate-400">
                      Up to 20MB · Vectorized on Upload
                    </span>
                  </div>

                  <input
                    type="file"
                    ref={fileInputRef}
                    accept=".pdf,application/pdf"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleFileUpload(e.target.files[0]);
                      }
                    }}
                  />

                  {!uploadedDoc ? (
                    <div
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      onClick={() => !isUploading && fileInputRef.current?.click()}
                      className={cn(
                        'border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[160px]',
                        isDragging
                          ? 'border-brand-blue bg-blue-50/80 scale-[1.01]'
                          : 'border-slate-300 hover:border-brand-blue/70 bg-slate-50/50 hover:bg-slate-50'
                      )}
                    >
                      {isUploading ? (
                        <div className="space-y-3 flex flex-col items-center">
                          <Loader2 size={32} className="animate-spin text-brand-blue" />
                          <div className="space-y-1">
                            <p className="text-sm font-semibold text-brand-navy">
                              Parsing & Vectorizing PDF...
                            </p>
                            <p className="text-xs text-slate-500">
                              Extracting pages, generating overlapping passages, and computing 768-dim embeddings.
                            </p>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-2.5 flex flex-col items-center">
                          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-brand-blue flex items-center justify-center shadow-subtle">
                            <UploadCloud size={24} />
                          </div>
                          <div className="space-y-0.5">
                            <p className="text-sm font-semibold text-slate-800">
                              Drop your PDF here, or <span className="text-brand-blue underline underline-offset-2">browse</span>
                            </p>
                            <p className="text-xs text-slate-400">
                              Supports textbooks, papers, documentation, or technical manuals
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/30 flex items-center justify-between gap-4">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
                          <FileCheck size={20} />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-brand-navy truncate">
                              {uploadedDoc.filename}
                            </span>
                            <span className="text-xs text-slate-500 flex-shrink-0">
                              ({formatBytes(uploadedDoc.file_size_bytes)})
                            </span>
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-[10px] bg-emerald-50 text-emerald-800 border-emerald-300 font-medium">
                              ✓ {uploadedDoc.total_pages} Pages Extracted · {uploadedDoc.chunks_count} Vectorized Chunks Ready
                            </Badge>
                          </div>
                        </div>
                      </div>

                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setUploadedDoc(null);
                          if (fileInputRef.current) {
                            fileInputRef.current.value = '';
                          }
                        }}
                        className="text-slate-400 hover:text-red-600 hover:bg-red-50 flex-shrink-0 h-8 px-2.5"
                      >
                        <Trash2 size={15} className="mr-1" />
                        <span className="text-xs">Remove</span>
                      </Button>
                    </div>
                  )}
                </div>

                {/* Parameters Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-3 border-t border-border">
                  
                  {/* Parameter 1: Map Depth */}
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-brand-navy flex items-center gap-1">
                      <Layers size={14} className="text-brand-blue" />
                      <span>Hierarchy Depth</span>
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { depth: 2, label: '2 Levels', desc: 'Overview (~6 nodes)' },
                        { depth: 3, label: '3 Levels', desc: 'Standard (~14 nodes)' },
                        { depth: 4, label: '4 Levels', desc: 'Deep (~28 nodes)' },
                      ].map((item) => (
                        <button
                          key={item.depth}
                          type="button"
                          onClick={() => setMaxDepth(item.depth)}
                          className={cn(
                            'p-2.5 rounded-lg border text-left transition-all',
                            maxDepth === item.depth
                              ? 'border-brand-blue bg-blue-50/60 text-brand-blue font-semibold ring-1 ring-brand-blue'
                              : 'border-border bg-white text-slate-700 hover:bg-slate-50'
                          )}
                        >
                          <div className="text-xs">{item.label}</div>
                          <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Parameter 2: Explanation Level */}
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-brand-navy flex items-center gap-1">
                      <GraduationCap size={14} className="text-brand-purple" />
                      <span>Explanation Difficulty</span>
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {(['beginner', 'intermediate', 'advanced'] as ExplanationLevel[]).map((level) => (
                        <button
                          key={level}
                          type="button"
                          onClick={() => setExplanationLevel(level)}
                          className={cn(
                            'py-2 px-3 rounded-lg border text-xs capitalize text-center transition-all',
                            explanationLevel === level
                              ? 'border-brand-purple bg-purple-50/60 text-brand-purple font-semibold ring-1 ring-brand-purple'
                              : 'border-border bg-white text-slate-700 hover:bg-slate-50'
                          )}
                        >
                          {level}
                        </button>
                      ))}
                    </div>
                  </div>

                </div>

                {/* Additional Settings: Workspace & Examples Toggle */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-3 border-t border-border">
                  
                  {/* Target Workspace */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700 flex items-center gap-1">
                      <Briefcase size={13} className="text-slate-500" />
                      <span>Target Workspace</span>
                    </label>
                    <select
                      value={selectedWorkspaceId}
                      onChange={(e) => setSelectedWorkspaceId(e.target.value)}
                      className="w-full h-9 rounded-lg border border-border bg-white px-3 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                    >
                      {workspaces.length > 0 ? (
                        workspaces.map((ws) => (
                          <option key={ws.id} value={ws.id}>
                            {ws.name}
                          </option>
                        ))
                      ) : (
                        <option value="ws-personal-demo">Personal Workspace</option>
                      )}
                    </select>
                  </div>

                  {/* Examples Toggle */}
                  <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <div className="space-y-0.5">
                      <span className="text-xs font-semibold text-slate-800">
                        Include Concrete Examples
                      </span>
                      <p className="text-[11px] text-slate-500">
                        Extracts real-world formulas and code examples
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={includeExamples}
                      onChange={(e) => setIncludeExamples(e.target.checked)}
                      className="w-4 h-4 rounded text-brand-blue focus:ring-brand-blue cursor-pointer"
                    />
                  </div>

                </div>

                {/* Submit Action */}
                <div className="pt-4">
                  <Button
                    type="submit"
                    variant="default"
                    disabled={!uploadedDoc || isUploading}
                    className="w-full h-11 text-sm font-semibold bg-brand-navy hover:bg-brand-navy/90 text-white shadow-md disabled:opacity-50"
                  >
                    <Sparkles size={16} className="mr-2 text-brand-blue" />
                    Generate Mindmap from Document
                  </Button>
                </div>

              </CardContent>
            </form>
          )}

        </Card>
      )}

    </div>
  );
}
