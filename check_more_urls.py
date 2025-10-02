import requests

urls = [
    'https://raw.githubusercontent.com/ReceiptManager/reciept-images/master/receipts/receipt-1.jpg',
    'https://raw.githubusercontent.com/cvision-ai/receipt-parser/master/tests/data/receipt_1.jpg',
    'https://raw.githubusercontent.com/Courtbilly/receipt-parser/master/test_receipt.jpg',
    'https://raw.githubusercontent.com/Receiptary/receipt-samples/master/samples/receipt1.png',
    'https://raw.githubusercontent.com/clovaai/receipt-scene-text-recognition/master/dataset/receipt_1.jpg'
]

headers={'User-Agent':'Mozilla/5.0'}

for url in urls:
    try:
        r = requests.get(url, timeout=10, headers=headers)
        print(url, r.status_code, len(r.content))
    except Exception as e:
        print(url, 'ERROR', e)
