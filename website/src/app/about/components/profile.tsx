import React from 'react';

interface TeamMember {
  name: string;
  role: string;
  experience: string[];
  image?: string;
  linkedin?: string;
}

interface TeamProfileProps {
  member: TeamMember;
}

export default function TeamProfile({ member }: TeamProfileProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-shadow duration-300">
      <div className="flex flex-col items-center text-center space-y-6">
        {/* Profile Image */}
        <div className="relative">
          <div className="w-32 h-32 rounded-full overflow-hidden bg-gradient-to-br from-senchi-primary to-senchi-primary/80 p-1">
            <div className="w-full h-full rounded-full bg-white p-1">
              <div className="w-full h-full rounded-full bg-gradient-to-br from-senchi-primary/20 to-senchi-primary/40 flex items-center justify-center">
                <span className="text-3xl font-bold text-senchi-primary">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Name and Role */}
        <div className="space-y-2">
          <h3 className="text-2xl font-bold text-gray-900">{member.name}</h3>
          <p className="text-lg text-senchi-primary font-semibold">{member.role}</p>
        </div>

        {/* Experience */}
        <div className="space-y-3 w-full">
          <ul className="space-y-2">
            {member.experience.map((exp, index) => (
              <li key={index} className="text-gray-700 text-sm leading-relaxed">
                {exp}
              </li>
            ))}
          </ul>
        </div>

        {/* LinkedIn Link */}
        {member.linkedin && (
          <a
            href={member.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-senchi-primary hover:text-senchi-primary/80 transition-colors text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
            View Profile
          </a>
        )}
      </div>
    </div>
  );
}
