import React from 'react';
import { useRouter } from 'next/navigation';
import { Home, Wifi, Droplets, ChevronRight } from "lucide-react";


interface PropertyScore {
  overall: number;
  internal: number;
  external: number;
}

interface PropertyDevice {
  connected: number;
  total: number;
}

interface PropertyAlert {
  type: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
}

interface PropertyOverviewProps {
  id: string;
  address: string;
  name: string;
  property_type: string;
  description: string;
  scores: PropertyScore;
  total_savings: number;
  devices: PropertyDevice;
  alert?: PropertyAlert;
}

export default function PropertyOverview({ 
  id,
  address,
  name,
  property_type,
  description,
  scores, 
  total_savings,
  devices, 
  alert
}: PropertyOverviewProps) {
  const router = useRouter();

  console.log(`property_type: ${property_type}, name: ${name}, description: ${description}, total_savings: ${total_savings}`);
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

  const handleClick = () => {
    // Simply navigate to the property page - it will fetch all data from the API
    router.push(`/product/${id}`);
  };

  return (
    <div 
      className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow cursor-pointer ml-10"
      style={{
        width: 'calc(85vw - 5rem)',
        marginRight: 'calc(-70vw + 50%)',
      }}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between">
        {/* Property Identification */}
        <div className="flex items-start gap-4 flex-1">
          <div className="bg-senchi-primary rounded-lg p-2">
            <Home className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl text-gray-900 mb-1">{address}</h3>
            <p className="text-md text-gray-500 mb-1">{description}</p>
            {alert && (
              <div className="flex items-center gap-2 bg-senchi-primary/20 text-black px-3 py-2 rounded-lg max-w-xs mt-2">
                <Droplets className="w-4 h-4" />
                <span className="text-sm truncate">{alert.message}</span>
              </div>
            )}
          </div>
        </div>

        {/* Performance Scores */}
        <div className="flex items-center gap-6 mr-8">
          <div className="text-center">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm ${getScoreBgColor(scores.overall)} ${getScoreColor(scores.overall)}`}>
              {scores.overall}
            </div>
            <p className="text-xs text-gray-500 mt-1">Overall</p>
          </div>
          <div className="text-center">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm ${getScoreBgColor(scores.internal)} ${getScoreColor(scores.internal)}`}>
              {scores.internal}
            </div>
            <p className="text-xs text-gray-500 mt-1">Internal</p>
          </div>
          <div className="text-center">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm ${getScoreBgColor(scores.external)} ${getScoreColor(scores.external)}`}>
              {scores.external}
            </div>
            <p className="text-xs text-gray-500 mt-1">External</p>
          </div>
        </div>

        {/* Device Status */}
        <div className="flex items-center gap-6">
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-white border-2 border-gray-200 flex flex-col items-center justify-center">
              <Wifi className="w-4 h-4 text-black mb-1" />
              <span className="text-sm font-semibold text-black">{devices.connected}/{devices.total}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Devices</p>
          </div>

          <ChevronRight className="w-5 h-5 text-gray-400" />
        </div>
      </div>
    </div>
  );
}