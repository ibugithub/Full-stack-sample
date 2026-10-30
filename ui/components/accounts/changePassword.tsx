'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { apiErrorMessage } from '@/lib/apiError';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, CheckCircle2, KeyRound, LoaderCircle } from 'lucide-react';
import { useAppSelector } from '@/configs/redux/hooks';
import type { ProfileInterface } from '@/types/interface';
import { AxiosReqInstance } from './utils/axiosInstance';

export function ChangePassword() {
  const { isAuthenticated, status, loogedInUser: account } = useAppSelector((state) => state.auth);
  const router = useRouter();
  const owner = (account?.user?.email ?? account?.email)?.trim().toLowerCase();

  useEffect(() => {
    if (status === 'unauthenticated') router.replace('/accounts/signin');
  }, [status, router]);

  return (
    <main className="min-h-[calc(100svh_-_64px)] bg-gray-50 px-4 py-8 text-gray-900 sm:py-12 lg:min-h-[calc(100svh_-_90px)]">
      <div className="mx-auto max-w-xl">
        <Link
          href="/accounts/profile/"
          className="mb-5 inline-flex min-h-11 items-center gap-2 text-sm text-gray-500 hover:text-blue-700 focus-visible:outline-blue-600"
        >
          <ArrowLeft
            size={16}
            aria-hidden="true"
          />
          Back to profile
        </Link>
        <section
          aria-labelledby="password-title"
          className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm"
        >
          <div className="h-1 bg-blue-600" />
          <div className="p-6 sm:p-8">
            <span className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
              <KeyRound
                size={24}
                aria-hidden="true"
              />
            </span>
            <h1
              id="password-title"
              className="text-2xl font-bold tracking-tight"
            >
              Change password
            </h1>
            <p className="mt-2 text-sm leading-6 text-gray-500">
              Keep your Template account secure with a strong password.
            </p>
            {isAuthenticated && status === 'authenticated' && owner ? (
              <PasswordForm
                key={owner}
                owner={owner}
              />
            ) : (
              <p
                role="status"
                className="mt-6 text-sm text-gray-600"
              >
                {status === 'unauthenticated'
                  ? 'Returning to Sign In...'
                  : 'Checking your session...'}
              </p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function PasswordForm({ owner }: { owner: string }) {
  const controller = useRef<AbortController | null>(null);
  const [method, setMethod] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    const request = new AbortController();
    controller.current = request;
    setLoading(true);
    setLoadError(false);
    void AxiosReqInstance()
      .get<ProfileInterface>(
        `${process.env.NEXT_PUBLIC_BACKEND_BASE_URL || ''}/api/profile/getProfile/`,
        { signal: request.signal, timeout: 30000 },
      )
      .then(({ data }) => {
        if (request.signal.aborted) return;
        const signInMethod = data.user?.signup_method?.trim().toLowerCase();
        if (
          data.user?.email.trim().toLowerCase() !== owner ||
          !signInMethod ||
          !['email', 'google', 'facebook', 'microsoft'].includes(signInMethod)
        ) {
          setLoadError(true);
          return;
        }
        setMethod(signInMethod);
      })
      .catch(() => {
        if (!request.signal.aborted) setLoadError(true);
      })
      .finally(() => {
        if (!request.signal.aborted) setLoading(false);
      });
    return () => request.abort();
  }, [owner, attempt]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (saving || method !== 'email' || !controller.current || controller.current.signal.aborted)
      return;
    setResult(null);
    if (newPassword !== confirmPassword) {
      setResult({ type: 'error', message: 'The new passwords do not match.' });
      return;
    }
    const signal = controller.current.signal;
    setSaving(true);
    try {
      await AxiosReqInstance().post(
        `${process.env.NEXT_PUBLIC_BACKEND_BASE_URL || ''}/api/profile/changePassword/`,
        { old_password: oldPassword, new_password: newPassword },
        { signal, timeout: 30000 },
      );
      if (signal.aborted) return;
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setResult({ type: 'success', message: 'Your password has been changed.' });
    } catch (error) {
      if (signal.aborted) return;
      setResult({
        type: 'error',
        message: apiErrorMessage(error, 'Could not change your password. Please try again.'),
      });
    } finally {
      if (!signal.aborted) setSaving(false);
    }
  };

  if (loading)
    return (
      <p
        role="status"
        className="mt-6 flex items-center gap-2 text-sm text-gray-600"
      >
        <LoaderCircle
          size={18}
          className="motion-safe:animate-spin"
          aria-hidden="true"
        />
        Loading password settings...
      </p>
    );
  if (loadError)
    return (
      <div className="mt-6">
        <p
          role="alert"
          className="text-sm text-red-700"
        >
          Could not load your password settings.
        </p>
        <button
          type="button"
          onClick={() => setAttempt((value) => value + 1)}
          className="mt-3 min-h-11 rounded-lg border border-gray-300 px-4 text-sm font-semibold text-blue-700 hover:bg-blue-50"
        >
          Try again
        </button>
      </div>
    );
  if (method !== 'email')
    return (
      <p className="mt-6 rounded-xl bg-blue-50 p-4 text-sm leading-6 text-gray-700">
        You sign in with{' '}
        {(
          { google: 'Google', facebook: 'Facebook', microsoft: 'Microsoft' } as Record<
            string,
            string
          >
        )[method ?? ''] || 'another provider'}
        . Manage your password through that account.
      </p>
    );

  return (
    <div className="mt-7">
      {result?.type === 'success' ? (
        <div
          role="status"
          className="rounded-xl border border-green-200 bg-green-50 p-5 text-green-800"
        >
          <CheckCircle2
            size={24}
            aria-hidden="true"
          />
          <p className="mt-3 text-sm font-medium">{result.message}</p>
          <Link
            href="/accounts/profile/"
            className="mt-4 inline-flex min-h-11 items-center rounded-lg bg-white px-4 text-sm font-semibold text-blue-700 hover:bg-blue-50"
          >
            Back to profile
          </Link>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          aria-busy={saving}
          className="space-y-5"
        >
          {[
            {
              id: 'current-password',
              label: 'Current password',
              value: oldPassword,
              set: setOldPassword,
              autoComplete: 'current-password',
            },
            {
              id: 'new-password',
              label: 'New password',
              value: newPassword,
              set: setNewPassword,
              autoComplete: 'new-password',
            },
            {
              id: 'confirm-password',
              label: 'Confirm new password',
              value: confirmPassword,
              set: setConfirmPassword,
              autoComplete: 'new-password',
            },
          ].map((field) => (
            <div key={field.id}>
              <label
                htmlFor={field.id}
                className="mb-2 block text-sm font-medium"
              >
                {field.label}
              </label>
              <input
                id={field.id}
                name={field.id}
                type="password"
                value={field.value}
                onChange={(event) => field.set(event.target.value)}
                autoComplete={field.autoComplete}
                required
                minLength={field.id === 'current-password' ? undefined : 8}
                disabled={saving}
                aria-describedby={field.id === 'new-password' ? 'password-hint' : undefined}
                className="min-h-12 w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100 disabled:bg-gray-50"
              />
              {field.id === 'new-password' && (
                <p
                  id="password-hint"
                  className="mt-2 text-xs text-gray-500"
                >
                  Use at least 8 characters.
                </p>
              )}
            </div>
          ))}
          {result?.type === 'error' && (
            <p
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
            >
              {result.message}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-3 border-t border-gray-200 pt-5">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-yellow-300 px-5 text-sm font-semibold hover:bg-yellow-500 disabled:cursor-wait disabled:opacity-60"
            >
              {saving && (
                <LoaderCircle
                  size={16}
                  className="motion-safe:animate-spin"
                  aria-hidden="true"
                />
              )}
              {saving ? 'Saving...' : 'Save password'}
            </button>
            <Link
              href="/accounts/profile/"
              className="inline-flex min-h-11 items-center rounded-lg px-4 text-sm text-gray-600 hover:bg-gray-50"
            >
              Cancel
            </Link>
          </div>
        </form>
      )}
    </div>
  );
}
