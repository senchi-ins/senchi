"use client"

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Home, Wifi, Droplets, AlertTriangle } from "lucide-react";

interface PropertyDetails {
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
  alerts: Array<{
    id: string;
    type: string;
    message: string;
    severity: 'high' | 'medium' | 'low';
    timestamp: string;
  }>;
  details: {
    type: string;
    yearBuilt: number;
    squareFootage: number;
    rooms: number;
    lastInspection: string;
  };
}

// Mock API function
const fetchPropertyDetails = async (id: string): Promise<PropertyDetails> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const mockData: Record<string, PropertyDetails> = {
    '1': {
      id: '1',
      address: '123 Maple Street, Toronto, ON',
      propertyId: '123-maple-street',
      scores: { overall: 77, internal: 79, external: 73 },
      devices: { connected: 5, total: 6 },
      alerts: [
        {
          id: '1',
          type: 'water_flow',
          message: 'Abnormal water flow detected in kitchen sink',
          severity: 'medium',
          timestamp: '2024-01-15T10:30:00Z'
        }
      ],
      details: {
        type: 'Single Family Home',
        yearBuilt: 1995,
        squareFootage: 2500,
        rooms: 8,
        lastInspection: '2024-01-10'
      }
    },
    '2': {
      id: '2',
      address: '456 Oak Avenue, Vancouver, BC',
      propertyId: '456-oak-avenue',
      scores: { overall: 85, internal: 82, external: 88 },
      devices: { connected: 6, total: 6 },
      alerts: [],
      details: {
        type: 'Townhouse',
        yearBuilt: 2010,
        squareFootage: 1800,
        rooms: 6,
        lastInspection: '2024-01-12'
      }
    },
    '3': {
      id: '3',
      address: '789 Pine Road, Calgary, AB',
      propertyId: '789-pine-road',
      scores: { overall: 92, internal: 90, external: 94 },
      devices: { connected: 4, total: 5 },
      alerts: [
        {
          id: '2',
          type: 'temperature',
          message: 'High temperature detected in basement',
          severity: 'high',
          timestamp: '2024-01-15T14:20:00Z'
        }
      ],
      details: {
        type: 'Condo',
        yearBuilt: 2015,
        squareFootage: 1200,
        rooms: 4,
        lastInspection: '2024-01-08'
      }
    },
    '4': {
      id: '4',
      address: '321 Elm Drive, Montreal, QC',
      propertyId: '321-elm-drive',
      scores: { overall: 68, internal: 65, external: 71 },
      devices: { connected: 3, total: 6 },
      alerts: [
        {
          id: '3',
          type: 'pressure',
          message: 'Low water pressure detected',
          severity: 'low',
          timestamp: '2024-01-15T09:15:00Z'
        }
      ],
      details: {
        type: 'Duplex',
        yearBuilt: 1988,
        squareFootage: 2200,
        rooms: 7,
        lastInspection: '2024-01-05'
      }
    }
  };

  return mockData[id] || mockData['1'];
};

export default function PropertyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [property, setProperty] = useState<PropertyDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProperty = async () => {
      if (params.id) {
        try {
          const data = await fetchPropertyDetails(params.id as string);
          setProperty(data);
        } catch (error) {
          console.error('Failed to fetch property details:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    loadProperty();
  }, [params.id]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-400 text-white';
    if (score >= 70) return 'bg-yellow-400 text-white';
    return 'bg-red-400 text-white';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-32 mb-8"></div>
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!property) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg p-6 shadow-sm text-center">
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Property Not Found</h1>
            <p className="text-gray-600">The property you&apos;re looking for doesn&apos;t exist.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Properties</span>
          </button>
        </div>

        {/* Property Header */}
        <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
          <div className="flex items-start gap-4">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Home className="w-8 h-8 text-purple-600" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{property.address}</h1>
              <p className="text-gray-600">Property ID: {property.propertyId}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Performance Scores */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Scores</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Overall</span>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getScoreBgColor(property.scores.overall)} ${getScoreColor(property.scores.overall)}`}>
                  {property.scores.overall}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Internal</span>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getScoreBgColor(property.scores.internal)} ${getScoreColor(property.scores.internal)}`}>
                  {property.scores.internal}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">External</span>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getScoreBgColor(property.scores.external)} ${getScoreColor(property.scores.external)}`}>
                  {property.scores.external}
                </div>
              </div>
            </div>
          </div>

          {/* Device Status */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Device Status</h2>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-white border-2 border-gray-200 flex flex-col items-center justify-center">
                <Wifi className="w-5 h-5 text-gray-600 mb-1" />
                <span className="text-sm font-semibold text-gray-900">{property.devices.connected}/{property.devices.total}</span>
              </div>
              <div>
                <p className="text-sm text-gray-600">Connected Devices</p>
                <p className="text-lg font-semibold text-gray-900">{property.devices.connected} of {property.devices.total}</p>
              </div>
            </div>
          </div>

          {/* Property Details */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Property Details</h2>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-600">Type:</span>
                <p className="font-medium">{property.details.type}</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Year Built:</span>
                <p className="font-medium">{property.details.yearBuilt}</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Square Footage:</span>
                <p className="font-medium">{property.details.squareFootage} sq ft</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Rooms:</span>
                <p className="font-medium">{property.details.rooms}</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Last Inspection:</span>
                <p className="font-medium">{property.details.lastInspection}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Alerts */}
        {property.alerts.length > 0 && (
          <div className="bg-white rounded-lg p-6 shadow-sm mt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              Active Alerts ({property.alerts.length})
            </h2>
            <div className="space-y-3">
              {property.alerts.map((alert) => (
                <div key={alert.id} className="flex items-start gap-3 p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <Droplets className="w-5 h-5 text-orange-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{alert.message}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Severity: <span className="capitalize">{alert.severity}</span> • 
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
