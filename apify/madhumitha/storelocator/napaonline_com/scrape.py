import requests
from bs4 import BeautifulSoup

s = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Method': 'GET',
    'Authority': 'www.napaonline.com',
    'Path': '/en/find-store',
    'Scheme': 'https',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'upgrade-insecure-requests': 1
}

s.headers.update(headers)

url = "https://www.napaonline.com/en/find-store"
response = s.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
print("soup: ", soup) # Getting captcha here
