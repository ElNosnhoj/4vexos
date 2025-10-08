import requests

r = requests.get("http://192.168.169.1:8021/suicide")
print(r.status_code, r.text)