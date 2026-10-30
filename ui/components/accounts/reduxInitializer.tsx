'use client';

import { useEffect } from 'react';
import { useAppDispatch } from '@/configs/redux/hooks';
import { fetchLoggedInUser } from '@/configs/redux/auth/authSlice';

const ReduxInitializer = ({ children }: { children: React.ReactNode }) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchLoggedInUser());
  }, [dispatch]);

  return <>{children}</>;
};

export default ReduxInitializer;
