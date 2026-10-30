'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useId, useRef, useState } from 'react';
import { ChevronDown, LogOut, UserRound } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@/configs/redux/hooks';
import { signOut } from '@/configs/redux/auth/authSlice';
import Cookies from 'js-cookie';
import { toast } from 'react-toastify';
import { revokeRefreshToken } from '@/lib/logout';

type ProfileModalProps = {
  mobile?: boolean;
  onNavigate?: () => void;
};

export const ProfileModal = ({ mobile = false, onNavigate }: ProfileModalProps) => {
  const { isAuthenticated, loogedInUser } = useAppSelector((state) => state.auth);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const dispatch = useAppDispatch();
  const pathname = usePathname();
  const router = useRouter();
  const menuId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const name = loogedInUser?.name?.trim() || loogedInUser?.display_name?.trim() || 'My Account';
  const controlClass =
    'inline-flex min-h-11 items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-blue-50 hover:text-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600';

  useEffect(() => {
    setIsModalOpen(false);
  }, [pathname, isAuthenticated]);

  useEffect(() => {
    if (!isModalOpen) return;
    const onPointerDown = (event: PointerEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setIsModalOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsModalOpen(false);
        buttonRef.current?.focus();
      }
    };
    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [isModalOpen]);

  const close = () => {
    setIsModalOpen(false);
    onNavigate?.();
  };
  const handleLogout = async () => {
    const refresh = Cookies.get('refreshToken');
    // Clear this device immediately, even if the server is unreachable.
    localStorage.removeItem('accessToken');
    Cookies.remove('refreshToken', { path: '/' });
    dispatch(signOut());
    close();
    if (pathname === '/accounts/profile' || pathname.startsWith('/accounts/profile/')) {
      router.replace('/accounts/signin');
    }
    if (!refresh) return;
    try {
      await revokeRefreshToken(refresh);
    } catch {
      toast.warning(
        'Signed out on this device, but the server could not revoke the refresh token.',
      );
    }
  };

  if (!isAuthenticated)
    return (
      <Link
        href="/accounts/signin"
        onClick={close}
        aria-current={pathname === '/accounts/signin' ? 'page' : undefined}
        className={`${controlClass} ${pathname === '/accounts/signin' ? 'bg-blue-50 text-blue-700' : ''}`}
      >
        Sign In
      </Link>
    );

  return (
    <div
      ref={containerRef}
      className="relative"
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null))
          setIsModalOpen(false);
      }}
    >
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsModalOpen((value) => !value)}
        aria-expanded={isModalOpen}
        aria-controls={menuId}
        className={`${controlClass} ${mobile ? 'w-full justify-between' : ''}`}
      >
        <span className="flex min-w-0 items-center gap-2">
          <UserRound
            size={17}
            className="shrink-0"
            aria-hidden="true"
          />
          <span
            className={mobile ? 'truncate' : 'max-w-28 truncate'}
            title={name}
          >
            {name}
          </span>
        </span>
        <ChevronDown
          size={15}
          aria-hidden="true"
          className={`shrink-0 transition-transform ${isModalOpen ? 'rotate-180' : ''}`}
        />
      </button>
      {isModalOpen && (
        <div
          id={menuId}
          className={
            mobile
              ? 'mt-1 space-y-1 rounded-lg border border-gray-200 bg-gray-50 p-2'
              : 'absolute right-0 top-full z-50 mt-2 w-52 space-y-1 rounded-xl border border-gray-200 bg-white p-2 shadow-lg'
          }
        >
          <Link
            href="/accounts/profile"
            onClick={close}
            className="flex min-h-11 items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 focus-visible:outline-blue-600"
          >
            <UserRound
              size={16}
              aria-hidden="true"
            />
            My Profile
          </Link>
          <button
            type="button"
            onClick={handleLogout}
            className="flex min-h-11 w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-gray-700 hover:bg-red-50 hover:text-red-700 focus-visible:outline-blue-600"
          >
            <LogOut
              size={16}
              aria-hidden="true"
            />
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
};
