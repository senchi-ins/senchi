"use client"

import React, { useState } from 'react';

import SidebarProvider from './components/SidebarProvider';
import { SectionCards } from './components/Card';
import { Line } from './components/Line';
import { FilterBar } from './components/FilterBar';
import PropertyOverview from './components/PropertyOverview';

interface Property {
  id: string;
  address: string;
  propertyId: string;
  scores: {
    overall: number;
    internal: number;
    external: number;
  };
  devices: {
    connected: number;
    total: number;
  };
  alert?: {
    type: string;
    message: string;
    severity: 'high' | 'medium' | 'low';
  };
}

export default function ProductPage() {
  const [allProperties] = useState<Property[]>([
    {
      id: '1',
      address: '123 Maple Street, Toronto, ON',
      propertyId: '123-maple-street',
      scores: { overall: 77, internal: 79, external: 73 },
      devices: { connected: 5, total: 6 },
      alert: {
        type: 'water_flow',
        message: 'Abnormal water flow detected in kitchen sink',
        severity: 'medium'
      }
    },
    {
      id: '2',
      address: '456 Oak Avenue, Vancouver, BC',
      propertyId: '456-oak-avenue',
      scores: { overall: 85, internal: 82, external: 88 },
      devices: { connected: 6, total: 6 }
    },
    {
      id: '3',
      address: '789 Pine Road, Calgary, AB',
      propertyId: '789-pine-road',
      scores: { overall: 92, internal: 90, external: 94 },
      devices: { connected: 4, total: 5 },
      alert: {
        type: 'temperature',
        message: 'High temperature detected in basement',
        severity: 'low'
      }
    },
    {
      id: '4',
      address: '321 Elm Drive, Montreal, QC',
      propertyId: '321-elm-drive',
      scores: { overall: 68, internal: 65, external: 71 },
      devices: { connected: 3, total: 6 },
      alert: {
        type: 'pressure',
        message: 'Low water pressure detected',
        severity: 'low'
      }
    }
  ]);

  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('Alert severity');
  const [filteredProperties, setFilteredProperties] = useState<Property[]>(allProperties);

  // Filter properties based on search and filter criteria
  const filterProperties = (searchQuery: string, filter: string) => {
    let filtered = allProperties;

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(property =>
        property.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
        property.propertyId.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply severity filter
    if (filter !== 'Alert severity') {
      filtered = filtered.filter(property => {
        if (!property.alert) return false;
        return property.alert.severity.toLowerCase() === filter.toLowerCase();
      });
    }

    setFilteredProperties(filtered);
  };

  const handlePropertySelect = (property: Property) => {
    setSelectedProperty(property);
    console.log('Property selected:', property);
    // Handle property selection - you can update state here
  };

  const handleSearchChange = (searchQuery: string) => {
    console.log('Search changed:', searchQuery);
    filterProperties(searchQuery, selectedFilter);
  };

  const handleFilterChange = (filter: string) => {
    setSelectedFilter(filter);
    console.log('Filter changed:', filter);
    // Re-filter properties with current search and new filter
    filterProperties(selectedProperty?.address || '', filter);
  };

  const handleAddProperty = () => {
    console.log('Add property clicked');
    // Handle add property - you can open modal or navigate here
  };

  return (
    <div>
      <SidebarProvider>
        <div className="pl-1">
          <SectionCards />
          <Line thickness={1} color="#e5e7eb" className="my-2 mx-10 pl-10" />
          <FilterBar 
            properties={allProperties}
            onPropertySelect={handlePropertySelect}
            onFilterChange={handleFilterChange}
            onAddProperty={handleAddProperty}
            onSearchChange={handleSearchChange}
          />
          
          {/* Property Overview Cards */}
          <div className="space-y-4 mt-8">
            {filteredProperties.map((property) => (
              <PropertyOverview
                key={property.id}
                id={property.id}
                address={property.address}
                scores={property.scores}
                devices={property.devices}
                alert={property.alert}
              />
            ))}
          </div>
        </div>
      </SidebarProvider>
    </div>
  )
}