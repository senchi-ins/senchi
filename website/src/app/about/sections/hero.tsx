import { style } from '@/config'
import React from 'react'

const content = {
    title: "About Us",
    header: "We're a new kind of insurance company.",
    description: `Our belief is that insurance doesn't need to be expensive, and the money 
    shouldn't just evaporate into corporate profits.
    
    We use AI to streamline quotes, automate claims processing, and 
    detect fraud to help you save time and money. Then, we take any remaining
    profit and donate it to charity so you can feel good about your purchase.

    We've spent the last 2 years builing pricing models and developing GenAI workflows
    at McKinsey to help some of the world's largest companies. Now, we're bringing our
    experience to insurance to help Canadians get the best deals on insurance.
    `,
}

export default function hero() {
  return (
    <section className="w-full h-[80vh] flex flex-col">
        <div className="w-screen bg-senchi-main text-white relative left-1/2 right-1/2 -mx-[50vw]">
            <h1 
                className={
                    `text-5xl text-left py-12 max-w-10xl mx-auto px-27
                    ${style.colors.sections.hero.accentFont}
                    `
                }
            >
                {content.title}
            </h1>
        </div>
        <div className="flex flex-col flex-1 max-w-10xl mx-auto px-16 pt-12">
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
    </section>
  )
}
