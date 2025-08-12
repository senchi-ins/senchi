"use client";

import { Button } from "./ui/button";
import { Shield, Zap, Thermometer, Droplets, Lock, Wifi, Battery, TrendingUp, CheckCircle, AlertTriangle } from "lucide-react";
// import { addToWaitlist } from "@/utils/waitlist";
import { useState } from "react";

export default function HeroSection() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<null | 'success' | 'error'>(null);
  const [loading, setLoading] = useState(false);

  const handleJoinWaitlist = async () => {
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (res.ok) {
        setStatus("success");
        setEmail("");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative bg-gradient-to-b from-senchi-primary via-senchi-primary-light/50 to-white overflow-hidden" style={{ marginTop: '-4rem', paddingTop: '4rem' }}>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-12 items-stretch">
          {/* Content */}
          <div className="flex-1 flex flex-col justify-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight">
                  Water leaks cost $12,000 on average.
                  <br />
                  <span className="text-senchi-accent-light">We catch them before they happen.</span>
                </h1>
                <p className="text-lg text-gray-100 max-w-2xl">
                Smart sensors detect temperature, pressure, and other changes days before pipes burst or appliances fail. Save thousands in damage and skip the insurance headache
                </p>
              </div>
              
              {/* Waitlist Email Field */}
              <div className="bg-white rounded-xl p-2 shadow-lg max-w-md">
                <div className="flex flex-col sm:flex-row items-center gap-3">
                  <input
                    type="email"
                    placeholder="Enter your email to join the waitlist"
                    className="flex-1 px-2 py-3 rounded-lg focus:outline-none text-base"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    disabled={loading}
                  />
                  <Button 
                    className="bg-senchi-primary hover:bg-senchi-primary/80 text-white font-semibold px-8 py-4 rounded-lg shadow-sm" 
                    size="lg"
                    onClick={handleJoinWaitlist}
                    disabled={loading || !email}
                  >
                    {loading ? "Joining..." : "Join Waitlist"}
                  </Button>
                </div>
              </div>
              <p className="text-gray-500 text-sm max-w-md">
                We expect to launch beta with our first customers in Q4 2025.
              </p>
                             {status === 'success' && (
                 <div className="text-green-300 text-sm">You&apos;ve been added to the waitlist!</div>
               )}
              {status === 'error' && (
                <div className="text-red-300 text-sm">There was an error. Please try again.</div>
              )}
            </div>
          </div>

          {/* Visual */}
          <div className="flex-1 flex flex-col relative">
            <div className="relative rounded-2xl bg-gradient-to-br from-senchi-accent-light to-white p-8 shadow-2xl flex-1 flex flex-col">
              <div className="flex flex-col gap-6 h-full justify-between">
                {/* Policy Status & Property Types Combined */}
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-senchi-primary" />
                      <h3 className="text-sm font-semibold text-gray-900">Active Monitoring</h3>
                    </div>
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="h-3 w-3 text-green-500" />
                      <span className="text-xs text-green-600 font-medium">Monitored</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-senchi-accent-light border border-senchi-primary/20 p-1.5 rounded text-center">
                      <div className="text-senchi-primary font-medium">Homeowner</div>
                    </div>
                    <div className="bg-gray-50 p-1.5 rounded text-center text-gray-600">
                      <div>PM</div>
                    </div>
                    <div className="bg-gray-50 p-1.5 rounded text-center text-gray-600">
                      <div>Insurer</div>
                    </div>
                  </div>
                </div>

                {/* Senchi Halo Monitoring Grid */}
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Wifi className="h-4 w-4 text-senchi-primary" />
                      <h3 className="text-sm font-semibold text-gray-900">Senchi HomeGuard</h3>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <span className="text-xs text-green-600">Online</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-xs">
                    <div className="text-center">
                      <Thermometer className="h-4 w-4 text-blue-500 mx-auto mb-1" />
                      <div className="font-medium text-gray-900">72°F</div>
                      <div className="text-gray-600 text-xs">Temp</div>
                    </div>
                    <div className="text-center">
                      <Droplets className="h-4 w-4 text-cyan-500 mx-auto mb-1" />
                      <div className="font-medium text-gray-900">43%</div>
                      <div className="text-gray-600 text-xs">Humid</div>
                    </div>
                    <div className="text-center">
                      <Lock className="h-4 w-4 text-green-500 mx-auto mb-1" />
                      <div className="font-medium text-green-600">Safe</div>
                      <div className="text-gray-600 text-xs">Security</div>
                    </div>
                    <div className="text-center">
                      <Battery className="h-4 w-4 text-orange-500 mx-auto mb-1" />
                      <div className="font-medium text-gray-900">98%</div>
                      <div className="text-gray-600 text-xs">Power</div>
                    </div>
                  </div>
                </div>

                {/* Alert & Prevention */}
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-amber-800">AI Prevention Alert</h4>
                      <p className="text-xs text-amber-700 mt-1">Water pressure anomaly detected. Maintenance scheduled.</p>
                      <div className="mt-1.5">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-amber-100 text-amber-800 font-medium">
                          Claim prevented
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Savings & Performance */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-1 mb-1">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <h4 className="text-sm font-semibold text-green-800">Savings</h4>
                    </div>
                    <div className="text-lg font-bold text-green-700">$847</div>
                    <div className="text-xs text-green-600">This year</div>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center space-x-1 mb-1">
                      <Shield className="h-4 w-4 text-blue-600" />
                      <h4 className="text-sm font-semibold text-blue-800">Claim-worthy event</h4>
                    </div>
                    <div className="text-lg font-bold text-blue-700">3</div>
                    <div className="text-xs text-blue-600">Prevented</div>
                  </div>
                </div>

                {/* Risk Assessment */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Zap className="h-4 w-4 text-purple-600" />
                      <h4 className="text-sm font-semibold text-purple-800">Risk Score</h4>
                    </div>
                    <span className="text-sm font-bold text-purple-600">Low</span>
                  </div>
                  <div className="w-full bg-purple-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{width: '25%'}}></div>
                  </div>
                  <div className="text-xs text-purple-700 mt-1">Excellent home maintenance</div>
                </div>

                {/* Community Impact - Compact */}
                {/* <div className="bg-senchi-accent-light rounded-lg p-3"> */}
                  {/* <div className="flex items-center justify-between mb-2"> */}
                    {/* TODO: Long term goal */}
                    {/* <div className="flex items-center space-x-2">
                      <Heart className="h-4 w-4 text-senchi-primary" />
                      <h4 className="text-sm font-semibold text-senchi-primary">Do Good</h4>
                    </div> */}
                    {/* <span className="text-sm font-bold text-senchi-primary">$127</span> */}
                  {/* </div> */}
                  {/* <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white rounded p-2 text-center">
                      <div className="font-medium text-gray-900">342</div>
                      <div className="text-gray-600">Families helped</div>
                    </div>
                    <div className="bg-white rounded p-2 text-center">
                      <div className="font-medium text-gray-900">12</div>
                      <div className="text-gray-600">Organizations</div>
                    </div>
                  </div> */}
                {/* </div> */}
              </div>
            </div>

            {/* Floating elements */}
            <div className="absolute -top-4 -right-4 w-8 h-8 bg-senchi-primary rounded-full opacity-20"></div>
            <div className="absolute -bottom-6 -left-6 w-12 h-12 bg-senchi-accent-light rounded-full opacity-60"></div>
          </div>
        </div>
      </div>
    </section>
  );
}