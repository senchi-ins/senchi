'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface UserProperty {
  id: string;
  name: string;
  address?: string;
  propertyId?: string;
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

interface PropertiesContextType {
  properties: UserProperty[];
  isLoading: boolean;
  error: string | null;
  refreshProperties: () => Promise<void>;
}

const PropertiesContext = createContext<PropertiesContextType | undefined>(undefined);

export function PropertiesProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [properties, setProperties] = useState<UserProperty[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProperties = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/properties', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          property_name: null,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/login');
          return;
        }
        throw new Error('Failed to fetch properties');
      }

      const data = await response.json();
      setProperties(data.properties || []);
    } catch (error) {
      console.error('Error fetching properties:', error);
      setError('Failed to load properties');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshProperties = async () => {
    await fetchProperties();
  };

  useEffect(() => {
    fetchProperties();
  }, [router]);

  return (
    <PropertiesContext.Provider value={{
      properties,
      isLoading,
      error,
      refreshProperties,
    }}>
      {children}
    </PropertiesContext.Provider>
  );
}

export function useProperties() {
  const context = useContext(PropertiesContext);
  if (context === undefined) {
    throw new Error('useProperties must be used within a PropertiesProvider');
  }
  return context;
}
