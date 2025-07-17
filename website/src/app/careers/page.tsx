import React from 'react'
import { Header } from '@/app/components/Header'
import { Footer } from '@/app/components/Footer'
import Hero from './sections/hero'

import { style } from '@/config'

export default function Careers() {
  return (
    <div className={`items-center justify-items-center min-h-screen gap-16 font-[family-name:var(--font-geist-sans)] ${style.colors.sections.main.bg}`}>
      <Header />
      <Hero />
      <Footer />
    </div>
  )
}