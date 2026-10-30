'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ProfileModal } from '@/components/accounts/profileModal';
import { useAppSelector } from '@/configs/redux/hooks';

export const NavBar = () => {
  const pathname = usePathname();
  const { isAuthenticated, status, loogedInUser } = useAppSelector((state) => state.auth);
  const user = loogedInUser.user ?? loogedInUser;
  const showAdmin = isAuthenticated && status === 'authenticated' && user.is_staff === true;
  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-gray-200 bg-white">
      <nav
        aria-label="Main navigation"
        className="mx-auto flex min-h-16 max-w-6xl items-center justify-between gap-3 px-4 sm:px-6 lg:min-h-[90px]"
      >
        <Link
          href="/"
          aria-label="Template home"
          className="flex items-center gap-3 font-semibold text-gray-900"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-sm font-bold text-white">
            FT
          </span>
          <span className="hidden sm:inline">Full-stack Template</span>
        </Link>
        <div className="flex items-center gap-1 sm:gap-3">
          <Link
            href="/"
            aria-current={pathname === '/' ? 'page' : undefined}
            className="rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-blue-50 focus-visible:outline-blue-600"
          >
            Home
          </Link>
          {showAdmin && user.admin_url && (
            <a
              href={user.admin_url}
              className="rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-blue-50 focus-visible:outline-blue-600"
            >
              Admin
            </a>
          )}
          <ProfileModal />
        </div>
      </nav>
    </header>
  );
};
