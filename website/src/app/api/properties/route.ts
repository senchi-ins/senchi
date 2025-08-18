import { NextRequest, NextResponse } from 'next/server';
import { getUserIdFromRequest, isTokenValid } from '@/utils/auth';

interface PropertyResponse {
    id: string;
    name: string;
    address?: string;
    propertyId?: string;
    total_savings?: number;
    scores?: {
        overall: number;
        internal: number;
        external: number;
    };
    devices?: {
        connected: number;
        total: number;
    };
    alert?: {
        type: string;
        message: string;
        severity: 'high' | 'medium' | 'low';
    };
}

export async function POST(req: NextRequest) {
  try {
    // Get user ID from JWT token
    const userId = getUserIdFromRequest(req);
    
    if (!userId) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const token = req.cookies.get('jwt_token')?.value;
    if (!token || !isTokenValid(token)) {
      return NextResponse.json(
        { error: 'Invalid or expired token' },
        { status: 401 }
      );
    }

    const { property_name } = await req.json().catch(() => ({}));

    const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:8000';
    
    const response = await fetch(`${serverUrl}/api/v1/property/list`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        property_name: property_name || null,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch properties' },
        { status: response.status }
      );
    }

    const data: PropertyResponse[] = await response.json();
    
    return NextResponse.json({
      success: true,
      properties: data || []
    });

  } catch (error: unknown) {
    console.error('Properties API error:', error);
    
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
