'use client';

import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import { apiErrorMessage } from '@/lib/apiError';

export const VerifyEmail = ({ token }: { token: string }) => {
  const router = useRouter();
  const attempted = useRef<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // React Strict Mode must not redeem the same one-time link twice.
    if (!token || attempted.current === token) return;
    attempted.current = token;
    const base = (process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '').replace(/\/$/, '');
    void axios
      .post(`${base}/api/users/verifyEmail/`, { token }, { timeout: 30000 })
      .then(() => {
        toast.success('Email verified successfully!');
        router.replace('/accounts/signin');
      })
      .catch((error) =>
        setError(
          apiErrorMessage(
            error,
            'This verification link is invalid or expired. Request a new link from Sign In.',
          ),
        ),
      );
  }, [token, router]);

  const message = !token ? 'The verification link is missing its token.' : error;
  return (
    <main className="flex min-h-[70vh] items-center justify-center bg-gray-50 px-4">
      <section className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Verify your email</h1>
        <p
          role={message ? 'alert' : 'status'}
          className="mt-4 text-sm leading-6 text-gray-600"
        >
          {message || 'Verifying your email...'}
        </p>
        {message && (
          <Link
            href="/accounts/signin"
            className="mt-6 inline-flex min-h-11 items-center font-semibold text-blue-700"
          >
            Back to Sign In
          </Link>
        )}
      </section>
    </main>
  );
};
