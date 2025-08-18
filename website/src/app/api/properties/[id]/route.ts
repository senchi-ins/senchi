import { NextRequest, NextResponse } from 'next/server';
import { getUserIdFromRequest, isTokenValid } from '@/utils/auth';

interface PropertyResponse {
    id: string;
    name: string;
    address?: string;
    propertyId?: string;
    property_type?: string;
    description?: string;
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

export async function GET(
  req: NextRequest,
  context: { params: Promise<{ id: string }> }
) {
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

    const params = await context.params;
    const propertyId = params.id;

    const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:8000';
    
    // First, get all properties to find the one with matching ID
    const response = await fetch(`${serverUrl}/api/v1/property/list`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        property_name: null,
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
    
    // Find the property with the matching ID
    const property = data.find(p => p.id === propertyId);
    
    if (!property) {
      return NextResponse.json(
        { error: 'Property not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      property: property
    });

  } catch (error: unknown) {
    console.error('Property API error:', error);
    
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
