"use client"

import React, { useState, useRef, useEffect } from 'react'
import Logo from './logo'
import { style } from '../../config'
import Link from 'next/link'

export type NavDropdownItem = {
  name: string;
  href: string;
};

export type MegaMenuSection = {
  title?: string;
  links?: { title: string; href: string }[];
  divider?: boolean;
};

export type MegaMenu = {
  title: string;
  sections: MegaMenuSection[];
};

export type NavItem = {
  name: string;
  href?: string;
  badge?: string;
  dropdownItems?: NavDropdownItem[];
  megaMenu?: MegaMenu | null;
};

interface HeaderProps {
  navItems?: NavItem[];
}

const defaultNavItems: NavItem[] = [
    {
      name: 'About us',
      href: '/about',
      // megaMenu: {
      //   title: 'About Us',
      //   sections: [
      //     {
      //       title: 'About Us',
      //       links: [
      //         { title: 'Our Story', href: '/story' },
      //         { title: 'Contact Us', href: '/contact' },
      //       ]
      //     },
          // { divider: true },
          // {
          //   title: 'For Investors',
          //   links: [
          //     { title: 'Corporate Overview', href: '/overview' },
          //     { title: 'Press Releases & Events', href: '/press' },
          //     { title: 'SEC Filings & Financials', href: '/sec' },
          //     { title: 'Governance', href: '/governance' },
          //     { title: 'Resources & Contacts', href: '/resources' },
          //   ]
          // }
        // ]
      // }
    },
    // { 
    //     name: 'Products', 
    //     href: '/product',
    //     badge: 'New drop!',
    //     dropdownItems: [
    //         { name: 'Fraud', href: '#fraud' },
    //         { name: 'Claims Processing', href: '#claims' },
    //     ],
    // },
    // { name: 'Pricing', href: '/pricing' },
    { 
        name: 'Careers', 
        href: '/careers', 
        // badge: "We're hiring!",
        // dropdownItems: [
        //     { name: 'About', href: '#about' },
        //     { name: 'Careers', href: '#careers' },
        // ],
    },

];

export default function Header({ navItems = defaultNavItems }: HeaderProps) {
  const [openMenuIdx, setOpenMenuIdx] = useState<number | null>(null);
  const navRef = useRef<HTMLDivElement>(null);

  // Close menu on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setOpenMenuIdx(null);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close menu on escape
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpenMenuIdx(null);
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <header className={`flex items-center ${style.colors.sections.header.bg} w-full border-b-2 border-gray-300 py-2`}>
      <div ref={navRef} className="w-full max-w-7xl mx-auto px-16 flex items-center py-0.5">
        <Link href="/">
          <Logo imgPath='/senchi.png' width={100} height={54}/>
        </Link>
        <nav className="flex items-center gap-6 text-gray-800 text-sm ml-auto pr-10">
          {navItems.map((item, idx) => (
            <div key={item.name + idx} className={`relative ${style.colors.sections.header.text}`}>
              <div className="flex items-center">
                {item.megaMenu ? (
                  <button
                    type="button"
                    className={`flex items-center gap-1 focus:outline-none relative after:content-[''] after:absolute after:h-0.5 after:bottom-[-0.5rem] after:left-0 after:bg-current after:transition-all after:duration-300 ${openMenuIdx === idx ? 'after:w-full' : 'after:w-0'} hover:after:w-full`}
                    onClick={() => setOpenMenuIdx(openMenuIdx === idx ? null : idx)}
                    aria-expanded={openMenuIdx === idx}
                  >
                    <span>{item.name}</span>
                    <svg
                      className={`w-3 h-3 ml-1 transition-transform duration-200 ${openMenuIdx === idx ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                ) : item.href ? (
                  <a href={item.href} className="flex items-center gap-1 relative after:content-[''] after:absolute after:w-0 after:h-0.5 after:bottom-[-0.5rem] after:left-0 after:bg-current after:transition-all after:duration-300 hover:after:w-full">
                    <span>{item.name}</span>
                    {item.badge && (
                      <span className={`ml-1 bg-green-100 ${style.colors.baseAccent.badge} px-2 py-0.5 rounded text-xs`}>{item.badge}</span>
                    )}
                  </a>
                ) : (
                  <span className="flex items-center gap-1 cursor-pointer">
                    {item.name}
                  </span>
                )}
              </div>
              {item.dropdownItems && (
                <div className="absolute left-0 top-full mt-2 hidden group-hover:block bg-white border rounded shadow-lg min-w-[100px] z-10">
                  {item.dropdownItems.map((drop, dIdx) => (
                    <a
                      key={drop.name + dIdx}
                      href={drop.href}
                      className="block px-4 py-2 text-gray-800 hover:bg-gray-100 whitespace-nowrap"
                    >
                      {drop.name}
                    </a>
                  ))}
                </div>
              )}
              {item.megaMenu && openMenuIdx === idx && (
                <div className="absolute left-1/2 -translate-x-1/2 top-full mt-4 flex bg-white border border-gray-200 rounded shadow-2xl z-20 px-12 py-10 min-w-[900px] gap-12 text-gray-900 pointer-events-auto">
                  {/* Mega menu sections: can be divider or content, in any order */}
                  {item.megaMenu.sections.map((section, sIdx) => (
                    section.divider ? (
                      <div key={sIdx} className="w-px bg-gray-300 mx-8" />
                    ) : (
                      <div key={sIdx} className="min-w-[220px] flex flex-col justify-start">
                        {/* Only show the main menu title in the first non-divider section */}
                        {sIdx === 0 && (
                          <h2 className="text-3xl font-serif mb-8">{item.megaMenu ? item.megaMenu.title : ''}</h2>
                        )}
                        {section.title && <div className="uppercase text-xs tracking-widest text-gray-500 mb-4">{section.title}</div>}
                        {section.links && section.links.map((link, lIdx) => (
                          <a
                            key={link.title + lIdx}
                            href={link.href}
                            className="text-lg mb-4 hover:underline"
                            onClick={() => setOpenMenuIdx(null)}
                          >
                            {link.title}
                          </a>
                        ))}
                      </div>
                    )
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
        {/* <a 
          href="#start"
          className={`${style.colors.baseAccent.bg} ${style.colors.baseAccent.bgHover} text-white px-4 py-1.5 rounded flex items-center gap-2 transition-colors`}>
          Book a demo
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7 7" /></svg>
        </a> */}
      </div>
    </header>
  )
}
