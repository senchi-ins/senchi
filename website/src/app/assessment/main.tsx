// "use client"

// import React, { useState, useEffect } from 'react';
// import BespokeHouse from '../generated/bespokeHouse';
// import { uploadFile, generateModel, getModelOutput, analyzeHouse, AnalyzeHouseResponse } from '@/utils/api';
// import AssessmentScore from './score';
// import MapView from './mapView';
// import Recommendation from './recommendation';
// import { fallback_url } from '@/utils/fallback';
// import { useSearchParams } from 'next/navigation';

// export default function AssessmentMain() {
//   const [input, setInput] = useState("");
//   const [imageURL, setImageURL] = useState(fallback_url);
//   const [modelLoading, setModelLoading] = useState(false);
//   const [analysisLoading, setAnalysisLoading] = useState(false);
//   const [labellingResponse, setLabellingResponse] = useState<AnalyzeHouseResponse | undefined>(undefined);
//   const searchParams = useSearchParams();

//   useEffect(() => {
//     if (!searchParams) return;
//     const address = searchParams.get('address') || "";
//     setInput(address);
//     if (!address) return;

//     const fetchModel = async () => {
//       setModelLoading(true);
//       try {
//         const upload_response = await uploadFile(address);
//         let imageToken;
//         if ('data' in upload_response && upload_response.data && typeof upload_response.data === 'object' && 'image_token' in upload_response.data) {
//           imageToken = upload_response.data.image_token;
//         } else if ('image_token' in upload_response) {
//           imageToken = upload_response.image_token;
//         } else {
//           throw new Error('No image_token found in upload response');
//         }
//         const fileData = {
//           type: "png",
//           file_token: imageToken
//         };
//         const task = await generateModel(fileData, "png", "image_to_model");
//         const taskId = (task && typeof task === 'object' && 'data' in task && task.data && typeof task.data === 'object' && 'task_id' in task.data) ? (task.data as { task_id?: string }).task_id : undefined;
//         if (!taskId) throw new Error('No task_id returned from generateModel');
//         const model_output = await getModelOutput(taskId);
//         let model_url;
//         if (model_output && typeof model_output === 'object') {
//           if ('pbr_model_url' in model_output && typeof model_output.pbr_model_url === 'string') {
//             model_url = model_output.pbr_model_url;
//           } else if ('data' in model_output && model_output.data && typeof model_output.data === 'object' && 'result' in model_output.data) {
//             const data = (model_output as { data?: unknown }).data;
//             if (data && typeof data === 'object' && 'result' in data) {
//               const result = (data as { result?: unknown }).result;
//               if (result && typeof result === 'object' && 'pbr_model' in result) {
//                 const pbr_model = (result as { pbr_model?: unknown }).pbr_model;
//                 if (pbr_model && typeof pbr_model === 'object' && 'url' in pbr_model) {
//                   const url = (pbr_model as { url?: unknown }).url;
//                   if (typeof url === 'string') {
//                     model_url = url;
//                   }
//                 }
//               }
//             }
//           }
//         }
//         if (model_url) {
//           setImageURL(model_url);
//         } else {
//           throw new Error('Could not extract model URL from response');
//         }
//       } catch (error) {
//         console.error('Error details:', error);
//       } finally {
//         setModelLoading(false);
//       }
//     };

//     const performHouseAnalysis = async () => {
//       setAnalysisLoading(true);
//       try {
//         await new Promise(resolve => setTimeout(resolve, 1000));
//         const response = await analyzeHouse(address);
//         setLabellingResponse(response);
//       } catch {
//         console.error("Failed to analyze house. Please refresh the page and try again.");
//       } finally {
//         setAnalysisLoading(false);
//       }
//     };

//     const runPipeline = async () => {
//       try {
//         await fetchModel();
//         await performHouseAnalysis();
//       } catch {
//         console.error('Pipeline error. Please refresh the page and try again.');
//       }
//     };

//     runPipeline();
//   }, [searchParams]);

//   return (
//     <div className="min-h-screen flex flex-col">
//       <div className="bg-senchi-background flex-1 w-full">
//         <div className="max-w-7xl mx-auto px-4 md:px-16">
//           <div className="flex flex-col pt-10 pb-6 gap-2 max-w-3xl w-full">
//             <h1 className="text-2xl font-bold text-senchi-main text-left w-full mb-1">
//               Property Assessment Dashboard
//             </h1>
//             <h4 className="text-base text-gray-700 text-left w-full mb-1">
//               {`AI-powered home evaluation and risk analysis for ${input}`}
//             </h4>
//             <div className="text-sm text-gray-500 text-left w-full italic rounded py-1">
//               Note: This dashboard is for demo purposes only. We&apos;re continuing to refine our models and the full dashboard will be available soon.
//             </div>
//           </div>
//           <div className="flex items-center justify-center w-full min-h-[80vh]">
//             {(modelLoading || analysisLoading) ? (
//               <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: 80 }}>
//                 <svg
//                   width="48"
//                   height="48"
//                   viewBox="0 0 48 48"
//                   fill="none"
//                   style={{ display: "block" }}
//                   xmlns="http://www.w3.org/2000/svg"
//                 >
//                   <circle
//                     cx="24"
//                     cy="24"
//                     r="20"
//                     stroke="#EBE9FC"
//                     strokeWidth="6"
//                     fill="none"
//                   />
//                   <circle
//                     cx="24"
//                     cy="24"
//                     r="20"
//                     stroke="#240DBF"
//                     strokeWidth="6"
//                     strokeLinecap="round"
//                     fill="none"
//                     strokeDasharray="100"
//                     strokeDashoffset="60"
//                   >
//                     <animateTransform
//                       attributeName="transform"
//                       type="rotate"
//                       from="0 24 24"
//                       to="360 24 24"
//                       dur="1s"
//                       repeatCount="indefinite"
//                     />
//                   </circle>
//                 </svg>
//               </div>
//             ) : (
//               <div className="grid grid-cols-2 md:grid-cols-2 gap-5">
//                 <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                   {imageURL && <BespokeHouse imageURL={imageURL} labellingResponse={labellingResponse} />}
//                 </div>
//                 <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                   {labellingResponse && <AssessmentScore labellingResponse={labellingResponse} />}
//                 </div>
//                 <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                   <MapView />
//                 </div>
//                 <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                   {labellingResponse && <Recommendation labellingResponse={labellingResponse} />}
//                 </div>
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// } 