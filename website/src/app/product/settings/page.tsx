'use client'

import React, { useState } from 'react';
import { Phone, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useProperties } from '@/contexts/PropertiesContext';

interface PhoneNumber {
  id: string;
  number: string;
  name: string;
}

export default function SettingsPage() {
  const { properties } = useProperties();
  const [phoneNumbers, setPhoneNumbers] = useState<PhoneNumber[]>([]);
  const [newName, setNewName] = useState('');
  const [newProperty, setNewProperty] = useState('');
  const [newNumber, setNewNumber] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddPhoneNumber = async () => {
    if (!newName.trim() || !newProperty.trim() || !newNumber.trim()) return;
    
    // Find the property by name to get the property_id
    const selectedProperty = properties.find(prop => prop.name === newProperty.trim());
    if (!selectedProperty) {
      console.error('Property not found');
      return;
    }
    
    try {
      const response = await fetch('/api/phone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newName.trim(),
          property_name: newProperty.trim(),
          property_id: selectedProperty.id, // Send the actual property_id
          role: 'manager',
          number: newNumber.trim(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setPhoneNumbers([...phoneNumbers, data]);
        setNewName('');
        setNewProperty('');
        setNewNumber('');
        setIsAdding(false);
      } else {
        console.error('Failed to add phone number');
      }
    } catch (error) {
      console.error('Error adding phone number:', error);
    }
  };

  const handleRemovePhoneNumber = (id: string) => {
    setPhoneNumbers(phoneNumbers.filter(phone => phone.id !== id));
  };

  const formatPhoneNumber = (number: string) => {
    // Simple phone number formatting
    const cleaned = number.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return number;
  };



  return (
    <div className="min-h-screen bg-white w-full">
    {/* Header */}
      <div className="bg-white px-6 py-4">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        </div>
      </div>

              {/* Content */}
        <div className="px-6 py-8 flex items-center">
          <Card className="w-[600px] h-[500px]">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Phone className="h-6 w-6 text-senchi-primary" />
              <div>
                <CardTitle>SMS Notifications</CardTitle>
                <CardDescription>
                  Add phone numbers to receive SMS alerts for your properties
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Existing Phone Numbers */}
            {phoneNumbers.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-medium text-gray-900">Current Recipients</h3>
                {phoneNumbers.map((phone) => (
                  <div
                    key={phone.id}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg bg-gray-50"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{phone.name}</p>
                      <p className="text-sm text-gray-600">{formatPhoneNumber(phone.number)}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemovePhoneNumber(phone.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Add New Phone Number */}
            {isAdding ? (
              <div className="space-y-4 p-4 border border-gray-200 rounded-lg ">
                <h3 className="font-medium text-gray-900">Add New Recipient</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Name
                    </label>
                    <Input
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      placeholder="Enter recipient name"
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Property
                    </label>
                    <select
                      value={newProperty}
                      onChange={(e) => setNewProperty(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-senchi-primary focus:border-transparent"
                    >
                      <option value="">Select a property</option>
                      {properties.map((property) => (
                        <option key={property.id} value={property.name}>
                          {property.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <Input
                      value={newNumber}
                      onChange={(e) => setNewNumber(e.target.value)}
                      placeholder="(555) 123-4567"
                      className="w-full"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={handleAddPhoneNumber}
                      disabled={!newName.trim() || !newNumber.trim()}
                      className="bg-senchi-primary text-white hover:bg-senchi-primary/80"
                    >
                      Add Recipient
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setIsAdding(false);
                        setNewName('');
                        setNewNumber('');
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <Button
                onClick={() => setIsAdding(true)}
                className="w-full bg-senchi-primary text-white hover:bg-senchi-primary/80"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Phone Number
              </Button>
            )}

            {phoneNumbers.length === 0 && !isAdding && (
              <div className="text-center py-8 text-gray-500">
                <Phone className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>No phone numbers added yet</p>
                <p className="text-sm">Add a phone number to receive SMS notifications</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
