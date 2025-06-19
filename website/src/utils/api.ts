export const apiBase = process.env.NEXT_PUBLIC_SENCHI_API_URL;

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
    const response = await fetch(`${apiBase}/risk/upload-file?address=${encodeURIComponent(address)}&heading=${heading}&bucket=${bucket}`,
        {
            method: "POST",
        }
    );
    return response.json();
};



export interface GenerateModelResponse {
    [key: string]: unknown; // Adjust this type as needed
}

export const generateModel = async (
    file: unknown, // You may want to type this more strictly
    fileType: string = "png",
    modelType: string = "image_to_model"
): Promise<GenerateModelResponse> => {
    const response = await fetch(`${apiBase}/risk/generate-model`, {
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
    return response.json();
};


export interface GetModelOutputResponse {
    [key: string]: unknown; // Adjust this type as needed
}

export const getModelOutput = async (
    taskId: string
): Promise<GetModelOutputResponse> => {
    const url = `${apiBase}/risk/get-model-output?task_id=${encodeURIComponent(taskId)}`;
    const response = await fetch(url, {
        method: "GET",
    });
    return response.json();
};