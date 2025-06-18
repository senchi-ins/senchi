export const api_url = process.env.NEXT_PUBLIC_SENCHI_API_URL;

export const test_api = async () => {
    const response = await fetch(`${api_url}/api/v1/quote`, {
        method: "GET",
    });
    return response.json();
};

export const upload_address = async (address: string) => {
    const response = await fetch(`${api_url}/upload-file`, {
        method: "POST",
        body: JSON.stringify({ address }),
    });
    return response.json();
};

export const generate_model = async (address: string) => {
    const response = await fetch(`${api_url}/generate-model`, {
        method: "POST",
        body: JSON.stringify({ address }),
    });
    return response.json();
};

export const get_model_output = async (model_id: string) => {
    const response = await fetch(`${api_url}/get-model-output`, {
        method: "GET",
        body: JSON.stringify({ model_id }),
    });
    return response.json();
};