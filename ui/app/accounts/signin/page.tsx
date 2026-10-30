import Signin from '@/components/accounts/signin';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign In | Full-stack Template',
  description: 'Sign in to your Full-stack Template account.',
  robots: { index: false, follow: true },
};

const SigninPage = () => {
  return (
    <>
      <Signin />
    </>
  );
};

export default SigninPage;
