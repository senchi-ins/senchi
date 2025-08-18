import { NextRequest, NextResponse } from 'next/server';

interface LoginRequest {
  email: string;
  password: string;
}

interface UserInfoResponse {
  user_id: string;
  location_id: string | null;
  device_serial: string | null;
  full_name: string;
  iat: number;
  exp: number;
  created_at: string;
}

interface TokenResponse {
  jwt_token: string;
  expires_at: string;
  user_info: UserInfoResponse;
}

export async function POST(req: NextRequest) {
  try {
    const { email, password }: LoginRequest = await req.json();
    
    // Validate request body
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' }, 
        { status: 400 }
      );
    }

    // Get server URL from environment variable or use default
    const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:8000';
    
    const response = await fetch(`${serverUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Login failed' },
        { status: response.status }
      );
    }

    const data: TokenResponse = await response.json();
    
    // Set JWT token in HTTP-only cookie for security
    const responseHeaders = new Headers();
    responseHeaders.append('Set-Cookie', `jwt_token=${data.jwt_token}; HttpOnly; Path=/; Max-Age=${60 * 60 * 24 * 7}; SameSite=Strict`);
    
    return NextResponse.json(
      { 
        success: true,
        user_info: data.user_info,
        expires_at: data.expires_at
      },
      { 
        status: 200,
        headers: responseHeaders
      }
    );

  } catch (error: unknown) {
    console.error('Login API error:', error);
    
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
