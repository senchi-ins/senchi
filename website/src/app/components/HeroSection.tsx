"use client";

export default function HeroSection() {
  return (
    <section
      className="bg-[#f5f0e8]"
      style={{ fontFamily: "'Georgia', 'Times New Roman', serif" }}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Old-school beveled hero box */}
        <div
          className="border-2 border-[#8b7635] bg-white"
          style={{ boxShadow: "4px 4px 0px #8b7635" }}
        >
          <div className="bg-[#1a3a1a] px-6 py-3 border-b-2 border-[#8b7635]">
            <h2 className="text-[#d4c9a8] text-lg sm:text-xl font-bold tracking-wider uppercase text-center">
              Welcome to Senchi Chemical Supply Co.
            </h2>
          </div>

          <div className="p-6 sm:p-10">
            <div className="flex flex-col lg:flex-row gap-8 items-start">
              {/* Left content */}
              <div className="flex-1 space-y-6">
                <div className="border-l-4 border-[#8b7635] pl-4">
                  <h3 className="text-2xl sm:text-3xl font-bold text-[#1a3a1a] leading-tight mb-3">
                    Your Trusted Source for
                    <br />
                    Commodity-Derived Chemicals
                  </h3>
                  <p className="text-[#1a3a1a] leading-relaxed">
                    Senchi Chemical Supply Co. is a leading manufacturer and
                    distributor of high-purity chemicals synthesized from
                    commodity feedstocks. From our facilities in Ontario, we
                    serve industrial, agricultural, and municipal clients across
                    North America.
                  </p>
                </div>

                <hr className="fancy" />

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                  <div className="bevel-box">
                    <div className="text-2xl font-bold text-[#1a3a1a]">
                      200+
                    </div>
                    <div className="text-xs uppercase tracking-wider text-[#8b7635]">
                      Chemical Products
                    </div>
                  </div>
                  <div className="bevel-box">
                    <div className="text-2xl font-bold text-[#1a3a1a]">
                      50K+
                    </div>
                    <div className="text-xs uppercase tracking-wider text-[#8b7635]">
                      Tonnes Annually
                    </div>
                  </div>
                  <div className="bevel-box">
                    <div className="text-2xl font-bold text-[#1a3a1a]">
                      ISO 9001
                    </div>
                    <div className="text-xs uppercase tracking-wider text-[#8b7635]">
                      Certified Quality
                    </div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-4">
                  <a
                    href="#catalog"
                    className="inline-block bg-[#1a3a1a] text-[#d4c9a8] px-6 py-3 text-center uppercase tracking-wider text-sm font-bold hover:bg-[#2a5a2a] transition-colors"
                    style={{ border: "2px outset #4a7a4a" }}
                  >
                    &gt;&gt; View Product Catalog
                  </a>
                  <a
                    href="#contact"
                    className="inline-block bg-[#8b7635] text-white px-6 py-3 text-center uppercase tracking-wider text-sm font-bold hover:bg-[#a08940] transition-colors"
                    style={{ border: "2px outset #b09950" }}
                  >
                    &gt;&gt; Request a Quote
                  </a>
                </div>
              </div>

              {/* Right side - "What's New" box */}
              <div className="lg:w-80 w-full">
                <div
                  className="border-2 border-[#8b7635]"
                  style={{ boxShadow: "3px 3px 0px #8b7635" }}
                >
                  <div className="bg-[#8b7635] px-4 py-2">
                    <h4 className="text-white font-bold text-sm uppercase tracking-wider">
                      &bull; What&apos;s New &bull;
                    </h4>
                  </div>
                  <div className="bg-white p-4 space-y-4 text-sm">
                    <div className="border-b border-[#d4c9a8] pb-3">
                      <div className="text-[#8b7635] text-xs font-bold">
                        Jan 15, 2026
                      </div>
                      <div className="text-[#1a3a1a]">
                        New expanded capacity for sodium hydroxide production
                        line now operational.
                      </div>
                    </div>
                    <div className="border-b border-[#d4c9a8] pb-3">
                      <div className="text-[#8b7635] text-xs font-bold">
                        Dec 3, 2025
                      </div>
                      <div className="text-[#1a3a1a]">
                        Senchi Chemical receives 2025 Responsible Care&reg;
                        Excellence Award.
                      </div>
                    </div>
                    <div className="border-b border-[#d4c9a8] pb-3">
                      <div className="text-[#8b7635] text-xs font-bold">
                        Nov 18, 2025
                      </div>
                      <div className="text-[#1a3a1a]">
                        Now offering bulk ethanol &amp; methanol from renewable
                        feedstock sources.
                      </div>
                    </div>
                    <div>
                      <div className="text-[#8b7635] text-xs font-bold">
                        Oct 1, 2025
                      </div>
                      <div className="text-[#1a3a1a]">
                        Updated MSDS sheets available for all chlor-alkali
                        products.
                      </div>
                    </div>
                  </div>
                </div>

                {/* Certifications box */}
                <div className="mt-4 border-2 inset border-[#ccc] bg-[#f5f0e8] p-3 text-center">
                  <div className="text-xs uppercase tracking-wider text-[#8b7635] font-bold mb-2">
                    Certifications
                  </div>
                  <div className="flex flex-wrap justify-center gap-3 text-xs text-[#1a3a1a]">
                    <span className="border border-[#8b7635] px-2 py-1 bg-white">
                      ISO 9001:2015
                    </span>
                    <span className="border border-[#8b7635] px-2 py-1 bg-white">
                      ISO 14001
                    </span>
                    <span className="border border-[#8b7635] px-2 py-1 bg-white">
                      REACH
                    </span>
                    <span className="border border-[#8b7635] px-2 py-1 bg-white">
                      GMP
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
