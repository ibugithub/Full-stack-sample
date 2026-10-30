import axios from 'axios';

export async function revokeRefreshToken(refresh: string): Promise<void> {
  if (!refresh) return;
  const base = (process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '').replace(/\/$/, '');
  try {
    // Do not refresh access credentials as part of signing out.
    await axios.post(`${base}/api/users/logout/`, { refresh }, { timeout: 10000 });
  } catch (error) {
    // An expired, invalid or already-revoked token cannot renew a session.
    if (axios.isAxiosError(error) && error.response?.status === 401) return;
    throw error;
  }
}
