import { cookies } from 'next/headers';
import { NextRequest } from 'next/server';

export interface UserInfo {
  user_id: string;
  location_id: string | null;
  device_serial: string | null;
  full_name: string;
  iat: number;
  exp: number;
  created_at: string;
}

export async function getUserIdFromToken(): Promise<string | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('jwt_token')?.value;
    
    if (!token) {
      return null;
    }

    // Decode JWT token to get user info
    const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
    return payload.user_id;
  } catch (error) {
    console.error('Error extracting user ID from token:', error);
    return null;
  }
}

export function getUserIdFromRequest(req: NextRequest): string | null {
  try {
    const token = req.cookies.get('jwt_token')?.value;
    
    if (!token) {
      return null;
    }

    // Decode JWT token to get user info
    const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
    return payload.user_id;
  } catch (error) {
    console.error('Error extracting user ID from request:', error);
    return null;
  }
}

export function isTokenValid(token: string): boolean {
  try {
    const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp > currentTime;
  } catch (error) {
    console.error('Error validating token:', error);
    return false;
  }
}
