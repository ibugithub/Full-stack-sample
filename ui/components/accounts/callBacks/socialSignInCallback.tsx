'use client';

import axios from 'axios';
import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { ArrowLeft, CircleAlert } from 'lucide-react';
import { useSaveTokens } from '../utils/useSaveTokens';
import { consumeOAuthState } from '@/lib/oauth';
import { apiErrorMessage } from '@/lib/apiError';

const endpoints = {
  Google: 'getGoogleUsrInfo',
  Facebook: 'getFbUsrInfo',
  Microsoft: 'getMsUsrInfo',
};

type Provider = keyof typeof endpoints;

export function SocialSignInCallback({ provider }: { provider: Provider }) {
  const saveTokens = useSaveTokens();
  const started = useRef(false);
  const mounted = useRef(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    // An authorization code can only be exchanged once, including in Strict Mode.
    if (started.current) return;
    started.current = true;
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (params.has('error') || !code || !consumeOAuthState(provider, params.get('state'))) {
      setError(
        `Sign-in with ${provider} was not completed. Please return to Sign In and try again.`,
      );
      return;
    }

    const completeSignIn = async () => {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '';
        const response = await axios.post(
          `${baseUrl}/api/users/${endpoints[provider]}/`,
          { code },
          { timeout: 30000 },
        );
        if (!mounted.current) return;
        const tokens = response.data;
        if (
          typeof tokens?.access !== 'string' ||
          !tokens.access ||
          typeof tokens?.refresh !== 'string' ||
          !tokens.refresh
        ) {
          throw new Error('Missing sign-in tokens');
        }
        saveTokens(tokens);
      } catch (error) {
        if (!mounted.current) return;
        setError(
          apiErrorMessage(
            error,
            `We could not complete your ${provider} sign-in. Please return to Sign In and try again.`,
          ),
        );
      }
    };
    void completeSignIn();
  }, [provider, saveTokens]);

  return (
    <main className="flex min-h-[calc(100svh_-_64px)] items-center justify-center bg-gray-50 px-4 py-10 text-gray-900 lg:min-h-[calc(100svh_-_90px)]">
      <section
        aria-labelledby="social-signin-title"
        className="w-full max-w-sm overflow-hidden rounded-2xl border border-gray-200 bg-white text-center shadow-sm"
      >
        <div className="h-1 bg-blue-600" />
        <div className="px-6 py-9 sm:px-8">
          <div className="relative mx-auto flex h-20 w-20 items-center justify-center">
            {!error && (
              <span
                aria-hidden="true"
                className="absolute inset-0 rounded-full border-[3px] border-blue-100 border-t-blue-600 motion-safe:animate-spin"
              />
            )}
            <span
              aria-hidden="true"
              className="flex h-14 w-14 items-center justify-center rounded-full bg-yellow-300 text-xl font-bold text-blue-700"
            >
              FT
            </span>
          </div>
          {error ? (
            <div
              role="alert"
              className="mt-6"
            >
              <CircleAlert
                size={22}
                className="mx-auto text-red-600"
                aria-hidden="true"
              />
              <h1
                id="social-signin-title"
                className="mt-3 text-xl font-bold"
              >
                Sign-in incomplete
              </h1>
              <p className="mt-3 text-sm leading-6 text-gray-600">{error}</p>
            </div>
          ) : (
            <div
              role="status"
              aria-live="polite"
              className="mt-6"
            >
              <h1
                id="social-signin-title"
                className="text-xl font-bold"
              >
                Signing you in
              </h1>
              <p className="mt-3 text-sm leading-6 text-gray-600">
                Connecting your {provider} account to Template.
              </p>
              <p className="mt-2 text-xs leading-5 text-gray-500">
                You will be taken to the website shortly.
              </p>
            </div>
          )}
          <Link
            href="/accounts/signin"
            className={`mt-7 inline-flex min-h-11 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 ${error ? 'bg-yellow-300 text-gray-900 hover:bg-yellow-500' : 'text-gray-500 hover:bg-gray-50 hover:text-blue-700'}`}
          >
            <ArrowLeft
              size={15}
              aria-hidden="true"
            />
            Back to Sign In
          </Link>
        </div>
      </section>
    </main>
  );
}
