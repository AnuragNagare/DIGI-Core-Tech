import requests

urls = [
    'https://raw.githubusercontent.com/caltechlibrary/sample-data/main/receipts/receipt-001.png',
    'https://raw.githubusercontent.com/caltechlibrary/sample-data/main/receipts/receipt-002.png',
    'https://raw.githubusercontent.com/caltechlibrary/sample-data/main/receipts/receipt-003.png'
]

for url in urls:
    try:
        r = requests.get(url, timeout=10)
        print(url, r.status_code, len(r.content))
    except Exception as e:
        print(url, 'ERROR', e)
