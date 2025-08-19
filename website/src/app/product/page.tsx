"use client"

import React, { useState } from 'react';
import { useProperties } from '@/contexts/PropertiesContext';

import { SectionCards } from './components/Card';
import { Line } from './components/Line';
import { FilterBar } from './components/FilterBar';
import PropertyOverview from './components/PropertyOverview';

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

export default function ProductPage() {
  const { properties: allProperties, isLoading, error } = useProperties();
  const [selectedProperty, setSelectedProperty] = useState<UserProperty | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('Alert severity');
  const [filteredProperties, setFilteredProperties] = useState<UserProperty[]>(allProperties);

  // Update filtered properties when allProperties changes
  React.useEffect(() => {
    setFilteredProperties(allProperties);
  }, [allProperties]);
  // Filter properties based on search and filter criteria
  const filterProperties = (searchQuery: string, filter: string) => {
    let filtered = allProperties;

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(property =>
        property.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (property.address && property.address.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (property.propertyId && property.propertyId.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    if (filter !== 'All') {
      filtered = filtered.filter(property => {
        if (!property.alert) return false;
        return property.alert.severity.toLowerCase() === filter.toLowerCase();
      });
    }

    setFilteredProperties(filtered);
  };

  const handlePropertySelect = (property: UserProperty) => {
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

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your properties...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
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
      <p className="text-gray-600 text-sm mt-4 pl-10">Found {filteredProperties.length} properties. New properties will be added as users connect their homes to Senchi</p>
      
      <div className="space-y-4 mt-8">
        {filteredProperties.length === 0 ? (
          <div className="text-center">
            <p className="text-gray-600">No properties found.</p>
          </div>
        ) : (
          filteredProperties.map((property) => (
            <PropertyOverview
              key={property.id}
              id={property.id}
              name={property.name || property.propertyId || ''}
              address={property.address || property.name}
              property_type={property.property_type || ''}
              description={property.description || ''}
              scores={property.scores || { overall: 0, internal: 0, external: 0 }}
              devices={property.devices || { connected: 0, total: 0 }}
              total_savings={property.total_savings || 0}
              alert={property.alert}
            />
          ))
        )}
      </div>
    </div>
  )
}