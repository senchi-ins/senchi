'use client'

import { Button } from "./ui/button";
import { Menu, X, ArrowRight } from "lucide-react";
import { useState } from "react";
import Image from 'next/image';
import Link from 'next/link';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-senchi-footer/80 backdrop-blur-sm">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between z-1 bg-senchi-footer relative">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <Image src="/senchi.png" alt="Senchi logo" width={1000} height={1000} className="h-8 w-auto" />
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#halo" className="text-gray-600 hover:text-senchi-primary transition-colors">
              Senchi Halo
            </a>
            <a href="#plans" className="text-gray-600 hover:text-senchi-primary transition-colors">
              Plans
            </a>
            <a href="#do-good" className="text-gray-600 hover:text-senchi-primary transition-colors">
              Do Good
            </a>
            <Button asChild className="bg-senchi-primary hover:bg-senchi-primary/90 text-white px-4 py-2" size="sm">
              <Link href="/ext-assessment" className="flex items-center gap-2">
                Take our assessment
                <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden absolute bg-senchi-footer backdrop-blur-sm w-full left-1/2 -translate-x-1/2"
          style={{
            transform: isMenuOpen ? 'translateY(0)' : 'translateY(-100%)',
            opacity: isMenuOpen ? 1 : 0,
            transition: 'transform 0.3s ease-in-out, opacity 0.3s ease-in-out',
          }}
        >
          <div className="px-2 md:px-22 border-b">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a
                href="#halo"
                className="block px-3 py-2 text-gray-600 hover:text-senchi-primary transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Senchi Halo
              </a>
              <a
                href="#coverage"
                className="block px-3 py-2 text-gray-600 hover:text-senchi-primary transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Coverage
              </a>
              <a
                href="#do-good"
                className="block px-3 py-2 text-gray-600 hover:text-senchi-primary transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Do Good
              </a>
              <Button
                asChild
                className="mt-4 w-full bg-senchi-primary hover:bg-senchi-primary/90 text-white px-4 py-2"
                size="sm"
              >
                {/* TODO Update to be in line with the desktop version */}
                <a
                  href="https://senchi.ca/ext-assessment"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Take our assessment
                  <ArrowRight className="w-4 h-4" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
