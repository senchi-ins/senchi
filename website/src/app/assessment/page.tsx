// "use client"

// import React, { useState, useEffect } from 'react'
// // import Header from '../components/Header'
// import Search from './search'
// import BespokeHouse from '../generated/bespokeHouse'

// import { uploadFile, generateModel, getModelOutput, analyzeHouse, AnalyzeHouseResponse } from '@/utils/api'
// import AssessmentScore from './score'
// import MapView from './mapView'
// import Recommendation from './recommendation'
// import { fallback_url } from '@/utils/fallback'
// // import sampleReturn from '@/utils/sampleReturn.json'

// export default function Assessment() {
//   const [input, setInput] = useState("");
//   const [imageURL, setImageURL] = useState(fallback_url);
//   const [modelLoading, setModelLoading] = useState(false);
//   const [analysisLoading, setAnalysisLoading] = useState(false);
//   const [enterPressed, setEnterPressed] = useState(false);
//   const [labellingResponse, setLabellingResponse] = useState<AnalyzeHouseResponse | undefined>(undefined);

//   useEffect(() => {
//     if (!enterPressed) return;

//     // const fetchModel = async () => {
//     //   // console.log('=== Starting fetchModel pipeline ===');
//     //   setModelLoading(true);
//     //   try {
//     //     // Upload the address to the API
//     //     // console.log('Step 1: Calling uploadFile...');
//     //     const upload_response = await uploadFile(input);
//     //     // console.log('Step 1 complete - Full upload_response:', upload_response);
        
//     //     // Check if the response has the expected structure
//     //     if (!upload_response || typeof upload_response !== 'object') {
//     //       throw new Error('Invalid upload response format');
//     //     }
        
//     //     // Try to extract the image token from the response
//     //     let imageToken;
//     //     if ('data' in upload_response && upload_response.data && typeof upload_response.data === 'object' && 'image_token' in upload_response.data) {
//     //       imageToken = upload_response.data.image_token;
//     //     } else if ('image_token' in upload_response) {
//     //       imageToken = upload_response.image_token;
//     //     } else {
//     //       console.error('Could not find image_token in response. Please refresh the page and try again.');
//     //       throw new Error('No image_token found in upload response');
//     //     }
        
//     //     // console.log(`Step 1 complete - imageToken extracted: ${imageToken}`);
        
//     //     // Generate the model - pass the correct file structure
//     //     // console.log('Step 2: Calling generateModel...');
//     //     const fileData = {
//     //         type: "png",
//     //         file_token: imageToken  // Use the extracted imageToken string, not the full object
//     //     };
//     //     // console.log('Step 2 - Calling generateModel with fileData:', fileData);
        
//     //     // Add retry logic for generateModel
//     //     let generateSuccess = false;
//     //     let generateRetryCount = 0;
//     //     const maxGenerateRetries = 3;
//     //     let task: unknown = null;
        
//     //     while (!generateSuccess && generateRetryCount < maxGenerateRetries) {
//     //       try {
//     //         task = await generateModel(fileData, "png", "image_to_model");
//     //         // console.log('Step 2 complete - generateModel response:', task);
//     //         generateSuccess = true;
//     //       } catch (error) {
//     //         generateRetryCount++;
//     //         // console.log(`Step 2 - generateModel failed (retry ${generateRetryCount}/${maxGenerateRetries}):`, error);
            
//     //         if (generateRetryCount >= maxGenerateRetries) {
//     //           console.error('Step 2 - All generateModel retries failed');
//     //           throw error;
//     //         }
            
//     //         // Wait before retry
//     //         await new Promise(res => setTimeout(res, 1000));
//     //       }
//     //     }
        
//     //     // Use type guards to safely access task_id and result
//     //     const taskId = (task && typeof task === 'object' && 'data' in task && task.data && typeof task.data === 'object' && 'task_id' in task.data) ? (task.data as { task_id?: string }).task_id : undefined;
//     //     if (!taskId) {
//     //       console.error('No task_id found in generateModel response:', task);
//     //       throw new Error('No task_id returned from generateModel');
//     //     }
//     //     // console.log(`Step 2 complete - taskId extracted: ${taskId}`);

//     //     // Wait for model output - single request that waits for completion
//     //     // console.log('Step 3: Waiting for model generation to complete...');
        
//     //     // Add retry logic for getModelOutput
//     //     let pollSuccess = false;
//     //     let retryCount = 0;
//     //     const maxRetries = 3;
//     //     let model_output: unknown = null;
        
//     //     while (!pollSuccess && retryCount < maxRetries) {
//     //       try {
//     //         // console.log(`Step 3 - Attempt ${retryCount + 1}/${maxRetries} to get model output...`);
//     //         model_output = await getModelOutput(taskId);
//     //         // console.log(`Step 3 - Model output received:`, model_output);
            
//     //         // Check if the response indicates an error
//     //         if (model_output && typeof model_output === 'object' && 'error' in model_output) {
//     //           // console.log(`Step 3 - Backend returned error: ${model_output.error}`);
//     //           retryCount++;
//     //           if (retryCount >= maxRetries) {
//     //             console.error(`Failed to generate model, using placeholder model`);
//     //             throw new Error(`Backend error: ${model_output.error}`);
//     //           }
//     //           // Wait before retry
//     //           await new Promise(res => setTimeout(res, 2000));
//     //           continue;
//     //         }
            
//     //         // Check if we have a successful response with the expected structure
//     //         if (model_output && typeof model_output === 'object') {
//     //           // Check for either the new structure (pbr_model_url) or the old structure (data.result.pbr_model.url)
//     //           const hasNewStructure = 'pbr_model_url' in model_output;
//     //           const hasOldStructure = 'data' in model_output && 
//     //                                 model_output.data && 
//     //                                 typeof model_output.data === 'object' && 
//     //                                 'result' in model_output.data &&
//     //                                 model_output.data.result &&
//     //                                 typeof model_output.data.result === 'object' &&
//     //                                 'pbr_model' in model_output.data.result;
              
//     //           if (hasNewStructure || hasOldStructure) {
//     //             // console.log(`Step 3 - Success! Model output has valid structure`);
//     //             pollSuccess = true;
//     //             break;
//     //           } else {
//     //             // console.log(`Step 3 - Response doesn't have expected structure:`, model_output);
//     //             retryCount++;
//     //             if (retryCount >= maxRetries) {
//     //               // console.error(`Step 3 - All retries failed - invalid response structure`);
//     //               throw new Error(`Invalid response structure from backend`);
//     //             }
//     //             // Wait before retry
//     //             await new Promise(res => setTimeout(res, 2000));
//     //             continue;
//     //           }
//     //         } else {
//     //           // console.log(`Step 3 - Invalid response format:`, model_output);
//     //           retryCount++;
//     //           if (retryCount >= maxRetries) {
//     //             // console.error(`Step 3 - All retries failed - invalid response format`);
//     //             throw new Error(`Invalid response format from backend`);
//     //           }
//     //           // Wait before retry
//     //           await new Promise(res => setTimeout(res, 2000));
//     //           continue;
//     //         }
//     //       } catch (error) {
//     //         retryCount++;
//     //         // console.log(`Step 3 - Attempt ${retryCount}/${maxRetries} failed:`, error);
            
//     //         if (retryCount >= maxRetries) {
//     //           // console.error(`Step 3 - All retries failed`);
//     //           throw error; // Re-throw to be caught by outer try-catch
//     //         }
            
//     //         // Wait before retry
//     //         await new Promise(res => setTimeout(res, 2000));
//     //       }
//     //     }

//     //     // Extract the model URL from the response
//     //     // console.log('Step 4: Extracting model URL...');
//     //     let model_url: string | undefined = undefined;
        
//     //     if (model_output && typeof model_output === 'object') {
//     //       // Try the new structure first (pbr_model_url)
//     //       if ('pbr_model_url' in model_output && typeof model_output.pbr_model_url === 'string') {
//     //         model_url = model_output.pbr_model_url;
//     //         // console.log(`Step 4 - Found model URL using new structure: ${model_url}`);
//     //       }
//     //       // Try the old structure (data.result.pbr_model.url)
//     //       else if ('data' in model_output && model_output.data && typeof model_output.data === 'object' && 'result' in model_output.data) {
//     //         const data = (model_output as { data?: unknown }).data;
//     //         if (data && typeof data === 'object' && 'result' in data) {
//     //           const result = (data as { result?: unknown }).result;
//     //           if (result && typeof result === 'object' && 'pbr_model' in result) {
//     //             const pbr_model = (result as { pbr_model?: unknown }).pbr_model;
//     //             if (pbr_model && typeof pbr_model === 'object' && 'url' in pbr_model) {
//     //               const url = (pbr_model as { url?: unknown }).url;
//     //               if (typeof url === 'string') {
//     //                 model_url = url;
//     //                 // console.log(`Step 4 - Found model URL using old structure: ${model_url}`);
//     //               }
//     //             }
//     //           }
//     //         }
//     //       }
//     //     }
        
//     //     if (model_url) {
//     //       // console.log(`Step 4 complete - Model URL set: ${model_url}`);
//     //       setImageURL(model_url);
//     //     } else {
//     //       // console.error('Step 4 failed - Could not extract model URL from response');
//     //       // console.error('Response structure:', model_output);
//     //       throw new Error('Could not extract model URL from response');
//     //     }
        
//     //     // console.log('=== fetchModel pipeline completed successfully ===');
//     //   } catch (error) {
//     //     // console.error('=== fetchModel pipeline failed ===');
//     //     console.error('Error details:', error);
//     //     // Optionally handle error in UI
//     //   } finally {
//     //     setModelLoading(false);
//     //   }
//     // };

//     const performHouseAnalysis = async () => {
//       // console.log('=== Starting performHouseAnalysis ===');
//       setAnalysisLoading(true);
//       try {
//         // Simulate a network delay for robust testing
//         await new Promise(resolve => setTimeout(resolve, 1000));
//         // console.log('Calling analyzeHouse...');
//         const response = await analyzeHouse(input);
//         // console.log('analyzeHouse response:', response);
//         setLabellingResponse(response);
//         // console.log('=== performHouseAnalysis completed successfully ===');
//       } catch (e) {
//         // console.error("=== performHouseAnalysis failed ===");
//         console.log(e);
//         console.error("Failed to analyze house. Please refresh the page and try again.");
//         // Optionally, handle the error in the UI
//       } finally {
//         setAnalysisLoading(false);
//       }
//     }

//     // Run the pipeline sequentially to avoid race conditions
//     const runPipeline = async () => {
//       // console.log('=== Starting full pipeline ===');
//       try {
//         // await fetchModel();
//         await performHouseAnalysis();
//         // console.log('=== Full pipeline completed ===');
//       } catch {
//         // console.error('=== Full pipeline failed ===');
//         console.error('Pipeline error. Please refresh the page and try again.');
//       }
//     };

//     // TODO: Uncomment this when the pipeline is ready
//     runPipeline();
//   }, [enterPressed, input]);

//   return (
//     <div className="min-h-screen flex flex-col">
//       {/* <Header /> */}
//       <div className="bg-senchi-background flex-1 w-full">
//         <div className="max-w-7xl mx-auto px-4 md:px-16">
//           {enterPressed && (
//             <div className="flex flex-col pt-10 pb-6 gap-2 max-w-3xl w-full">
//               <h1 className="text-2xl font-bold text-senchi-main text-left w-full mb-1">
//                 Property Assessment Dashboard
//               </h1>
//               <h4 className="text-base text-gray-700 text-left w-full mb-1">
//                 {`AI-powered home evaluation and risk analysis for ${input}`}
//               </h4>
//               <div className="text-sm text-gray-500 text-left w-full italic rounded py-1">
//                 Note: This dashboard is for demo purposes only. We&apos;re continuing to refine our models and the full dashboard will be available soon.
//               </div>
//             </div>
//           )}
//           <div className="flex items-center justify-center w-full min-h-[80vh]">
//             {!enterPressed ? (
//               <Search setInput={setInput} input={input} setEnterPressed={setEnterPressed} />
//             ) : (
//               (modelLoading || analysisLoading) ? (
//                 <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: 80 }}>
//                   <svg
//                     width="48"
//                     height="48"
//                     viewBox="0 0 48 48"
//                     fill="none"
//                     style={{ display: "block" }}
//                     xmlns="http://www.w3.org/2000/svg"
//                   >
//                     <circle
//                       cx="24"
//                       cy="24"
//                       r="20"
//                       stroke="#EBE9FC"
//                       strokeWidth="6"
//                       fill="none"
//                     />
//                     <circle
//                       cx="24"
//                       cy="24"
//                       r="20"
//                       stroke="#240DBF"
//                       strokeWidth="6"
//                       strokeLinecap="round"
//                       fill="none"
//                       strokeDasharray="100"
//                       strokeDashoffset="60"
//                     >
//                       <animateTransform
//                         attributeName="transform"
//                         type="rotate"
//                         from="0 24 24"
//                         to="360 24 24"
//                         dur="1s"
//                         repeatCount="indefinite"
//                       />
//                     </circle>
//                   </svg>
//                 </div>
//               ) : (
//                 <div className="grid grid-cols-2 md:grid-cols-2 gap-5">
//                   <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                     {imageURL && <BespokeHouse imageURL="/3D/sample_house.glb" labellingResponse={labellingResponse} />}
//                   </div>
//                   <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                     {labellingResponse && <AssessmentScore labellingResponse={labellingResponse} />}
//                   </div>
//                   <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                     <MapView />
//                   </div>
//                   <div className="flex flex-col items-center justify-center bg-white rounded-2xl shadow min-h-[500px] w-full max-w-md">
//                     {labellingResponse && <Recommendation labellingResponse={labellingResponse} />}
//                   </div>
//                 </div>
//               )
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }
