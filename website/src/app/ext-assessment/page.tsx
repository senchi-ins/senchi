"use client"

import React, { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation';
import Search from './search'
import { 
    fetchLocationSurvey, 
    LocationRiskResponse,
    CreateSurveyRequest,
    createSurveyAndRedirect
} from '../api/survey/survey'

function ExternalAssessmentContent() {
    const [input, setInput] = useState("");
    const [enterPressed, setEnterPressed] = useState(false);
    const [survey, setSurvey] = useState<LocationRiskResponse | null>(null);
    const router = useRouter();
    const searchParams = useSearchParams();

    // Check for address parameter and auto-trigger survey
    useEffect(() => {
        const addressParam = searchParams.get('address');
        if (addressParam && !enterPressed) {
            setInput(addressParam);
            setEnterPressed(true);
        }
    }, [searchParams, enterPressed]);

    useEffect(() => {
        if (enterPressed) {
            fetchLocationSurvey(input).then(setSurvey);
        }
    }, [enterPressed, input]);

    useEffect(() => {
        if (!survey) return;
        const handleSurvey = async () => {
            const title = "How protected is your home?";
            const description = "Please answer the following questions to assess your home's risk.";

            const surveyContent = {
                title: title,
                description: description,
                workspaceId: "default-workspace",
                ...survey
            };
            
            let i = 0;
            for (const question of surveyContent.questions) {
                question['order'] = i;
                question['type'] = "MULTIPLE_CHOICE";
                // Only split if rubric is a string, otherwise use an empty array
                question['options'] = typeof question.rubric === "string"
                    ? question.rubric.split("\n").map(option => option.trim())
                    : ["Yes", "No"];
                question['text'] = question.question;
                i++;
            }

            await createSurveyAndRedirect(surveyContent as CreateSurveyRequest);
        };
        handleSurvey();
    }, [survey, router]);

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-senchi-footer">
            <Search setInput={setInput} input={input} setEnterPressed={setEnterPressed} />
        </div>
    )
}

export default function ExternalAssessment() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center h-screen bg-senchi-footer">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                <p className="mt-4 text-white">Loading...</p>
            </div>
        }>
            <ExternalAssessmentContent />
        </Suspense>
    );
}