import React from 'react'
import Header from '../components/Header'
import Footer from '../components/Footer'
import MissionSection from './components/MissionSection'
import TeamSection from './components/TeamSection'

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-senchi-primary via-senchi-primary-light/50 to-white">
      <Header />
      <main>
        <MissionSection />
        <TeamSection />
      </main>
      <Footer />
    </div>
  )
}
