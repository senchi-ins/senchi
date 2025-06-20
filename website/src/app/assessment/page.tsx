"use client"

import React, { useState, useEffect } from 'react'
import Header from '../components/header'
import Search from './search'
import BespokeHouse from '../generated/bespokeHouse'

import { uploadFile, generateModel, getModelOutput, analyzeHouse, AnalyzeHouseResponse } from '@/utils/api'
import AssessmentScore from './score'
import MapView from './mapView'
import Recommendation from './recommendation'
// import sampleReturn from '@/utils/sampleReturn.json'

// const url = "https://tripo-data.rg1.data.tripo3d.com/tcli_452312b4252d418cbd41cff1e5c98d35/20250618/21a6930a-143f-44c3-9e2f-db343792298c/tripo_pbr_model_21a6930a-143f-44c3-9e2f-db343792298c.glb?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly90cmlwby1kYXRhLnJnMS5kYXRhLnRyaXBvM2QuY29tL3RjbGlfNDUyMzEyYjQyNTJkNDE4Y2JkNDFjZmYxZTVjOThkMzUvMjAyNTA2MTgvMjFhNjkzMGEtMTQzZi00NGMzLTllMmYtZGIzNDM3OTIyOThjL3RyaXBvX3Bicl9tb2RlbF8yMWE2OTMwYS0xNDNmLTQ0YzMtOWUyZi1kYjM0Mzc5MjI5OGMuZ2xiIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzUwMjkxMjAwfX19XX0_&Signature=iWrhXBjsfvFwt~~ZXi3U3SuR1kcUdVUBXBofBYJvzfcJcKMfwylRj1Iefok9tsrNUABSVAeHms5LCGJICFG62p8E3jloxR-fviw6gt09yKIv56nJ803dDOSF1lUht5UWrez1MOHKqLkbNadLN1~xhROYQMlFKU9~z9t8YwhquD8O7seI8Umn31sPXcPS~OW3E~UdpcqvunMSoUlR5c2HLhTDtWpGhzYAcwOhHQuw9OhC~w4WRzKHkWIGib8VkbdV1G1-RGDcYt-NtXhSUX6tdncG9zaXkpu-k0zHJkW8buqN5dbUbj9qOdo-nJ9Fa9WulG7yT-LD96nIue97oivORQ__&Key-Pair-Id=K1676C64NMVM2J"

// const url = "tripo_convert_4c0f25aa-21f5-46a2-9111-28feef8fd803.glb"
const url = "./3D/sample_house.glb"

export default function Assessment() {
  const [input, setInput] = useState("");
  const [imageURL, setImageURL] = useState(url);
  const [modelLoading, setModelLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [enterPressed, setEnterPressed] = useState(false);
  const [labellingResponse, setLabellingResponse] = useState<AnalyzeHouseResponse | null>(null);

  useEffect(() => {
    if (!enterPressed) return;

    const fetchModel = async () => {
      setModelLoading(true);
      try {
        // Upload the address to the API
        const upload_response = await uploadFile(input);

        // console.log(`upload_response: ${upload_response.data.image_token}`);
        // Generate the model
        const task = await generateModel(upload_response, "png", "image_to_model");
        // console.log(`task: ${task.data}`);
        // Use type guards to safely access task_id and result
        const taskId = (task && typeof task === 'object' && 'data' in task && task.data && typeof task.data === 'object' && 'task_id' in task.data) ? (task.data as { task_id?: string }).task_id : undefined;
        if (!taskId) throw new Error('No task_id returned from generateModel');

        // Poll for model output until it's ready
        let model_output: unknown = null;
        let attempts = 0;
        const maxAttempts = 20;
        const delay = 1500; // ms

        while (attempts < maxAttempts) {
          model_output = await getModelOutput(taskId);
          let result: unknown = undefined;
          if (model_output && typeof model_output === 'object' && 'data' in model_output) {
            const data = (model_output as { data?: unknown }).data;
            if (data && typeof data === 'object' && 'result' in data) {
              result = (data as { result?: unknown }).result;
            }
          }
          let hasUrl = false;
          if (result && typeof result === 'object' && 'pbr_model' in result) {
            const pbr_model = (result as { pbr_model?: unknown }).pbr_model;
            if (pbr_model && typeof pbr_model === 'object' && 'url' in pbr_model) {
              hasUrl = typeof (pbr_model as { url?: unknown }).url === 'string';
            }
          }
          if (hasUrl) break;
          await new Promise(res => setTimeout(res, delay));
          attempts++;
        }

        // Safely extract the model_url as a string
        let model_url: string | undefined = undefined;
        if (model_output && typeof model_output === 'object' && 'data' in model_output) {
          const data = (model_output as { data?: unknown }).data;
          if (data && typeof data === 'object' && 'result' in data) {
            const result = (data as { result?: unknown }).result;
            if (result && typeof result === 'object' && 'pbr_model' in result) {
              const pbr_model = (result as { pbr_model?: unknown }).pbr_model;
              if (pbr_model && typeof pbr_model === 'object' && 'url' in pbr_model) {
                const url = (pbr_model as { url?: unknown }).url;
                if (typeof url === 'string') {
                  model_url = url;
                }
              }
            }
          }
        }
        if (model_url) setImageURL(model_url);
      } catch (error) {
        // Optionally handle error
        console.error(error);
      } finally {
        setModelLoading(false);
      }
    };

    const performHouseAnalysis = async () => {
      setAnalysisLoading(true);
      try {
        // Simulate a network delay for robust testing
        await new Promise(resolve => setTimeout(resolve, 1000));
        const response = await analyzeHouse(input);
        setLabellingResponse(response);
      } catch (error) {
        console.error("Failed to analyze house:", error);
        // Optionally, handle the error in the UI
      } finally {
        setAnalysisLoading(false);
      }
    }
    // Conduct the analysis of the home
    performHouseAnalysis();
    // TODO: Uncomment below when running the actual pipeline
    fetchModel();
  }, [enterPressed]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="bg-senchi-background flex-1 w-full">
        <div className="max-w-7xl mx-auto px-4 md:px-16">
          {enterPressed && (
            <div className="flex flex-col pt-10 pb-6 gap-2 max-w-3xl w-full">
              <h1 className="text-2xl font-bold text-senchi-main text-left w-full mb-1">
                Property Assessment Dashboard
              </h1>
              <h4 className="text-base text-gray-700 text-left w-full mb-1">
                {`AI-powered home evaluation and risk analysis for ${input}`}
              </h4>
              <div className="text-sm text-gray-500 text-left w-full italic rounded py-1">
                Note: This dashboard is for demo purposes only. We&apos;re continuing to refine our models and the full dashboard will be available soon.
              </div>
            </div>
          )}
          <div className="flex items-center justify-center w-full min-h-[80vh]">
            {!enterPressed ? (
              <Search setInput={setInput} input={input} setEnterPressed={setEnterPressed} />
            ) : (
              (modelLoading || analysisLoading) ? (
                <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: 80 }}>
                  <svg
                    width="48"
                    height="48"
                    viewBox="0 0 48 48"
                    fill="none"
                    style={{ display: "block" }}
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <circle
                      cx="24"
                      cy="24"
                      r="20"
                      stroke="#EBE9FC"
                      strokeWidth="6"
                      fill="none"
                    />
                    <circle
                      cx="24"
                      cy="24"
                      r="20"
                      stroke="#240DBF"
                      strokeWidth="6"
                      strokeLinecap="round"
                      fill="none"
                      strokeDasharray="100"
                      strokeDashoffset="60"
                    >
                      <animateTransform
                        attributeName="transform"
                        type="rotate"
                        from="0 24 24"
                        to="360 24 24"
                        dur="1s"
                        repeatCount="indefinite"
                      />
                    </circle>
                  </svg>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-2 gap-5">
                  <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
                    {labellingResponse && <BespokeHouse imageURL={imageURL} labellingResponse={labellingResponse} />}
                  </div>
                  <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
                    {labellingResponse && <AssessmentScore labellingResponse={labellingResponse} />}
                  </div>
                  <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
                    <MapView />
                  </div>
                  <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
                    {labellingResponse && <Recommendation labellingResponse={labellingResponse} />}
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
