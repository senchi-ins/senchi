import { NextRequest, NextResponse } from 'next/server';
import { addToWaitlist } from '@/utils/waitlist';

export async function POST(req: NextRequest) {
  try {
    const { email } = await req.json();
    if (!email || typeof email !== 'string') {
      return NextResponse.json({ error: 'Invalid email' }, { status: 400 });
    }
    await addToWaitlist(email);
    return NextResponse.json({ success: true });
  } catch (error: unknown) {
    let message = 'Server error';
    if (error && typeof error === 'object' && 'message' in error && typeof (error as { message?: unknown }).message === 'string') {
      message = (error as { message: string }).message;
    }
    return NextResponse.json({ error: message }, { status: 500 });
  }
} 