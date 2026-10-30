'use client';

import Cookies from 'js-cookie';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

export const AxiosReqInstance = () => {
  const baseURL = (process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '').replace(/\/$/, '');
  const instance = axios.create({ baseURL, withCredentials: true, timeout: 30000 });

  instance.interceptors.request.use(async (request) => {
    let access = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
    if (!access) return request;
    let expires = 0;
    try {
      expires = jwtDecode(access).exp ?? 0;
    } catch {
      throw new axios.CanceledError('Invalid session token. Please sign in again.');
    }
    if (expires * 1000 <= Date.now() + 5000) {
      const previous = access;
      const refresh = Cookies.get('refreshToken');
      if (!refresh)
        throw new axios.CanceledError('Your session has expired. Please sign in again.');
      const { data } = await axios.post(
        `${baseURL}/api/users/refresh/`,
        { refresh },
        { timeout: 30000 },
      );
      if (localStorage.getItem('accessToken') !== previous) {
        throw new axios.CanceledError('The signed-in account changed.');
      }
      access = data.access;
      localStorage.setItem('accessToken', access);
    }
    request.headers.Authorization = `Bearer ${access}`;
    return request;
  });
  return instance;
};
