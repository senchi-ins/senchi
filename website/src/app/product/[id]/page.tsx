"use client"

import React, { useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';

import { ArrowLeft, Home, Wifi, Droplets, AlertTriangle, Clock, Plus, RefreshCw } from "lucide-react";
import { fetchLocationSurvey, createSurveyAndRedirect, CreateSurveyRequest } from '../../api/survey/survey';
import { sampleDevices } from './sampleDevices';


interface Device {
  id: string;
  name: string;
  friendly_name: string;
  location: string;
  device_type: string;
  status: 'connected' | 'warning' | 'disconnected';
  last_seen?: string;
  battery_level?: number;
  signal_strength?: number;
  ieee_address: string; // Added ieee_address
}

interface PropertyData {
  id: string;
  name: string;
  address?: string;
  propertyId?: string;
  property_type?: string;
  description?: string;
  total_savings?: number;
  scores?: {
    overall: number;
    internal: number;
    external: number;
  };
  devices?: {
    connected: number;
    total: number;
  };
  alert?: {
    type: string;
    message: string;
    severity: 'high' | 'medium' | 'low';
  };
}

interface PropertyDetails {
  id: string;
  name?: string;
  address: string;
  propertyId?: string;
  property_type?: string;
  description?: string;
  scores: {
    overall: number;
    internal: number;
    external: number;
  };
  devices: {
    connected: number;
    total: number;
    list?: Array<{
      name: string;
      location: string;
      connection: 'connected' | 'warning' | 'disconnected';
      status: string;
      icon: string;
      action?: {
        label: string;
        type: 'primary' | 'secondary' | 'danger';
        onClick: () => void;
      };
    }>;
  };
  alerts?: Array<{
    id: string;
    type: string;
    message: string;
    severity: 'high' | 'medium' | 'low';
    timestamp: string;
    details?: string;
  }>;
  total_savings?: number;
  moneySaved?: number;
  lastUpdated?: string;
}

interface SurveyResults {
  id: string;
  user_id: string;
  property_id: string;
  response: Record<string, string | number | boolean>; // JSON field containing the survey responses
  total_score: number;
  points_earned: number;
  points_possible: number;
  created_at: string;
  updated_at: string;
}

const fetchPropertyDetails = async (propertyId: string): Promise<PropertyData> => {
  try {
    const response = await fetch(`/api/properties/${propertyId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch property: ${response.status}`);
    }

    const data = await response.json();
    return data.property;
  } catch (error) {
    console.error('Error fetching property details:', error);
    throw error;
  }
};

// API function to fetch devices
const fetchDevices = async (property_name: string): Promise<Device[]> => {
  try {
    const response = await fetch('/api/devices', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        property_name,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Devices API error response:', errorText);
      throw new Error(`Failed to fetch devices: ${response.status} - ${errorText}`);
    }

    const devices = await response.json();
    return devices || [];
  } catch (error) {
    console.error('Error fetching devices:', error);
    return [];
  }
};

// API function to fetch alerts
const fetchAlerts = async (property_id: string): Promise<Array<{
  id: string;
  type: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
  timestamp: string;
  details?: string;
}>> => {
  try {
    const response = await fetch('/api/alerts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        property_id: property_id
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Alerts API error response:', errorText);
      throw new Error(`Failed to fetch alerts: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data.alerts || [];
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return [];
  }
};

// API function to fetch survey results
const fetchSurveyResults = async (property_id: string): Promise<SurveyResults[] | SurveyResults | null> => {
  try {
    const response = await fetch('/api/survey-results', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        property_id: property_id
      }),
    });

    if (!response.ok) {
      if (response.status === 404) {
        // No survey results found
        return null;
      }
      const errorText = await response.text();
      console.error('Survey results API error response:', errorText);
      throw new Error(`Failed to fetch survey results: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching survey results:', error);
    return null;
  }
};

// TODO: This is a temporary fix to map the device names to the correct names. To be removed
const transformDevices = (devices: Device[]) => {
  // NOTE: These are real ieee_addresses from the devices, their names are just not stored currently
  const deviceNameMap: Record<string, {name: string, location: string}> = {
    '0x00158d008b87f199': {name: 'Leak Sensor', location: 'Kitchen'},
    '0x00158d008b87f5e7': {name: 'Leak Sensor', location: 'Master Bathroom'},
    '0xa4c138ebc21645f4': {name: 'Shutoff Valve', location: 'Main Line'},
    '0x00158d008b91089c': {name: 'Flow Monitor', location: 'Main Line'},
    '0x00158d008b87f2a1': {name: 'Leak Sensor', location: 'Basement'},
    '0x00158d008b87f3b2': {name: 'Temperature Sensor', location: 'Utility Room'}
  };

  return devices.map(device => {
    const mappedDevice = deviceNameMap[device.ieee_address];
    
    return {
      name: mappedDevice?.name || device.friendly_name || device.name, // Use mapped name if available, fallback to friendly_name, then name
      location: mappedDevice?.location || device.location,
      connection: device.status || "connected",
      status: getDeviceStatus(device),
      icon: getDeviceIcon(device.device_type),
      action: getDeviceAction(device),
    };
  });
};

// TODO: Fix this on the backend to properly update the status when something happens
const getDeviceStatus = (device: Device): string => {
  if (device.status) {
    return "";
  } else {
    return "";
  }
  // if (!device.status) {
  //   return "Connected";
  // } else {
  //   switch (device.device_type.toLowerCase()) {
  //     case 'leak_sensor':
  //       return 'No Leak';
  //     case 'water_flow_monitor':
  //       return 'Normal Flow';
  //     case 'shut_off_valve':
  //       return 'Open';
  //     case 'temperature_sensor':
  //       return 'Normal Temp';
  //     default:
  //       return 'Active';
  //   }
  // }
};

const getDeviceIcon = (deviceType: string): string => {
  switch (deviceType.toLowerCase()) {
    case 'leak_sensor':
      return 'droplets';
    case 'water_flow_monitor':
      return 'activity';
    case 'shut_off_valve':
      return 'settings';
    case 'temperature_sensor':
      return 'thermometer';
    default:
      return 'wifi';
  }
};

const getDeviceAction = (device: Device) => {
  // Add actions based on device type and status
  if (device.status === 'warning') {
    return {
      label: 'Reset Alert',
      type: 'secondary' as const,
      onClick: () => console.log('Reset alert for device:', device.id)
    };
  }
  
  return undefined;
};

// Property-specific recommendations data
const propertyRecommendations: Record<string, Array<{
  id: number;
  action: string;
  severity: 'high' | 'medium' | 'low';
  rationale: string;
  location: 'internal' | 'external';
  component: string;
}>> = {
  // TODO: Remove this once we have the recommendation generation working
  // Specific recommendations for property ID: 0563f455-4cda-4203-8e37-51ed73604f73
  "0563f455-4cda-4203-8e37-51ed73604f73": [
    {
      id: 1,
      action: "Install additional water leak sensors in second bathroom",
      severity: "medium",
      rationale: "The second bathroom is located near the washing machine and is prone to water damage.",
      location: "internal",
      component: "Appliances"
    },
  ],
  
  // Specific recommendations for property ID: 98fff33b-435d-4bdb-9833-20858c128fbd
  "98fff33b-435d-4bdb-9833-20858c128fbd": [
    {
      id: 1,
      action: "Add sump pump monitor",
      severity: "high",
      rationale: "This property is in close proximity to a pond and is prone to flooding.",
      location: "internal",
      component: "Water System"
    },
    {
      id: 2,
      action: "Replace roof shingles",
      severity: "medium",
      rationale: "The roof shingles are 10 years old and need to be replaced. This will prevent water damage and extend the lifespan of the roof",
      location: "external",
      component: "Roof"
    },
  ],
};

// Function to get recommendations for a specific property
const getRecommendationsForProperty = (propertyId?: string, propertyType?: string) => {
  // First check if there are specific recommendations for this property ID
  if (propertyId && propertyRecommendations[propertyId]) {
    return propertyRecommendations[propertyId];
  }
  
  // Fall back to property type recommendations
  if (propertyType && propertyRecommendations[propertyType]) {
    return propertyRecommendations[propertyType];
  }
  
  // Default recommendations if no specific ones found
  return propertyRecommendations.default;
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'high': return 'bg-red-100 text-red-800';
    case 'medium': return 'bg-yellow-100 text-yellow-800';
    case 'low': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const getLocationColor = (location: string) => {
  switch (location) {
    case 'internal': return 'bg-blue-100 text-blue-800';
    case 'external': return 'bg-purple-100 text-purple-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export default function PropertyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [property, setProperty] = useState<PropertyDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [devicesLoading, setDevicesLoading] = useState(false);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [assessmentLoading, setAssessmentLoading] = useState(false);
  const [devicesAttempted, setDevicesAttempted] = useState(false);
  const [surveyResults, setSurveyResults] = useState<SurveyResults | null>(null);
  const [surveyLoading, setSurveyLoading] = useState(false);

  const loadDevices = async (propertyName: string) => {
    setDevicesLoading(true);
    setDevicesAttempted(true);
    try {
      const devices = await fetchDevices(propertyName);
      
      // Use sample devices if API returns empty list
      const devicesToUse = devices.length === 0 ? sampleDevices : devices;
      
      const transformedDevices = transformDevices(devicesToUse);
      setProperty(prev => prev ? {
        ...prev,
        devices: {
          ...prev.devices,
          list: transformedDevices,
          connected: devicesToUse.filter(d => d.status === 'connected').length,
          total: devicesToUse.length
        }
      } : null);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
      // Use sample devices as fallback if API fails
      const transformedDevices = transformDevices(sampleDevices);
      setProperty(prev => prev ? {
        ...prev,
        devices: {
          ...prev.devices,
          list: transformedDevices,
          connected: sampleDevices.filter(d => d.status === 'connected').length,
          total: sampleDevices.length
        }
      } : null);
    } finally {
      setDevicesLoading(false);
    }
  };

  const loadAlerts = async (propertyId: string) => {
    setAlertsLoading(true);
    try {
      const alerts = await fetchAlerts(propertyId);
      console.log('Alerts:', alerts);
      setProperty(prev => prev ? {
        ...prev,
        alerts: alerts
      } : null);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setAlertsLoading(false);
    }
  };

  const loadSurveyResults = async (propertyId: string) => {
    setSurveyLoading(true);
    try {
      const results = await fetchSurveyResults(propertyId);
      
      // Helper function to extract survey data
      const extractSurveyData = (surveyItem: SurveyResults): SurveyResults => {
        return {
          id: surveyItem.id,
          user_id: surveyItem.user_id,
          property_id: surveyItem.property_id,
          total_score: surveyItem.total_score || 0,
          points_earned: surveyItem.points_earned || 0,
          points_possible: surveyItem.points_possible || 0,
          response: surveyItem.response || {},
          created_at: surveyItem.created_at,
          updated_at: surveyItem.updated_at
        };
      };
      
      // If results is an object with numeric keys (like {0: {...}, 1: {...}, success: true})
      if (results && typeof results === 'object' && !Array.isArray(results)) {
        // Convert object with numeric keys to array
        const resultsArray = Object.keys(results)
          .filter(key => !isNaN(Number(key))) // Only numeric keys
          .map(key => results[key])
          .filter(item => item && typeof item === 'object'); // Filter out non-objects
        
        if (resultsArray.length > 0) {
          // Find the most recent one
          const mostRecent = resultsArray.reduce((latest, current) => {
            const latestDate = new Date(latest.created_at);
            const currentDate = new Date(current.created_at);
            return currentDate > latestDate ? current : latest;
          });
          
          setSurveyResults(extractSurveyData(mostRecent));
        } else {
          setSurveyResults(null);
        }
      } else if (Array.isArray(results) && results.length > 0) {
        // If it's already an array, find the most recent one
        const mostRecent = results.reduce((latest, current) => {
          const latestDate = new Date(latest.created_at);
          const currentDate = new Date(current.created_at);
          return currentDate > latestDate ? current : latest;
        });
        
        setSurveyResults(extractSurveyData(mostRecent));
      } else if (results) {
        // If it's a single result, use it directly
        setSurveyResults(extractSurveyData(results as unknown as SurveyResults));
      } else {
        setSurveyResults(null);
      }
    } catch (error) {
      console.error('Failed to fetch survey results:', error);
      setSurveyResults(null);
    } finally {
      setSurveyLoading(false);
    }
  };

  useEffect(() => {
    const loadProperty = async () => {
      if (params.id) {
        try {
          // Check if property data was passed through URL parameters
          const urlData = searchParams.get('data');
          
          if (urlData) {
            try {
              const decodedData = JSON.parse(atob(urlData));
              
              // Create minimal property data and fetch the rest
              const minimalData: PropertyDetails = {
                id: decodedData.id,
                address: decodedData.address,
                scores: { overall: 0, internal: 0, external: 0 },
                devices: { connected: 0, total: 0, list: [] },
                moneySaved: 0,
                lastUpdated: new Date().toLocaleTimeString()
              };
              
              setProperty(minimalData);
              
              // Fetch devices for this property
              await loadDevices(decodedData.address);
              
              // Load survey results
              await loadSurveyResults(decodedData.id);
              
              setLoading(false);
              return;
            } catch (error) {
              console.error('Failed to parse URL data:', error);
              // Fall back to API call if URL data parsing fails
            }
          } else {
            // No URL data provided - fetch property data from API
            try {
              const propertyData = await fetchPropertyDetails(params.id as string);
              
              const transformedData: PropertyDetails = {
                id: propertyData.id,
                name: propertyData.name,
                address: propertyData.address || propertyData.name,
                propertyId: propertyData.propertyId,
                property_type: propertyData.property_type,
                description: propertyData.description,
                scores: propertyData.scores || { overall: 0, internal: 0, external: 0 },
                devices: {
                  connected: propertyData.devices?.connected || 0,
                  total: propertyData.devices?.total || 0,
                  list: []
                },
                moneySaved: propertyData.total_savings || 0,
                lastUpdated: new Date().toLocaleTimeString()
              };
              
              setProperty(transformedData);
              
              // Load devices, alerts, and survey results
              await Promise.all([
                loadDevices(transformedData.name || transformedData.address),
                loadAlerts(propertyData.id),
                loadSurveyResults(propertyData.id)
              ]);
              
              setLoading(false);
            } catch (error) {
              console.error('Failed to load property:', error);
              setLoading(false);
            }
          }
        } catch (error) {
          console.error('Error in loadProperty:', error);
          setLoading(false);
        }
      }
    };

    loadProperty();
  }, [params.id, searchParams]);

  // Ensure devices are loaded when property is set (fallback)
  useEffect(() => {
    if (property && !devicesAttempted && (!property.devices.list || property.devices.list.length === 0)) {
      loadDevices(property.name || property.address);
    }
  }, [property, devicesAttempted]);



  const getConnectionColor = (connection: string) => {
    switch (connection) {
      case 'connected': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'disconnected': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const handleRefreshDevices = async () => {
    if (property) {
      setDevicesLoading(true);
      try {
        console.log('Refreshing devices for property:', property.name || property.address);
        
        const devices = await fetchDevices(property.name || property.address);
        
        const transformedDevices = transformDevices(devices);
        setProperty(prev => prev ? {
          ...prev,
          devices: {
            ...prev.devices,
            list: transformedDevices,
            connected: devices.filter(d => d.status === 'connected').length,
            total: devices.length
          },
          lastUpdated: new Date().toLocaleTimeString()
        } : null);
      } catch (error) {
        console.error('Failed to refresh devices:', error);
      } finally {
        setDevicesLoading(false);
      }
    }
  };

  const getAlertBgColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-50 border-red-200';
      case 'medium': return 'bg-orange-50 border-orange-200';
      case 'low': return 'bg-blue-50 border-blue-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'water_flow': return <AlertTriangle className="w-5 h-5 text-orange-600" />;
      case 'maintenance': return <Clock className="w-5 h-5 text-blue-600" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-600" />;
    }
  };

  const handleTakeAssessment = async () => {
    if (!property) return;
    
    setAssessmentLoading(true);
    try {
      // Fetch the survey for the property address
      const surveyData = await fetchLocationSurvey(property.address);
      
      const title = "How protected is your home?";
      const description = "Please answer the following questions to assess your home's risk.";

      const surveyContent = {
        title: title,
        description: description,
        workspaceId: "default-workspace",
        ...surveyData
      };
      
      let i = 0;
      for (const question of surveyContent.questions) {
        question['order'] = i;
        question['type'] = "MULTIPLE_CHOICE";
        question['options'] = typeof question.rubric === "string"
          ? question.rubric.split("\n").map(option => option.trim())
          : ["Yes", "No"];
        question['text'] = question.question;
        i++;
      }

      await createSurveyAndRedirect(surveyContent as CreateSurveyRequest);
    } catch (error) {
      console.error('Failed to create assessment:', error);
      alert('Failed to create assessment. Please try again.');
    } finally {
      setAssessmentLoading(false);
    }
  };
  console.log(surveyResults);

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
    <div className="min-h-screen p-6 flex justify-center items-start mx-auto lg:mx-auto xl:ml-20 xl:mr-auto 2xl:ml-96 2xl:mr-auto">
      <div className="w-full max-w-6xl">
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

        {/* Dashboard Header */}
        <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex items-start gap-4 flex-1 min-w-0">
              <div className="bg-senchi-primary p-2 rounded-lg flex-shrink-0">
                <Home className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
                <p className="text-gray-600 break-words">Monitor your home&apos;s health and connected devices at {property.address}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              {surveyLoading ? (
                <div className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700"></div>
                  Loading Survey...
                </div>
              ) : surveyResults ? (
                <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-2 rounded-lg flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Assessment Complete
                </div>
              ) : (
                <button 
                  onClick={handleTakeAssessment}
                  disabled={assessmentLoading}
                  className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-gray-200 transition-colors disabled:opacity-50"
                >
                  {assessmentLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700"></div>
                      Creating Assessment...
                    </>
                  ) : (
                    'Take Assessment'
                  )}
                </button>
              )}
              <button 
                onClick={() => alert('Setting HomeGuard Hub to pairing mode...')}
                className="bg-senchi-primary text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-senchi-primary/90 transition-colors">
                <Plus className="w-4 h-4" />
                Add a device
              </button>
            </div>
          </div>
        </div>

        {/* Financial Overview Cards */}
        <div className="bg-white rounded-lg p-6 shadow-sm mb-6">
          <div className="flex gap-10">
            {/* Total Savings */}
            <div>
              <div className="text-sm text-gray-600 mb-2">Home Health Score</div>
              <div className="text-5xl font-bold text-gray-900">{property.scores.overall}%</div>
            </div>
            
            {/* Claims Avoided */}
            <div>
              <div className="text-sm text-gray-600 mb-2">Total Savings</div>
              <div className="text-5xl font-bold text-gray-900">{formatMoney(property.moneySaved || 0)}</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Device Monitoring */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Device Monitoring</h2>
              <div className="flex items-center gap-2">
                {/* TODO: Fix number of connected devices */}
                <span className="text-sm text-gray-600">{property.devices.total}/{property.devices.total}</span>
                <Wifi className="w-5 h-5 text-gray-600" />
              </div>
            </div>
            <div className="space-y-3">
              {property.devices.list && property.devices.list.length > 0 ? (
                property.devices.list.map((device, index) => (
                <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                  <div className="flex items-center gap-3">
                    <Droplets className="w-4 h-4 text-gray-600" />
                    <div>
                      <p className="font-medium text-gray-900">{device.name}</p>
                      <p className="text-sm text-gray-600">({device.location})</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {device.action && (
                      <button
                        onClick={device.action.onClick}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                          device.action.type === 'primary' 
                            ? 'bg-senchi-primary text-white hover:bg-senchi-primary/90' 
                            : device.action.type === 'danger'
                            ? 'bg-red-500 text-white hover:bg-red-600'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {device.action.label}
                      </button>
                    )}
                    <div className="text-right">
                      <p className={`text-sm font-medium ${getConnectionColor(device.connection)}`}>
                        {device.connection}
                      </p>
                      <p className="text-xs text-gray-600">{device.status}</p>
                    </div>
                  </div>
                </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-500">
                  <p>No device details available</p>
                </div>
              )}
            </div>
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
              <span className="text-sm text-gray-500">Last updated: {property.lastUpdated}</span>
              <button 
                onClick={handleRefreshDevices}
                disabled={devicesLoading}
                className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${devicesLoading ? 'animate-spin' : ''}`} />
                {devicesLoading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>

          {/* Right Column - Smart Home Alerts */}
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Smart Home Alerts</h2>
              <AlertTriangle className="w-5 h-5 text-orange-500" />
            </div>
            <div className="space-y-3">
              {alertsLoading ? (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-300 mx-auto mb-2"></div>
                  <p>Loading alerts...</p>
                </div>
              ) : property.alerts && property.alerts.length > 0 ? (
                property.alerts.map((alert) => (
                  <div key={alert.id} className={`p-4 rounded-lg border ${getAlertBgColor(alert.severity)}`}>
                    <div className="flex items-start gap-3">
                      {getAlertIcon(alert.type)}
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{alert.message}</p>
                        {alert.details && (
                          <p className="text-sm text-gray-600 mt-1">{alert.details}</p>
                        )}
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(alert.timestamp + 'Z').toLocaleDateString('en-US', { timeZone: 'America/New_York' })} • {new Date(alert.timestamp + 'Z').toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour12: true })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                  <p>No active alerts</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recommendations Section */}
        <div className="bg-white rounded-lg p-6 shadow-sm mt-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Recommendations</h2>
            <span className="text-sm text-gray-600">Based on your property assessment</span>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Action</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Severity</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Rationale</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Location</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900">Component Impacted</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {getRecommendationsForProperty(property?.id, property?.property_type).map((recommendation) => (
                  <tr key={recommendation.id} className="hover:bg-gray-50">
                    <td className="py-4 px-4">
                      <div className="font-medium text-gray-900">{recommendation.action}</div>
                    </td>
                    <td className="py-4 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(recommendation.severity)}`}>
                        {recommendation.severity.charAt(0).toUpperCase() + recommendation.severity.slice(1)}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {recommendation.rationale}
                    </td>
                    <td className="py-4 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLocationColor(recommendation.location)}`}>
                        {recommendation.location.charAt(0).toUpperCase() + recommendation.location.slice(1)}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-gray-600">{recommendation.component}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Survey Results Section */}
        {surveyResults && (
          <div className="bg-white rounded-lg p-6 shadow-sm mt-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Assessment Results</h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  Completed: {surveyResults.created_at ? new Date(surveyResults.created_at).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  }) : 'Date not available'}
                </span>
                {surveyResults.total_score && (
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                    Score: {surveyResults.total_score}%
                  </span>
                )}
              </div>
            </div>
            
            <div className="space-y-6">

              {/* Score Summary */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-md font-medium text-gray-900 mb-4">Score Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{surveyResults.total_score || 0}%</p>
                    <p className="text-sm text-gray-600">Total Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{surveyResults.points_earned || 0}</p>
                    <p className="text-sm text-gray-600">Points Earned</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-600">{surveyResults.points_possible || 0}</p>
                    <p className="text-sm text-gray-600">Points Possible</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function formatMoney(amount: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}