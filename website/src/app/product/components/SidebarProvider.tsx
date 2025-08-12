import React from 'react';

import ProductSidebar from './Sidebar';
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';


export default function ProductPage({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex h-screen">
        <ProductSidebar />
        <main className="flex-1 flex flex-col">
          <div className="p-4">
            <SidebarTrigger />
          </div>
          <div className="flex-1">
            {children}
          </div>
        </main>
      </div>
    </SidebarProvider>
  )
}