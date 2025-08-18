interface PropertyData {
  address: string;
  [key: string]: unknown;
}

// Temporary storage for property data (in production, you might want to use Redis or similar)
const propertyDataStore = new Map<string, PropertyData>();

// Generate a deterministic short hash based on the address
function generateShortHash(address: string): string {
  // Simple hash function - convert address to a number and then to base36
  let hash = 0;
  for (let i = 0; i < address.length; i++) {
    const char = address.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Convert to base36 and take first 6 characters
  return Math.abs(hash).toString(36).substring(0, 6);
}

// Store property data and return a deterministic short hash
export function storePropertyData(data: PropertyData): string {
  const address = data.address || '';
  const hash = generateShortHash(address);
  propertyDataStore.set(hash, data);
  
  // Clean up old data after 5 minutes
  setTimeout(() => {
    propertyDataStore.delete(hash);
  }, 5 * 60 * 1000);
  
  return hash;
}

// Retrieve property data by hash
export function getPropertyData(hash: string): PropertyData | null {
  return propertyDataStore.get(hash) || null;
}

// Clean up data immediately (for testing)
export function cleanupPropertyData(hash: string): void {
  propertyDataStore.delete(hash);
}
