import React from 'react';
import SidebarProvider from './components/SidebarProvider';
import { PropertiesProvider } from '@/contexts/PropertiesContext';

export default function ProductLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <PropertiesProvider>
      <SidebarProvider>
        {children}
      </SidebarProvider>
    </PropertiesProvider>
  );
}
