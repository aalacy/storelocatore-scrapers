import requests
from bs4 import BeautifulSoup

url = "https://www.napaonline.com/en/find-store"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
print("soup: ", soup) # Getting captcha here
