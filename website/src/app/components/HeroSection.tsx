"use client";

import { Button } from "./ui/button";

import Image from "next/image";

export default function HeroSection() {
  const handleBookDemo = () => {
    window.open("https://cal.com/mldawes/senchi-demo", "_blank");
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
              
              {/* Demo Booking Button */}
              <div className="bg-white rounded-xl shadow-lg max-w-sm">
                <Button 
                  className="w-full bg-senchi-primary hover:bg-senchi-primary/80 text-white font-semibold px-8 py-6 rounded-lg shadow-sm flex items-center justify-center gap-2 text-lg" 
                  size="lg"
                  onClick={handleBookDemo}
                >
                  Book a demo
                  <svg 
                    width="16" 
                    height="16" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  >
                    <path d="M5 12h14"/>
                    <path d="m12 5 7 7-7 7"/>
                  </svg>
                </Button>
              </div>
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