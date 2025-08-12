import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import Image from 'next/image';
import { Brain, AlertTriangle, Car, Shield, Droplets, Activity, Settings } from "lucide-react";


export default function HaloSection() {

  const sensors = [
    {
      icon: Activity,
      title: "Ultrasonic clamp-on water flow monitor",
      description: "Non-invasive monitoring of water flow rates to detect leaks and unusual usage patterns.",
      image: '/assets/flow_monitor.png'
    },
    {
      icon: Droplets,
      title: "Multi purpose leak detectors",
      description: "Advanced sensor technology that detects water presence and alerts you before damage occurs.",
      image: '/assets/leak_sensor.png'
    },
    {
      icon: Settings,
      title: "Non-intrusive automatic valve control",
      description: "Smart valve control system that can automatically shut off water flow when issues are detected.",
      image: '/assets/valve_control.png'
    }
  ];

  return (
    <section id="halo" className="py-16 sm:py-24 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Smart sensors that actually work.
          </h2>
          <p className="text-lg text-gray-600">
            Professional-grade monitoring that catches problems before they become expensive.
          </p>
        </div>

        {/* Three Core Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="text-center">
            <div className="w-16 h-16 bg-senchi-accent-light rounded-full flex items-center justify-center mx-auto mb-4">
              <Brain className="h-8 w-8 text-senchi-primary" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Catch leaks early</h3>
            <p className="text-gray-600">
              Smart sensors detect pressure drops and moisture changes before pipes burst or appliances fail.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-senchi-accent-light rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="h-8 w-8 text-senchi-primary" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Water shuts off automatically</h3>
            <p className="text-gray-600">
              System immediately stops water flow and sends you alerts, preventing damage while you&apos;re away.
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-senchi-accent-light rounded-full flex items-center justify-center mx-auto mb-4">
              <Car className="h-8 w-8 text-senchi-primary" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Trusted plumbers dispatched</h3>
            <p className="text-gray-600">
              Pre-vetted contractors arrive quickly to fix the issue before it becomes expensive.
            </p>
          </div>
        </div>

        {/* How it Works */}
        <div className="bg-gradient-to-r from-senchi-accent-light to-white rounded-2xl p-8 lg:p-12">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6">
                How Senchi HomeGuard Works
              </h3>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-senchi-primary text-white rounded-full flex items-center justify-center text-sm font-bold">1</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Connect Your Smart Home</h4>
                    <p className="text-gray-600">Install wireless sensors in 5 minutes. No tools, wiring, or plumber needed.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-senchi-primary text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">AI Analyzes Data</h4>
                    <p className="text-gray-600">AI monitors pressure, temperature, and flow 24/7. Detects problems 6 hours before pipes burst.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-senchi-primary text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Stops Disasters Automatically</h4>
                    <p className="text-gray-600">System automatically shuts off water and calls trusted repair services. Damage prevented, not just detected.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="bg-white rounded-xl p-6 shadow-xl border border-gray-100">
                {/* Dashboard Preview */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-gray-900">HomeGuard Dashboard</h4>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">Online</span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-sm text-gray-600">Risk Score</div>
                      <div className="text-xl font-bold text-green-600">Low</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="text-sm text-gray-600">Savings</div>
                      <div className="text-xl font-bold text-senchi-primary">$1,247</div>
                    </div>
                  </div>

                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium text-green-800">All systems protected</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-900">Recent Alerts</div>
                    <div className="text-xs text-gray-600">• Increased water usage by dishwasher</div>
                    <div className="text-xs text-gray-600">• Proper water flow restored</div>
                    <div className="text-xs text-gray-600">• Outdoor temperature to drop 5 degree in the next week</div>
                  </div>
                </div>
              </div>

              {/* Floating notification */}
              <div className="absolute -right-4 -top-4 bg-yellow-100 border border-yellow-300 rounded-lg p-3 shadow-lg">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  <span className="text-xs font-medium text-yellow-800">Prediction Alert</span>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">

          </div>
        </div>

        {/* Smart AI Sensors Section */}
        <div className="mt-16">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
              Smart AI Powered Sensors Provided by Senchi
            </h3>
            <p className="text-lg text-gray-600">
              Our comprehensive sensor suite works together to provide complete home monitoring and protection.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {sensors.map((sensor, index) => (
              <Card key={index} className="border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300">
                <CardHeader className="text-center">
                  <div className="w-32 h-32 mx-auto mb-4 flex items-center justify-center">
                    {sensor.image ? (
                      <Image 
                        src={sensor.image} 
                        alt={sensor.title}
                        width={128}
                        height={128}
                      />
                    ) : (
                      <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
                        <div className="text-center">
                          <sensor.icon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                          <span className="text-sm text-gray-500">Coming Soon</span>
                        </div>
                      </div>
                    )}
                  </div>
                  <CardTitle className="text-xl">{sensor.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600 text-center">
                    {sensor.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}