import { AnalyzeHouseResponse } from '@/utils/api';
import React from 'react'

interface RecommendationProps {
  labellingResponse?: AnalyzeHouseResponse;
}

export default function Recommendation({ labellingResponse }: RecommendationProps) {
  // Gracefully handle cases where data is not yet available
  if (!labellingResponse || !labellingResponse.recommendations || !labellingResponse.category_scores) {
    return (
      <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md mx-auto flex items-center justify-center h-full">
        <div className="text-gray-500">Loading recommendations...</div>
      </div>
    );
  }

  const recommendations = labellingResponse.recommendations;
  const categoryScores = labellingResponse.category_scores;
  
  const getScoreForTitle = (title: string) => {
    const category = categoryScores.find(cat => cat.title === title);
    return category?.score || 'medium';
  };
  
  return (
    <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md mx-auto">
      <div className="text-lg font-semibold text-gray-900 mb-6">Top AI Recommendations</div>
      <div className="flex flex-col gap-6 mb-6">
        {recommendations.map((rec) => {
          const score = getScoreForTitle(rec.title);
          const scoreColor = score === 'high' ? '#F87171' : score === 'medium' ? '#F59E0B' : '#10B981';
          const scoreBgColor = score === 'high' ? '#F87171/10' : score === 'medium' ? '#F59E0B/10' : '#10B981/10';
          
          return (
            <div key={rec.title} className="flex gap-4 items-stretch">
              {/* Left vertical line */}
              <div className="w-1 rounded bg-[#BFA6F6]" />
              {/* Content */}
              <div className="flex-1 py-1">
                <div className="flex items-center gap-2 mb-1">
                  {/* Alert icon */}
                  <svg width="20" height="20" fill="none" viewBox="0 0 20 20" className="inline-block align-text-bottom mr-1"><path d="M10 3.5l7.5 13H2.5l7.5-13z" stroke="#F87171" strokeWidth="1.5"/><circle cx="10" cy="14.5" r="1" fill="#F87171"/><path d="M10 8v3" stroke="#F87171" strokeWidth="1.5" strokeLinecap="round"/></svg>
                  <span className="font-semibold text-gray-900 text-base">{rec.title}</span>
                  <span className={`ml-2 text-xs font-semibold px-2 py-0.5 rounded-full`} style={{ backgroundColor: scoreBgColor, color: scoreColor }}>
                    {score.charAt(0).toUpperCase() + score.slice(1)}
                  </span>
                </div>
                <div className="text-gray-700 text-sm mb-2">{rec.description}</div>
                <div className="flex items-center text-xs text-[#7C6FCB] font-medium">
                  <svg width="18" height="18" fill="none" viewBox="0 0 24 24" className="inline-block align-text-bottom mr-1"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" stroke="#BFA6F6" strokeWidth="1.5"/><circle cx="12" cy="9" r="2.5" stroke="#BFA6F6" strokeWidth="1.5"/></svg>
                  {rec.location}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="bg-[#F6F0FF] border border-[#BFA6F6] rounded-lg px-4 py-3 text-[#7C6FCB] text-sm font-medium">
        <span className="font-semibold">AI Analysis:</span> These are the top 3 most critical improvements identified for your property. Implementing these high-priority items will provide the greatest impact on your insurance score and property safety.
      </div>
    </div>
  )
}