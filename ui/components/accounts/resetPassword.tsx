'use client';
import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import { apiErrorMessage } from '@/lib/apiError';

const ResetPassword = ({ token }: { token: string }) => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setError('');
    try {
      const url = `${process.env.NEXT_PUBLIC_BACKEND_BASE_URL || ''}/api/users/resetPassword/`;
      const response = await axios.post(url, {
        token: token,
        password: formData.password,
      });
      if (response.status === 200) {
        toast.success('Password reset successfully!');
        router.push('/accounts/signin');
      }
    } catch (error) {
      console.error('An error occurred while resetting password at resetPassword.tsx', error);
      setError(apiErrorMessage(error, 'Failed to reset password. Please try again.'));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 space-y-6 bg-white backdrop-blur-lg border border-gray-300 rounded-lg shadow-2xl">
        <h2 className="text-2xl font-bold text-center text-gray-900 tracking-wider">
          Reset Password
        </h2>
        <p className="text-center text-gray-600">Enter your new password below.</p>
        <form
          className="mt-6 space-y-4"
          onSubmit={handleSubmit}
        >
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-900"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              required
              placeholder="Enter your password"
              className="w-full mt-1 px-4 py-2 border border-gray-300 bg-transparent rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-900 placeholder-gray-500"
              value={formData.password}
              onChange={handleChange}
            />
          </div>
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-900"
            >
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              required
              placeholder="Enter your password again"
              className="w-full mt-1 px-4 py-2 border border-gray-300 bg-transparent rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-900 placeholder-gray-500"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          </div>
          {error && <div className="text-red-500 text-center">{error}</div>}
          <button
            type="submit"
            className="w-full py-2 px-4 text-black bg-yellow-300 hover:bg-yellow-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded-full transition ease-in-out duration-300"
          >
            Reset Password
          </button>
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

export default ResetPassword;
