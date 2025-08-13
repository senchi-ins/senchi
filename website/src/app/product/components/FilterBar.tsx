"use client"

import React, { useState } from 'react';
import { Search, ChevronDown, Plus } from "lucide-react";

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

interface FilterBarProps {
  properties: Property[];
  onPropertySelect: (property: Property) => void;
  onFilterChange: (filter: string) => void;
  onAddProperty: () => void;
  onSearchChange: (searchQuery: string) => void;
}

export function FilterBar({ properties, onPropertySelect, onFilterChange, onAddProperty, onSearchChange }: FilterBarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('Alert severity');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);

  const severityOptions = ['High', 'Medium', 'Low'];

  const filteredProperties = properties.filter(property =>
    property.address.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSearchSubmit = () => {
    console.log('Search submitted:', searchQuery);
    setShowSuggestions(false);
    // Add your search logic here
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearchSubmit();
    }
  };

  const handlePropertySelect = (property: Property) => {
    setSearchQuery(property.address);
    setShowSuggestions(false);
    onPropertySelect(property);
  };

  const handleSeveritySelect = (severity: string) => {
    setSelectedFilter(severity);
    setShowFilterDropdown(false);
    onFilterChange(severity);
  };

  const handleAddProperty = () => {
    onAddProperty();
  };

  return (
    <div className="flex items-end justify-between px-8 py-4 pr-4">
      <div className="flex items-end gap-24">
        {/* Filter by search */}
        <div className="flex items-center gap-3">
          <Search className="w-5 h-5 text-gray-500" />
          <div className="relative">
            <input
              type="text"
              placeholder="Search properties by address..."
              value={searchQuery}
                          onChange={(e) => {
              const value = e.target.value;
              setSearchQuery(value);
              setShowSuggestions(value.length > 0);
              onSearchChange(value);
            }}
              onKeyPress={handleKeyPress}
              onFocus={() => setShowSuggestions(searchQuery.length > 0)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              className="border-b border-gray-300 bg-transparent px-2 py-2 text-base focus:outline-none focus:border-gray-600 w-80"
            />
            {showSuggestions && filteredProperties.length > 0 && (
              <div className="absolute top-full left-0 w-full bg-white border border-gray-200 rounded-md shadow-lg z-10 mt-1">
                              {filteredProperties.map((property) => (
                <div
                  key={property.id}
                  className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                  onClick={() => handlePropertySelect(property)}
                >
                  {property.address}
                </div>
              ))}
              </div>
            )}
          </div>
        </div>

        {/* Slice: Alert severity */}
        <div className="flex flex-col relative">
          <label className="text-sm text-gray-600 mb-2">Filter by</label>
          <div 
            className="flex items-center gap-3 border-b border-gray-300 pb-2 cursor-pointer w-48"
            onClick={() => setShowFilterDropdown(!showFilterDropdown)}
            onBlur={() => setTimeout(() => setShowFilterDropdown(false), 200)}
          >
            <span className="text-base">{selectedFilter}</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </div>
          {showFilterDropdown && (
            <div className="absolute top-full left-0 w-48 bg-white border border-gray-200 rounded-md shadow-lg z-10 mt-1">
              {severityOptions.map((severity, index) => (
                <div
                  key={index}
                  className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                  onClick={() => handleSeveritySelect(severity)}
                >
                  {severity}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Add Property Button */}
      <button
        onClick={handleAddProperty}
        className="flex items-center gap-2 px-4 py-2 bg-senchi-primary text-white rounded-md hover:bg-senchi-primary/90 transition-colors -mr-4"
      >
        <Plus className="w-4 h-4" />
        <span>Add property</span>
      </button>
    </div>
  );
}
