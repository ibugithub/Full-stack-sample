'use client';
import { apiErrorMessage } from '@/lib/apiError';
import { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { LoaderCircle } from 'lucide-react';

export const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const HandleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setResult(null);
    const url = `${process.env.NEXT_PUBLIC_BACKEND_BASE_URL || ''}/api/users/forgetPassword/`;
    try {
      const response = await axios.post(url, { email }, { timeout: 30000 });
      if (response.status === 200) {
        setResult({
          type: 'success',
          message: 'Reset instructions sent. Check your inbox and spam folder.',
        });
        toast.success('Email sent successfully!');
      }
    } catch (error) {
      setResult({
        type: 'error',
        message: apiErrorMessage(error, 'Could not send the reset link. Please try again.'),
      });
      toast.error('Failed to send email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const HandleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setEmail(e.target.value);
    setResult(null);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 space-y-6 bg-white backdrop-blur-lg border border-gray-300 rounded-lg shadow-2xl">
        <h2 className="text-2xl font-bold text-center text-gray-900 tracking-wider">
          Forgot Password
        </h2>
        <p className="text-center text-gray-600">
          Enter your email below to receive instructions to reset your password.
        </p>
        <form
          className="mt-6 space-y-4"
          onSubmit={HandleSubmit}
          aria-busy={loading}
        >
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-900"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              required
              disabled={loading}
              autoComplete="email"
              placeholder="Enter your email"
              className="w-full mt-1 px-4 py-2 border border-gray-300 bg-transparent rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-900 placeholder-gray-500"
              value={email}
              onChange={HandleChange}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex min-h-11 w-full items-center justify-center gap-2 py-2 px-4 text-black bg-yellow-300 hover:bg-yellow-500 focus:ring-2 focus:ring-blue-500 rounded-full transition duration-300 ease-in-out disabled:cursor-wait disabled:opacity-70"
          >
            {loading ? (
              <>
                <LoaderCircle
                  size={18}
                  className="motion-safe:animate-spin"
                  aria-hidden="true"
                />
                Sending reset link...
              </>
            ) : (
              'Send Reset Link'
            )}
          </button>
          <div
            aria-live="polite"
            aria-atomic="true"
          >
            {loading && (
              <p className="text-center text-sm text-gray-600">
                Please wait while we send your reset instructions.
              </p>
            )}
            {result && (
              <p
                role={result.type === 'error' ? 'alert' : undefined}
                className={`rounded-lg border px-4 py-3 text-sm leading-6 ${result.type === 'success' ? 'border-green-200 bg-green-50 text-green-800' : 'border-red-200 bg-red-50 text-red-700'}`}
              >
                {result.message}
              </p>
            )}
          </div>
        </form>
        <div className="text-center">
          <a
            href="/accounts/signin"
            className="text-blue-700 hover:underline"
          >
            Back to Login
          </a>
        </div>
      </div>
    </div>
  );
};
