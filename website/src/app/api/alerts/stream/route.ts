import { NextRequest } from 'next/server';
import { getUserIdFromRequest, isTokenValid } from '@/utils/auth';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const propertyId = searchParams.get('property_id');

  if (!propertyId) {
    return new Response('property_id is required', { status: 400 });
  }

  // Check authentication
  const userId = getUserIdFromRequest(request);
  if (!userId) {
    return new Response('Authentication required', { status: 401 });
  }

  const token = request.cookies.get('jwt_token')?.value;
  if (!token || !isTokenValid(token)) {
    return new Response('Invalid or expired token', { status: 401 });
  }

  // Set up SSE headers
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      const sendEvent = (data: { alerts: {
        id: string;
        type: string;
        message: string;
        severity: 'high' | 'medium' | 'low';
        timestamp: string;
        details?: string;
      }[] }) => {
        const event = `data: ${JSON.stringify(data)}\n\n`;
        controller.enqueue(encoder.encode(event));
      };

      // Send initial data
      const fetchInitialAlerts = async () => {
        try {
          const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:8000';
          const response = await fetch(`${serverUrl}/api/v1/property/alerts`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ property_id: propertyId }),
          });

          if (response.ok) {
            const backendData = await response.json();
            const transformedAlerts = Array.isArray(backendData) 
              ? backendData.map((alert, index) => ({
                  id: `alert-${index}`,
                  type: alert.alert_type || 'unknown',
                  message: alert.message || 'Unknown alert',
                  severity: (alert.severity || 'medium') as 'high' | 'medium' | 'low',
                  timestamp: alert.timestamp || new Date().toISOString(),
                  details: alert.message || undefined
                }))
              : [];

            sendEvent({ alerts: transformedAlerts });
          }
        } catch (error) {
          console.error('Error fetching initial alerts:', error);
        }
      };

      fetchInitialAlerts();

      // Set up polling to simulate real-time updates
      // In a real implementation, this would be replaced with actual event-driven updates
      const interval = setInterval(async () => {
        try {
          const serverUrl = process.env.NEXT_PUBLIC_SERVER_URL || 'http://localhost:8000';
          const response = await fetch(`${serverUrl}/api/v1/property/alerts`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ property_id: propertyId }),
          });

          if (response.ok) {
            const backendData = await response.json();
            const transformedAlerts = Array.isArray(backendData) 
              ? backendData.map((alert, index) => ({
                  id: `alert-${index}`,
                  type: alert.alert_type || 'unknown',
                  message: alert.message || 'Unknown alert',
                  severity: (alert.severity || 'medium') as 'high' | 'medium' | 'low',
                  timestamp: alert.timestamp || new Date().toISOString(),
                  details: alert.message || undefined
                }))
              : [];

            sendEvent({ alerts: transformedAlerts });
          }
        } catch (error) {
          console.error('Error polling alerts:', error);
        }
      }, 30000); // Poll every 30 seconds

      // Cleanup on close
      return () => {
        clearInterval(interval);
      };
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Cache-Control',
    },
  });
}
