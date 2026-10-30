import { apiErrorMessage } from '@/lib/apiError';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useState } from 'react';
import { useAppDispatch } from '@/configs/redux/hooks';
import { setUnVerified } from '@/configs/redux/auth/authSlice';

export const ResendVerification = ({ emailProp }: { emailProp: string }) => {
  const dispatch = useAppDispatch();
  const [email, setEmail] = useState(emailProp);

  const handleSendVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '';
      const response = await axios.post(`${baseUrl}/api/users/resendVerification/`, {
        email: email,
      });
      if (response.status === 200) {
        toast.success('Verification link sent!');
        dispatch(setUnVerified(false));
      }
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Failed to send verification. Please try again.'));
      console.error(err);
    }
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 text-gray-900">
      <div className="max-w-md w-full p-6 space-y-6 bg-gray-800 border border-red-500 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold text-center text-blue-700">Account Verification</h2>
        <p className="text-center text-gray-400">
          Your account is not verified. Check your email for the verification link.
        </p>
        <p className="text-center text-gray-500">
          Or enter your email below to resend the verification link.
        </p>

        <form
          className="flex flex-col space-y-4"
          onSubmit={handleSendVerification}
        >
          <input
            type="email"
            placeholder="Enter your email"
            name="email"
            value={email}
            onChange={handleChange}
            className="w-full p-3 bg-white border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all duration-300"
          />
          <button
            type="submit"
            className="w-full py-3 px-6 bg-yellow-300 hover:bg-yellow-500 text-gray-900 font-semibold rounded-lg shadow-md transition-all duration-300 focus:ring-2 focus:ring-blue-400"
          >
            Resend Verification Link
          </button>
        </form>
      </div>
    </div>
  );
};
