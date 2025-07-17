import { Header } from '@/app/components/Header'
import { Footer } from '@/app/components/Footer'
import React from 'react'

import { style } from '@/config'
import Hero from './sections/hero'

export default function About() {
  return (
    <div className={`items-center justify-items-center min-h-screen gap-16 font-[family-name:var(--font-geist-sans)] ${style.colors.sections.main.bg}`}>
      <Header />
      <Hero />
      <Footer />
    </div>
  )
}
