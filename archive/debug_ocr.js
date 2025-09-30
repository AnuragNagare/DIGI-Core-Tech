// Debug script to test OCR endpoint
async function debugOcr() {
    console.log('Starting OCR debug...');
    
    // Create a small test image
    const canvas = document.createElement('canvas');
    canvas.width = 100;
    canvas.height = 100;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, 100, 100);
    ctx.fillStyle = 'black';
    ctx.font = '12px Arial';
    ctx.fillText('Test Receipt', 10, 50);
    
    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
    console.log('Data URL length:', dataUrl.length);
    
    try {
        console.log('Making request...');
        const response = await fetch('/api/ocr/receipt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ imageDataUrl: dataUrl })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers.get('content-type'));
        
        const text = await response.text();
        console.log('Response text (first 200 chars):', text.substring(0, 200));
        
        try {
            const data = JSON.parse(text);
            console.log('✅ Valid JSON response:', data);
        } catch (e) {
            console.error('❌ JSON parsing failed:', e);
            console.log('Full response:', text);
        }
        
    } catch (error) {
        console.error('❌ Request failed:', error);
    }
}

// Run debug
console.log('Running OCR endpoint debug...');
debugOcr();