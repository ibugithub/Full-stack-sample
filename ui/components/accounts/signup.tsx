'use client';

import { ArrowLeft, ArrowRight, Eye, EyeOff, LoaderCircle } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';
import { GoogleSignInButton } from './googleSignIn';
import { FacebookSignInButton } from './facebookSignIn';
import { MicrosoftSignInButton } from './microsoftSignIn';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { apiErrorMessage } from '@/lib/apiError';

const Signup = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();
  const [visiblePasswords, setVisiblePasswords] = useState({
    password: false,
    confirmPassword: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError(null);

    if (!formData.username) {
      setError('Your name is required');
      setLoading(false);
      return;
    }
    if (!formData.email) {
      setError('Email is required');
      setLoading(false);
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }
    if (!formData.password) {
      setError('Password is required');
      setLoading(false);
      return;
    }
    if (!formData.confirmPassword) {
      setError('Confirm Password is required');
      setLoading(false);
      return;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    try {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '';
      await axios.post(`${baseUrl}/api/users/create/`, {
        name: formData.username,
        email: formData.email,
        password: formData.password,
        password2: formData.confirmPassword,
      });
      toast.success('A verification email has been sent to your email address');
      router.push('/accounts/signin');
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not create your account. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    'min-h-12 w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100 disabled:bg-gray-50';
  const socialClass =
    '[&_span]:mr-0 flex min-h-12 w-full items-center justify-center rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 transition hover:border-blue-300 hover:bg-blue-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600';

  return (
    <main className="flex min-h-[calc(100svh_-_64px)] items-center justify-center bg-gray-50 px-4 py-8 text-gray-900 sm:py-12 lg:min-h-[calc(100svh_-_90px)]">
      <div className="w-full max-w-md">
        <section
          aria-labelledby="signup-title"
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
                id="signup-title"
                className="mt-5 text-2xl font-bold tracking-tight"
              >
                Create an account
              </h1>
              <p className="mt-2 text-sm text-gray-500">Join Full-stack Template.</p>
            </div>
            <form
              onSubmit={handleSubmit}
              className="mt-7"
              aria-busy={loading}
            >
              <div className="space-y-5">
                <div>
                  <label
                    htmlFor="signup-name"
                    className="mb-2 block text-sm font-semibold"
                  >
                    Full name
                  </label>
                  <input
                    id="signup-name"
                    name="username"
                    type="text"
                    autoComplete="name"
                    placeholder="Your full name"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    disabled={loading}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label
                    htmlFor="signup-email"
                    className="mb-2 block text-sm font-semibold"
                  >
                    Email address
                  </label>
                  <input
                    id="signup-email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    disabled={loading}
                    className={inputClass}
                  />
                </div>
                {(['password', 'confirmPassword'] as const).map((field) => (
                  <div key={field}>
                    <label
                      htmlFor={`signup-${field}`}
                      className="mb-2 block text-sm font-semibold"
                    >
                      {field === 'password' ? 'Password' : 'Confirm password'}
                    </label>
                    <div className="relative">
                      <input
                        id={`signup-${field}`}
                        name={field}
                        type={visiblePasswords[field] ? 'text' : 'password'}
                        autoComplete="new-password"
                        placeholder={
                          field === 'password' ? 'Create a password' : 'Enter your password again'
                        }
                        value={formData[field]}
                        onChange={handleChange}
                        required
                        minLength={8}
                        disabled={loading}
                        aria-describedby={field === 'password' ? 'signup-password-hint' : undefined}
                        className={`${inputClass} pr-14`}
                      />
                      <button
                        type="button"
                        onClick={() =>
                          setVisiblePasswords((current) => ({
                            ...current,
                            [field]: !current[field],
                          }))
                        }
                        aria-label={`${visiblePasswords[field] ? 'Hide' : 'Show'} ${field === 'password' ? 'password' : 'confirmation password'}`}
                        aria-controls={`signup-${field}`}
                        aria-pressed={visiblePasswords[field]}
                        className="absolute right-1 top-1 flex h-10 w-10 items-center justify-center rounded-md text-gray-500 hover:bg-gray-50 hover:text-blue-700 focus-visible:outline-blue-600"
                      >
                        {visiblePasswords[field] ? (
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
                    {field === 'password' && (
                      <p
                        id="signup-password-hint"
                        className="mt-2 text-xs text-gray-500"
                      >
                        Use at least 8 characters.
                      </p>
                    )}
                  </div>
                ))}
                {error && (
                  <p
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
                    Creating account...
                  </>
                ) : (
                  <>
                    Create Account
                    <ArrowRight
                      size={18}
                      aria-hidden="true"
                    />
                  </>
                )}
              </button>
              <p className="mt-3 text-center text-xs leading-5 text-gray-500">
                We will email you a link to verify your account.
              </p>
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
              Already have an account?{' '}
              <Link
                href="/accounts/signin"
                className="font-semibold text-blue-700 hover:underline focus-visible:outline-blue-600"
              >
                Sign in
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

export default Signup;
