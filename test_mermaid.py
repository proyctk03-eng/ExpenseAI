import urllib.request
import base64
import json

# A small mermaid code
graph = 'graph TD; A-->B;'
# mermaid.ink uses base64 string
b64 = base64.urlsafe_b64encode(graph.encode('utf-8')).decode('utf-8')
url = 'https://mermaid.ink/img/' + b64

try:
    urllib.request.urlretrieve(url, 'test_mermaid.png')
    print("Success")
except Exception as e:
    print("Error:", e)
