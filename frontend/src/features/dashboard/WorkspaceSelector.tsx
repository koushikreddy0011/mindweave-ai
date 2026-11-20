import React, { useState, useRef, useEffect } from 'react';
import { Briefcase, ChevronDown, Plus, Check } from 'lucide-react';
import { useWorkspaceStore } from '@/store/useWorkspaceStore';
import { CreateWorkspaceModal } from './CreateWorkspaceModal';
import { cn } from '@/lib/utils';

export function WorkspaceSelector(): React.JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { workspaces, activeWorkspace, setActiveWorkspace } = useWorkspaceStore();

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent): void {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-border text-xs text-slate-700 font-medium transition-colors"
      >
        <Briefcase size={14} className="text-brand-blue" />
        <span className="max-w-[140px] truncate">{activeWorkspace?.name || 'Select Workspace'}</span>
        <ChevronDown size={14} className={cn('text-slate-400 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1.5 w-60 bg-white rounded-xl shadow-elevated border border-border py-1.5 z-40 animate-in fade-in zoom-in-95 duration-100">
          <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
            Workspaces
          </div>

          <div className="max-h-56 overflow-y-auto">
            {workspaces.map((ws) => (
              <button
                key={ws.id}
                onClick={() => {
                  setActiveWorkspace(ws);
                  setIsOpen(false);
                }}
                className={cn(
                  'w-full flex items-center justify-between px-3 py-2 text-xs text-left transition-colors',
                  activeWorkspace?.id === ws.id
                    ? 'bg-brand-blue/10 text-brand-blue font-semibold'
                    : 'text-slate-700 hover:bg-slate-50'
                )}
              >
                <span className="truncate">{ws.name}</span>
                {activeWorkspace?.id === ws.id && <Check size={14} className="text-brand-blue flex-shrink-0" />}
              </button>
            ))}
          </div>

          <div className="border-t border-border mt-1 pt-1 px-1">
            <button
              onClick={() => {
                setIsOpen(false);
                setIsModalOpen(true);
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-brand-blue font-medium hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Plus size={14} />
              <span>Create Workspace</span>
            </button>
          </div>
        </div>
      )}

      <CreateWorkspaceModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
