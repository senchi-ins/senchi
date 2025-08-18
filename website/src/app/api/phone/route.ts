import { NextRequest, NextResponse } from 'next/server';
import { getUserIdFromRequest, isTokenValid } from '@/utils/auth';

interface AddManagerPhoneNumberRequest {
  user_id: string;
  property_id: string;
  phone_number: string;
  role?: string;
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

    // Validate token
    const token = req.cookies.get('jwt_token')?.value;
    if (!token || !isTokenValid(token)) {
      return NextResponse.json(
        { error: 'Invalid or expired token' },
        { status: 401 }
      );
    }

    // Get request body
    const { name, property_name, property_id, number, role } = await req.json();
    
    // Validate request body
    if (!name || !property_id || !number) {
      return NextResponse.json(
        { error: 'Name, property ID, and phone number are required' },
        { status: 400 }
      );
    }

    // Prepare request for your server
    const serverRequest: AddManagerPhoneNumberRequest = {
      user_id: userId,
      property_id: property_id,
      phone_number: number,
      role: role || 'manager'
    };

    // Send request to your server
    const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:8000';
    
    const response = await fetch(`${serverUrl}/api/v1/property/add-manager-phone-number`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(serverRequest),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to add phone number' },
        { status: response.status }
      );
    }

    await response.json(); // Consume the response
    
    // Return the phone number data in the format expected by the frontend
    return NextResponse.json({
      id: Date.now().toString(), // Generate a temporary ID
      name: name,
      number: number,
      property_name: property_name
    });

  } catch (error: unknown) {
    console.error('Phone API error:', error);
    
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
