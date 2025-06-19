import React from 'react'

const recommendations = [
  {
    title: 'Clear roof and gutters of debris',
    badge: 'High',
    description: 'Remove leaves, pine needles, and other flammable debris from the roof and gutters.',
    location: 'Roof',
    locationIcon: (
      <svg width="18" height="18" fill="none" viewBox="0 0 24 24" className="inline-block align-text-bottom mr-1"><path d="M3 10.5L12 4l9 6.5" stroke="#BFA6F6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M5 10.5V19a1 1 0 001 1h3v-4h6v4h3a1 1 0 001-1v-8.5" stroke="#BFA6F6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
    ),
  },
  {
    title: 'Create a 30-foot defensible space',
    badge: 'High',
    description: 'Clear a 30-foot zone around the house of flammable vegetation.',
    location: 'Yard',
    locationIcon: (
      <svg width="18" height="18" fill="none" viewBox="0 0 24 24" className="inline-block align-text-bottom mr-1"><path d="M4 20v-2a4 4 0 014-4h8a4 4 0 014 4v2" stroke="#BFA6F6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><circle cx="12" cy="7" r="4" stroke="#BFA6F6" strokeWidth="1.5"/></svg>
    ),
  },
  {
    title: 'Reinforce the garage door',
    badge: 'High',
    description: 'Install a vertical bracing system or a wind-rated garage door.',
    location: 'Garage door',
    locationIcon: (
      <svg width="18" height="18" fill="none" viewBox="0 0 24 24" className="inline-block align-text-bottom mr-1"><rect x="3" y="8" width="18" height="10" rx="2" stroke="#BFA6F6" strokeWidth="1.5"/><path d="M3 12h18" stroke="#BFA6F6" strokeWidth="1.5" strokeLinecap="round"/><path d="M7 16h.01M12 16h.01M17 16h.01" stroke="#BFA6F6" strokeWidth="1.5" strokeLinecap="round"/></svg>
    ),
  },
];

export default function Recommendation() {
  return (
    <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md mx-auto">
      <div className="text-lg font-semibold text-gray-900 mb-6">Top AI Recommendations</div>
      <div className="flex flex-col gap-6 mb-6">
        {recommendations.map((rec) => (
          <div key={rec.title} className="flex gap-4">
            {/* Left vertical line */}
            <div className="w-1 rounded bg-[#BFA6F6] mt-1 mb-1" style={{ minHeight: 56 }} />
            {/* Content */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                {/* Alert icon */}
                <svg width="20" height="20" fill="none" viewBox="0 0 20 20" className="inline-block align-text-bottom mr-1"><path d="M10 3.5l7.5 13H2.5l7.5-13z" stroke="#F87171" strokeWidth="1.5"/><circle cx="10" cy="14.5" r="1" fill="#F87171"/><path d="M10 8v3" stroke="#F87171" strokeWidth="1.5" strokeLinecap="round"/></svg>
                <span className="font-semibold text-gray-900 text-base">{rec.title}</span>
                <span className="ml-2 bg-[#F87171]/10 text-[#F87171] text-xs font-semibold px-2 py-0.5 rounded-full">{rec.badge}</span>
              </div>
              <div className="text-gray-700 text-sm mb-2">{rec.description}</div>
              <div className="flex items-center text-xs text-[#7C6FCB] font-medium">
                {rec.locationIcon}
                {rec.location}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="bg-[#F6F0FF] border border-[#BFA6F6] rounded-lg px-4 py-3 text-[#7C6FCB] text-sm font-medium">
        <span className="font-semibold">AI Analysis:</span> These are the top 3 most critical improvements identified for your property. Implementing these high-priority items will provide the greatest impact on your insurance score and property safety.
      </div>
    </div>
  )
}