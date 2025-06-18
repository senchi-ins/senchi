"use client"

import React from 'react'
import Image from 'next/image'
import { style } from '../../config'
import { useRouter } from 'next/navigation'

// import DynamicHouse3D from '../generated/dynamic'
// import sampleConfigs from '../generated/data.json'

// import HouseScene from '../generated/chatHouse'

const title = "Building Canada's first AI-powered insurance company"
const subtitle = `
Senchi uses AI to prevent claims before they happen, saving you time and money.
`

// const claims = [
//   "Decrease fraudulant claims paid out",
//   "Automate e2e claims processing and payout"
// ];

export default function Hero() {
  const router = useRouter();

  return (
    <section className="w-full h-[80vh] flex flex-col md:flex-row items-stretch max-w-7xl mx-auto px-4 md:px-16 pt-12">
      {/* Left column: headline, claims, button */}
      <div className="flex flex-col flex-1 w-full justify-center h-full items-center text-center md:items-start md:text-left md:pl-0">
        <h1 className={`text-5xl font-bold pb-6 ${style.colors.sections.hero.mainFontColoured}`}>{title}</h1>
        <p className={`text-xl ${style.colors.sections.hero.secondaryFont}`}>{subtitle}</p>
        <div className="mb-8">
          <ul className="mb-4">
            {/* {claims.map((claim, idx) => (
              <li key={idx} className={`text-xl mb-2 text-left last:mb-6 ${style.colors.sections.hero.secondaryFont}`}>
                {claim}
              </li>
            ))} */}
          </ul>
          <a
            className={`${style.colors.baseAccent.bg} ${style.colors.baseAccent.bgHover} text-white px-4 py-1.5 rounded font-mono flex items-center gap-2 transition-colors w-fit mt-8`}
            href="#"
            onClick={e => { e.preventDefault(); router.push('/assessment'); }}
          >
            {"Check Your Home's Protection Level"}
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7-7" /></svg>
          </a>
        </div>
      </div>
      {/* Right column: image, bottom-aligned (hidden on mobile) */}
      <div className="hidden md:flex flex-col justify-center items-end flex-1 h-full">
        <div
          style={{
            position: 'relative',
            width: 320,
            height: 320,
            display: 'flex',
            alignItems: 'flex-end',
            justifyContent: 'flex-end',
            margin: '0 auto',
          }}
        >
          {/* Apartment (behind, shifted right) */}
          <Image
            src="/assets/abnb_condo.png"
            alt="Apartment"
            width={320}
            height={320}
            style={{
              position: 'absolute',
              left: 160,   // shift right
              top: -10,    // shift down if needed
              zIndex: 1,  // behind
              opacity: 0.85, // optional, for a subtle effect
            }}
          />
          {/* House (in front) */}
          <Image
            src="/assets/abnb_home.png"
            alt="Home"
            width={260}
            height={260}
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              zIndex: 2, // in front
            }}
          />
          {/* Car in front of the apartment */}
          <Image
            src="/assets/abnb_car.png"
            alt="Canada"
            width={200}
            height={200}
            style={{
              position: 'absolute',
              left: 140,
              top: 200,
              zIndex: 2, // in front
            }}
          />
        </div>
      </div>
    </section>
  )
}
