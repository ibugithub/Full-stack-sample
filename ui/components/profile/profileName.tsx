'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import axios from 'axios';
import { LoaderCircle, Pencil } from 'lucide-react';
import { AxiosReqInstance } from '@/components/accounts/utils/axiosInstance';
import type { ProfileInterface } from '@/types/interface';
import { apiErrorMessage } from '@/lib/apiError';

export function ProfileName({
  profile,
  onSaved,
}: {
  profile: ProfileInterface;
  onSaved: (profile: ProfileInterface) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [firstName, setFirstName] = useState(profile.user.first_name ?? '');
  const [lastName, setLastName] = useState(profile.user.last_name ?? '');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const input = useRef<HTMLInputElement>(null);
  const request = useRef<AbortController | null>(null);
  const busy = useRef(false);

  useEffect(() => () => request.current?.abort(), []);
  useEffect(() => {
    if (editing) input.current?.focus();
  }, [editing]);

  const start = () => {
    setFirstName(profile.user.first_name ?? '');
    setLastName(profile.user.last_name ?? '');
    setError('');
    setMessage('');
    setEditing(true);
  };

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (busy.current) return;
    const first = firstName.trim();
    const last = lastName.trim();
    if (!first) {
      setError('Enter your first name.');
      input.current?.focus();
      return;
    }
    if ([first, last].filter(Boolean).join(' ').length > 255) {
      setError('Your full name must be 255 characters or fewer.');
      return;
    }
    const controller = new AbortController();
    request.current = controller;
    busy.current = true;
    setSaving(true);
    setError('');
    try {
      const response = await AxiosReqInstance().patch<ProfileInterface>(
        '/api/profile/updateName/',
        {
          first_name: first,
          last_name: last,
        },
        { signal: controller.signal, timeout: 30000 },
      );
      if (controller.signal.aborted) return;
      onSaved(response.data);
      setEditing(false);
      setMessage('Your name has been saved.');
    } catch (failure) {
      if (controller.signal.aborted || axios.isCancel(failure)) return;
      setError(apiErrorMessage(failure, 'We could not save your name. Please try again.'));
    } finally {
      if (!controller.signal.aborted) {
        busy.current = false;
        setSaving(false);
      }
    }
  };

  return (
    <section
      className="min-w-0"
      aria-label="Your name"
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2
            id="personal-details-title"
            className="text-lg font-semibold"
          >
            Personal details
          </h2>
          <p className="mt-1 text-sm text-gray-500">The name associated with your account.</p>
        </div>
        {!editing && (
          <button
            type="button"
            onClick={start}
            className="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-lg border border-gray-200 px-3 text-sm font-semibold text-blue-700 hover:bg-blue-50 focus-visible:outline-blue-600"
          >
            <Pencil
              size={15}
              aria-hidden="true"
            />
            Edit name
          </button>
        )}
      </div>
      {!editing ? (
        <>
          <dl className="grid gap-5 sm:grid-cols-2">
            <div className="flex min-w-0 items-baseline gap-3 rounded-xl bg-gray-50 p-4">
              <dt className="shrink-0 text-xs font-medium text-gray-500">First name</dt>
              <dd className="min-w-0 break-words text-sm font-medium">
                {profile.user.first_name || 'Not set'}
              </dd>
            </div>
            <div className="flex min-w-0 items-baseline gap-3 rounded-xl bg-gray-50 p-4">
              <dt className="shrink-0 text-xs font-medium text-gray-500">Last name</dt>
              <dd className="min-w-0 break-words text-sm font-medium">
                {profile.user.last_name || 'Not set'}
              </dd>
            </div>
          </dl>
        </>
      ) : (
        <form
          onSubmit={(event) => void save(event)}
          aria-busy={saving}
          className="rounded-xl border border-gray-200 bg-gray-50 p-5"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label
                htmlFor="profile-first-name"
                className="mb-2 block text-sm font-medium"
              >
                First name
              </label>
              <input
                ref={input}
                id="profile-first-name"
                autoComplete="given-name"
                value={firstName}
                onChange={(event) => setFirstName(event.target.value)}
                required
                maxLength={255}
                disabled={saving}
                className="min-h-12 w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm focus:outline-blue-600 disabled:opacity-60"
              />
            </div>
            <div>
              <label
                htmlFor="profile-last-name"
                className="mb-2 block text-sm font-medium"
              >
                Last name <span className="font-normal text-gray-500">(optional)</span>
              </label>
              <input
                id="profile-last-name"
                autoComplete="family-name"
                value={lastName}
                onChange={(event) => setLastName(event.target.value)}
                maxLength={255}
                disabled={saving}
                className="min-h-12 w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm focus:outline-blue-600 disabled:opacity-60"
              />
            </div>
          </div>
          {error && (
            <p
              role="alert"
              className="mt-3 text-sm text-red-700"
            >
              {error}
            </p>
          )}
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-yellow-300 px-5 text-sm font-semibold disabled:opacity-60"
            >
              {saving && (
                <LoaderCircle
                  size={16}
                  className="animate-spin"
                  aria-hidden="true"
                />
              )}
              {saving ? 'Saving...' : 'Save name'}
            </button>
            <button
              type="button"
              disabled={saving}
              onClick={() => setEditing(false)}
              className="min-h-11 rounded-lg px-4 text-sm text-gray-600"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
      {message && (
        <p
          role="status"
          className="mt-2 text-sm text-green-800"
        >
          {message}
        </p>
      )}
    </section>
  );
}
