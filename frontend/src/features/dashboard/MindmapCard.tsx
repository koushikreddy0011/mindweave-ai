import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Network, Calendar, ArrowRight, Loader2, AlertCircle, Trash2, Check, X } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils';
import { useWorkspaceStore } from '@/store/useWorkspaceStore';
import type { Mindmap } from '@/types';

interface MindmapCardProps {
  mindmap: Mindmap;
}

export function MindmapCard({ mindmap }: MindmapCardProps): React.JSX.Element {
  const { deleteMindmap } = useWorkspaceStore();
  const [isConfirming, setIsConfirming] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = async (e: React.MouseEvent): Promise<void> => {
    e.preventDefault();
    e.stopPropagation();
    if (!isConfirming) {
      setIsConfirming(true);
      return;
    }
    try {
      setIsDeleting(true);
      await deleteMindmap(mindmap.id);
    } catch {
      setIsDeleting(false);
      setIsConfirming(false);
    }
  };

  const handleCancelClick = (e: React.MouseEvent): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsConfirming(false);
  };

  return (
    <Link to={`/mindmaps/${mindmap.id}`} className="group block">
      <Card className="h-full hover:border-brand-blue/60 hover:shadow-card transition-all duration-200 cursor-pointer flex flex-col justify-between relative overflow-hidden">
        
        <CardContent className="p-5 space-y-3 flex-1 flex flex-col justify-between">
          <div className="space-y-2">
            
            {/* Top Bar: Icon + Status + Delete */}
            <div className="flex items-center justify-between gap-2">
              <div className="w-9 h-9 rounded-lg bg-blue-50 text-brand-blue flex items-center justify-center group-hover:bg-brand-blue group-hover:text-white transition-colors">
                <Network size={18} />
              </div>

              <div className="flex items-center gap-1.5">
                {mindmap.status === 'completed' && (
                  <Badge variant="blue" className="text-[10px]">Ready</Badge>
                )}
                {mindmap.status === 'processing' && (
                  <Badge variant="generating" className="text-[10px]">
                    <Loader2 size={10} className="mr-1 animate-spin" />
                    Generating
                  </Badge>
                )}
                {mindmap.status === 'failed' && (
                  <Badge variant="destructive" className="text-[10px]">
                    <AlertCircle size={10} className="mr-1" />
                    Failed
                  </Badge>
                )}
                {mindmap.status === 'draft' && (
                  <Badge variant="outline" className="text-[10px]">Draft</Badge>
                )}

                {/* Inline Confirmation Delete Button */}
                {isConfirming ? (
                  <div className="flex items-center gap-1 bg-red-50 p-1 rounded-md border border-red-200 z-20">
                    <button
                      onClick={handleDeleteClick}
                      disabled={isDeleting}
                      title="Confirm Delete"
                      className="p-1 rounded bg-red-600 text-white hover:bg-red-700 transition-colors"
                    >
                      {isDeleting ? <Loader2 size={12} className="animate-spin" /> : <Check size={12} />}
                    </button>
                    <button
                      onClick={handleCancelClick}
                      title="Cancel"
                      className="p-1 rounded text-slate-500 hover:bg-slate-200 transition-colors"
                    >
                      <X size={12} />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={handleDeleteClick}
                    title="Delete Mindmap"
                    className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all z-20"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
            </div>

            {/* Title & Description */}
            <div>
              <h3 className="font-semibold text-slate-900 group-hover:text-brand-blue transition-colors line-clamp-1 text-sm sm:text-base">
                {mindmap.title}
              </h3>
              <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                {mindmap.description || mindmap.input_prompt || 'Interactive visual knowledge tree.'}
              </p>
            </div>
          </div>

          {/* Footer Metadata */}
          <div className="pt-3 border-t border-border flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <Calendar size={12} />
              {formatDate(mindmap.created_at)}
            </span>
            <span className="flex items-center gap-1 font-medium text-brand-blue group-hover:translate-x-0.5 transition-transform">
              Open Canvas <ArrowRight size={12} />
            </span>
          </div>

        </CardContent>

      </Card>
    </Link>
  );
}
