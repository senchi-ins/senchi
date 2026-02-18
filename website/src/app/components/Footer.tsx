"use client";

import { useState, useEffect } from "react";

export default function Footer() {
  const [hitCount, setHitCount] = useState(0);

  useEffect(() => {
    setHitCount(14832 + Math.floor(Math.random() * 200));
  }, []);

  return (
    <footer
      className="bg-[#1a3a1a]"
      style={{ fontFamily: "'Georgia', 'Times New Roman', serif" }}
    >
      {/* Contact / Quote Request section */}
      <div id="contact" className="border-b-2 border-[#8b7635]">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="text-center mb-8">
            <h3 className="text-xl font-bold text-[#d4c9a8] uppercase tracking-wider">
              Request a Quote / Contact Us
            </h3>
            <div className="w-48 mx-auto border-t-2 border-[#8b7635] mt-2"></div>
          </div>

          <div className="grid md:grid-cols-3 gap-8 text-[#d4c9a8]">
            {/* Sales */}
            <div className="text-center">
              <div className="border-2 border-[#8b7635] bg-[#2a5a2a] p-4">
                <h4 className="font-bold text-[#d4c9a8] uppercase tracking-wider text-sm mb-3">
                  Sales Department
                </h4>
                <div className="space-y-1 text-sm">
                  <div>
                    Toll-Free:{" "}
                    <span className="text-white font-bold">1-800-555-CHEM</span>
                  </div>
                  <div>Direct: (416) 555-0142</div>
                  <div>Fax: (416) 555-0199</div>
                  <div className="pt-2">
                    <a
                      href="mailto:sales@senchichem.com"
                      className="text-[#d4c9a8] underline hover:text-white"
                    >
                      sales@senchichem.com
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Technical */}
            <div className="text-center">
              <div className="border-2 border-[#8b7635] bg-[#2a5a2a] p-4">
                <h4 className="font-bold text-[#d4c9a8] uppercase tracking-wider text-sm mb-3">
                  Technical Support
                </h4>
                <div className="space-y-1 text-sm">
                  <div>Direct: (416) 555-0155</div>
                  <div>Hours: Mon&ndash;Fri 8am&ndash;5pm EST</div>
                  <div className="pt-2">
                    <a
                      href="mailto:techsupport@senchichem.com"
                      className="text-[#d4c9a8] underline hover:text-white"
                    >
                      techsupport@senchichem.com
                    </a>
                  </div>
                  <div className="pt-1 text-xs text-[#8b7635]">
                    MSDS requests &bull; Custom formulations
                    <br />
                    Product compatibility inquiries
                  </div>
                </div>
              </div>
            </div>

            {/* Address */}
            <div className="text-center">
              <div className="border-2 border-[#8b7635] bg-[#2a5a2a] p-4">
                <h4 className="font-bold text-[#d4c9a8] uppercase tracking-wider text-sm mb-3">
                  Head Office &amp; Plant
                </h4>
                <div className="space-y-1 text-sm">
                  <div>Senchi Chemical Supply Co.</div>
                  <div>2450 Industrial Parkway</div>
                  <div>Mississauga, ON L5K 1B3</div>
                  <div>Canada</div>
                  <div className="pt-2 text-xs text-[#8b7635]">
                    Shipping hours: Mon&ndash;Sat 6am&ndash;6pm EST
                    <br />
                    Truck &amp; Rail access available
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-[#8b7635]">
          <div className="text-center md:text-left">
            &copy; 1987&ndash;2026 Senchi Chemical Supply Co. All Rights
            Reserved.
            <br />
            Responsible Care&reg; &bull; ISO 9001:2015 &bull; ISO 14001 &bull;
            Member, Chemistry Industry Association of Canada
          </div>
          <div className="flex flex-col items-center gap-2">
            <div className="flex items-center gap-4">
              <a href="#" className="text-[#d4c9a8] underline hover:text-white">
                Privacy Policy
              </a>
              <span className="text-[#8b7635]">|</span>
              <a href="#" className="text-[#d4c9a8] underline hover:text-white">
                Terms &amp; Conditions
              </a>
              <span className="text-[#8b7635]">|</span>
              <a href="#" className="text-[#d4c9a8] underline hover:text-white">
                Site Map
              </a>
            </div>
            <div className="flex items-center gap-3">
              <span>Visitors:</span>
              <span className="hit-counter">{hitCount.toLocaleString()}</span>
              <span className="text-[#555]">|</span>
              <span>Best viewed at 1024x768</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
