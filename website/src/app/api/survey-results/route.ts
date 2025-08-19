import { NextRequest, NextResponse } from 'next/server';
import { getUserIdFromRequest, isTokenValid } from '@/utils/auth';

interface SurveyResultsResponse {
  id: string;
  property_id: string;
  completed_at: string;
  answers: Array<{
    question: string;
    answer: string;
    score?: number;
  }>;
  total_score?: number;
  recommendations?: Array<{
    action: string;
    severity: 'high' | 'medium' | 'low';
    rationale: string;
  }>;
}

export async function POST(request: NextRequest) {
  try {
    // Get user ID from JWT token
    const userId = getUserIdFromRequest(request);
    
    if (!userId) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const token = request.cookies.get('jwt_token')?.value;
    if (!token || !isTokenValid(token)) {
      return NextResponse.json(
        { error: 'Invalid or expired token' },
        { status: 401 }
      );
    }

    // Get property_id from request body
    const { property_id } = await request.json();

    if (!property_id) {
      return NextResponse.json(
        { error: 'property_id is required' },
        { status: 400 }
      );
    }

    const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:8000';
    
    const response = await fetch(`${serverUrl}/api/v1/external/assessments/property/${property_id}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        // No survey results found
        return NextResponse.json(
          { error: 'Survey results not found' },
          { status: 404 }
        );
      }
      
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch survey results' },
        { status: response.status }
      );
    }

    const backendData: SurveyResultsResponse = await response.json();
    console.log('Backend survey results response:', backendData);
    
    return NextResponse.json({
      success: true,
      ...backendData
    });

  } catch (error: unknown) {
    console.error('Survey results API error:', error);
    
    let message = 'Internal server error';
    if (error && typeof error === 'object' && 'message' in error && typeof (error as { message?: unknown }).message === 'string') {
      message = (error as { message: string }).message;
    }
    
    return NextResponse.json(
      { error: message },
      { status: 500 }
    );
  }
}
