import requests

urls = [
    'https://raw.githubusercontent.com/UB-Mannheim/tesseract/wiki/receipt-example.jpg',
    'https://raw.githubusercontent.com/tesseract-ocr/tesseract/master/doc/images/phototest.tif',
    'https://raw.githubusercontent.com/aws-samples/amazon-textract-document-understanding-sample/master/docs/sample_forms/expense_receipt.png'
]

for url in urls:
    try:
        r = requests.get(url, timeout=10)
        print(url, r.status_code, len(r.content))
    except Exception as e:
        print(url, 'ERROR', e)
