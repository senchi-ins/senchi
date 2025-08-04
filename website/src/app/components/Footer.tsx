"use client";

import { Mail, MapPin, Home, Building } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import Image from 'next/image';
// import { addToWaitlist } from "@/utils/waitlist";


export default function Footer() {
  return (
    <footer className="bg-senchi-footer border-t">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="py-16 grid lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="flex items-center">
              <Image src="/senchi.png" alt="Senchi logo" width={1000} height={1000} className="h-8 w-auto" />
            </div>
            <p className="text-gray-600 max-w-sm"> 
              AI powered prediction meets charitable giving for complete protection.
            </p>
            <div className="flex space-x-4">
              {/* <a href="#" className="text-gray-400 hover:text-senchi-primary transition-colors" aria-label="Follow us on X">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-senchi-primary transition-colors" aria-label="Follow us on LinkedIn">
                <Linkedin className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-senchi-primary transition-colors" aria-label="Follow us on Instagram">
                <Instagram className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-senchi-primary transition-colors" aria-label="Follow us on TikTok">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19.321 5.562a5.124 5.124 0 0 1-.443-.258 6.228 6.228 0 0 1-1.137-.966c-.849-.849-1.341-1.984-1.341-3.338h-2.891v15.729c0 1.659-1.341 3-3 3s-3-1.341-3-3 1.341-3 3-3c.338 0 .659.056.956.162v-3.018a6.02 6.02 0 0 0-.956-.078c-3.309 0-6 2.691-6 6s2.691 6 6 6 6-2.691 6-6V9.321a9.065 9.065 0 0 0 5.321 1.679V8.115a6.147 6.147 0 0 1-2.509-2.553z"/>
                </svg>
              </a> */}
            </div>
          </div>

          {/* Insurance Types */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Protection Plans</h3>
            <ul className="space-y-3">
              <li className="flex items-center space-x-2">
                <Home className="h-4 w-4 text-senchi-primary" />
                <a href="#plans" className="text-gray-600 hover:text-senchi-primary transition-colors">Homeowners</a>
              </li>
              <li className="flex items-center space-x-2">
                <Building className="h-4 w-4 text-senchi-primary" />
                <a href="#plans" className="text-gray-600 hover:text-senchi-primary transition-colors">Property Managers</a>
              </li>
              <li className="flex items-center space-x-2">
                <Building className="h-4 w-4 text-senchi-primary" />
                <a href="#plans" className="text-gray-600 hover:text-senchi-primary transition-colors">Insurers</a>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Company</h3>
            <ul className="space-y-3">
              <li><a href="#halo" className="text-gray-600 hover:text-senchi-primary transition-colors">Senchi HomeGuard</a></li>
              <li><a href="#plans" className="text-gray-600 hover:text-senchi-primary transition-colors">Coverage</a></li>
              {/* <li><a href="#do-good" className="text-gray-600 hover:text-senchi-primary transition-colors">Do Good</a></li> */}
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Join the waitlist!</h3>
            <div className="space-y-3">
              <Input 
                type="email" 
                placeholder="Enter your email" 
                className="bg-white border-gray-200"
              />
              <Button 
                className="w-full bg-senchi-primary hover:bg-senchi-primary/90"
                // onClick={() => addToWaitlist(email)}
                >
                Join Waitlist
              </Button>
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div className="border-t border-gray-200 py-8">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-senchi-accent-light rounded-lg flex items-center justify-center">
                <Mail className="h-5 w-5 text-senchi-primary" />
              </div>
              <div>
                <div className="font-medium text-gray-900">Contact Us</div>
                <div className="text-gray-600 text-sm">
                  <a href="mailto:adam@senchi.ca" className="hover:text-senchi-primary transition-colors">adam@senchi.ca</a>
                  <span className="mx-2">|</span>
                  <a href="mailto:mike@senchi.ca" className="hover:text-senchi-primary transition-colors">mike@senchi.ca</a>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-senchi-accent-light rounded-lg flex items-center justify-center">
                <MapPin className="h-5 w-5 text-senchi-primary" />
              </div>
              <div>
                <div className="font-medium text-gray-900">Visit Us</div>
                <div className="text-gray-600 text-sm">Toronto, Canada</div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-200 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-600 text-sm mb-4 md:mb-0">
              © 2025 Senchi Technologies Inc.
            </div>
            {/* <div className="flex items-center space-x-6 text-sm">
              <a href="#" className="text-gray-600 hover:text-senchi-primary transition-colors">Privacy Policy</a>
              <a href="#" className="text-gray-600 hover:text-senchi-primary transition-colors">Terms of Service</a>
              <a href="#" className="text-gray-600 hover:text-senchi-primary transition-colors">Cookie Policy</a>
            </div> */}
          </div>
        </div>
      </div>
    </footer>
  );
}
