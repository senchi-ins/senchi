import React, { useState, useRef, useEffect } from 'react'

const mapOptions = [
  {
    label: 'Flood Risk Forecast',
    subtitle: 'Water damage assessment',
  },
  {
    label: 'Forest Fire Forecast',
    subtitle: 'Fire hazard zones',
  },
];

export default function MapView() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(mapOptions[0]);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open]);

  return (
    <div className="bg-white rounded-2xl shadow flex flex-col w-full max-w-md mx-auto h-full justify-center p-8">
      <div className="text-lg font-semibold text-gray-900 mb-6">Predictive forecasts</div>
      {/* Dropdown */}
      <div className="mb-6" ref={dropdownRef}>
        <div className="relative">
          <button
            className={`w-full text-left bg-white border-2 ${open ? 'border-[#BFA6F6]' : 'border-[#BFA6F6]'} rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#BFA6F6] transition flex flex-col relative`}
            style={{ boxShadow: '0 0 0 1.5px #BFA6F6' }}
            onClick={() => setOpen((v) => !v)}
            type="button"
            aria-haspopup="listbox"
            aria-expanded={open}
          >
            <span className="font-medium text-gray-900">{selected.label}</span>
            <span className="text-sm text-gray-500">{selected.subtitle}</span>
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
              <svg width="20" height="20" fill="none" viewBox="0 0 20 20">
                <path d="M6 8l4 4 4-4" stroke="#BFA6F6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </span>
          </button>
          {open && (
            <div className="absolute z-10 mt-2 w-full bg-white rounded-xl shadow-lg border border-[#E5E7EB] overflow-hidden animate-fade-in" role="listbox">
              {mapOptions.map((option) => (
                <button
                  key={option.label}
                  className={`w-full text-left px-4 py-3 flex flex-col transition
                    ${selected.label === option.label ? 'bg-[#F6F0FF]' : 'hover:bg-gray-50'}
                  `}
                  onClick={() => {
                    setSelected(option);
                    setOpen(false);
                  }}
                  role="option"
                  aria-selected={selected.label === option.label}
                  tabIndex={0}
                >
                  <span className="font-medium text-gray-900">{option.label}</span>
                  <span className="text-sm text-gray-500">{option.subtitle}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
      {/* Map Preview Placeholder */}
      <div className="rounded-xl border-2 border-dashed border-[#BFA6F6] bg-gradient-to-r from-green-100 via-blue-100 to-purple-100 flex flex-col items-center justify-center min-h-[120px] py-8">
        <span className="text-gray-500 font-medium">{selected.label}</span>
        <span className="text-gray-400 text-sm">Map previews coming soon</span>
      </div>
    </div>
  )
}