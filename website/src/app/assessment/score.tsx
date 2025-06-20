import { AnalyzeHouseResponse } from '@/utils/api';
import React from 'react'

interface AssessmentScoreProps {
  labellingResponse: AnalyzeHouseResponse;
}

export default function AssessmentScore({ labellingResponse }: AssessmentScoreProps) {
  const score = labellingResponse.final_score;
  console.log(labellingResponse);
  const maxScore = 100;
  const percent = Math.round((score / maxScore) * 100);
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (percent / 100) * circumference;

  const getColor = (score: number): string => {
    if (score >= 80) return "#10B981"; // Green
    if (score >= 60) return "#F59E0B"; // Orange
    if (score >= 50) return "#F6C700"; // Yellow
    return "#EF4444"; // Red
  };

  const strokeColor = getColor(score);

  return (
    <div className="bg-white rounded-2xl p-8 w-full max-w-md mx-auto flex flex-col items-center justify-center">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            className="text-gray-200"
            strokeWidth="10"
            stroke="currentColor"
            fill="transparent"
            r="45"
            cx="50"
            cy="50"
          />
          {/* Progress circle */}
          <circle
            className="transform -rotate-90 origin-center"
            stroke={strokeColor}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            r="45"
            cx="50"
            cy="50"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color: strokeColor }}>{percent}%</span>
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
