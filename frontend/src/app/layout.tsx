import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { FlowProvider } from '@/context/FlowContext';

import './globals.css';

export const metadata: Metadata = {
  title: 'K-Labor Shield',
  description: '외국인 근로자를 위한 노동권 보호 통합 AI',
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="ko">
      <body>
        <FlowProvider>{children}</FlowProvider>
      </body>
    </html>
  );
}
