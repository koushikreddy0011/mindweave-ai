import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAuthStore } from '@/store/useAuthStore';

export function SettingsPage(): React.JSX.Element {
  const { user } = useAuthStore();

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-xl font-bold text-brand-navy">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your account and AI model preferences.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>User Profile</CardTitle>
          <CardDescription>Account credentials and active workspace</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 font-mono text-xs">
          <div><span className="text-slate-500">User ID:</span> {user?.id}</div>
          <div><span className="text-slate-500">Email:</span> {user?.email}</div>
          <div><span className="text-slate-500">Full Name:</span> {user?.full_name || 'Not set'}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>AI Model Configuration</CardTitle>
            <Badge variant="purple">Active</Badge>
          </div>
          <CardDescription>Primary generative intelligence engine</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-xs text-slate-600">
          <div><span className="font-semibold text-slate-800">Model:</span> gemini-3.6-flash</div>
          <div><span className="font-semibold text-slate-800">Strategy:</span> Strict Pydantic JSON response schema</div>
          <div><span className="font-semibold text-slate-800">Cache:</span> PostgreSQL on-demand explanation caching</div>
        </CardContent>
      </Card>
    </div>
  );
}
