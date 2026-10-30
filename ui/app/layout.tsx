'use client';

import './globals.css';
import { NavBar } from '@/components/navBar/navbar';
import StoreProvider from '@/app/utils/provider/StoreProvider';
import ReduxInitializer from '@/components/accounts/reduxInitializer';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <StoreProvider>
      <html
        lang="en"
        suppressHydrationWarning
      >
        <body>
          <ReduxInitializer>
            <NavBar />
            <ToastContainer />
            <div className="pt-16 lg:pt-[90px]">{children}</div>
          </ReduxInitializer>
        </body>
      </html>
    </StoreProvider>
  );
}
