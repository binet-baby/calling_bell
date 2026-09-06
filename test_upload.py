import urllib.request
body = b'--boundary\r\nContent-Disposition: form-data; name="name"\r\n\r\nTest Name\r\n--boundary\r\nContent-Disposition: form-data; name="photo"; filename="test.png"\r\nContent-Type: image/png\r\n\r\nfakeimagebytes\r\n--boundary--\r\n'
req = urllib.request.Request('http://127.0.0.1:5000/register', data=body, headers={'Content-Type': 'multipart/form-data; boundary=boundary'})
try:
    print(urllib.request.urlopen(req).read().decode())
except Exception as e:
    print(e)
