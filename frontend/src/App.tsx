import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { PublicRoute } from '@/components/layout/PublicRoute';
import { DashboardPage } from '@/features/dashboard/DashboardPage';
import { CreateMindmapPage } from '@/features/mindmap/CreateMindmapPage';
import { MindmapEditorPage } from '@/features/mindmap/MindmapEditorPage';
import { SettingsPage } from '@/features/settings/SettingsPage';
import { LoginPage } from '@/features/auth/LoginPage';
import { RegisterPage } from '@/features/auth/RegisterPage';
import { NotFoundPage } from '@/features/common/NotFoundPage';
import { useAuthStore } from '@/store/useAuthStore';

export default function App(): React.JSX.Element {
  const { initialize } = useAuthStore();

  // Hydrate auth session on app boot
  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <BrowserRouter>
      <Routes>
        
        {/* Public Routes (Redirect to /dashboard if logged in) */}
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* Protected App Routes (Wrapped with AppLayout) */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/create" element={<CreateMindmapPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>

          {/* Fullscreen Editor Canvas (Outside standard AppLayout) */}
          <Route path="/mindmaps/:id" element={<MindmapEditorPage />} />
        </Route>

        {/* 404 Catch-All */}
        <Route path="*" element={<NotFoundPage />} />

      </Routes>
    </BrowserRouter>
  );
}
