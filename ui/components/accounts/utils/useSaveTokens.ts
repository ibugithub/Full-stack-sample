import { useCallback } from 'react';

import { useRouter } from 'next/navigation';
import { useAppDispatch } from '@/configs/redux/hooks';
import { fetchLoggedInUser } from '@/configs/redux/auth/authSlice';

interface Tokens {
  access: string;
  refresh: string;
}

export const useSaveTokens = () => {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const SaveTokensToLocal = useCallback(
    (Tokens: Tokens): void => {
      const HandleFetchUser = (): void => {
        dispatch(fetchLoggedInUser());
      };
      localStorage.setItem('accessToken', Tokens.access);
      const cookieName = 'refreshToken';
      const cookieValue = Tokens.refresh;
      const expirationDate = new Date();
      expirationDate.setMonth(expirationDate.getMonth() + 1);
      document.cookie = `${cookieName}=${cookieValue}; expires=${expirationDate.toUTCString()}; path=/; SameSite=strict${window.location.protocol === 'https:' ? '; Secure' : ''}`;
      HandleFetchUser();
      router.push('/accounts/profile');
    },
    [dispatch, router],
  );
  return SaveTokensToLocal;
};
