"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
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

interface Property {
  id: string;
  name: string;
  address?: string;
  property_type?: string;
  description?: string;
  scores?: {
    overall: number;
    internal: number;
    external: number;
  };
  devices?: {
    connected: number;
    total: number;
  };
  total_savings?: number;
  alert?: {
    type: string;
    message: string;
    severity: 'high' | 'medium' | 'low';
  };
}

export function CommandSearch() {
  const router = useRouter()
  const [open, setOpen] = React.useState(false)
  const [properties, setProperties] = React.useState<Property[]>([])
  const [loading, setLoading] = React.useState(false)

  // Fetch properties from API
  const fetchProperties = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/properties', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          property_name: null, // Get all properties
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch properties: ${response.status}`)
      }

      const data = await response.json()
      if (data.success && data.properties) {
        setProperties(data.properties)
      }
    } catch (error) {
      console.error('Error fetching properties:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch properties when component mounts
  React.useEffect(() => {
    fetchProperties()
  }, [])

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
          <CommandGroup heading="Properties">
            {loading ? (
              <CommandItem disabled>
                <Home className="w-4 h-4" />
                <span>Loading properties...</span>
              </CommandItem>
            ) : properties.length > 0 ? (
              properties.map((property) => (
                <CommandItem 
                  key={property.id}
                  onSelect={() => {
                    router.push(`/product/${property.id}`)
                    setOpen(false)
                  }}
                >
                  <Home className="w-4 h-4" />
                  <span>{property.address || property.name}</span>
                </CommandItem>
              ))
            ) : (
              <CommandItem disabled>
                <Home className="w-4 h-4" />
                <span>No properties found</span>
              </CommandItem>
            )}
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading="Navigation">
            <CommandItem 
              onSelect={() => {
                router.push('/product')
                setOpen(false)
              }}
            >
              <Home />
              <span>Properties</span>
            </CommandItem>
            <CommandItem 
              onSelect={() => {
                router.push('/product/settings')
                setOpen(false)
              }}
            >
              <Settings />
              <span>Settings</span>
            </CommandItem>
          </CommandGroup>
          <CommandSeparator />
        </CommandList>
      </CommandDialog>
    </>
  )
}