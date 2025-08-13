"use client";

import { Button } from "./ui/button";

import { useState } from "react";
import Image from "next/image";

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
    <section className="relative bg-gradient-to-b from-senchi-primary via-senchi-primary-light/50 to-white overflow-hidden" style={{ marginTop: '-4rem', paddingTop: '10rem', paddingBottom: '4rem' }}>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-20 items-stretch">
          {/* Content */}
          <div className="flex-1 flex flex-col justify-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight">
                  {/* https://ipropertymanagement.com/research/water-damage-statistics */}
                  Water leaks cost $14,000 on average.
                  <br />
                  <span className="text-white">We catch them before they happen.</span>
                </h1>
                <p className="text-lg text-gray-100 max-w-2xl">
                Smart sensors detect temperature, flow, and other changes hours before pipes burst or appliances fail. Save thousands in damage and skip the insurance headache
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
              {/* <p className="text-gray-500 text-sm max-w-md">
                We expect to launch beta with our first customers in Q4 2025.
              </p> */}
              {status === 'success' && (
                <div className="text-green-300 text-sm">You&apos;ve been added to the waitlist!</div>
              )}
              {status === 'error' && (
                <div className="text-red-300 text-sm">There was an error. Please try again.</div>
              )}
            </div>
          </div>

          {/* Device Mockups */}
          <div className="flex-1 flex items-center justify-center relative min-h-[500px] lg:min-h-[600px]">
            {/* iPad/Desktop Monitor - Behind */}
            <div className="relative z-10">
              <Image
                src="/mocks/webdemo.png"
                alt="Senchi Web Dashboard"
                width={1200}
                height={900}
                className="w-full max-w-sm sm:max-w-md md:max-w-lg lg:max-w-xl xl:max-w-2xl h-auto rounded-lg shadow-2xl"
                priority
              />
            </div>

            {/* iPhone Mockup - In Front */}
            <div className="relative z-20
                          -ml-8 sm:-ml-12 md:-ml-16 lg:-ml-20 xl:-ml-24
                          mt-8 sm:mt-12 md:mt-16 lg:mt-20 xl:mt-24">
              <Image
                src="/mocks/iphone-demo.png"
                alt="Senchi Mobile App"
                width={346}
                height={717}
                className="w-24 sm:w-32 md:w-40 lg:w-48 xl:w-56 h-auto rounded-3xl shadow-2xl"
                priority
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}