import React from 'react';
import { useLocation } from 'react-router-dom';
import { WorkspaceSelector } from '@/features/dashboard/WorkspaceSelector';
import { Badge } from '@/components/ui/badge';

const routeTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/create': 'Create Mindmap',
  '/settings': 'Settings',
};

export function Header(): React.JSX.Element {
  const location = useLocation();
  const currentTitle = routeTitles[location.pathname] || 'Workspace';

  return (
    <header className="h-16 bg-white border-b border-border px-6 flex items-center justify-between flex-shrink-0">
      <div>
        <h2 className="text-lg font-semibold text-brand-navy tracking-tight">{currentTitle}</h2>
      </div>

      <div className="flex items-center gap-3">
        <WorkspaceSelector />
        <Badge variant="purple" className="text-[10px]">Gemini 3.6 Flash</Badge>
      </div>
    </header>
  );
}
