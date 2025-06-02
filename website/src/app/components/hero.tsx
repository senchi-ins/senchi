"use client"

import React from 'react'
import Image from 'next/image'
import { style } from '../../config'

const title = "Building Canada's first AI-powered insurance company"
const subtitle = `
Senchi uses AI to speed up processing time and reduce fraud, saving you time and money.
`

// const claims = [
//   "Decrease fraudulant claims paid out",
//   "Automate e2e claims processing and payout"
// ];

export default function Hero() {
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
          {/* <a
            href="#start"
            className={`${style.colors.baseAccent.bg} ${style.colors.baseAccent.bgHover} text-white px-4 py-1.5 rounded font-mono flex items-center gap-2 transition-colors w-fit`}
            onClick={() => window.open(process.env.NEXT_PUBLIC_CAL_LINK, '_blank')}
          >
            Book a demo
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M12 5l7 7-7-7" /></svg>
          </a> */}
        </div>
      </div>
      {/* Right column: image, bottom-aligned (hidden on mobile) */}
      <div className="hidden md:flex flex-col justify-end items-end flex-1 h-full">
        <Image
          src="/images/hero_img.png"
          alt="Insurance AI Illustration"
          width={500}
          height={500}
          sizes="(max-width: 1024px) 300px, 400px"
          style={{ height: 'auto', maxWidth: '100%' }}
          priority
        />
      </div>
    </section>
  )
}
