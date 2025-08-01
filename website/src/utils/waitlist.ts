import { GoogleSpreadsheet } from 'google-spreadsheet';
import { JWT } from 'google-auth-library';

const serviceAccountAuth = new JWT({
  email: process.env.NEXT_PUBLIC_GOOGLE_SERVICE_ACCOUNT_EMAIL,
  key: process.env.NEXT_PUBLIC_GOOGLE_PRIVATE_KEY,
  scopes: ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file'],
});

const SHEET_ID = '1qRAG7-aWdKak7-Ner_QOM34Tl6NTohmoeA3ZXxG9bWk';
const SHEET_TITLE = 'Waitlist';

export async function addToWaitlist(email: string): Promise<void> {
  try {
    const doc = new GoogleSpreadsheet(SHEET_ID, serviceAccountAuth);
    await doc.loadInfo();
    const sheet = doc.sheetsByTitle[SHEET_TITLE];
    if (!sheet) {
      throw new Error(`Sheet '${SHEET_TITLE}' not found.`);
    }
    await sheet.addRow({ Email: email });
  } catch (error) {
    console.error('Failed to add to waitlist:', error);
    throw error;
  }
}