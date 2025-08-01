"use client"

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation';
import Search from './search'
import { 
    fetchLocationSurvey, 
    LocationRiskResponse,
    CreateSurveyRequest,
    createSurveyAndRedirect
} from '../api/survey/survey'

export default function ExternalAssessment() {
    const [input, setInput] = useState("");
    const [enterPressed, setEnterPressed] = useState(false);
    const [survey, setSurvey] = useState<LocationRiskResponse | null>(null);
    const router = useRouter();

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

            await createSurveyAndRedirect(surveyContent as CreateSurveyRequest, router);
        };
        handleSurvey();
    }, [survey, router]);

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-senchi-footer">
            <Search setInput={setInput} input={input} setEnterPressed={setEnterPressed} />
        </div>
    )
}