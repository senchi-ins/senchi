"use client";

import { Button } from "./ui/button";
import { Shield, Zap, Heart, Thermometer, Droplets, Lock, Wifi, Battery, TrendingUp, CheckCircle, AlertTriangle } from "lucide-react";
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
    <section className="relative py-16 sm:py-24 bg-senchi-footer overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-12 items-stretch">
          {/* Content */}
          <div className="flex-1 flex flex-col">
            <div className="space-y-4 mb-8">
              <div className="inline-flex items-center rounded-full bg-senchi-accent-light px-4 py-2 text-sm">
                <Zap className="h-4 w-4 text-senchi-primary mr-2" />
                Smart Risk Prevention for Every Home
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Smart Risk Prevention for
                <span className="text-senchi-primary"> Every Home</span>
              </h1>
              <p className="text-lg text-gray-600 max-w-xl">
                Whether you own a home or manage properties 
                Senchi&apos;s Halo predicts and prevents claims while supporting charitable causes.
              </p>
            </div>

            {/* Key Value Propositions */}
            <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm flex-1">
              <h3 className="font-semibold text-gray-900 mb-6 text-center">Predictions Powered by Senchi</h3>
              <div className="grid grid-cols-1 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 flex items-start gap-4 hover:bg-gray-100 transition-colors duration-200">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center border border-gray-200 flex-shrink-0">
                    <Zap className="h-6 w-6 text-senchi-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">AI predictive protection</h4>
                    <p className="text-xs text-gray-600">Smart technology that prevents claims before they happen</p>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 flex items-start gap-4 hover:bg-gray-100 transition-colors duration-200">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center border border-gray-200 flex-shrink-0">
                    <Shield className="h-6 w-6 text-senchi-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">Comprehensive monitoring</h4>
                    <p className="text-xs text-gray-600">Internal sensors and external modelling to provide 360 degree protection</p>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 flex items-start gap-4 hover:bg-gray-100 transition-colors duration-200">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center border border-gray-200 flex-shrink-0">
                    <Heart className="h-6 w-6 text-senchi-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">Give back program</h4>
                    <p className="text-xs text-gray-600">Portion of savings donated to charitable causes in your community</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Waitlist Email Field (below the value prop box, outside the card) */}
            <div id="waitlist-email" className="flex flex-col sm:flex-row items-center gap-2 mb-8 mt-8 max-w-lg mx-auto w-full">
              <input
                type="email"
                placeholder="Enter your email to join the waitlist"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-senchi-primary text-sm"
                value={email}
                onChange={e => setEmail(e.target.value)}
                disabled={loading}
              />
              <Button 
                className="bg-senchi-primary hover:bg-senchi-primary/90 w-full sm:w-auto" 
                size="lg"
                onClick={handleJoinWaitlist}
                disabled={loading || !email}
              >
                {loading ? "Joining..." : "Join Waitlist"}
              </Button>
            </div>
            {status === 'success' && (
              <div className="text-green-600 text-center mb-4">You&apos;ve been added to the waitlist!</div>
            )}
            {status === 'error' && (
              <div className="text-red-600 text-center mb-4">There was an error. Please try again.</div>
            )}
          </div>

          {/* Visual */}
          <div className="flex-1 flex flex-col relative">
            <div className="relative rounded-2xl bg-gradient-to-br from-senchi-accent-light to-white p-8 shadow-2xl flex-1 flex flex-col">
              <div className="flex flex-col gap-4 h-full justify-between">
                {/* Policy Status & Property Types Combined */}
                <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-senchi-primary" />
                      <h3 className="text-sm font-semibold text-gray-900">Active Monitoring</h3>
                    </div>
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="h-3 w-3 text-green-500" />
                      <span className="text-xs text-green-600 font-medium">Monitored</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-senchi-accent-light border border-senchi-primary/20 p-1.5 rounded text-center">
                      <div className="text-senchi-primary font-medium">Homeowner</div>
                    </div>
                    <div className="bg-gray-50 p-1.5 rounded text-center text-gray-600">
                      <div>PM</div>
                    </div>
                    {/* <div className="bg-gray-50 p-1.5 rounded text-center text-gray-600">
                      <div>Rental</div>
                    </div> */}
                  </div>
                </div>

                {/* Senchi Halo Monitoring Grid */}
                <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Wifi className="h-4 w-4 text-senchi-primary" />
                      <h3 className="text-sm font-semibold text-gray-900">Senchi Halo</h3>
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
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
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
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center space-x-1 mb-1">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <h4 className="text-sm font-semibold text-green-800">Savings</h4>
                    </div>
                    <div className="text-lg font-bold text-green-700">$847</div>
                    <div className="text-xs text-green-600">This year</div>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <div className="flex items-center space-x-1 mb-1">
                      <Shield className="h-4 w-4 text-blue-600" />
                      <h4 className="text-sm font-semibold text-blue-800">Claim-worthy event</h4>
                    </div>
                    <div className="text-lg font-bold text-blue-700">3</div>
                    <div className="text-xs text-blue-600">Prevented</div>
                  </div>
                </div>

                {/* Risk Assessment */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
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
                <div className="bg-senchi-accent-light rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Heart className="h-4 w-4 text-senchi-primary" />
                      <h4 className="text-sm font-semibold text-senchi-primary">Do Good</h4>
                    </div>
                    <span className="text-sm font-bold text-senchi-primary">$127</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white rounded p-2 text-center">
                      <div className="font-medium text-gray-900">342</div>
                      <div className="text-gray-600">Families helped</div>
                    </div>
                    <div className="bg-white rounded p-2 text-center">
                      <div className="font-medium text-gray-900">12</div>
                      <div className="text-gray-600">Organizations</div>
                    </div>
                  </div>
                </div>
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