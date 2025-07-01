import { style } from '@/config'
import React from 'react'
import Image from 'next/image'

const content = {
    title: "Do Good",
    header: "Protecting what matters.",
    description: `We believe that insurance should make you feel good, not just be a necessary evil. To achieve this, we operate under a capped profit structure - we take a flat fee, cover costs, and donate the rest to a charity of your choosing.

    For you, this means that when you buy insurance from us, you're protecting the things that matter to you regardless of if you ever make a claim.

    For us, it means that we're not incentivized to take unnecessary risks or avoid paying out claims.

    Together, we're making the world a better place.
    `,
}

export default function hero() {
  return (
    <section className={`w-full h-[80vh] flex flex-col justify-center ${style.colors.sections.hero.mainBg}`}>
        <div className={`w-screen bg-senchi-main text-white relative left-1/2 right-1/2 -mx-[50vw]`}>
            <div className="max-w-7xl mx-auto px-4 md:px-16">
            <h1 
                className={
                    `text-5xl text-left py-12 max-w-10xl mx-auto
                    ${style.colors.sections.hero.accentFont}
                    `
                }
            >
                {content.title}
            </h1>
            </div>
        </div>
        <div className="flex flex-col flex-1 max-w-7xl mx-auto px-4 md:px-16 pt-12">
            <h2 className={`text-3xl text-left pb-6 ${style.colors.sections.hero.mainFont}`}>
                {content.header}
            </h2>
            <p className={`text-xl text-left ${style.colors.sections.hero.secondaryFont}`}>
                {content.description.split('\n').map((line, idx, arr) => (
                      <React.Fragment key={idx}>
                        {line}
                        {idx < arr.length - 1 && <br />}
                      </React.Fragment>
                ))}
            </p>
        </div>
        <div className="hidden md:flex flex-col justify-center items-center flex-1 h-full">
            <Image
            src="/images/do_good_visual.png"
            alt="Senchi's fee structure visualization"
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
