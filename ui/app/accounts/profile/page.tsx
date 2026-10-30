import { Profile } from '@/components/profile/profile';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Profile | Full-stack Template',
  robots: { index: false, follow: true },
};

export default function ProfilePage() {
  return (
    <>
      <Profile />
    </>
  );
}
