import { NextResponse } from 'next/server';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export async function POST(request: Request) {
  console.log('Received receipt processing request');

  try {
    const body = await request.json().catch((e) => {
      console.error('Error parsing request body:', e);
      return {};
    }) as { imageDataUrl?: string };

    if (!body.imageDataUrl) {
      console.error('No imageDataUrl provided in request');
      return NextResponse.json(
        { success: false, error: 'imageDataUrl required' } as ApiResponse<any>,
        { status: 400 }
      );
    }

    console.log('Calling Python OCR service');

    // The Python service lives at this URL
    const ocrServiceUrl = process.env.NEXT_PUBLIC_OCR_SERVICE_URL || 'http://localhost:8000';

    // Convert base64 to buffer
    const base64Data = body.imageDataUrl.split(',')[1];
    const imageBuffer = Buffer.from(base64Data, 'base64');

    // Create proper multipart form data
    const boundary = '----formdata-boundary-' + Date.now();
    const CRLF = '\r\n';

    let postData = '';
    postData += `--${boundary}${CRLF}`;
    postData += `Content-Disposition: form-data; name="file"; filename="receipt.jpg"${CRLF}`;
    postData += `Content-Type: image/jpeg${CRLF}${CRLF}`;

    const postBuffer = Buffer.concat([
      Buffer.from(postData, 'utf8'),
      imageBuffer,
      Buffer.from(`${CRLF}--${boundary}${CRLF}`, 'utf8'),
      Buffer.from(`Content-Disposition: form-data; name="lang"${CRLF}${CRLF}`, 'utf8'),
      Buffer.from('en', 'utf8'),
      Buffer.from(`${CRLF}--${boundary}--${CRLF}`, 'utf8')
    ]);

    const response = await fetch(`${ocrServiceUrl}/ocr`, {
      method: 'POST',
      headers: {
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': postBuffer.length.toString(),
      },
      body: postBuffer,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('OCR service returned error status:', response.status, errorText);
      return NextResponse.json({ success: false, error: `OCR service failed: ${errorText}` }, { status: 500 });
    }

    const result = await response.json();

    if (!result.success) {
      console.error('OCR service returned success=false:', result.error);
      return NextResponse.json({ success: false, error: result.error || 'OCR processing failed in Python service' }, { status: 500 });
    }

    // Directly return the structured data from the Python service
    // The apiCall wrapper on the frontend will handle the { success: true, data: result } structure
    return NextResponse.json({ success: true, data: result });

  } catch (error) {
    console.error('Error processing receipt:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to process receipt';
    return NextResponse.json(
      { success: false, error: errorMessage } as ApiResponse<any>,
      { status: 500 }
    );
  }
}
