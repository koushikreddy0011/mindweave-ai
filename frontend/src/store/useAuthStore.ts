import { create } from 'zustand';
import { authApi, type LoginPayload, type RegisterPayload } from '@/lib/api/auth';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  loginAsDemo: () => void;
  logout: () => void;
  initialize: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (credentials: LoginPayload) => {
    set({ isLoading: true, error: null });
    try {
      const { access_token } = await authApi.login(credentials);
      localStorage.setItem('access_token', access_token);
      
      const user = await authApi.getMe();
      set({
        token: access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Login failed';
      localStorage.removeItem('access_token');
      set({
        token: null,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: message,
      });
      throw err;
    }
  },

  register: async (payload: RegisterPayload) => {
    set({ isLoading: true, error: null });
    try {
      await authApi.register(payload);
      // Auto-login upon registration
      const { access_token } = await authApi.login({
        username: payload.email,
        password: payload.password,
      });
      localStorage.setItem('access_token', access_token);
      const user = await authApi.getMe();

      set({
        token: access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      set({ isLoading: false, error: message });
      throw err;
    }
  },

  loginAsDemo: () => {
    const demoUser: User = {
      id: 'demo-user-12345',
      email: 'explorer@mindweave.ai',
      full_name: 'MindWeave Explorer',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    localStorage.setItem('access_token', 'demo-session-token');
    set({
      user: demoUser,
      token: 'demo-session-token',
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  initialize: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isLoading: false, isAuthenticated: false, user: null });
      return;
    }

    // Handle demo token without pinging backend
    if (token === 'demo-session-token') {
      const demoUser: User = {
        id: 'demo-user-12345',
        email: 'explorer@mindweave.ai',
        full_name: 'MindWeave Explorer',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      set({
        user: demoUser,
        token,
        isAuthenticated: true,
        isLoading: false,
      });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authApi.getMe();
      set({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch {
      localStorage.removeItem('access_token');
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));
