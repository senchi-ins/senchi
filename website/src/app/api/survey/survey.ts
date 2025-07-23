import { useRouter } from 'next/navigation';


export const SENCHI_API_BASE = process.env.NEXT_PUBLIC_SENCHI_API_URL;
export const SURVEY_WEB_URL = process.env.NEXT_PUBLIC_SENCHI_WEB_URL;

export interface AddressRequest {
  address: string;
}

export interface RiskQuestion {
  question: string;
  risk_type: string;
  importance: string;
  rubric: string;
  requires_photo: boolean;
  risk_level: string;
  order?: number;
  type?: "MULTIPLE_CHOICE" | "TEXT" | "PHOTO_UPLOAD";
  text?: string;
  required?: boolean;
  options?: string[];
}

export interface LocationRiskResponse {
  location_risks: Record<string, string>;
  questions: RiskQuestion[];
}

export async function fetchLocationSurvey(address: string): Promise<LocationRiskResponse> {
  const response = await fetch(`${SENCHI_API_BASE}/external/survey`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address }),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

// Auth and survey completion
// Adjust these types as needed to match your backend
export interface CreateSurveyRequest {
  title: string;
  description?: string;
  workspaceId?: string;
  questions: Array<{
    order: number;
    type: 'TEXT' | 'MULTIPLE_CHOICE' | 'PHOTO_UPLOAD';
    text: string;
    required: boolean;
    options?: string[]; // or your QuestionOption type
  }>;
}

export interface CreateSurveyResponse {
  id: string;
}

export async function createSurveyAndRedirect(
  surveyData: CreateSurveyRequest,
  router: ReturnType<typeof useRouter>
): Promise<void> {
  try {
    const response = await fetch(`${SURVEY_WEB_URL}/api/proxy-create-survey`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(surveyData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create survey');
    }

    const data: CreateSurveyResponse = await response.json();

    router.push(`${SURVEY_WEB_URL}/survey/${data.id}/landing`);
  } catch (error: unknown) {
    // Handle error (show toast, modal, etc.)
    alert((error as Error).message || 'An error occurred');
  }
}