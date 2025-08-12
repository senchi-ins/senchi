"use client"

import * as React from "react"
import {
  CreditCard,
  Settings,
  User,
  Home,
} from "lucide-react"

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command"

export function CommandSearch() {
  const [open, setOpen] = React.useState(false)

  const recentProperties = [
    {
      id: 1,
      address: "123 Oak Street, Toronto, ON",
      icon: Home,
    },
    {
      id: 2,
      address: "456 Maple Avenue, Vancouver, BC",
      icon: Home,
    },
    {
      id: 3,
      address: "789 Pine Road, Calgary, AB",
      icon: Home,
    },
    {
      id: 4,
      address: "321 Elm Drive, Montreal, QC",
      icon: Home,
    },
    {
      id: 5,
      address: "654 Birch Lane, Ottawa, ON",
      icon: Home,
    },
  ]

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <>
      <div className="relative">
        <input
          type="text"
          placeholder="Search..."
          className="w-full h-9 px-3 py-2 text-sm bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
          onClick={() => setOpen(true)}
          readOnly
        />
        <kbd className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-muted text-muted-foreground pointer-events-none inline-flex h-5 items-center gap-1 rounded border px-1.5 font-mono text-[10px] font-medium opacity-100 select-none">
          <span className="text-xs">⌘</span>K
        </kbd>
      </div>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Type a command or search..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Recent Properties">
            {recentProperties.map((property) => (
              <CommandItem key={property.id}>
                <property.icon />
                <span>{property.address}</span>
              </CommandItem>
            ))}
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading="Settings">
            <CommandItem>
              <User />
              <span>Profile</span>
              <CommandShortcut>⌘P</CommandShortcut>
            </CommandItem>
            <CommandItem>
              <CreditCard />
              <span>Billing</span>
              <CommandShortcut>⌘B</CommandShortcut>
            </CommandItem>
            <CommandItem>
              <Settings />
              <span>Settings</span>
              <CommandShortcut>⌘S</CommandShortcut>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  )
}
