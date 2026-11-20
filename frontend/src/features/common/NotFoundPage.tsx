import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileQuestion } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function NotFoundPage(): React.JSX.Element {
  return (
    <div className="min-h-screen bg-brand-canvas flex flex-col items-center justify-center p-4 text-center">
      <div className="w-14 h-14 rounded-2xl bg-white border border-border flex items-center justify-center text-slate-400 mb-4 shadow-subtle">
        <FileQuestion size={28} />
      </div>
      <h1 className="text-3xl font-bold text-brand-navy tracking-tight">404</h1>
      <p className="text-sm text-slate-500 mt-1 max-w-sm">
        The knowledge map or page you are looking for does not exist or has been moved.
      </p>
      <div className="mt-6">
        <Link to="/dashboard">
          <Button variant="default">
            <ArrowLeft size={16} className="mr-2" />
            Back to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
}
