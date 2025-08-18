import React from 'react';
import TeamProfile from './profile';

const teamMembers = [
  {
    name: "Michael Dawes",
    role: "Co-Founder & CEO",
    experience: [
      "Former McKinsey Consultant and software engineer",
    ],
    linkedin: "https://www.linkedin.com/in/michaelldawes/"
  },
  {
    name: "Adam Trotman",
    role: "Co-Founder & CRO",
    experience: [
      "Former McKinsey Consultant and physics graduate",
    ],
    linkedin: "https://www.linkedin.com/in/adamtrotman/"
  }
];

export default function TeamSection() {
  return (
    <section className="py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Meet Our Team
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            We&apos;re a team of ex-consultants with backgrounds in software engineering and physics.
          </p>
        </div>

        {/* Team Grid */}
        <div className="flex justify-center">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl">
            {teamMembers.map((member, index) => (
              <TeamProfile key={index} member={member} />
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Join Our Mission
            </h3>
            <p className="text-gray-600 mb-6">
              If you&apos;re passionate about 
              IoT, machine learning, or protecting families from water damage, 
              we&apos;d love to hear from you.
            </p>
            <a
              href="mailto:mike@senchi.ca"
              className="inline-flex items-center gap-2 bg-senchi-primary hover:bg-senchi-primary/90 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              Get in Touch
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
