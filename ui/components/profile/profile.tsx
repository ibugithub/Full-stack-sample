'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import axios from 'axios';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, ArrowRight, KeyRound, LoaderCircle, ShieldCheck } from 'lucide-react';
import { AxiosReqInstance } from '../accounts/utils/axiosInstance';
import { useAppDispatch, useAppSelector } from '@/configs/redux/hooks';
import { updateAccountName } from '@/configs/redux/auth/authSlice';
import type { ProfileInterface } from '@/types/interface';
import { ProfileName } from './profileName';

export const Profile = () => {
  const { loogedInUser: account, isAuthenticated, status } = useAppSelector((state) => state.auth);
  const router = useRouter();
  const dispatch = useAppDispatch();
  const email = account?.user?.email || account?.email;
  const owner = isAuthenticated && email ? email.trim().toLowerCase() : null;
  const requestVersion = useRef(0);
  const [profile, setProfile] = useState<ProfileInterface | null>(null);
  const [fetching, setFetching] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [imageFailed, setImageFailed] = useState(false);

  const fetchProfile = useCallback(async (signal?: AbortSignal) => {
    const version = ++requestVersion.current;
    setFetching(true);
    setFetchError(null);
    setImageFailed(false);
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setFetchError('Please sign in to view your profile.');
        return;
      }
      const response = await AxiosReqInstance().get(
        `${process.env.NEXT_PUBLIC_BACKEND_BASE_URL || ''}/api/profile/getProfile/`,
        { signal, timeout: 30000 },
      );
      // Refreshing an expired token legitimately changes its value during this request.
      // Guard against sign-out and superseded requests without rejecting that refresh.
      if (
        signal?.aborted ||
        requestVersion.current !== version ||
        !localStorage.getItem('accessToken')
      )
        return;
      if (!response.data?.user?.email) {
        setFetchError('The profile service returned incomplete details. Please try again.');
        return;
      }
      setProfile(response.data);
    } catch (error) {
      if (signal?.aborted || axios.isCancel(error) || requestVersion.current !== version) return;
      const responseStatus = axios.isAxiosError(error) ? error.response?.status : undefined;
      const message =
        responseStatus === 401 || responseStatus === 403
          ? 'Your session has expired. Please sign in again.'
          : responseStatus === 404
            ? 'Your profile could not be found. Please contact Template for help.'
            : responseStatus && responseStatus >= 500
              ? 'The profile service is temporarily unavailable. Please try again shortly.'
              : axios.isAxiosError(error) && !error.response
                ? 'Could not connect to the profile service. Please check your connection and try again.'
                : 'We could not load your profile. Please try again.';
      setFetchError(message);
    } finally {
      if (!signal?.aborted && requestVersion.current === version) setFetching(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      requestVersion.current++;
      setProfile(null);
      if (status === 'unauthenticated') {
        router.replace('/accounts/signin');
      }
      return;
    }
    const controller = new AbortController();
    void fetchProfile(controller.signal);
    return () => controller.abort();
  }, [fetchProfile, isAuthenticated, status, router, owner]);

  const name =
    profile?.user?.name?.trim() ||
    profile?.display_name?.trim() ||
    account?.name?.trim() ||
    'My Account';
  const method = profile?.user?.signup_method?.toLowerCase();
  const provider =
    (
      {
        google: 'Google',
        facebook: 'Facebook',
        microsoft: 'Microsoft',
        email: 'Email and password',
      } as Record<string, string>
    )[method ?? ''] || 'Not available';

  if (!isAuthenticated)
    return (
      <main className="flex min-h-[calc(100svh_-_64px)] items-center justify-center bg-gray-50 px-4 text-gray-600 lg:min-h-[calc(100svh_-_90px)]">
        <p
          role="status"
          className="flex items-center gap-3 text-sm"
        >
          <LoaderCircle
            size={20}
            className="text-blue-600 motion-safe:animate-spin"
            aria-hidden="true"
          />
          {status === 'unauthenticated' ? 'Returning to Sign In...' : 'Checking your session...'}
        </p>
      </main>
    );

  return (
    <main className="min-h-[calc(100svh_-_64px)] bg-gray-50 px-4 py-6 text-gray-900 sm:px-6 sm:py-10 lg:min-h-[calc(100svh_-_90px)]">
      <div className="mx-auto max-w-6xl">
        <Link
          href="/"
          className="mb-5 inline-flex min-h-11 items-center gap-2 text-sm text-gray-500 hover:text-blue-700 focus-visible:outline-blue-600"
        >
          <ArrowLeft
            size={16}
            aria-hidden="true"
          />{' '}
          Back to website
        </Link>
        <header className="mb-7">
          <h1 className="text-3xl font-bold tracking-tight">My account</h1>
          <p className="mt-2 text-sm leading-6 text-gray-500">
            Your personal details and account security.
          </p>
        </header>
        {fetching ? (
          <div
            role="status"
            className="flex items-center justify-center gap-3 rounded-2xl border border-gray-200 bg-white py-20 text-sm text-gray-600"
          >
            <LoaderCircle
              size={22}
              className="text-blue-600 motion-safe:animate-spin"
              aria-hidden="true"
            />
            Loading your profile...
          </div>
        ) : fetchError ? (
          <div className="rounded-2xl border border-gray-200 bg-white p-6">
            <p
              role="alert"
              className="text-sm leading-6 text-gray-700"
            >
              {fetchError}
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => void fetchProfile()}
                className="min-h-11 rounded-lg bg-yellow-300 px-4 text-sm font-semibold hover:bg-yellow-500"
              >
                Try again
              </button>
              <Link
                href="/accounts/signin"
                className="inline-flex min-h-11 items-center rounded-lg px-4 text-sm font-semibold text-blue-700 hover:bg-blue-50"
              >
                Sign in
              </Link>
            </div>
          </div>
        ) : profile && profile.user.email.trim().toLowerCase() === owner ? (
          <>
            <section
              aria-label="Account summary"
              className="relative overflow-hidden rounded-2xl border border-blue-100 bg-white p-6 sm:p-8"
            >
              <div
                aria-hidden="true"
                className="pointer-events-none absolute -right-12 -top-24 h-64 w-64 rounded-full border-[36px] border-blue-50"
              />
              <div className="relative flex flex-wrap items-center justify-between gap-5">
                <div className="flex min-w-0 items-center gap-4 sm:gap-5">
                  {profile.profile_picture && !imageFailed ? (
                    <Image
                      src={profile.profile_picture}
                      alt="Your profile photo"
                      width={72}
                      height={72}
                      unoptimized
                      onError={() => setImageFailed(true)}
                      className="h-[72px] w-[72px] shrink-0 rounded-2xl object-cover"
                    />
                  ) : (
                    <span
                      aria-hidden="true"
                      className="flex h-[72px] w-[72px] shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-2xl font-semibold text-white"
                    >
                      {name
                        .split(/\s+/)
                        .filter(Boolean)
                        .slice(0, 2)
                        .map((part) => part[0])
                        .join('')
                        .toUpperCase()}
                    </span>
                  )}
                  <div className="min-w-0">
                    <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-blue-700">
                      Personal account
                    </p>
                    <h2 className="break-words text-xl font-semibold sm:text-2xl">{name}</h2>
                    <p className="mt-1 break-all text-sm text-gray-500">{profile.user.email}</p>
                  </div>
                </div>
              </div>
            </section>
            <div className="mt-6 grid items-stretch gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
              <section
                aria-labelledby="personal-details-title"
                className="min-w-0 rounded-2xl border border-gray-200 bg-white p-6 sm:p-7"
              >
                <ProfileName
                  key={profile.user.email}
                  profile={profile}
                  onSaved={(updated) => {
                    if (updated.user.email.trim().toLowerCase() !== owner) return;
                    setProfile(updated);
                    dispatch(
                      updateAccountName({
                        email: updated.user.email,
                        name: updated.user.name ?? '',
                        first_name: updated.user.first_name ?? '',
                        last_name: updated.user.last_name ?? '',
                      }),
                    );
                  }}
                />
                <div className="mt-6 border-t border-gray-100 pt-5">
                  <p className="text-xs font-medium text-gray-500">Email address</p>
                  <p className="mt-2 break-all text-sm font-medium">{profile.user.email}</p>
                </div>
              </section>
              <section
                aria-labelledby="security-title"
                className="rounded-2xl border border-gray-200 bg-white p-6 sm:p-7"
              >
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
                  <ShieldCheck
                    size={22}
                    aria-hidden="true"
                  />
                </div>
                <h2
                  id="security-title"
                  className="text-lg font-semibold"
                >
                  Account security
                </h2>
                <p className="mt-2 text-sm leading-6 text-gray-500">
                  Manage how you sign in to your account.
                </p>
                <div className="mt-5 border-t border-gray-100 pt-5">
                  <p className="text-xs font-medium text-gray-500">Sign-in method</p>
                  <p className="mt-2 text-sm font-medium">{provider}</p>
                </div>
                {method === 'email' ? (
                  <Link
                    href="/accounts/change-password/"
                    className="mt-5 flex min-h-12 items-center justify-between gap-3 rounded-lg border border-gray-200 px-4 py-3 text-sm font-semibold text-blue-700 transition hover:border-blue-200 hover:bg-blue-50 focus-visible:outline-blue-600"
                  >
                    <span className="flex items-center gap-2">
                      <KeyRound
                        size={16}
                        aria-hidden="true"
                      />{' '}
                      Change password
                    </span>
                    <ArrowRight
                      size={16}
                      className="shrink-0"
                      aria-hidden="true"
                    />
                  </Link>
                ) : (
                  <p className="mt-4 text-sm leading-6 text-gray-500">
                    {method
                      ? `You sign in with ${provider}. Manage your password through that account.`
                      : 'Password settings are unavailable until your sign-in method is confirmed.'}
                  </p>
                )}
              </section>
            </div>
          </>
        ) : null}
      </div>
    </main>
  );
};
