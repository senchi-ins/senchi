"use client"

import React from 'react';
import { Home, Settings, User2, ChevronUp, LogOut } from "lucide-react"
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarHeader,
    SidebarFooter,
  } from "@/components/ui/sidebar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu"
import { CommandSearch } from './CommandSearch';


  const items = [
    {
      title: "Properties",
      url: "/product",
      icon: Home,
      // badge: "10", // TODO: Link this alert to api
    },
    {
      title: "Settings",
      url: "/product/settings",
      icon: Settings,
    },
]

const accountItems = [
  // {
  //   title: "Account",
  //   url: "#",
  //   icon: User2,
  // },
  {
    title: "Sign Out",
    url: "#",
    icon: LogOut,
  }
]
const userName = "Senchi Demo"

export default function ProductSidebar() {
  const router = useRouter();
  const { logout } = useAuth();

  const handleMouseEnter = (url: string) => {
    // Preload the page on hover
    router.prefetch(url);
  };

  const handleNavigation = (url: string) => {
    // Force navigation even if we're in the same section
    router.push(url);
  };

  const handleSignOut = () => {
    logout();
    router.push('/login');
  };

  const handleAccountItemClick = (title: string) => {
    if (title === "Sign Out") {
      handleSignOut();
    } else if (title === "Account") {
      // Handle account navigation if needed
      console.log("Account clicked");
    }
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="p-2">
        <div className="flex items-center justify-start">
          <Image 
            src="/senchi-logo.png" 
            alt="Senchi" 
            width={60} 
            height={60} 
            className="h-12 w-auto group-data-[collapsible=icon]:h-8 group-data-[collapsible=icon]:w-8"
          />
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="group-data-[collapsible=icon]:hidden">{}</SidebarGroupLabel>
          <div className="group-data-[collapsible=icon]:hidden pb-2">
            <CommandSearch />
          </div>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton 
                    className="group w-full"
                    onMouseEnter={() => handleMouseEnter(item.url)}
                    onClick={() => handleNavigation(item.url)}
                  >
                    <item.icon className="group-data-[collapsible=icon]:h-4 group-data-[collapsible=icon]:w-4" />
                    <span className="group-data-[collapsible=icon]:hidden group-data-[collapsible=icon]:text-sm">{item.title}</span>
                    {/* {item.badge && (
                      <span className="ml-auto bg-senchi-primary p-2 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium group-data-[collapsible=icon]:absolute group-data-[collapsible=icon]:-top-1 group-data-[collapsible=icon]:-right-1 group-data-[collapsible=icon]:ml-0 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5 group-data-[collapsible=icon]:text-[10px]">
                        {item.badge}
                      </span>
                    )} */}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton>
                  <User2 />
                  <span className="group-data-[collapsible=icon]:hidden">{userName}</span>
                  <ChevronUp className="ml-auto group-data-[collapsible=icon]:hidden" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                side="top"
                align="start"
                className="w-60 group-data-[collapsible=icon]:align-end"
              >
                {accountItems.map((item) => (
                  <DropdownMenuItem 
                    key={item.title}
                    onClick={() => handleAccountItemClick(item.title)}
                  >
                    <item.icon />
                    <span>{item.title}</span>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}