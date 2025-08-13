import React from 'react';

export default function MissionSection() {
  return (
    <section className="py-20 bg-senchi-primary to-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          {/* Mission Statement */}
          <div className="mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-white mb-8">
              Our Mission
            </h2>
            <p className="text-xl text-gray-100 leading-relaxed">
              We believe the best insurance is the one you never need. That&apos;s why we&apos;re building the future of home protection by preventing water damage before it happens.
            </p>
          </div>

          {/* Values Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 text-center">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Prevention First</h3>
              <p className="text-gray-100">
                We believe in stopping problems before they start. Our technology 
                detects issues hours before they become disasters.
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 text-center">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Smart detection</h3>
              <p className="text-gray-100">
              Our sensors learn your home&apos;s unique patterns, detecting small changes that signal potential water damage. From subtle temperature drops to unusual flow readings.
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 text-center">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Peace of Mind</h3>
              <p className="text-gray-100">
                We protect what matters most: your family&apos;s safety and your home&apos;s future. No more worrying about returning from vacation to a flooded basement.
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">$14,000</div>
              <div className="text-gray-100">Average cost of water damage</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">1+</div>
              <div className="text-gray-100">Hours of advanced warning</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">24/7</div>
              <div className="text-gray-100">Continuous monitoring</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
