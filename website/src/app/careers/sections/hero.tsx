import { style } from '@/config'
import React from 'react'

const content = {
    title: "Help us build the future of insurance",
    header: "Check back soon for opportunities to join our team!",
    description: `We're a small team and expect to grow quickly. If you're interested in working with us, 
    please send an email to founders@senchi.ca.
    `,
}

export default function hero() {
  return (
    <section className="w-full h-[80vh] flex flex-col">
        <div className={`w-screen bg-senchi-main text-white relative left-1/2 right-1/2 -mx-[50vw]`}>
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
                {content.description.split('\n').map((line, idx, arr) => {
                  const email = 'founders@senchi.ca';
                  const parts = line.split(email);
                  return (
                    <React.Fragment key={idx}>
                      {parts.map((part, i) => (
                        <React.Fragment key={i}>
                          {part}
                          {i < parts.length - 1 && (
                            <a 
                              href={`mailto:${email}`}
                              className="underline"
                              style={{ color: '#240DBF' }}
                            >
                              {email}
                            </a>
                          )}
                        </React.Fragment>
                      ))}
                      {idx < arr.length - 1 && <br />}
                    </React.Fragment>
                  );
                })}
            </p>
        </div>
    </section>
  )
}
