import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Network, Sparkles, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuthStore } from '@/store/useAuthStore';

interface LocationState {
  from?: {
    pathname?: string;
  };
}

export function LoginPage(): React.JSX.Element {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const { login, loginAsDemo, isLoading, error: authError, clearError } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const destination = (location.state as LocationState)?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setFormError(null);
    clearError();

    if (!email || !password) {
      setFormError('Please enter both email and password');
      return;
    }

    try {
      await login({ username: email, password });
      navigate(destination, { replace: true });
    } catch {
      // Error handled by Zustand error state
    }
  };

  const handleDemoLogin = (): void => {
    loginAsDemo();
    navigate(destination, { replace: true });
  };

  const activeError = formError || authError;

  return (
    <div className="min-h-screen bg-brand-canvas flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6">
        
        {/* Brand Header */}
        <div className="flex flex-col items-center gap-2">
          <div className="w-12 h-12 rounded-xl bg-brand-navy flex items-center justify-center text-white shadow-elevated">
            <Network size={26} className="text-brand-blue" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-brand-navy">MindWeave AI</h1>
          <p className="text-xs text-slate-500">Interactive Visual Knowledge Exploration</p>
        </div>

        {/* Login Card */}
        <Card className="shadow-elevated">
          <CardHeader>
            <CardTitle className="text-xl">Sign In to Your Workspace</CardTitle>
            <CardDescription>Enter your credentials to access your mindmaps.</CardDescription>
          </CardHeader>
          
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              
              {/* Error Alert */}
              {activeError && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2.5 text-xs text-red-700">
                  <AlertCircle size={16} className="mt-0.5 flex-shrink-0 text-red-600" />
                  <span>{activeError}</span>
                </div>
              )}

              {/* Email Input */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700" htmlFor="email">
                  Email Address
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  autoComplete="email"
                  required
                />
              </div>

              {/* Password Input */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-slate-700" htmlFor="password">
                    Password
                  </label>
                </div>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  autoComplete="current-password"
                  required
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                variant="default"
                className="w-full mt-2"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="mr-2 animate-spin" />
                    Signing In...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>

              {/* Instant Demo Preview Option */}
              <div className="relative pt-2">
                <div className="absolute inset-0 flex items-center pt-2">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-slate-400 font-medium">Or explore instantly</span>
                </div>
              </div>

              <Button
                type="button"
                variant="outline"
                onClick={handleDemoLogin}
                className="w-full text-brand-blue border-brand-blue/30 hover:bg-brand-blue/5 hover:text-brand-blue justify-center font-medium"
              >
                <Sparkles size={15} className="mr-2 text-brand-purple" />
                Enter as Demo Explorer <ArrowRight size={14} className="ml-1" />
              </Button>

            </CardContent>

            <CardFooter className="justify-center border-t border-border pt-4 text-xs text-slate-500">
              Don&apos;t have an account?{' '}
              <Link to="/register" className="text-brand-blue font-semibold hover:underline ml-1">
                Create Account
              </Link>
            </CardFooter>
          </form>
        </Card>

      </div>
    </div>
  );
}
