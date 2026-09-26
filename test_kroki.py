import urllib.request
import base64
import zlib
import urllib.parse

graph = 'graph TD\nA-->B'
# kroki expects zlib compressed then base64 encoded
compressed = zlib.compress(graph.encode('utf-8'))
b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')
url = 'https://kroki.io/mermaid/png/' + b64

try:
    urllib.request.urlretrieve(url, 'test_kroki.png')
    print("Success")
except Exception as e:
    print("Error:", e)
