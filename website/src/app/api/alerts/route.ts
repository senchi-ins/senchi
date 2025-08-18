import { NextRequest, NextResponse } from 'next/server';
import { getUserIdFromRequest, isTokenValid } from '@/utils/auth';

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
    
    // Send as POST request with body to match your backend
    const response = await fetch(`${serverUrl}/api/v1/property/alerts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        property_id: property_id
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch alerts' },
        { status: response.status }
      );
    }

    const backendData = await response.json();
    console.log('Backend alerts response:', backendData);
    
    // Transform the backend response to match frontend expectations
    // Backend returns: [PropertyAlerts(...), PropertyAlerts(...)]
    // Frontend expects: { alerts: [{ id, type, message, severity, timestamp, details }] }
    
    let transformedAlerts: Array<{
      id: string;
      type: string;
      message: string;
      severity: 'high' | 'medium' | 'low';
      timestamp: string;
      details?: string;
    }> = [];
    
    if (Array.isArray(backendData)) {
      transformedAlerts = backendData.map((alert, index) => {
        return {
          id: `alert-${index}`,
          type: alert.alert_type || 'unknown',
          message: alert.message || 'Unknown alert',
          severity: (alert.severity || 'medium') as 'high' | 'medium' | 'low',
          timestamp: alert.timestamp || new Date().toISOString(),
          details: alert.message || undefined
        };
      });
    }
    
    return NextResponse.json({
      success: true,
      alerts: transformedAlerts
    });

  } catch (error: unknown) {
    console.error('Alerts API error:', error);
    
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
