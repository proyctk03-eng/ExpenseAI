import urllib.request
import base64
import zlib

graph = 'graph TD\nA-->B'
compressed = zlib.compress(graph.encode('utf-8'))
b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')
url = 'https://kroki.io/mermaid/png/' + b64

req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req) as response:
        with open('test_kroki.png', 'wb') as out_file:
            out_file.write(response.read())
    print("Success")
except Exception as e:
    print("Error:", e)
