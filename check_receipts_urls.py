import requests

urls = [
    'https://raw.githubusercontent.com/chandrikadeb7/Receipt-Scanner/master/test.jpg',
    'https://raw.githubusercontent.com/sharma-shruti/ReceiptOCR/master/receipt.jpg',
    'https://raw.githubusercontent.com/napsternxg/receipt-scanner/master/assets/receipt.jpg',
    'https://raw.githubusercontent.com/jrozner/ReceiptProcessor/master/receipt.jpg',
]

for url in urls:
    try:
        r = requests.get(url, timeout=10)
        print(url, r.status_code, len(r.content))
    except Exception as e:
        print(url, 'ERROR', e)
