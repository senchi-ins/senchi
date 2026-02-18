"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header
      className="w-full"
      style={{ fontFamily: "'Georgia', 'Times New Roman', serif" }}
    >
      {/* Top marquee banner */}
      <div className="marquee-banner">
        <span>
          *** Senchi Chemical Supply Co. &mdash; ISO 9001:2000 Certified &mdash;
          Serving Industry Across North America &mdash; Call Toll-Free:
          1-800-555-CHEM &mdash; Fax: (416) 555-0199 ***
        </span>
      </div>

      {/* Main header bar */}
      <div className="bg-[#f5f0e8] border-b-4 border-double border-[#1a3a1a]">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            {/* Company name / logo area */}
            <div className="flex items-center gap-4">
              <div className="hidden sm:block w-16 h-16 border-2 border-[#8b7635] bg-[#1a3a1a] flex items-center justify-center">
                <div
                  className="w-16 h-16 flex items-center justify-center text-[#d4c9a8] font-bold text-lg"
                  style={{ fontFamily: "'Courier New', monospace" }}
                >
                  SCS
                </div>
              </div>
              <div>
                <h1
                  className="text-xl sm:text-2xl font-bold text-[#1a3a1a] tracking-wide"
                  style={{ fontFamily: "'Georgia', serif" }}
                >
                  SENCHI CHEMICAL SUPPLY CO.
                </h1>
                <p className="text-xs text-[#8b7635] tracking-widest uppercase">
                  Commodity-Derived Chemical Products
                </p>
              </div>
            </div>

            {/* Contact info - desktop */}
            <div className="hidden lg:block text-right text-sm text-[#1a3a1a]">
              <div className="font-bold">Toll-Free: 1-800-555-CHEM</div>
              <div>Fax: (416) 555-0199</div>
              <div className="text-xs text-[#8b7635]">sales@senchichem.com</div>
            </div>

            {/* Mobile menu button */}
            <div className="lg:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="p-2 text-[#1a3a1a]"
              >
                {isMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation bar */}
      <nav className="bg-[#1a3a1a] border-b-2 border-[#8b7635]">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="hidden lg:flex items-center justify-center gap-1 py-1">
            {[
              { label: "Home", href: "#" },
              { label: "Product Catalog", href: "#catalog" },
              { label: "Industries Served", href: "#industries" },
              { label: "Request a Quote", href: "#contact" },
              { label: "MSDS Sheets", href: "#catalog" },
              { label: "Contact", href: "#contact" },
            ].map((item, i) => (
              <a
                key={i}
                href={item.href}
                className="px-4 py-2 text-[#d4c9a8] hover:bg-[#8b7635] hover:text-white text-sm uppercase tracking-wider transition-colors"
                style={{ fontFamily: "'Georgia', serif" }}
              >
                {item.label}
              </a>
            ))}
          </div>
        </div>
      </nav>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="lg:hidden bg-[#1a3a1a] border-b-2 border-[#8b7635]">
          <div className="px-4 py-2 space-y-1">
            {[
              { label: "Home", href: "#" },
              { label: "Product Catalog", href: "#catalog" },
              { label: "Industries Served", href: "#industries" },
              { label: "Request a Quote", href: "#contact" },
              { label: "MSDS Sheets", href: "#catalog" },
              { label: "Contact", href: "#contact" },
            ].map((item, i) => (
              <a
                key={i}
                href={item.href}
                onClick={() => setIsMenuOpen(false)}
                className="block px-4 py-2 text-[#d4c9a8] hover:bg-[#8b7635] hover:text-white text-sm uppercase tracking-wider"
                style={{ fontFamily: "'Georgia', serif" }}
              >
                {item.label}
              </a>
            ))}
            <div className="border-t border-[#8b7635] pt-2 mt-2 px-4 pb-2">
              <div className="text-[#d4c9a8] text-sm">
                Toll-Free: 1-800-555-CHEM
              </div>
              <div className="text-[#8b7635] text-xs">sales@senchichem.com</div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
