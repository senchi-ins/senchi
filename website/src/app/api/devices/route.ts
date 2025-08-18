import { NextRequest, NextResponse } from 'next/server';

// Simple JWT decode function for extracting user_id
function decodeJWT(token: string): Record<string, unknown> {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding JWT:', error);
    throw error;
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { property_name } = body;

    if (!property_name) {
      return NextResponse.json(
        { error: 'property_name is required' },
        { status: 400 }
      );
    }

    // Get JWT token from cookies
    const token = request.cookies.get('jwt_token')?.value;
    
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Extract user_id from JWT token
    let user_id: string;
    try {
      const decodedToken = decodeJWT(token);
      const userIdFromToken = decodedToken.user_id;
      if (!userIdFromToken || typeof userIdFromToken !== 'string') {
        return NextResponse.json(
          { error: 'Invalid token: no user_id found' },
          { status: 401 }
        );
      }
      user_id = userIdFromToken;
    } catch (error) {
      console.error('Error decoding JWT token:', error);
      return NextResponse.json(
        { error: 'Invalid token' },
        { status: 401 }
      );
    }

    // Forward the request to your backend API with the JWT token
    const backendUrl = process.env.ZIGBEE_BACKEND_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/devices`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        user_id,
        property_name,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      throw new Error(`Backend API error: ${response.status} - ${errorText}`);
    }

    const devices = await response.json();
    return NextResponse.json(devices);

  } catch (error) {
    console.error('Error in devices API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch devices' },
      { status: 500 }
    );
  }
}
