import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Network, Loader2, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuthStore } from '@/store/useAuthStore';

export function RegisterPage(): React.JSX.Element {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const { register, isLoading, error: authError, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setFormError(null);
    clearError();

    if (!email || !password) {
      setFormError('Email and password are required');
      return;
    }

    if (password.length < 6) {
      setFormError('Password must be at least 6 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setFormError('Passwords do not match');
      return;
    }

    try {
      await register({
        email,
        password,
        full_name: fullName.trim() || undefined,
      });
      navigate('/dashboard', { replace: true });
    } catch {
      // Error handled by Zustand error state
    }
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
          <p className="text-xs text-slate-500">Create your knowledge exploration workspace</p>
        </div>

        {/* Registration Card */}
        <Card className="shadow-elevated">
          <CardHeader>
            <CardTitle className="text-xl">Create Account</CardTitle>
            <CardDescription>
              Sign up to provision your personal workspace and start generating maps.
            </CardDescription>
          </CardHeader>
          
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              
              {activeError && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2.5 text-xs text-red-700">
                  <AlertCircle size={16} className="mt-0.5 flex-shrink-0 text-red-600" />
                  <span>{activeError}</span>
                </div>
              )}

              {/* Full Name */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700" htmlFor="fullName">
                  Full Name (Optional)
                </label>
                <Input
                  id="fullName"
                  type="text"
                  placeholder="Alan Turing"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              {/* Email */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700" htmlFor="email">
                  Email Address
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="alan@turing.ac.uk"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  autoComplete="email"
                  required
                />
              </div>

              {/* Password */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700" htmlFor="password">
                  Password (min. 6 characters)
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  autoComplete="new-password"
                  required
                />
              </div>

              {/* Confirm Password */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700" htmlFor="confirmPassword">
                  Confirm Password
                </label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={isLoading}
                  autoComplete="new-password"
                  required
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                variant="navy"
                className="w-full mt-2"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="mr-2 animate-spin" />
                    Creating Workspace...
                  </>
                ) : (
                  'Create Account'
                )}
              </Button>

            </CardContent>

            <CardFooter className="justify-center border-t border-border pt-4 text-xs text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="text-brand-blue font-semibold hover:underline ml-1">
                Sign In
              </Link>
            </CardFooter>
          </form>
        </Card>

      </div>
    </div>
  );
}
