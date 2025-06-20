export const apiBase = process.env.NEXT_PUBLIC_SENCHI_API_URL;

console.log('API Base URL:', apiBase);

export const test_api = async () => {
    const response = await fetch(`${apiBase}/api/v1/quote`, {
        method: "GET",
    });
    return response.json();
};

export const healthCheck = async (healthCheckUrl: string): Promise<Response> => {
    return fetch(healthCheckUrl);
};

export interface UploadFileResponse {
    code: number;
    data: {
        image_token: string;
    };
}

// Risk endpoints

export const uploadFile = async (
    address: string,
    heading: number = 120,
    bucket: string = "senchi-gen-dev"
): Promise<UploadFileResponse> => {
    const url = `${apiBase}/risk/upload-file?address=${encodeURIComponent(address)}&heading=${heading}&bucket=${bucket}`;
    console.log('Calling uploadFile with URL:', url);
    
    try {
        const response = await fetch(url, {
            method: "POST",
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('uploadFile response:', data);
        return data;
    } catch (error) {
        console.error('uploadFile error:', error);
        throw error;
    }
};



export interface GenerateModelResponse {
    [key: string]: unknown; // Adjust this type as needed
}

export const generateModel = async (
    file: unknown, // You may want to type this more strictly
    fileType: string = "png",
    modelType: string = "image_to_model"
): Promise<GenerateModelResponse> => {
    console.log('Calling generateModel with file:', file);
    const url = `${apiBase}/risk/generate-model`;
    console.log('Calling generateModel with URL:', url);
    
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                file,
                file_type: fileType,
                model_type: modelType,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('generateModel response:', data);
        return data;
    } catch (error) {
        console.error('generateModel error:', error);
        throw error;
    }
};


export interface GetModelOutputResponse {
    [key: string]: unknown; // Adjust this type as needed
}

export const getModelOutput = async (
    taskId: string
): Promise<GetModelOutputResponse> => {
    const url = `${apiBase}/risk/get-model-output?task_id=${encodeURIComponent(taskId)}`;
    console.log('Calling getModelOutput with URL:', url);
    
    try {
        const response = await fetch(url, {
            method: "GET",
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('getModelOutput response:', data);
        return data;
    } catch (error) {
        console.error('getModelOutput error:', error);
        throw error;
    }
};

export interface AnalyzeHouseResponse {
    category_scores: Array<{[key: string]: string }>;
    recommendations: Array<{[key: string]: string }>;
    final_score: number;
}

export const analyzeHouse = async (
    address: string,
    heading: number = 120,
    bucket: string = "senchi-gen-dev",
    zoom: number = 21,
    file_type: string = "png"
): Promise<AnalyzeHouseResponse> => {
    const params = new URLSearchParams({
        address: address,
        heading: heading.toString(),
        bucket: bucket,
        zoom: zoom.toString(),
        file_type: file_type
    });
    
    const response = await fetch(`${apiBase}/labelling/analyze-house?${params}`, {
        method: "POST",
    });
    return response.json();
};