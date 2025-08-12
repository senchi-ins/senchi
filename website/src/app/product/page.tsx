import React from 'react';

import SidebarProvider from './components/SidebarProvider';
// import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';



export default function ProductPage() {
  return (
    <div>
      <SidebarProvider>
        <div>
          <h1>Product</h1>
        </div>
      </SidebarProvider>
    </div>
  )
}