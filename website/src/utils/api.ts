let apiBase = process.env.NEXT_PUBLIC_SENCHI_API_URL;

// If the site is loaded over HTTPS, we must use an HTTPS API endpoint.
// This logic enforces HTTPS for the API URL on the client-side.
if (typeof window !== 'undefined' && apiBase && window.location.protocol === 'https:') {
  // Replace "http://" with "https://" at the beginning of the string.
  apiBase = apiBase.replace(/^http:/, 'https:');
}

export { apiBase };

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
    
    try {
        const response = await fetch(url, {
            method: "POST",
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
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
    const url = `${apiBase}/risk/generate-model`;
    
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
    
    try {
        const response = await fetch(url, {
            method: "GET",
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
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

export const proxyGLB = async (url: string): Promise<string> => {
    // console.log('proxyGLB called with URL:', url);
    
    const response = await fetch(`${apiBase}/proxy?url=${encodeURIComponent(url)}`, {
        method: "GET",
    });
    
    // console.log('Proxy response status:', response.status);
    // console.log('Proxy response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
        console.log(response);
        throw new Error(`Failed to fetch GLB: ${response.status} ${response.statusText}`);
    }
    
    // For binary files like GLB, we need to get the blob and create a blob URL
    const blob = await response.blob();
    // console.log('Blob size:', blob.size, 'bytes');
    // console.log('Blob type:', blob.type);
    
    // Check if the blob contains valid GLB data
    const arrayBuffer = await blob.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);
    // const firstBytes = Array.from(uint8Array.slice(0, 8)).map(b => b.toString(16).padStart(2, '0')).join(' ');
    // console.log('First 8 bytes (hex):', firstBytes);
    
    // GLB files start with "glTF" magic number
    // const glbMagic = [0x67, 0x6C, 0x54, 0x46]; // "glTF" in ASCII

    // Debugging code
    // const isGLB = uint8Array.length >= 4 && 
    //               uint8Array[0] === glbMagic[0] && 
    //               uint8Array[1] === glbMagic[1] && 
    //               uint8Array[2] === glbMagic[2] && 
    //               uint8Array[3] === glbMagic[3];
    
    // console.log('Is valid GLB file:', isGLB);
    
    // Check if it's HTML (error page)
    const textDecoder = new TextDecoder();
    const firstChars = textDecoder.decode(uint8Array.slice(0, 20));
    
    if (firstChars.includes('<!DOCTYPE') || firstChars.includes('<html')) {
        console.error('ERROR: Response contains HTML instead of GLB data.');
        throw new Error('Proxy returned HTML error page instead of GLB file');
    }
    
    const blobUrl = URL.createObjectURL(blob);
    
    return blobUrl;
};