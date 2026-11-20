import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  Network, 
  LayoutDashboard, 
  PlusCircle, 
  Settings, 
  LogOut, 
  User as UserIcon,
  Sparkles,
  type LucideIcon
} from 'lucide-react';
import { useAuthStore } from '@/store/useAuthStore';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  to: string;
  icon: LucideIcon;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Create Mindmap', to: '/create', icon: PlusCircle },
  { label: 'Settings', to: '/settings', icon: Settings },
];

export function Sidebar(): React.JSX.Element {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = (): void => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-white border-r border-border flex flex-col h-screen select-none">
      
      {/* Brand Header */}
      <div className="p-5 border-b border-border flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-brand-navy flex items-center justify-center text-white shadow-subtle">
          <Network size={20} className="text-brand-blue" />
        </div>
        <div>
          <h1 className="text-base font-bold text-brand-navy tracking-tight leading-none">MindWeave AI</h1>
          <p className="text-[11px] text-slate-500 mt-1">Knowledge Canvas</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Platform
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-brand-blue/10 text-brand-blue font-semibold'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 font-medium'
                )
              }
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* AI Status Pill */}
      <div className="px-3 py-2">
        <div className="p-3 rounded-lg bg-brand-canvas border border-border/80 flex items-center gap-2 text-xs text-slate-600">
          <Sparkles size={14} className="text-brand-purple flex-shrink-0" />
          <span className="truncate">Gemini 3.6 Flash Active</span>
        </div>
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-border bg-slate-50/50">
        <div className="flex items-center justify-between gap-2 p-2 rounded-lg">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-brand-blue/10 text-brand-blue flex items-center justify-center font-semibold text-xs flex-shrink-0">
              {user?.full_name ? user.full_name[0].toUpperCase() : <UserIcon size={14} />}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-slate-800 truncate">
                {user?.full_name || 'Active User'}
              </p>
              <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            title="Sign out"
            className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

    </aside>
  );
}
