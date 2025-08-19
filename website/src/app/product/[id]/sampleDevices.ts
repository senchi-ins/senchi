export interface SampleDevice {
  id: string;
  name: string;
  friendly_name: string;
  location: string;
  device_type: string;
  status: 'connected' | 'warning' | 'disconnected';
  last_seen?: string;
  battery_level?: number;
  signal_strength?: number;
  ieee_address: string;
}

export const sampleDevices: SampleDevice[] = [
  {
    id: '1',
    name: 'Leak Sensor',
    friendly_name: 'Kitchen Leak Sensor',
    location: 'Kitchen',
    device_type: 'leak_sensor',
    status: 'connected',
    last_seen: new Date().toISOString(),
    battery_level: 85,
    signal_strength: 90,
    ieee_address: '0x00158d008b87f199'
  },
  {
    id: '2',
    name: 'Leak Sensor',
    friendly_name: 'Master Bathroom Leak Sensor',
    location: 'Master Bathroom',
    device_type: 'leak_sensor',
    status: 'connected',
    last_seen: new Date().toISOString(),
    battery_level: 92,
    signal_strength: 88,
    ieee_address: '0x00158d008b87f5e7'
  },
  {
    id: '3',
    name: 'Shutoff Valve',
    friendly_name: 'Main Water Valve',
    location: 'Main Line',
    device_type: 'shut_off_valve',
    status: 'connected',
    last_seen: new Date().toISOString(),
    battery_level: 100,
    signal_strength: 95,
    ieee_address: '0xa4c138ebc21645f4'
  },
  {
    id: '4',
    name: 'Flow Monitor',
    friendly_name: 'Main Water Flow Monitor',
    location: 'Main Line',
    device_type: 'water_flow_monitor',
    status: 'connected',
    last_seen: new Date().toISOString(),
    battery_level: 78,
    signal_strength: 92,
    ieee_address: '0x00158d008b91089c'
  },
  {
    id: '5',
    name: 'Leak Sensor',
    friendly_name: 'Basement Leak Sensor',
    location: 'Basement',
    device_type: 'leak_sensor',
    status: 'connected',
    last_seen: new Date().toISOString(),
    battery_level: 88,
    signal_strength: 85,
    ieee_address: '0x00158d008b87f2a1'
  },
  {
    id: '6',
    name: 'Temperature Sensor',
    friendly_name: 'Water Heater Temperature Sensor',
    location: 'Utility Room',
    device_type: 'temperature_sensor',
    status: 'connected',
    last_seen: new Date().toISOString(),
    battery_level: 95,
    signal_strength: 87,
    ieee_address: '0x00158d008b87f3b2'
  }
];
