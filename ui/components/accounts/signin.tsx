'use client';

import { ArrowLeft, ArrowRight, Eye, EyeOff, LoaderCircle } from 'lucide-react';
import Link from 'next/link';
import { useAppSelector, useAppDispatch } from '@/configs/redux/hooks';
import { setUnVerified } from '@/configs/redux/auth/authSlice';
import { useState } from 'react';
import { GoogleSignInButton } from './googleSignIn';
import { FacebookSignInButton } from './facebookSignIn';
import { MicrosoftSignInButton } from './microsoftSignIn';
import { useSaveTokens } from './utils/useSaveTokens';
import { toast } from 'react-toastify';
import axios from 'axios';
import { ResendVerification } from './reSendVerification';
import { signInError } from '@/lib/signInError';

export const Signin = () => {
  const dispatch = useAppDispatch();
  const isUnverified = useAppSelector((state) => state.auth.isUnVerified);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const saveTokensToLocal = useSaveTokens();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '').replace(/\/$/, '');
      const Tokens = await axios.post(
        `${baseUrl}/api/users/signin/`,
        {
          email: formData.email.trim(),
          password: formData.password,
        },
        { timeout: 30000 },
      );
      if (
        typeof Tokens.data?.access !== 'string' ||
        !Tokens.data.access ||
        typeof Tokens.data?.refresh !== 'string' ||
        !Tokens.data.refresh
      ) {
        throw new Error('Missing sign-in tokens');
      }
      saveTokensToLocal(Tokens.data);
    } catch (err) {
      const message = signInError(err);
      setError(message);
      toast.error(message);
      if (axios.isAxiosError(err) && err.response?.data?.code === 'email_unverified') {
        dispatch(setUnVerified(true));
      }
    } finally {
      setLoading(false);
    }
  };

  if (isUnverified) {
    return <ResendVerification emailProp={formData.email} />;
  }

  const inputClass =
    'min-h-12 w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100 disabled:bg-gray-50';
  const socialClass =
    '[&_span]:mr-0 flex min-h-12 w-full items-center justify-center rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 transition hover:border-blue-300 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600';

  return (
    <main className="flex min-h-[calc(100svh_-_64px)] items-center justify-center bg-gray-50 px-4 py-8 text-gray-900 sm:py-12 lg:min-h-[calc(100svh_-_90px)]">
      <div className="w-full max-w-md">
        <section
          aria-labelledby="signin-title"
          className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-[0_8px_40px_-16px_rgba(24,34,48,0.18)]"
        >
          <div className="h-1 bg-blue-600" />
          <div className="p-6 sm:p-8">
            <div className="text-center">
              <span
                className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-yellow-300 text-lg font-bold text-blue-700"
                aria-hidden="true"
              >
                FT
              </span>
              <h1
                id="signin-title"
                className="mt-5 text-2xl font-bold tracking-tight"
              >
                Welcome back
              </h1>
              <p className="mt-2 text-sm text-gray-500">Sign in to your Template account.</p>
            </div>
            <form
              onSubmit={handleEmailSignIn}
              className="mt-7"
              aria-busy={loading}
            >
              <div className="space-y-5">
                <div>
                  <label
                    htmlFor="signin-email"
                    className="mb-2 block text-sm font-semibold"
                  >
                    Email address
                  </label>
                  <input
                    id="signin-email"
                    type="email"
                    name="email"
                    autoComplete="username"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    disabled={loading}
                    aria-describedby={error ? 'signin-error' : undefined}
                    className={inputClass}
                  />
                </div>
                <div>
                  <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                    <label
                      htmlFor="signin-password"
                      className="text-sm font-semibold"
                    >
                      Password
                    </label>
                    <Link
                      href="/accounts/forgetPassword"
                      className="text-sm font-medium text-blue-700 hover:underline focus-visible:outline-blue-600"
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <input
                      id="signin-password"
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      autoComplete="current-password"
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      disabled={loading}
                      aria-describedby={error ? 'signin-error' : undefined}
                      className={`${inputClass} pr-14`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((value) => !value)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      aria-controls="signin-password"
                      aria-pressed={showPassword}
                      className="absolute right-1 top-1 flex h-10 w-10 items-center justify-center rounded-md text-gray-500 hover:bg-gray-50 hover:text-blue-700 focus-visible:outline-blue-600"
                    >
                      {showPassword ? (
                        <EyeOff
                          size={19}
                          aria-hidden="true"
                        />
                      ) : (
                        <Eye
                          size={19}
                          aria-hidden="true"
                        />
                      )}
                    </button>
                  </div>
                </div>
                {error && (
                  <p
                    id="signin-error"
                    role="alert"
                    className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
                  >
                    {error}
                  </p>
                )}
              </div>
              <button
                type="submit"
                disabled={loading}
                className="mt-6 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-lg bg-yellow-300 px-5 py-3 text-sm font-bold text-gray-900 transition hover:bg-yellow-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 disabled:cursor-wait disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <LoaderCircle
                      size={18}
                      className="animate-spin"
                      aria-hidden="true"
                    />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight
                      size={18}
                      aria-hidden="true"
                    />
                  </>
                )}
              </button>
            </form>
            {(process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ||
              process.env.NEXT_PUBLIC_FACEBOOK_APP_ID ||
              process.env.NEXT_PUBLIC_MICROSOFT_CLIENT_ID) && (
              <>
                <div className="my-6 flex items-center gap-3">
                  <span className="h-px flex-1 bg-gray-200" />
                  <span className="text-xs text-gray-500">Or continue with</span>
                  <span className="h-px flex-1 bg-gray-200" />
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <GoogleSignInButton
                    type="Continue"
                    iconOnly
                    className={socialClass}
                  />
                  <FacebookSignInButton
                    type="Continue"
                    iconOnly
                    className={socialClass}
                  />
                  <MicrosoftSignInButton
                    type="Continue"
                    iconOnly
                    className={socialClass}
                  />
                </div>
              </>
            )}
            <p className="mt-7 border-t border-gray-100 pt-5 text-center text-sm leading-6 text-gray-600">
              New to Template?{' '}
              <Link
                href="/accounts/signup"
                className="font-semibold text-blue-700 hover:underline focus-visible:outline-blue-600"
              >
                Create an account
              </Link>
            </p>
          </div>
        </section>
        <div className="mt-5 text-center">
          <Link
            href="/"
            className="inline-flex min-h-11 items-center gap-2 text-sm text-gray-500 hover:text-blue-700 focus-visible:outline-blue-600"
          >
            <ArrowLeft
              size={15}
              aria-hidden="true"
            />
            Back to website
          </Link>
        </div>
      </div>
    </main>
  );
};

export default Signin;
