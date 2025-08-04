import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import Image from 'next/image';
import { Brain, AlertTriangle, TrendingDown, Clock, Wifi, Shield, Droplets, Activity, Settings, Bot } from "lucide-react";


export default function HaloSection() {
  const features = [
    {
      icon: Brain,
      title: "AI-Powered Predictions",
      description: "Advanced machine learning algorithms analyze patterns to predict potential claims before they occur."
    },
    {
      icon: AlertTriangle,
      title: "Early Warning System", 
      description: "Get instant alerts about potential issues in and around your home, from water leaks to incoming severe weather."
    },
    {
      icon: TrendingDown,
      title: "Risk Reduction",
      description: "Proactive maintenance recommendations help prevent costly damage and reduce insurance claims."
    },
    {
      icon: Clock,
      title: "24/7 Monitoring",
      description: "Continuous monitoring of your smart home devices ensures round-the-clock protection."
    },
    {
      icon: Wifi,
      title: "Smart Integration",
      description: "Seamlessly connects with popular smart home platforms and IoT devices."
    },
    {
      icon: Bot,
      title: "Autonomous Mitigation",
      description: "Autonomous routing of plumbers, electricians, and other service providers to stop damages"
    }
  ];

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
          <div className="inline-flex items-center rounded-full bg-white px-4 py-2 text-sm mb-4">
            <Brain className="h-4 w-4 text-senchi-primary mr-2" />
            Senchi HomeGuard Platform
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Smart Home Data Platform
          </h2>
          <p className="text-lg text-gray-600">
            Senchi HomeGuard uses cutting-edge AI and IoT integration to predict claims before they happen, 
            saving you money while protecting your home.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="border-gray-100 hover:border-senchi-primary/20 hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-senchi-accent-light rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-senchi-primary" />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
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
                    <p className="text-gray-600">Set up your smart home devices and sensors through our app.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-senchi-primary text-white rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">AI Analyzes Data</h4>
                    <p className="text-gray-600">Our AI processes real-time data to identify patterns and potential risks.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-senchi-primary text-white rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Prevent Claims</h4>
                    <p className="text-gray-600">Receive alerts and recommendations to prevent issues before they become claims and set up automatic responses to prevent damages.</p>
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