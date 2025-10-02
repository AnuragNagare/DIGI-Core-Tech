import requests

urls = [
    'https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/v2.1/Receipts/sample-data/contoso-receipt.png',
    'https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/v2.1/Receipts/sample-data/contoso-all-items.jpg',
    'https://raw.githubusercontent.com/Azure/azure-document-intelligence-samples/main/demo-data/receipts/contoso-receipt.png',
    'https://raw.githubusercontent.com/Azure/azure-document-intelligence-samples/main/demo-data/receipts/contoso-all-items.jpg'
]

for url in urls:
    try:
        r = requests.get(url, timeout=10)
        print(url, r.status_code, len(r.content))
    except Exception as e:
        print(url, 'ERROR', e)
