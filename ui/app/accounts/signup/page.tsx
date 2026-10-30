import Signup from '@/components/accounts/signup';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Create an Account | Full-stack Template',
  description: 'Create your Full-stack Template account.',
  robots: { index: false, follow: true },
};

export default function Register() {
  return (
    <>
      <Signup />
    </>
  );
}
