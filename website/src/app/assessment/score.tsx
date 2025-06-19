import React from 'react'

interface AssessmentScoreProps {
  score?: number;
  maxScore?: number;
}

export default function AssessmentScore({ score = 73, maxScore = 100 }: AssessmentScoreProps) {
  const percent = Math.round((score / maxScore) * 100);
  const radius = 60;
  const stroke = 8;
  const normalizedRadius = radius - stroke / 2;
  const circumference = 2 * Math.PI * normalizedRadius;
  const progress = circumference - (percent / 100) * circumference;

  return (
    <div className="bg-white rounded-2xl shadow flex flex-col items-center w-full max-w-md mx-auto h-full justify-center">
      <div className="relative flex items-center justify-center mb-4" style={{ width: 140, height: 140 }}>
        <svg width={140} height={140}>
          <circle
            cx={70}
            cy={70}
            r={normalizedRadius}
            stroke="#E5E7EB"
            strokeWidth={stroke}
            fill="none"
          />
          <circle
            cx={70}
            cy={70}
            r={normalizedRadius}
            stroke="#F6C700"
            strokeWidth={stroke}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-[#F6C700]">{percent}%</span>
          <span className="text-gray-500 text-sm">{score}/{maxScore}</span>
        </div>
      </div>
      <div className="text-center">
        <div className="font-semibold text-lg text-gray-900 mb-1">Assessment Score</div>
        <div className="text-gray-500 text-base mb-4">External Home Evaluation</div>
        <div className="bg-gray-50 rounded-lg px-4 py-2 text-gray-600 text-sm font-medium">
          Based on comprehensive analysis of property condition, location risk factors, and safety features
        </div>
      </div>
    </div>
  )
}
