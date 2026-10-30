import axios from 'axios';
import { apiErrorMessage } from './apiError';

export function signInError(error: unknown): string {
  const fallback = 'We could not sign you in. Please try again.';
  if (!axios.isAxiosError(error)) return fallback;
  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
    return 'Sign-in took too long. Please try again.';
  }
  if (!error.response) {
    return 'We could not connect to the sign-in service. Check your connection and try again.';
  }
  const { status } = error.response;
  if (status >= 500) return 'Sign-in is temporarily unavailable. Please try again shortly.';
  if (status === 429)
    return apiErrorMessage(error, 'Too many sign-in attempts. Please wait a moment and try again.');
  if (status === 401) return 'The email or password is incorrect.';
  const message = apiErrorMessage(error, fallback);
  return message === 'Invalid credentials' ? 'The email or password is incorrect.' : message;
}
